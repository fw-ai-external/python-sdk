"""Private SDK-owned trainer/deployment setup for Tinker-compatible recipes."""

from __future__ import annotations

import time
import logging
import warnings
from typing import Any
from datetime import timedelta
from dataclasses import field, replace, dataclass
from concurrent.futures import ThreadPoolExecutor

from fireworks.training.sdk.client import (
    DEFAULT_LORA_ALPHA,
    FiretitanServiceClient,
    FiretitanSamplingClient,
    FiretitanTrainingClient,
)
from fireworks.training.sdk.trainer import (
    TrainerJobConfig,
    CreatedTrainerJob,
    TrainerJobManager,
    TrainerServiceEndpoint,
    _new_trainer_job_id,
)
from fireworks.training.sdk._constants import (
    POLL_INTERVAL_S,
    HOTLOAD_TIMEOUT_S,
    DEFAULT_TRAINER_TIMEOUT_S,
    REATTACH_SETTLE_TIMEOUT_S,
    DEPLOYMENT_READY_TIMEOUT_S,
    DEFAULT_TRAINER_PENDING_TIMEOUT_S,
    CLEANUP_DEPLOYMENT_ON_CLOSE_DELETE,
    CLEANUP_DEPLOYMENT_ON_CLOSE_SCALE_TO_ZERO,
    SDK_MANAGED_ROLLOUT_DEPLOYMENT_ANNOTATION,
    DeploymentCleanupOnClose,
)
from fireworks.training.sdk.deployment import (
    DEFAULT_DELTA_COMPRESSION,
    DeploymentInfo,
    DeploymentConfig,
    DeploymentManager,
    DeploymentSampler,
)
from fireworks.training.sdk.concurrency import SamplingConcurrencyController
from fireworks.training.sdk._snapshot_chain import (
    build_incremental_metadata,
)

logger = logging.getLogger(__name__)

DEPLOYMENT_TERMINAL_STATES = frozenset({"FAILED", "DELETED", "DELETING"})
DEPLOYMENT_SERVING_STATES = frozenset({"READY", "UPDATING"})
_POLICY_TRAINER_MODE = "POLICY_TRAINER"
_LORA_TRAINER_MODE = "LORA_TRAINER"
_REFERENCE_TRAINER_MODES_RANK0 = frozenset({_LORA_TRAINER_MODE})


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
    lora_alpha: int | None = None
    training_shape_id: str | None = None
    # Optional separate reference trainer shape. Full-parameter references
    # without this ask the backend to auto-select a LoRA-capable shape.
    reference_training_shape_id: str | None = None
    # Optional existing reference trainer to reattach to. When set, it disables
    # LoRA shared-reference and is never cleaned up on close.
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
    region: str | None = None  # Leave unset unless the caller explicitly needs placement.
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
    trainer_pending_timeout_s: float = DEFAULT_TRAINER_PENDING_TIMEOUT_S
    inactivity_timeout: timedelta | str | None = None
    disable_inactivity_cleanup: bool = False
    deployment_timeout_s: float = DEPLOYMENT_READY_TIMEOUT_S
    hotload_timeout_s: int = HOTLOAD_TIMEOUT_S
    reattach_settle_timeout_s: float = REATTACH_SETTLE_TIMEOUT_S
    reattach_poll_interval_s: float = POLL_INTERVAL_S
    cleanup_trainer_on_close: bool = False
    cleanup_deployment_on_close: DeploymentCleanupOnClose | None = None
    display_name: str | None = None
    purpose: str | None = None
    managed_by: str | None = None
    skip_validations: bool = False
    disable_speculative_decoding: bool = False

    def __post_init__(self) -> None:
        if self.replica_count is None:
            object.__setattr__(self, "replica_count", 1)
        elif self.replica_count == 0:
            logger.warning("deployment replica_count=0 is not valid for an inference deployment; using 1.")
            object.__setattr__(self, "replica_count", 1)
        if self.hotload_timeout_s is None:
            object.__setattr__(self, "hotload_timeout_s", HOTLOAD_TIMEOUT_S)

        for infra_field in ("accelerator_type", "accelerator_count", "node_count"):
            if getattr(self, infra_field) is not None:
                warnings.warn(
                    f"{infra_field!r} is deprecated and ignored: trainer infrastructure "
                    "is configured by the training shape. Use "
                    "'trainer_replica_count' for data-parallel scaling.",
                    DeprecationWarning,
                    stacklevel=3,
                )
                object.__setattr__(self, infra_field, None)


_ManagedTinkerConfig = FiretitanProvisioningConfig


@dataclass
class _ManagedTinkerHandle:
    """Private resources owned by the SDK-managed Tinker compatibility path."""

    service_client: FiretitanServiceClient
    training_client: FiretitanTrainingClient
    trainer_endpoint: TrainerServiceEndpoint
    training_profile: Any | None = None
    max_context_length: int | None = None
    deployment_shape: str | None = None
    deployment: DeploymentInfo | None = None
    requires_initial_sampler_sync: bool = False
    sampler_backend: "_TinkerSamplerBackend | None" = None
    trainer_manager: TrainerJobManager | None = None
    deployment_manager: DeploymentManager | None = None
    reference_handle: "_ManagedTinkerHandle | None" = None
    cleanup_trainer_on_close: bool = False
    cleanup_deployment_on_close: DeploymentCleanupOnClose | None = None
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
            if self.cleanup_deployment_on_close == CLEANUP_DEPLOYMENT_ON_CLOSE_SCALE_TO_ZERO:
                self.deployment_manager.scale_to_zero(self.deployment.deployment_id)
            elif self.cleanup_deployment_on_close == CLEANUP_DEPLOYMENT_ON_CLOSE_DELETE:
                self.deployment_manager.delete(self.deployment.deployment_id)
            else:
                allowed = ", ".join(
                    [
                        CLEANUP_DEPLOYMENT_ON_CLOSE_DELETE,
                        CLEANUP_DEPLOYMENT_ON_CLOSE_SCALE_TO_ZERO,
                    ]
                )
                raise ValueError(f"cleanup_deployment_on_close must be None or one of: {allowed}")

        if self.cleanup_trainer_on_close and self.trainer_manager:
            self.trainer_manager.delete(self.trainer_endpoint.job_id)

    def __enter__(self) -> "_ManagedTinkerHandle":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()


@dataclass(frozen=True)
class _StartedTrainer:
    job: CreatedTrainerJob
    created: bool


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

    def reset_snapshot_chain(self) -> None:
        """Forget snapshots from a previous trainer namespace after reattach."""
        self._snapshot_types.clear()
        self._base_identity = None

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
        concurrency_controller: SamplingConcurrencyController | None = None,
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


@dataclass(frozen=True)
class _DeploymentAttachResult:
    deployment: DeploymentInfo
    reattached: bool = False
    created: bool = False


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
) -> tuple[DeploymentInfo, "_TinkerSamplerBackend", bool, bool]:
    """Create/reattach the managed deployment and build its sampler backend."""
    attach_result = _create_or_reattach_deployment_result(
        deploy_mgr,
        config,
        trainer_job_name=trainer_job_name,
        deployment_shape=deployment_shape,
    )
    deployment = attach_result.deployment
    sampler_backend = _TinkerSamplerBackend(
        deploy_mgr=deploy_mgr,
        deployment_id=deployment.deployment_id,
        base_model=config.base_model,
        hotload_timeout_s=config.hotload_timeout_s,
        lora_rank=config.lora_rank,
    )
    if attach_result.reattached:
        sampler_backend.reset_snapshot_chain()
    return deployment, sampler_backend, attach_result.reattached, attach_result.created


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

    reference_config = None
    if _should_provision_reference(config):
        reference_config = _reference_managed_config(config, policy_lora_rank=config.lora_rank)
        _validate_reference_training_shape(trainer_mgr, reference_config)

    started_trainer = _start_or_reuse_trainer(
        trainer_mgr,
        config,
        max_context_length=max_context_length,
        profile_training_shape=profile.training_shape_version if profile else None,
    )
    deployment_shape = config.deployment_shape or (profile.deployment_shape if profile else None)
    with ThreadPoolExecutor(max_workers=3, thread_name_prefix="firetitan-provision") as executor:
        trainer_future = executor.submit(
            _wait_for_started_trainer,
            trainer_mgr,
            started_trainer.job,
            config,
        )
        deployment_future = None
        if config.create_deployment:
            deployment_future = executor.submit(
                _attach_managed_deployment,
                deploy_mgr,
                config,
                trainer_job_name=started_trainer.job.job_name,
                deployment_shape=deployment_shape,
            )

        reference_future = None
        if reference_config is not None:
            reference_future = executor.submit(
                _create_managed_tinker_client,
                api_key=api_key,
                config=reference_config,
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
        deployment_reattached = False
        deployment_created = False
        if deployment_future is not None:
            (
                deployment,
                sampler_backend,
                deployment_reattached,
                deployment_created,
            ) = deployment_future.result()
        reference_handle = None
        if reference_future is not None:
            reference_handle = reference_future.result()

    resolved_max_context_length = max_context_length
    if resolved_max_context_length is None:
        resolved_max_context_length = endpoint.max_context_length

    service_client = FiretitanServiceClient(base_url=endpoint.base_url, api_key=api_key)
    create_model_kwargs: dict[str, Any] = {
        "base_model": config.base_model,
        "lora_rank": config.lora_rank,
        "user_metadata": user_metadata,
    }
    if config.lora_rank > 0:
        create_model_kwargs["lora_alpha"] = config.lora_alpha if config.lora_alpha is not None else DEFAULT_LORA_ALPHA
    training_client = service_client.create_training_client(**create_model_kwargs)
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
        max_context_length=resolved_max_context_length,
        deployment_shape=deployment_shape,
        deployment=deployment,
        requires_initial_sampler_sync=deployment_reattached,
        sampler_backend=sampler_backend,
        trainer_manager=trainer_mgr,
        deployment_manager=deploy_mgr,
        reference_handle=reference_handle,
        cleanup_trainer_on_close=config.cleanup_trainer_on_close and started_trainer.created,
        cleanup_deployment_on_close=(config.cleanup_deployment_on_close if deployment_created else None),
    )


def _should_provision_reference(config: _ManagedTinkerConfig) -> bool:
    return (
        config.reference_required
        and not config.forward_only
        and not _use_shared_base_reference(config, policy_lora_rank=config.lora_rank)
    )


def _validate_reference_training_shape(
    trainer_mgr: TrainerJobManager,
    reference_config: _ManagedTinkerConfig,
) -> None:
    """Validate a fresh separate reference trainer shape before policy create."""
    if not reference_config.training_shape_id:
        return
    profile = trainer_mgr.resolve_training_profile(reference_config.training_shape_id)
    allowed_modes = _allowed_reference_trainer_modes(reference_config.lora_rank)
    preferred_mode = _preferred_reference_trainer_mode(reference_config.lora_rank)
    raw_mode = getattr(profile, "trainer_mode", "") or ""
    actual = raw_mode or _POLICY_TRAINER_MODE
    if actual in allowed_modes:
        return
    allowed_label = ", ".join(sorted(allowed_modes))
    raise ValueError(
        f"reference_training_shape_id={reference_config.training_shape_id!r} "
        f"resolves to trainer_mode={actual!r}, "
        f"but this run requires trainer_mode in {{{allowed_label}}} "
        f"(preferred {preferred_mode!r}; "
        f"lora_rank={reference_config.lora_rank}, forward_only={reference_config.forward_only}). "
        "Use a training shape validated for the reference trainer mode."
    )


def _allowed_reference_trainer_modes(lora_rank: int) -> frozenset[str]:
    if lora_rank > 0:
        return frozenset({_LORA_TRAINER_MODE})
    return _REFERENCE_TRAINER_MODES_RANK0


def _preferred_reference_trainer_mode(lora_rank: int) -> str:
    return _LORA_TRAINER_MODE


def _use_shared_base_reference(config: _ManagedTinkerConfig, *, policy_lora_rank: int) -> bool:
    """Whether the KL/DPO reference reuses the policy trainer session.

    A LoRA policy without an explicit reference shape or reference job gets its
    frozen base for free by disabling the adapter on the policy session — no
    second trainer. Full-parameter references provision a separate trainer; when
    no reference shape is pinned, backend trainer creation auto-selects a
    LoRA-capable shape for that frozen reference runtime.
    """
    return (
        config.reference_training_shape_id is None and config.reference_trainer_job_id is None and policy_lora_rank > 0
    )


def _reference_managed_config(
    config: _ManagedTinkerConfig,
    *,
    policy_lora_rank: int,
) -> _ManagedTinkerConfig:
    """Derive the config for a separate frozen reference trainer.

    ``reference_training_shape_id`` selects a fresh reference trainer shape;
    ``reference_trainer_job_id`` reattaches an existing reference and leaves
    ownership with the caller. A LoRA reference with an explicit shape loads the
    adapter on top of the base; otherwise the reference forwards the frozen base
    directly. When no explicit reference shape is provided, backend trainer
    creation auto-selects a LoRA-capable shape. Fresh SDK-created references are
    cleaned by default unless the parent config explicitly keeps them for a
    later reattach phase.
    """
    reference_shape = config.reference_training_shape_id
    reference_lora_rank = policy_lora_rank if (config.reference_training_shape_id and policy_lora_rank > 0) else 0
    return replace(
        config,
        training_shape_id=reference_shape,
        lora_rank=reference_lora_rank,
        trainer_job_id=config.reference_trainer_job_id,
        deployment_id=None,
        create_deployment=False,
        forward_only=True,
        reference_required=False,
        trainer_replica_count=None,
        cleanup_trainer_on_close=config.cleanup_reference_trainer_on_close,
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
    return _wait_for_started_trainer(trainer_mgr, started_trainer.job, config)


_RESUMABLE_TRAINER_STATES = frozenset(
    {
        "JOB_STATE_FAILED",
        "JOB_STATE_CANCELLED",
        "JOB_STATE_PAUSED",
        "JOB_STATE_COMPLETED",
    }
)


def _uses_manual_training_infra(config: _ManagedTinkerConfig) -> bool:
    # Only explicit accelerator placement overrides force the manual (shape
    # validation skipping) create path. extra_args are runtime training flags
    # that are forwarded on the auto-shape payload too, so they must not disable
    # auto shape selection -- doing so sends skipValidations=true, which the
    # server rejects with 400 for non-superuser (customer) API keys.
    return any(
        value not in (None, "", 0, False)
        for value in (
            config.accelerator_type,
            config.accelerator_count,
        )
    )


def _build_trainer_job_config(
    config: _ManagedTinkerConfig,
    *,
    max_context_length: int | None,
    profile_training_shape: str | None,
    requested_job_id: str | None = None,
) -> TrainerJobConfig:
    auto_select_training_shape = profile_training_shape is None and not _uses_manual_training_infra(config)
    return TrainerJobConfig(
        base_model=config.base_model,
        lora_rank=config.lora_rank,
        max_context_length=max_context_length,
        learning_rate=config.learning_rate,
        gradient_accumulation_steps=config.gradient_accumulation_steps,
        node_count=None if auto_select_training_shape else config.node_count,
        trainer_replica_count=config.trainer_replica_count,
        display_name=config.display_name,
        region=config.region,
        custom_image_tag=config.custom_image_tag,
        extra_args=config.extra_args,
        accelerator_type=None if auto_select_training_shape else config.accelerator_type,
        accelerator_count=None if auto_select_training_shape else config.accelerator_count,
        training_shape_ref=profile_training_shape,
        auto_select_training_shape=auto_select_training_shape,
        skip_validations=config.skip_validations,
        purpose=config.purpose,
        managed_by=config.managed_by,
        forward_only=config.forward_only,
        inactivity_timeout=config.inactivity_timeout,
        disable_inactivity_cleanup=config.disable_inactivity_cleanup,
        requested_job_id=requested_job_id,
    )


def _start_or_reuse_trainer(
    trainer_mgr: TrainerJobManager,
    config: _ManagedTinkerConfig,
    *,
    max_context_length: int | None,
    profile_training_shape: str | None,
) -> _StartedTrainer:
    explicit_trainer_job_id = config.trainer_job_id is not None
    trainer_job_id = config.trainer_job_id or _new_trainer_job_id()
    if not explicit_trainer_job_id:
        object.__setattr__(config, "trainer_job_id", trainer_job_id)

    if explicit_trainer_job_id:
        if trainer_mgr.try_get(trainer_job_id) is not None:
            logger.info("Reusing trainer job %s", trainer_job_id)
            return _StartedTrainer(
                job=CreatedTrainerJob(
                    job_name=f"accounts/{trainer_mgr.account_id}/rlorTrainerJobs/{trainer_job_id}",
                    job_id=trainer_job_id,
                ),
                created=False,
            )
        logger.info(
            "Trainer job %s not found; creating with stable ID for managed SFT resume",
            trainer_job_id,
        )
        trainer_config = _build_trainer_job_config(
            config,
            max_context_length=max_context_length,
            profile_training_shape=profile_training_shape,
            requested_job_id=trainer_job_id,
        )
        return _StartedTrainer(job=trainer_mgr.create(trainer_config), created=True)

    trainer_config = _build_trainer_job_config(
        config,
        max_context_length=max_context_length,
        profile_training_shape=profile_training_shape,
        requested_job_id=trainer_job_id,
    )
    return _StartedTrainer(job=trainer_mgr.create(trainer_config), created=True)


def _wait_for_started_trainer(
    trainer_mgr: TrainerJobManager,
    started_trainer: CreatedTrainerJob,
    config: _ManagedTinkerConfig,
) -> TrainerServiceEndpoint:
    existing_job = trainer_mgr.try_get(started_trainer.job_id)
    if existing_job is not None:
        state = existing_job.get("state", "")
        if state in _RESUMABLE_TRAINER_STATES:
            logger.info("Resuming trainer job %s from %s", started_trainer.job_id, state)
            return trainer_mgr.resume_and_wait(
                started_trainer.job_id,
                timeout_s=config.trainer_timeout_s,
                pending_timeout_s=config.trainer_pending_timeout_s,
            )
    return trainer_mgr.wait_for_ready(
        started_trainer.job_id,
        job_name=started_trainer.job_name,
        timeout_s=config.trainer_timeout_s,
        pending_timeout_s=config.trainer_pending_timeout_s,
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
    return _create_or_reattach_deployment_result(
        deploy_mgr,
        config,
        trainer_job_name=trainer_job_name,
        deployment_shape=deployment_shape,
    ).deployment


def _create_or_reattach_deployment_result(
    deploy_mgr: DeploymentManager,
    config: _ManagedTinkerConfig,
    *,
    trainer_job_name: str,
    deployment_shape: str | None,
) -> _DeploymentAttachResult:
    explicit_deployment_id = config.deployment_id is not None
    deployment_id = config.deployment_id or _default_deployment_id(config.base_model)
    if not explicit_deployment_id:
        object.__setattr__(config, "deployment_id", deployment_id)

    existing = deploy_mgr.get(deployment_id) if explicit_deployment_id else None
    if existing and existing.state not in DEPLOYMENT_TERMINAL_STATES:
        if _deployment_shape_conflict(deployment_shape, existing.deployment_shape_version):
            raise ValueError(
                f"Reattach target deployment {deployment_id!r} serves shape "
                f"{existing.deployment_shape_version!r}, which does not match the requested "
                f"deployment_shape {deployment_shape!r}. Delete the existing deployment or "
                "request its shape; a reattach must not silently serve a different shape."
            )
        previous_trainer_job = getattr(existing, "hot_load_trainer_job", None)
        reattached = previous_trainer_job != trainer_job_name
        deployment = deploy_mgr.reattach_trainer(
            existing,
            base_model=config.base_model,
            trainer_job_name=trainer_job_name,
            timeout_s=config.reattach_settle_timeout_s,
            poll_interval_s=config.reattach_poll_interval_s,
        )
        if existing.state not in DEPLOYMENT_SERVING_STATES:
            deployment = deploy_mgr.wait_for_ready(deployment_id, timeout_s=config.deployment_timeout_s)
        return _DeploymentAttachResult(deployment=deployment, reattached=reattached, created=False)

    replica_count = max(config.replica_count, 0)
    if not deployment_shape and not config.accelerator_type:
        raise ValueError(
            "Cannot create a managed deployment without a deployment shape: the "
            "deployment accelerator is owned by the deployment shape. Provide a "
            "deployment_shape (or a training_shape_id whose shape references one)."
        )
    deployment_config = DeploymentConfig(
        deployment_id=deployment_id,
        base_model=config.base_model,
        region=config.region,
        deployment_shape=deployment_shape,
        min_replica_count=replica_count,
        max_replica_count=replica_count,
        accelerator_type=config.accelerator_type,
        hot_load_trainer_job=trainer_job_name,
        for_training=True,
        # ``skip_validations`` belongs to trainer shape creation. Deployment
        # shape validation is a separate control-plane permission and should
        # not be coupled to unvalidated training-shape tests.
        skip_shape_validation=False,
        disable_speculative_decoding=config.disable_speculative_decoding,
        extra_args=config.deployment_extra_args,
        extra_values=config.deployment_extra_values,
        annotations={SDK_MANAGED_ROLLOUT_DEPLOYMENT_ANNOTATION: "true"},
    )
    deployment = deploy_mgr.create_or_get(deployment_config)
    if deployment.state not in DEPLOYMENT_SERVING_STATES:
        deployment = deploy_mgr.wait_for_ready(deployment_id, timeout_s=config.deployment_timeout_s)
    return _DeploymentAttachResult(deployment=deployment, reattached=False, created=True)


def _default_deployment_id(base_model: str) -> str:
    model_short = base_model.rstrip("/").rsplit("/", 1)[-1].lower()
    safe = "".join(ch if ch.isalnum() else "-" for ch in model_short).strip("-")
    return f"{safe or 'model'}-{int(time.time())}"
