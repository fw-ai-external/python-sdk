"""Private SDK-owned trainer/deployment setup for Tinker-compatible recipes."""

from __future__ import annotations

import time
import logging
import warnings
from typing import Any
from dataclasses import field, replace, dataclass
from urllib.parse import urlencode
from concurrent.futures import ThreadPoolExecutor

from fireworks.training.sdk.client import FiretitanServiceClient, FiretitanTrainingClient
from fireworks.training.sdk.trainer import (
    TrainerJobConfig,
    CreatedTrainerJob,
    TrainerJobManager,
    TrainerServiceEndpoint,
)
from fireworks.training.sdk._constants import (
    POLL_INTERVAL_S,
    HOTLOAD_TIMEOUT_S,
    HTTP_READ_TIMEOUT_S,
    DEFAULT_TRAINER_TIMEOUT_S,
    REATTACH_SETTLE_TIMEOUT_S,
    DEPLOYMENT_READY_TIMEOUT_S,
)
from fireworks.training.sdk.deployment import (
    DEFAULT_DELTA_COMPRESSION,
    DeploymentInfo,
    DeploymentConfig,
    DeploymentManager,
    DeploymentSampler,
    FiretitanSamplingClient,
)
from fireworks.training.sdk._snapshot_chain import (
    build_incremental_metadata,
)

logger = logging.getLogger(__name__)

_DEPLOYMENT_ACCELERATOR_REGION_PREFIXES: tuple[tuple[str, str], ...] = (
    ("NVIDIA_H200", "US_VIRGINIA_1"),
    ("NVIDIA_B200", "US_OHIO_1"),
    ("NVIDIA_B300", "NA_BRITISHCOLUMBIA_1"),
)
DEPLOYMENT_TERMINAL_STATES = frozenset({"FAILED", "DELETED", "DELETING"})
DEPLOYMENT_SERVING_STATES = frozenset({"READY", "UPDATING"})


@dataclass(frozen=True)
class FiretitanProvisioningConfig:
    """FireTitan managed trainer/deployment configuration.

    Immutable: normalized once at the SDK boundary and never mutated by
    cookbook recipes. This is the single source of truth for SDK-managed
    trainer/deployment provisioning.
    """

    base_model: str
    tokenizer_model: str | None = None
    lora_rank: int = 0
    training_shape_id: str | None = None
    # Optional separate forward-only reference trainer shape. When set (or when
    # the policy is full-parameter), create_reference_client provisions a
    # dedicated reference trainer instead of reusing the policy session.
    reference_training_shape_id: str | None = None
    # Optional existing forward-only reference trainer to reattach to. When set,
    # it disables LoRA shared-reference and is never cleaned up on close.
    reference_trainer_job_id: str | None = None
    # SDK-owned separate references are cleaned by default. Sequential live
    # tests can keep them for later reattach and clean them explicitly.
    cleanup_reference_trainer_on_close: bool = True
    reference_required: bool = False
    deployment_shape: str | None = None
    trainer_job_id: str | None = None
    deployment_id: str | None = None
    create_deployment: bool = True
    # Forward-only trainer (no optimizer state). Set by the SDK when it
    # provisions a separate reference trainer; recipes never set this.
    forward_only: bool = False
    region: str | None = None
    deployment_region: str | None = None
    max_context_length: int | None = None
    learning_rate: float = 1e-5
    gradient_accumulation_steps: int = 1
    seed: int | None = None
    train_mlp: bool = True
    train_attn: bool = True
    train_unembed: bool = True
    node_count: int | None = None
    accelerator_type: str | None = None
    accelerator_count: int | None = None
    custom_image_tag: str | None = None
    extra_args: list[str] | None = None
    deployment_extra_args: list[str] | None = None
    deployment_extra_values: dict[str, str] | None = None
    trainer_replica_count: int | None = None  # data-parallel HSDP replicas for the trainer
    replica_count: int = 1  # inference deployment min/max replicas
    trainer_timeout_s: float = DEFAULT_TRAINER_TIMEOUT_S
    deployment_timeout_s: float = DEPLOYMENT_READY_TIMEOUT_S
    hotload_timeout_s: int = HOTLOAD_TIMEOUT_S
    reattach_settle_timeout_s: float = REATTACH_SETTLE_TIMEOUT_S
    reattach_poll_interval_s: float = POLL_INTERVAL_S
    cleanup_trainer_on_close: bool = False
    cleanup_deployment_on_close: str | None = None
    display_name: str | None = None
    purpose: str | None = None
    skip_validations: bool = False
    disable_speculative_decoding: bool = True

    def __post_init__(self) -> None:
        active_deployment_region = self.deployment_region if self.create_deployment else None
        if self.region and active_deployment_region and self.region != active_deployment_region:
            raise ValueError(
                f"deployment_region={active_deployment_region!r} conflicts with the trainer "
                f"region={self.region!r}: a hot-load deployment must be colocated with its "
                "trainer. Set a single region, or leave both unset for shape/control-plane defaults."
            )
        if active_deployment_region and not self.region:
            object.__setattr__(self, "region", active_deployment_region)
            logger.info(
                "Using region %s (from deployment_region) for both the trainer and its deployment.",
                active_deployment_region,
            )
        object.__setattr__(self, "deployment_region", None)

        if self.replica_count is None:
            object.__setattr__(self, "replica_count", 1)
        elif self.replica_count == 0:
            logger.warning(
                "deployment replica_count=0 is not valid for an inference deployment; using 1."
            )
            object.__setattr__(self, "replica_count", 1)
        if self.hotload_timeout_s is None:
            object.__setattr__(self, "hotload_timeout_s", HOTLOAD_TIMEOUT_S)

        for accel_field in ("accelerator_type", "accelerator_count"):
            if getattr(self, accel_field) is not None:
                warnings.warn(
                    f"{accel_field!r} is deprecated and ignored: trainer accelerator "
                    "type/count are configured by the training shape. Use "
                    "'trainer_replica_count' for data-parallel scaling.",
                    DeprecationWarning,
                    stacklevel=3,
                )
                object.__setattr__(self, accel_field, None)


_ManagedTinkerConfig = FiretitanProvisioningConfig


@dataclass
class _ManagedTinkerHandle:
    """Private resources owned by the SDK-managed Tinker compatibility path."""

    service_client: FiretitanServiceClient
    training_client: FiretitanTrainingClient
    trainer_endpoint: TrainerServiceEndpoint
    training_profile: Any | None = None
    max_context_length: int | None = None
    deployment: DeploymentInfo | None = None
    sampler_backend: "_TinkerSamplerBackend | None" = None
    trainer_manager: TrainerJobManager | None = None
    deployment_manager: DeploymentManager | None = None
    reference_handle: "_ManagedTinkerHandle | None" = None
    cleanup_trainer_on_close: bool = False
    cleanup_deployment_on_close: str | None = None
    _closed: bool = False

    def close(self) -> None:
        """Apply configured resource cleanup once."""
        if self._closed:
            return
        self._closed = True

        holder = getattr(self.training_client, "holder", None)
        if holder is not None:
            telemetry = holder.get_telemetry()
            if telemetry is not None:
                try:
                    telemetry._trigger_flush()
                    telemetry._wait_until_drained_sync()
                except Exception as e:
                    logger.warning(
                        "Failed to drain trainer telemetry for %s: %s",
                        self.trainer_endpoint.job_id,
                        e,
                    )
                finally:
                    try:
                        telemetry.stop()
                    except Exception as e:
                        logger.warning(
                            "Failed to stop trainer telemetry for %s: %s",
                            self.trainer_endpoint.job_id,
                            e,
                        )
            try:
                cleanup_future = holder.run_coroutine_threadsafe(holder._async_cleanup())
                cleanup_future.result(timeout=5.0)
            except Exception as e:
                logger.warning(
                    "Failed to stop trainer client holder for %s: %s",
                    self.trainer_endpoint.job_id,
                    e,
                )

        if self.cleanup_deployment_on_close and self.deployment and self.deployment_manager:
            if self.cleanup_deployment_on_close == "scale_to_zero":
                self.deployment_manager.scale_to_zero(self.deployment.deployment_id)
            elif self.cleanup_deployment_on_close == "delete":
                self.deployment_manager.delete(self.deployment.deployment_id)
            else:
                raise ValueError("cleanup_deployment_on_close must be None, 'delete', or 'scale_to_zero'")

        if self.cleanup_trainer_on_close and self.trainer_manager:
            self.trainer_manager.delete(self.trainer_endpoint.job_id)

    def __enter__(self) -> "_ManagedTinkerHandle":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()


@dataclass
class _TinkerSamplerBackend:
    """Private backend for Tinker-style save-weights/create-sampler flow.

    Tinker callers see only ``save_weights_for_sampler`` returning a
    ``model_path`` and ``create_sampling_client(model_path=...)`` consuming it.
    The SDK keeps that model path as the single snapshot identity and prepares
    the managed deployment to serve it.
    """

    deploy_mgr: DeploymentManager
    deployment_id: str
    base_model: str
    hotload_timeout_s: int = HOTLOAD_TIMEOUT_S
    reset_prompt_cache: bool = True
    lora_rank: int = 0
    compression_format: str = DEFAULT_DELTA_COMPRESSION
    _snapshot_types: dict[str, str] = field(default_factory=dict)
    _base_identity: str | None = None

    def _deployment_model(self) -> str:
        return f"accounts/{self.deploy_mgr.account_id}/deployments/{self.deployment_id}"

    def remember_saved_snapshot(
        self,
        model_path: str,
        checkpoint_type: str | None = None,
    ) -> None:
        if checkpoint_type is not None:
            self._snapshot_types[model_path] = checkpoint_type.lower()

    def hotload_saved_snapshot(self, model_path: str) -> bool:
        incremental = build_incremental_metadata(
            lora_rank=self.lora_rank,
            checkpoint_type=self._snapshot_types.get(model_path),
            base_identity=self._base_identity,
            compression_format=self.compression_format,
        )
        ok = self.deploy_mgr.hotload_and_wait(
            deployment_id=self.deployment_id,
            base_model=self.base_model,
            snapshot_identity=model_path,
            incremental_snapshot_metadata=incremental,
            reset_prompt_cache=self.reset_prompt_cache,
            timeout_seconds=self.hotload_timeout_s,
            path=None,
        )
        if ok:
            # Track the snapshot the deployment now holds so the next delta
            # references it (matches WeightSyncer.base_identity bookkeeping).
            self._base_identity = model_path
        return ok

    def get_sampling_client(
        self,
        tokenizer: Any | None = None,
        concurrency_controller: Any | None = None,
    ) -> FiretitanSamplingClient:
        sampler = DeploymentSampler(
            inference_url=self.deploy_mgr.inference_url,
            model=self._deployment_model(),
            api_key=self.deploy_mgr.api_key,
            tokenizer=tokenizer,
        )
        if concurrency_controller is not None:
            sampler.concurrency_controller = concurrency_controller
        return FiretitanSamplingClient(sampler)


def _build_resource_managers(
    *,
    api_key: str,
    base_url: str,
    inference_url: str | None,
    hotload_api_url: str | None,
    additional_headers: dict[str, str] | None,
    verify_ssl: bool | None,
) -> tuple[TrainerJobManager, DeploymentManager]:
    """Construct the trainer and deployment REST managers for one session."""
    trainer_mgr = TrainerJobManager(
        api_key=api_key,
        base_url=base_url,
        additional_headers=additional_headers,
        verify_ssl=verify_ssl,
    )
    deploy_mgr = DeploymentManager(
        api_key=api_key,
        base_url=base_url,
        inference_url=inference_url,
        hotload_api_url=hotload_api_url,
        additional_headers=additional_headers,
        verify_ssl=verify_ssl,
    )
    return trainer_mgr, deploy_mgr


def _attach_managed_deployment(
    deploy_mgr: DeploymentManager,
    config: _ManagedTinkerConfig,
    *,
    trainer_job_name: str,
    deployment_shape: str | None,
) -> tuple[DeploymentInfo, "_TinkerSamplerBackend"]:
    """Create/reattach the managed deployment and build its sampler backend."""
    deployment = _create_or_reattach_deployment(
        deploy_mgr,
        config,
        trainer_job_name=trainer_job_name,
        deployment_shape=deployment_shape,
    )
    sampler_backend = _TinkerSamplerBackend(
        deploy_mgr=deploy_mgr,
        deployment_id=deployment.deployment_id,
        base_model=config.base_model,
        hotload_timeout_s=config.hotload_timeout_s,
        lora_rank=config.lora_rank,
    )
    return deployment, sampler_backend


def _create_managed_tinker_client(
    *,
    api_key: str,
    config: _ManagedTinkerConfig,
    user_metadata: dict[str, str] | None = None,
    base_url: str = "https://api.fireworks.ai",
    inference_url: str | None = None,
    hotload_api_url: str | None = None,
    additional_headers: dict[str, str] | None = None,
    verify_ssl: bool | None = None,
) -> _ManagedTinkerHandle:
    """Provision trainer/deployment resources and return a Tinker client.

    ``config`` is the immutable, single-source infra + training config:
    ``base_model``/``lora_rank`` come from it (the per-call values passed to
    ``create_training_client`` must match — a divergent value is deprecated and
    ignored). ``max_context_length`` is resolved here from the shape and flows
    as a local; it is never folded back into ``config``.
    """
    trainer_mgr, deploy_mgr = _build_resource_managers(
        api_key=api_key,
        base_url=base_url,
        inference_url=inference_url,
        hotload_api_url=hotload_api_url,
        additional_headers=additional_headers,
        verify_ssl=verify_ssl,
    )

    profile = trainer_mgr.resolve_training_profile(config.training_shape_id) if config.training_shape_id else None
    max_context_length = config.max_context_length
    if max_context_length is None and profile is not None:
        max_context_length = profile.max_supported_context_length
    started_trainer = _start_or_reuse_trainer(
        trainer_mgr,
        config,
        max_context_length=max_context_length,
        profile_training_shape=profile.training_shape_version if profile else None,
    )
    deployment_shape = config.deployment_shape or (profile.deployment_shape if profile else None)
    should_provision_reference = (
        config.reference_required
        and not config.forward_only
        and not _use_shared_base_reference(config, policy_lora_rank=config.lora_rank)
    )
    with ThreadPoolExecutor(max_workers=3, thread_name_prefix="firetitan-provision") as executor:
        trainer_future = executor.submit(
            _wait_for_started_trainer,
            trainer_mgr,
            started_trainer,
            config,
        )
        deployment_future = None
        if config.create_deployment:
            deployment_future = executor.submit(
                _attach_managed_deployment,
                deploy_mgr,
                config,
                trainer_job_name=started_trainer.job_name,
                deployment_shape=deployment_shape,
            )

        reference_future = None
        if should_provision_reference:
            reference_future = executor.submit(
                _create_managed_tinker_client,
                api_key=api_key,
                config=_reference_managed_config(config, policy_lora_rank=config.lora_rank),
                user_metadata=user_metadata,
                base_url=base_url,
                inference_url=inference_url,
                hotload_api_url=hotload_api_url,
                additional_headers=additional_headers,
                verify_ssl=verify_ssl,
            )

        endpoint = trainer_future.result()
        deployment = None
        sampler_backend = None
        if deployment_future is not None:
            deployment, sampler_backend = deployment_future.result()
        reference_handle = None
        if reference_future is not None:
            reference_handle = reference_future.result()

    service_client = FiretitanServiceClient(base_url=endpoint.base_url, api_key=api_key)
    training_client = service_client.create_training_client(
        base_model=config.base_model,
        lora_rank=config.lora_rank,
        user_metadata=user_metadata,
    )
    # Let get_tokenizer() load from the HF tokenizer name without a get_info RPC.
    training_client._tokenizer_model = config.tokenizer_model

    if sampler_backend is not None:
        training_client._attach_sampler_backend(sampler_backend)
        service_client._attach_sampler_backend(sampler_backend)

    return _ManagedTinkerHandle(
        service_client=service_client,
        training_client=training_client,
        trainer_endpoint=endpoint,
        training_profile=profile,
        max_context_length=max_context_length,
        deployment=deployment,
        sampler_backend=sampler_backend,
        trainer_manager=trainer_mgr,
        deployment_manager=deploy_mgr,
        reference_handle=reference_handle,
        cleanup_trainer_on_close=config.cleanup_trainer_on_close,
        cleanup_deployment_on_close=config.cleanup_deployment_on_close,
    )


def _use_shared_base_reference(config: _ManagedTinkerConfig, *, policy_lora_rank: int) -> bool:
    """Whether the KL/DPO reference reuses the policy trainer session.

    A LoRA policy without an explicit reference shape or reference job gets its
    frozen base for free by disabling the adapter on the policy session — no
    second trainer. Full-parameter, an explicit reference shape, or an explicit
    reference job requires a separate forward-only reference trainer.
    """
    return (
        config.reference_training_shape_id is None
        and config.reference_trainer_job_id is None
        and policy_lora_rank > 0
    )


def _reference_managed_config(
    config: _ManagedTinkerConfig,
    *,
    policy_lora_rank: int,
) -> _ManagedTinkerConfig:
    """Derive the config for a separate forward-only reference trainer.

    Uses ``reference_training_shape_id`` when set, otherwise the policy
    ``training_shape_id`` (the control plane runs it forward-only). A LoRA
    reference with an explicit shape loads the adapter on top of the base;
    otherwise the reference forwards the frozen base directly. When
    ``reference_trainer_job_id`` is set, the reference reattaches that existing
    job and leaves ownership with the caller. The reference inherits the policy
    region (``config.region``) for checkpoint colocation and never provisions a
    deployment. Fresh SDK-created references are cleaned by default unless the
    parent config explicitly keeps them for a later reattach phase.
    """
    reference_shape = config.reference_training_shape_id or config.training_shape_id
    reference_lora_rank = (
        policy_lora_rank if (config.reference_training_shape_id and policy_lora_rank > 0) else 0
    )
    return replace(
        config,
        training_shape_id=reference_shape,
        lora_rank=reference_lora_rank,
        trainer_job_id=config.reference_trainer_job_id,
        deployment_id=None,
        create_deployment=False,
        forward_only=True,
        reference_required=False,
        cleanup_trainer_on_close=(
            config.reference_trainer_job_id is None
            and config.cleanup_reference_trainer_on_close
        ),
    )


def _get_or_create_trainer(
    trainer_mgr: TrainerJobManager,
    config: _ManagedTinkerConfig,
    *,
    max_context_length: int | None,
    profile_training_shape: str | None,
) -> TrainerServiceEndpoint:
    started_trainer = _start_or_reuse_trainer(
        trainer_mgr,
        config,
        max_context_length=max_context_length,
        profile_training_shape=profile_training_shape,
    )
    return _wait_for_started_trainer(trainer_mgr, started_trainer, config)


def _start_or_reuse_trainer(
    trainer_mgr: TrainerJobManager,
    config: _ManagedTinkerConfig,
    *,
    max_context_length: int | None,
    profile_training_shape: str | None,
) -> CreatedTrainerJob:
    if config.trainer_job_id:
        logger.info("Reusing trainer job %s", config.trainer_job_id)
        return CreatedTrainerJob(
            job_name=f"accounts/{trainer_mgr.account_id}/rlorTrainerJobs/{config.trainer_job_id}",
            job_id=config.trainer_job_id,
        )

    trainer_config = TrainerJobConfig(
        base_model=config.base_model,
        lora_rank=config.lora_rank,
        max_context_length=max_context_length,
        learning_rate=config.learning_rate,
        gradient_accumulation_steps=config.gradient_accumulation_steps,
        node_count=config.node_count,
        trainer_replica_count=config.trainer_replica_count,
        display_name=config.display_name,
        region=config.region,
        custom_image_tag=config.custom_image_tag,
        extra_args=config.extra_args,
        accelerator_type=config.accelerator_type,
        accelerator_count=config.accelerator_count,
        training_shape_ref=profile_training_shape,
        skip_validations=config.skip_validations,
        purpose=config.purpose,
        forward_only=config.forward_only,
    )
    return trainer_mgr.create(trainer_config)


def _wait_for_started_trainer(
    trainer_mgr: TrainerJobManager,
    started_trainer: CreatedTrainerJob,
    config: _ManagedTinkerConfig,
) -> TrainerServiceEndpoint:
    return trainer_mgr.wait_for_ready(
        started_trainer.job_id,
        job_name=started_trainer.job_name,
        timeout_s=config.trainer_timeout_s,
    )


def _deployment_shape_conflict(requested: str | None, existing_version: str | None) -> bool:
    """Whether a reattach target's shape disagrees with the requested shape.

    Compared at the *shape* level, ignoring the version. Different versions of
    the same deployment shape are the same training task, and the requested
    shape often comes from a training profile whose validated version drifts
    between the original run and a resume (e.g. ``/versions/1`` → ``/versions/2``).
    So version drift never conflicts on reattach — only a different *shape* does.
    An unset request (no shape requested/resolved) never conflicts. (Auto-select
    still resolves the exact validated version for *creating* a new deployment;
    this check only governs reattach.)
    """
    if not requested or not existing_version:
        return False
    return requested.split("/versions/")[0] != existing_version.split("/versions/")[0]


def _create_or_reattach_deployment(
    deploy_mgr: DeploymentManager,
    config: _ManagedTinkerConfig,
    *,
    trainer_job_name: str,
    deployment_shape: str | None,
) -> DeploymentInfo:
    deployment_id = config.deployment_id or _default_deployment_id(config.base_model)
    existing = deploy_mgr.get(deployment_id) if config.deployment_id else None
    if existing and existing.state not in DEPLOYMENT_TERMINAL_STATES:
        # Reconcile before mutating: a reattach reuses a warm deployment, but it
        # must not silently serve a different shape than requested (wrong
        # model/hardware). Fail fast on a shape conflict. The existing
        # deployment owns its other runtime settings (replicas, extra args) by
        # design; region is already reconciled at the cookbook boundary.
        if _deployment_shape_conflict(deployment_shape, existing.deployment_shape_version):
            raise ValueError(
                f"Reattach target deployment {deployment_id!r} serves shape "
                f"{existing.deployment_shape_version!r}, which does not match the requested "
                f"deployment_shape {deployment_shape!r}. Delete the existing deployment or "
                "request its shape; a reattach must not silently serve a different shape."
            )
        deployment = deploy_mgr.reattach_trainer(
            existing,
            base_model=config.base_model,
            trainer_job_name=trainer_job_name,
            timeout_s=config.reattach_settle_timeout_s,
            poll_interval_s=config.reattach_poll_interval_s,
        )
        if existing.state not in DEPLOYMENT_SERVING_STATES:
            return deploy_mgr.wait_for_ready(deployment_id, timeout_s=config.deployment_timeout_s)
        return deployment

    replica_count = max(config.replica_count, 0)
    region = config.deployment_region or config.region
    if region is None and deployment_shape:
        region = _infer_region_from_deployment_shape(deploy_mgr, deployment_shape)
    if not deployment_shape and not config.accelerator_type:
        raise ValueError(
            "Cannot create a managed deployment without a deployment shape: the "
            "deployment accelerator is owned by the deployment shape. Provide a "
            "deployment_shape (or a training_shape_id whose shape references one)."
        )
    deployment_config = DeploymentConfig(
        deployment_id=deployment_id,
        base_model=config.base_model,
        deployment_shape=deployment_shape,
        region=region,
        min_replica_count=replica_count,
        max_replica_count=replica_count,
        accelerator_type=config.accelerator_type,
        hot_load_trainer_job=trainer_job_name,
        # ``skip_validations`` belongs to trainer shape creation. Deployment
        # shape validation is a separate control-plane permission and should
        # not be coupled to unvalidated training-shape tests.
        skip_shape_validation=False,
        disable_speculative_decoding=config.disable_speculative_decoding,
        extra_args=config.deployment_extra_args,
        extra_values=config.deployment_extra_values,
    )
    deployment = deploy_mgr.create_or_get(deployment_config)
    if deployment.state not in DEPLOYMENT_SERVING_STATES:
        deployment = deploy_mgr.wait_for_ready(deployment_id, timeout_s=config.deployment_timeout_s)
    return deployment


def _default_deployment_id(base_model: str) -> str:
    model_short = base_model.rstrip("/").rsplit("/", 1)[-1].lower()
    safe = "".join(ch if ch.isalnum() else "-" for ch in model_short).strip("-")
    return f"{safe or 'model'}-{int(time.time())}"


def _infer_region_from_deployment_shape(
    deploy_mgr: DeploymentManager,
    deployment_shape: str,
) -> str | None:
    """Infer a deployment region from a validated deployment-shape snapshot."""
    try:
        version = _get_deployment_shape_version(deploy_mgr, deployment_shape)
    except Exception as e:
        logger.warning("Could not inspect deployment shape %s for region inference: %s", deployment_shape, e)
        return None

    snapshot = version.get("snapshot", {}) or {}
    accelerator = snapshot.get("acceleratorType", "")
    for prefix, region in _DEPLOYMENT_ACCELERATOR_REGION_PREFIXES:
        if accelerator.startswith(prefix):
            logger.info(
                "Inferred deployment region %s from deployment shape %s (accelerator=%s)",
                region,
                deployment_shape,
                accelerator,
            )
            return region
    return None


def _get_deployment_shape_version(
    deploy_mgr: DeploymentManager,
    deployment_shape: str,
) -> dict[str, Any]:
    if "/versions/" in deployment_shape:
        path = f"/v1/{deployment_shape}"
    else:
        query = urlencode({"filter": "latest_validated=true", "pageSize": 1})
        path = f"/v1/{deployment_shape}/versions?{query}"
    response = deploy_mgr._get(path, timeout=HTTP_READ_TIMEOUT_S)
    response.raise_for_status()
    data = response.json()
    if "/versions/" in deployment_shape:
        return data
    versions = data.get("deploymentShapeVersions", []) or []
    if not versions:
        raise RuntimeError(f"No latest validated deployment-shape version was returned for {deployment_shape!r}")
    return versions[0]
