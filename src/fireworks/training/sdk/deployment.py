"""Fireworks Deployment, Hotload & Sampling.

Manages inference deployment lifecycle, hotload operations for weight syncing,
and provides a thin wrapper for deployment completions API with client-side
tokenization (token-in, token-out).
"""

from __future__ import annotations

import time
import logging
from typing import TYPE_CHECKING, Any
from dataclasses import dataclass

if TYPE_CHECKING:
    pass

from fireworks.training.sdk.errors import (
    DOCS_SDK,
    CONSOLE_URL,
    HTTP_STATUS_HINTS,
    parse_api_error,
    format_sdk_error,
)
from fireworks.training.sdk._constants import (
    HTTP_READ_TIMEOUT_S,
    WARMUP_PROBE_TIMEOUT_S,
)
from fireworks.training.sdk._rest_client import _RestClient, _should_verify_ssl

logger = logging.getLogger(__name__)


DEFAULT_DELTA_COMPRESSION = "arc_v2"
DEFAULT_CHECKSUM_FORMAT = "alder32"

# Deployment-specific wait budgets and poll intervals (seconds).
# Default budget for the low-level wait_for_ready (direct deployment CRUD).
# SDK-managed large-model deployments pass the longer
# _constants.DEPLOYMENT_READY_TIMEOUT_S budget explicitly instead.
DEPLOYMENT_READY_DEFAULT_TIMEOUT_S: float = 600
DEPLOYMENT_READY_POLL_S: float = 15
DEPLOYMENT_DELETION_TIMEOUT_S: float = 60
DEPLOYMENT_DELETION_POLL_S: float = 2
HOTLOAD_WAIT_TIMEOUT_S: int = 400
HOTLOAD_WAIT_POLL_S: int = 5
DEFAULT_DEPLOYMENT_DESCRIPTION = "Fireworks training deployment"
HOTLOAD_RECOVERY_STEPS = (
    "Use the Fireworks training cookbook skill's hotload recovery self-check. "
    "Common recoveries are: reattach or recreate a stale deployment; for "
    "full-parameter training, retry from a matching base checkpoint or resume "
    "from DCP; for LoRA, fix deployment attachment rather than changing "
    "checkpoint_type."
)


def _format_snapshot_identity(identity: str | None) -> str:
    return identity if identity else "none"


@dataclass
class DeploymentInfo:
    """Metadata about a Fireworks deployment."""

    deployment_id: str
    name: str
    state: str
    hot_load_bucket_url: str | None = None
    hot_load_trainer_job: str | None = None
    deployment_shape_version: str | None = None
    inference_model: str | None = None
    """Model string for completions API (``accounts/{account}/deployments/{id}``)."""


def _deployment_hot_load_trainer_job(deployment: DeploymentInfo) -> str | None:
    """Return the trainer job currently attached to a parsed deployment."""
    return deployment.hot_load_trainer_job


@dataclass
class DeploymentConfig:
    """Configuration for creating/managing a Fireworks deployment.

    Two creation paths:

    * **Shape path** (``deployment_shape`` set): accelerator type, count,
      precision, and world size are derived from the shape.  Do not set
      ``accelerator_type`` -- the server rejects it.
    * **Manual path** (``deployment_shape`` is ``None``): ``accelerator_type``
      is required (server rejects ``UNSPECIFIED``).  Defaults to
      ``NVIDIA_H200_141GB``.
    """

    deployment_id: str
    base_model: str
    description: str | None = None
    deployment_shape: str | None = None
    region: str | None = None
    min_replica_count: int = 0
    max_replica_count: int = 1
    accelerator_type: str = "NVIDIA_H200_141GB"
    """Required for manual-path deployments (server has no default).
    Ignored when ``deployment_shape`` is set."""
    hot_load_bucket_type: str | None = "FW_HOSTED"
    hot_load_trainer_job: str | None = None
    """Trainer job whose hot_load_bucket_url this deployment should use.
    Format: accounts/{account}/rlorTrainerJobs/{job}.
    When set, the deployment shares the trainer's checkpoint bucket."""
    enable_hot_load: bool = True
    """Whether the deployment should be created with hot-load training support."""
    skip_shape_validation: bool = False
    disable_speculative_decoding: bool = False
    extra_args: list[str] | None = None
    extra_values: dict[str, str] | None = None
    annotations: dict[str, str] | None = None


class DeploymentManager(_RestClient):
    """Manages Fireworks deployment lifecycle and hotloading.

    Handles deployment creation, readiness polling, hotloading weight snapshots,
    and warmup.  All inference and hotload traffic goes through the gateway.

    Args:
        api_key: Fireworks API key.
        base_url: Control-plane URL for deployment CRUD operations.
        inference_url: Gateway URL for inference completions.  Defaults to *base_url*.
        hotload_api_url: Gateway URL for hotload operations.  Defaults to *base_url*.
        additional_headers: Extra headers added to every request (e.g. gateway secret).

    Example::

        mgr = DeploymentManager(
            api_key="...",
            base_url="https://api.fireworks.ai",
        )

        # Example with separate control-plane and gateway endpoints:
        mgr = DeploymentManager(
            api_key="...",
            base_url="http://GATEWAY_IP:8083",
            inference_url="https://api.fireworks.ai",
            hotload_api_url="https://api.fireworks.ai",
        )
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.fireworks.ai",
        inference_url: str | None = None,
        hotload_api_url: str | None = None,
        additional_headers: dict[str, str] | None = None,
        verify_ssl: bool | None = None,
        **kwargs,
    ):
        if "account_id" in kwargs:
            raise ValueError(
                "account_id is no longer accepted. The account is now automatically "
                "resolved from your API key. Please remove the account_id argument."
            )
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            additional_headers=additional_headers,
            verify_ssl=verify_ssl,
        )
        self.inference_url = (inference_url or base_url).rstrip("/")
        self.hotload_api_url = hotload_api_url or base_url
        self._hotload_reset_prompt_cache_supported: bool | None = None
        self._last_hotload_error_message: str | None = None
        self.boot_time_s: float | None = None
        """Wall-clock seconds spent in the most recent ``wait_for_ready`` call."""

    @property
    def last_hotload_error_message(self) -> str | None:
        return self._last_hotload_error_message

    # Header that carries the optional snapshot source URI. Some serving
    # backends use it to fetch the snapshot bytes inline at hot-load time;
    # others ignore it and resolve the snapshot from the deployment's
    # configured storage. Carried as a header (rather than a body field)
    # because the body schema rejects unknown fields, while unknown
    # headers are tolerated cross-engine.
    _HOTLOAD_SOURCE_URL_HEADER = "x-fireworks-hot-load-source-url"

    def _hotload_headers(
        self,
        deployment_id: str,
        base_model: str,
        path: str | None = None,
    ) -> dict[str, str]:
        """Construct headers for hotload API requests.

        Args:
            deployment_id: Target deployment id.
            base_model: Model name (used for routing).
            path: Optional object-storage URI (e.g. ``gs://bucket/prefix/``)
                forwarded as ``x-fireworks-hot-load-source-url``. Set when the
                trainer wants the deployment to fetch the snapshot bytes from
                a specific URI instead of resolving from the deployment's
                configured storage.
        """
        extra: dict[str, str] = {
            "fireworks-model": base_model,
            "fireworks-deployment": f"accounts/{self.account_id}/deployments/{deployment_id}",
        }
        if path:
            extra[self._HOTLOAD_SOURCE_URL_HEADER] = path
        return self._headers(Authorization=f"Bearer {self.api_key}", **extra)

    # -- Deployment CRUD -------------------------------------------------------

    def _get_deployment(self, deployment_id: str) -> dict | None:
        path = f"/v1/accounts/{self.account_id}/deployments/{deployment_id}"
        resp = self._get(path)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()

    def _get_trainer_region(self, trainer_job: str) -> str | None:
        """Resolve a trainer job's training region for hot-load colocation.

        ``trainer_job`` is a full resource name
        (``accounts/{account}/rlorTrainerJobs/{job}``). Returns the region
        string (e.g. ``US_OHIO_1``) or ``None`` when it can't be resolved.
        Best-effort: any failure returns ``None`` so deployment creation still
        proceeds and the control plane colocates server-side.
        """
        path = f"/v1/{trainer_job.lstrip('/')}"
        try:
            resp = self._get(path)
        except Exception:
            return None
        if not resp.is_success:
            return None
        region = resp.json().get("trainingConfig", {}).get("region")
        return region or None

    def _delete_deployment(self, deployment_id: str, ignore_checks: bool = True, hard: bool = True) -> None:
        path = f"/v1/accounts/{self.account_id}/deployments/{deployment_id}"
        params = []
        if ignore_checks:
            params.append("ignoreChecks=true")
        if hard:
            params.append("hard=true")
        if params:
            path = f"{path}?{'&'.join(params)}"
        resp = self._delete(path)
        resp.raise_for_status()

    def _create_deployment(self, config: DeploymentConfig) -> dict:
        path = f"/v1/accounts/{self.account_id}/deployments?deploymentId={config.deployment_id}"
        if config.skip_shape_validation:
            path = f"{path}&skipShapeValidation=true"
        if config.disable_speculative_decoding:
            path = f"{path}&disableSpeculativeDecoding=true"

        # Colocation: a hot-load deployment must live in the same region as its
        # trainer (the trainer writes checkpoints to region-local fast storage,
        # and cross-region hot-load silently falls back / fails). When a
        # hot_load_trainer_job is set we resolve the trainer's region and either
        # inherit it (region unset) or reject an explicit conflict, so SDK
        # callers get colocation without copying cookbook orchestration. The
        # control plane enforces the same invariant server-side; this is a
        # best-effort, friendlier client-side guard.
        region = config.region
        if config.hot_load_trainer_job:
            trainer_region = self._get_trainer_region(config.hot_load_trainer_job)
            if trainer_region:
                if config.region and config.region != trainer_region:
                    raise ValueError(
                        f"hot_load_trainer_job {config.hot_load_trainer_job} is in region "
                        f"{trainer_region}, but the deployment requests region {config.region}; "
                        "hot-load requires the deployment to be colocated with the trainer. "
                        "Leave region unset to inherit the trainer's region."
                    )
                if not config.region:
                    logger.info(
                        "Colocating hot-load deployment with trainer %s in region %s",
                        config.hot_load_trainer_job,
                        trainer_region,
                    )
                    # Resolved region flows through a local into the request body;
                    # the caller's DeploymentConfig is not mutated.
                    region = trainer_region

        body = self._build_deployment_body(config, region=region)

        logger.info("Creating deployment: %s", config.deployment_id)
        resp = self._post(path, json=body)
        if resp.status_code == 409:
            logger.info(
                "Deployment %s already exists (409 Conflict), fetching existing deployment",
                config.deployment_id,
            )
            existing = self._get_deployment(config.deployment_id)
            if existing:
                return existing
        if not resp.is_success:
            error_msg = parse_api_error(resp)
            hint = HTTP_STATUS_HINTS.get(resp.status_code, "")
            extra = ""
            if resp.status_code == 400:
                extra = (
                    "\n  Verify region, deployment_shape, base_model, and extra_args "
                    "match the selected deployment flow."
                    "\n  For hotload, use one documented scope: PER_TRAINER via "
                    "hot_load_trainer_job, or PER_DEPLOYMENT via a deployment-owned bucket."
                )
            logger.warning(
                "\n%s",
                format_sdk_error(
                    f"Deployment creation failed (HTTP {resp.status_code})",
                    error_msg,
                    f"{hint}{extra}",
                    docs_url=DOCS_SDK,
                ),
            )
        resp.raise_for_status()
        return resp.json()

    @staticmethod
    def _build_deployment_body(config: DeploymentConfig, *, region: str | None = None) -> dict[str, Any]:
        """Assemble the deployment creation request body from the config.

        ``region`` is the resolved placement region (falling back to
        ``config.region``); the caller passes the colocation-resolved value so
        this method never has to mutate the config. The accelerator type is
        omitted when a deployment shape is set — the shape owns the hardware
        selection.
        """
        region = region or config.region
        body: dict[str, Any] = {
            "baseModel": config.base_model,
            "description": config.description or DEFAULT_DEPLOYMENT_DESCRIPTION,
            "minReplicaCount": config.min_replica_count,
            "maxReplicaCount": config.max_replica_count,
            "enableHotLoad": config.enable_hot_load,
            "forTraining": config.enable_hot_load,
        }
        if region:
            body["placement"] = {"region": region}
        if config.hot_load_bucket_type:
            body["hotLoadBucketType"] = config.hot_load_bucket_type
        if config.hot_load_trainer_job:
            body["hotLoadTrainerJob"] = config.hot_load_trainer_job
        if config.deployment_shape:
            body["deploymentShape"] = config.deployment_shape
        else:
            body["acceleratorType"] = config.accelerator_type
        if config.extra_args:
            flat = []
            for arg in config.extra_args:
                if " " in arg:
                    flat.extend(arg.split())
                else:
                    flat.append(arg)
            body["extraArgs"] = flat
        if config.extra_values:
            body["extraValues"] = config.extra_values
        if config.annotations:
            body["annotations"] = config.annotations
        return body

    def _parse_deployment_info(self, deployment_id: str, data: dict) -> DeploymentInfo:
        return DeploymentInfo(
            deployment_id=deployment_id,
            name=data.get("name", ""),
            state=data.get("state", "UNKNOWN"),
            hot_load_bucket_url=data.get("hotLoadBucketUrl"),
            hot_load_trainer_job=data.get("hotLoadTrainerJob") or data.get("hot_load_trainer_job"),
            deployment_shape_version=data.get("deploymentShape") or data.get("deployment_shape"),
            inference_model=f"accounts/{self.account_id}/deployments/{deployment_id}",
        )

    def _wait_for_deletion(
        self,
        deployment_id: str,
        timeout_s: float = DEPLOYMENT_DELETION_TIMEOUT_S,
        poll_interval_s: float = DEPLOYMENT_DELETION_POLL_S,
    ) -> None:
        """Poll until the deployment is gone (404) or in DELETED state."""
        start = time.time()
        while time.time() - start < timeout_s:
            data = self._get_deployment(deployment_id)
            if data is None:
                return
            state = data.get("state", "UNKNOWN")
            if state == "DELETED":
                return
            logger.info(
                "[%ds] Waiting for deletion of %s (state=%s)...",
                int(time.time() - start),
                deployment_id,
                state,
            )
            time.sleep(poll_interval_s)
        logger.warning(
            "Deployment %s not fully deleted after %ds, proceeding anyway",
            deployment_id,
            timeout_s,
        )

    # -- High-level deployment operations --------------------------------------

    def create_or_get(
        self,
        config: DeploymentConfig,
        force_recreate: bool = False,
    ) -> DeploymentInfo:
        """Create or get a deployment, handling bad states."""
        existing = self._get_deployment(config.deployment_id)

        if existing:
            state = existing.get("state", "UNKNOWN")
            bad_states = ("FAILED", "DELETED", "DELETING")
            if state in bad_states or force_recreate:
                logger.info(
                    "Deployment %s in state %s (or force_recreate), deleting...",
                    config.deployment_id,
                    state,
                )
                try:
                    self._delete_deployment(config.deployment_id)
                    self._wait_for_deletion(config.deployment_id)
                except Exception as e:
                    logger.warning(
                        "Failed to delete deployment %s before recreate: %s. "
                        "You may need to delete it manually in the Fireworks console: %s",
                        config.deployment_id,
                        e,
                        CONSOLE_URL,
                    )
            else:
                return self._parse_deployment_info(config.deployment_id, existing)

        created = self._create_deployment(config)
        return self._parse_deployment_info(config.deployment_id, created)

    def wait_for_ready(
        self,
        deployment_id: str,
        timeout_s: float = DEPLOYMENT_READY_DEFAULT_TIMEOUT_S,
        poll_interval_s: float = DEPLOYMENT_READY_POLL_S,
    ) -> DeploymentInfo:
        """Wait for a deployment to reach READY state.

        Polls the control-plane state and probes the deployment with an
        inference request on every cycle.  The deployment is considered
        ready as soon as either condition is met:

        1. Control-plane state transitions to READY, or
        2. The deployment responds to a warmup inference request (HTTP 200).

        Condition 2 handles hotload-enabled deployments whose background
        reconciliation is intentionally skipped -- the control-plane
        state may stay CREATING even though the deployment is already
        serving.
        """
        start = time.time()
        model = f"accounts/{self.account_id}/deployments/{deployment_id}"
        while time.time() - start < timeout_s:
            data = self._get_deployment(deployment_id)
            if not data:
                raise RuntimeError(
                    format_sdk_error(
                        f"Deployment '{deployment_id}' not found",
                        "The control plane returned no deployment record for this deployment ID.",
                        "Verify the deployment ID and account. Create the deployment first if this is a new run.",
                        docs_url=DOCS_SDK,
                    )
                )
            state = data.get("state", "UNKNOWN")
            elapsed = int(time.time() - start)
            if state == "READY":
                logger.info("[%ds] Deployment %s: READY", elapsed, deployment_id)
                self.boot_time_s = time.time() - start
                return self._parse_deployment_info(deployment_id, data)
            if state in ("FAILED", "DELETED", "DELETING"):
                raise RuntimeError(
                    format_sdk_error(
                        f"Deployment '{deployment_id}' entered bad state: {state}",
                        f"The control plane reports deployment state {state}, so readiness polling stopped.",
                        f"Check deployment events and logs in the Fireworks console: {CONSOLE_URL}\n"
                        "  Recreate the deployment if the config is wrong or the resource was deleted.",
                        docs_url=DOCS_SDK,
                        show_support=True,
                    )
                )
            if state == "CREATING" and self._probe_inference(model):
                logger.info(
                    "[%ds] Deployment %s: CREATING but serving requests -- treating as ready",
                    elapsed,
                    deployment_id,
                )
                self.boot_time_s = time.time() - start
                return self._parse_deployment_info(deployment_id, data)
            logger.info("[%ds] Deployment %s: %s", elapsed, deployment_id, state)
            time.sleep(poll_interval_s)
        raise TimeoutError(
            format_sdk_error(
                f"Deployment '{deployment_id}' not ready within {timeout_s}s",
                "The control-plane state did not reach READY and the token-in warmup probe did not return HTTP 200 before the timeout.",
                f"Increase the deployment ready timeout (current: {timeout_s}s) and check deployment status in the Fireworks console: {CONSOLE_URL}",
                docs_url=DOCS_SDK,
            )
        )

    def get(self, deployment_id: str) -> DeploymentInfo | None:
        """Get info for an existing deployment."""
        data = self._get_deployment(deployment_id)
        if data:
            return self._parse_deployment_info(deployment_id, data)
        return None

    def delete(self, deployment_id: str) -> None:
        """Delete a deployment (best-effort)."""
        try:
            self._delete_deployment(deployment_id)
            logger.info("Deleted deployment: %s", deployment_id)
        except Exception as e:
            logger.warning(
                "Failed to delete deployment %s: %s. You can delete it manually in the Fireworks console: %s",
                deployment_id,
                e,
                CONSOLE_URL,
            )

    def scale_to_zero(self, deployment_id: str) -> None:
        """Scale a deployment to zero replicas, releasing all accelerators.

        This is a lighter alternative to :meth:`delete` -- the deployment
        remains available for future scale-up, but no GPUs are consumed.
        Useful for cleanup after training completes.
        """
        path = f"/v1/accounts/{self.account_id}/deployments/{deployment_id}"
        body = {"maxReplicaCount": 0, "minReplicaCount": 0}
        try:
            resp = self._patch(path, json=body)
            resp.raise_for_status()
            logger.info("Scaled deployment to zero: %s", deployment_id)
        except Exception as e:
            logger.warning(
                "Failed to scale deployment %s to zero: %s. "
                "The deployment may still be consuming GPU resources. "
                "You can scale it down manually in the Fireworks console: %s",
                deployment_id,
                e,
                CONSOLE_URL,
            )

    def update(
        self,
        deployment_id: str,
        body: dict[str, Any],
        update_mask: str | list[str],
    ) -> DeploymentInfo:
        """Partially update a deployment via PATCH.

        Args:
            deployment_id: ID of the deployment to update.
            body: JSON body with the fields to update (camelCase keys).
            update_mask: Field paths (snake_case) to update — either a
                comma-separated string or a list of strings. Required:
                only the listed fields are modified; other fields are
                left untouched. (Omitting the mask would cause the server
                to replace all mutable fields with whatever ``body``
                contained, silently zeroing out anything not specified.)

        Returns:
            The updated deployment as a :class:`DeploymentInfo`.
        """
        if isinstance(update_mask, list):
            update_mask = ",".join(update_mask)
        path = f"/v1/accounts/{self.account_id}/deployments/{deployment_id}"
        resp = self._patch(path, json=body, params={"updateMask": update_mask})
        resp.raise_for_status()
        return self._parse_deployment_info(deployment_id, resp.json())

    def _read_replica_identity(self, deployment_id: str, base_model: str) -> str | None:
        """Return the first replica identity from hotload status, or None if no replica is up."""
        status = self.hotload_check_status(deployment_id, base_model)
        replicas = status.get("replicas") or []
        if not replicas:
            return None
        replica = replicas[0]
        return replica.get("current_snapshot_identity") or replica.get("identity")

    def reattach_trainer(
        self,
        deployment: DeploymentInfo | str,
        *,
        base_model: str,
        trainer_job_name: str,
        timeout_s: float,
        poll_interval_s: float = HOTLOAD_WAIT_POLL_S,
    ) -> DeploymentInfo:
        """Point an existing deployment at a trainer bucket and wait for the serving pod to roll."""
        if isinstance(deployment, str):
            deployment_id = deployment
            deployment_info = self.get(deployment_id)
            if deployment_info is None:
                raise RuntimeError(f"Deployment {deployment_id!r} does not exist")
        else:
            deployment_info = deployment
            deployment_id = deployment.deployment_id

        if _deployment_hot_load_trainer_job(deployment_info) == trainer_job_name:
            logger.info(
                "Deployment %s is already attached to trainer %s",
                deployment_id,
                trainer_job_name,
            )
            return deployment_info

        logger.info(
            "Re-attaching deployment %s to trainer %s via hotLoadTrainerJob PATCH",
            deployment_id,
            trainer_job_name,
        )
        prev_identity = self._read_replica_identity(deployment_id, base_model)
        updated = self.update(
            deployment_id,
            body={"hotLoadTrainerJob": trainer_job_name},
            update_mask="hot_load_trainer_job",
        )

        deadline = time.time() + max(timeout_s, 1)
        saw_pod_gone = prev_identity is None
        while time.time() < deadline:
            current = self._read_replica_identity(deployment_id, base_model)
            if prev_identity is None:
                if current is not None:
                    logger.info("Re-attach settled: hotload manager up on pod %s", current)
                    return updated
            elif current is None:
                if not saw_pod_gone:
                    logger.info("Old pod %s has gone; waiting for new pod...", prev_identity)
                saw_pod_gone = True
            elif current != prev_identity:
                logger.info("Re-attach settled: new pod %s replaced %s", current, prev_identity)
                return updated
            time.sleep(poll_interval_s)

        raise TimeoutError(
            f"Re-attach for deployment {deployment_id!r} did not produce a fresh pod "
            f"within {timeout_s}s (prev_identity={prev_identity!r})."
        )

    # -- Hotload operations ----------------------------------------------------

    @staticmethod
    def _reset_prompt_cache_unsupported(resp: Any) -> bool:
        """Return True when the gateway rejects the deprecated field."""
        if getattr(resp, "status_code", None) != 400:
            return False
        parts = [parse_api_error(resp)]
        text = getattr(resp, "text", None)
        if text:
            parts.append(text)
        message = " ".join(parts).lower()
        return (
            "reset_prompt_cache" in message
            and "extra inputs are not permitted" in message
        )

    def hotload(
        self,
        deployment_id: str,
        base_model: str,
        snapshot_identity: str,
        incremental_snapshot_metadata: dict[str, Any] | None = None,
        reset_prompt_cache: bool = True,
        timeout: int = 60,
        path: str | None = None,
    ) -> dict[str, Any]:
        """Load a weight snapshot onto a deployment via the gateway.

        Args:
            deployment_id: Target deployment ID.
            base_model: Model name (e.g., accounts/fireworks/models/qwen3-8b).
            snapshot_identity: Snapshot identity to load.
            incremental_snapshot_metadata: For delta loads — must include
                previous_snapshot_identity, compression_format, checksum_format.
            reset_prompt_cache: Whether to reset the prompt cache after loading.
            timeout: Request timeout in seconds.
            path: Optional object-storage URI (``gs://bucket/prefix/``) the
                serving side may use to fetch the snapshot bytes when the
                deployment's configured storage is not sufficient. Forwarded
                as the ``x-fireworks-hot-load-source-url`` header (not a body
                field) so the same wire shape is accepted across serving
                backends; backends that do not consume the header simply
                ignore it.
        """
        headers = self._hotload_headers(deployment_id, base_model, path=path)
        url = f"{self.hotload_api_url}/hot_load/v1/models/hot_load"

        ckpt_type = "DELTA" if incremental_snapshot_metadata else "FULL"
        logger.info(
            "Hotloading %s snapshot '%s' to deployment '%s'%s",
            ckpt_type,
            snapshot_identity,
            deployment_id,
            f" (source={path})" if path else "",
        )

        include_reset_prompt_cache = self._hotload_reset_prompt_cache_supported is not False

        def _payload(include_reset: bool) -> dict[str, Any]:
            payload: dict[str, Any] = {"identity": snapshot_identity}
            if include_reset:
                payload["reset_prompt_cache"] = reset_prompt_cache
            if incremental_snapshot_metadata:
                payload["incremental_snapshot_metadata"] = incremental_snapshot_metadata
            return payload

        resp = self._sync_request(
            url,
            method="POST",
            headers=headers,
            json=_payload(include_reset_prompt_cache),
            timeout=timeout,
        )
        if (
            not resp.is_success
            and include_reset_prompt_cache
            and self._reset_prompt_cache_unsupported(resp)
        ):
            logger.info(
                "Hotload API rejected reset_prompt_cache; retrying without it"
            )
            self._hotload_reset_prompt_cache_supported = False
            resp = self._sync_request(
                url,
                method="POST",
                headers=headers,
                json=_payload(False),
                timeout=timeout,
            )
        elif resp.is_success and include_reset_prompt_cache:
            self._hotload_reset_prompt_cache_supported = True
        if not resp.is_success:
            error_msg = parse_api_error(resp)
            hint = HTTP_STATUS_HINTS.get(resp.status_code, "")
            logger.warning(
                "\n%s",
                format_sdk_error(
                    f"Hotload API error (HTTP {resp.status_code})",
                    error_msg,
                    f"{hint}\n"
                    "  Verify the deployment is hotload-enabled, the base model matches the deployment, "
                    "and the snapshot identity came from save_weights_for_sampler.",
                    docs_url=DOCS_SDK,
                ),
            )
        resp.raise_for_status()
        return resp.json()

    def hotload_check_status(
        self,
        deployment_id: str,
        base_model: str,
        timeout: int = 30,
    ) -> dict[str, Any]:
        """Check current hotload status for a deployment."""
        headers = self._hotload_headers(deployment_id, base_model)
        url = f"{self.hotload_api_url}/hot_load/v1/models/hot_load"

        resp = self._sync_request(url, method="GET", headers=headers, timeout=timeout)
        resp.raise_for_status()
        return resp.json()

    def wait_for_hotload(
        self,
        deployment_id: str,
        base_model: str,
        expected_identity: str,
        timeout_seconds: int = HOTLOAD_WAIT_TIMEOUT_S,
        poll_interval: int = HOTLOAD_WAIT_POLL_S,
    ) -> bool:
        """Wait for hotload to complete. Returns True on success."""
        logger.info("Waiting for hotload (identity=%s)...", expected_identity)
        start = time.time()
        self._last_hotload_error_message = None
        last_current_identity: str | None = None
        last_stage = "unknown"
        last_readiness: bool | None = None

        while time.time() - start < timeout_seconds:
            try:
                status = self.hotload_check_status(
                    deployment_id,
                    base_model,
                )

                # Strict modern schema: hotload status must be replicas-based.
                replicas = status.get("replicas")
                if not isinstance(replicas, list):
                    raise RuntimeError(
                        format_sdk_error(
                            "Unrecognized hotload status response format",
                            f"Expected 'replicas' list, got keys: {list(status.keys())}",
                            "The SDK hotload waiter expects the serving status endpoint to return a replicas list. "
                            "Check the cookbook skill for the supported SDK/serving path, then retry with matching versions.",
                            docs_url=DOCS_SDK,
                            show_support=True,
                        )
                    )
                if replicas:
                    replica = replicas[0]
                    current_identity = replica.get("current_snapshot_identity")
                    stage = replica.get("loading_state", {}).get("stage", "unknown")
                    readiness = replica.get("readiness", False)
                    loaded_adapters = replica.get("loaded_adapters") or []
                else:
                    current_identity = None
                    stage = "pending"
                    readiness = False
                    loaded_adapters = []
                last_current_identity = current_identity
                last_stage = stage
                last_readiness = readiness

                elapsed = int(time.time() - start)

                # Some serving backends report multi-adapter completion via a
                # per-adapter ``loaded_adapters`` array (one ``"loaded"`` entry
                # per adapter that finished loading) rather than a single
                # ``current_snapshot_identity`` (which only makes sense when
                # a single snapshot defines the deployment's identity at a
                # time). Both shapes are accepted.
                multi_adapter_loaded = any(
                    isinstance(a, dict)
                    and a.get("identity") == expected_identity
                    and a.get("status") == "loaded"
                    for a in loaded_adapters
                )
                if readiness and (
                    current_identity == expected_identity or multi_adapter_loaded
                ):
                    logger.info("Hotload complete: %s (took %ds)", expected_identity, elapsed)
                    return True
                elif stage == "error":
                    # Only treat the error as fatal if it's for the snapshot
                    # we just requested. A stale error from a previous
                    # snapshot (e.g., after re-attaching to a new trainer)
                    # should be ignored — the new hotload request may not
                    # have been processed yet.
                    error_target = replica.get("loading_state", {}).get(
                        "target_snapshot_identity"
                    )
                    if error_target == expected_identity:
                        cause = (
                            "The deployment status reported an error for the "
                            "requested snapshot. Expected client snapshot: "
                            f"{expected_identity}; current deployment snapshot: "
                            f"{_format_snapshot_identity(current_identity)}; "
                            f"target snapshot: {error_target}; stage=error."
                        )
                        self._last_hotload_error_message = format_sdk_error(
                            f"Hotload failed for snapshot '{expected_identity}'",
                            cause,
                            HOTLOAD_RECOVERY_STEPS,
                            docs_url=DOCS_SDK,
                            show_support=True,
                        )
                        logger.warning(
                            "\n%s",
                            self._last_hotload_error_message,
                        )
                        return False
                    logger.info(
                        "Hotload: stage=error (stale, target=%s != expected=%s), "
                        "waiting for server to process new request (%ds)",
                        error_target,
                        expected_identity,
                        elapsed,
                    )
                else:
                    logger.info(
                        "Hotload: stage=%s, current=%s, loading=%s, ready=%s, "
                        "loaded_adapters=%s (%ds)",
                        stage,
                        current_identity,
                        expected_identity,
                        readiness,
                        [
                            a.get("identity")
                            for a in loaded_adapters
                            if isinstance(a, dict)
                        ],
                        elapsed,
                    )
            except RuntimeError:
                raise
            except Exception as e:
                logger.warning(
                    "Error checking hotload status (will retry): %s. "
                    "This can be transient if the deployment is restarting.",
                    e,
                )

            time.sleep(poll_interval)

        logger.warning(
            "\n%s",
            self._format_hotload_timeout_error(
                expected_identity=expected_identity,
                timeout_seconds=timeout_seconds,
                current_identity=last_current_identity,
                stage=last_stage,
                readiness=last_readiness,
            ),
        )
        return False

    def _format_hotload_timeout_error(
        self,
        *,
        expected_identity: str,
        timeout_seconds: int,
        current_identity: str | None,
        stage: str,
        readiness: bool | None,
    ) -> str:
        snapshot_state = (
            f"Expected client snapshot: {expected_identity}; current deployment "
            f"snapshot: {_format_snapshot_identity(current_identity)}."
        )
        if current_identity and current_identity != expected_identity:
            cause = (
                "The deployment status did not report the requested snapshot "
                f"as loaded before the timeout. {snapshot_state}"
            )
        else:
            cause = (
                "The deployment status did not become ready for the requested "
                f"snapshot before the timeout. {snapshot_state}"
            )
        if stage != "unknown" or readiness is not None:
            cause = f"{cause} Last hotload state: stage={stage}, ready={readiness}."
        self._last_hotload_error_message = format_sdk_error(
            f"Hotload did not complete within {timeout_seconds}s",
            cause,
            f"{HOTLOAD_RECOVERY_STEPS}\n"
            f"  If the deployment is simply slow or unhealthy, increase the "
            f"hotload timeout (current: {timeout_seconds}s) and check "
            f"deployment health in the Fireworks console: {CONSOLE_URL}",
            docs_url=DOCS_SDK,
        )
        return self._last_hotload_error_message

    def hotload_and_wait(
        self,
        deployment_id: str,
        base_model: str,
        snapshot_identity: str,
        incremental_snapshot_metadata: dict[str, Any] | None = None,
        reset_prompt_cache: bool = True,
        timeout_seconds: int = HOTLOAD_WAIT_TIMEOUT_S,
        path: str | None = None,
    ) -> bool:
        """Hotload a snapshot and wait for it to complete. Returns True on success.

        See :meth:`hotload` for ``path`` semantics.
        """
        self.hotload(
            deployment_id=deployment_id,
            base_model=base_model,
            snapshot_identity=snapshot_identity,
            incremental_snapshot_metadata=incremental_snapshot_metadata,
            reset_prompt_cache=reset_prompt_cache,
            path=path,
        )
        return self.wait_for_hotload(
            deployment_id=deployment_id,
            base_model=base_model,
            expected_identity=snapshot_identity,
            timeout_seconds=timeout_seconds,
        )

    def _probe_inference(self, model: str) -> bool:
        """Silent single-shot probe: returns True if deployment responds HTTP 200."""
        url = f"{self.inference_url}/inference/v1/completions"
        headers = self._headers(Authorization=f"Bearer {self.api_key}")
        payload = {
            "model": model,
            "prompt": [1, 2],
            "max_tokens": 4,
            "temperature": 0.0,
        }
        try:
            resp = self._sync_request(
                url,
                method="POST",
                headers=headers,
                json=payload,
                timeout=WARMUP_PROBE_TIMEOUT_S,
            )
            return resp.status_code == 200
        except Exception:
            return False

    def warmup(
        self,
        model: str,
        max_retries: int = 30,
        retry_interval_s: float = 10.0,
    ) -> bool:
        """Send a token-in test request to the deployment and wait until it responds."""
        completions_url = f"{self.inference_url}/inference/v1/completions"
        verify = _should_verify_ssl(self.inference_url)

        headers = self._headers(Authorization=f"Bearer {self.api_key}")
        payload = {
            "model": model,
            "prompt": [1, 2],
            "max_tokens": 4,
            "temperature": 0.0,
        }

        logger.info("Warming up inference deployment (%d retries)...", max_retries)
        for attempt in range(1, max_retries + 1):
            try:
                resp = self._sync_request(
                    completions_url,
                    method="POST",
                    headers=headers,
                    json=payload,
                    timeout=HTTP_READ_TIMEOUT_S,
                )
                if resp.status_code == 200:
                    logger.info("Inference deployment ready after %d attempt(s)", attempt)
                    return True
                logger.info(
                    "Warmup attempt %d/%d: HTTP %d",
                    attempt,
                    max_retries,
                    resp.status_code,
                )
            except Exception as e:
                logger.info("Warmup attempt %d/%d: %s", attempt, max_retries, e)
            time.sleep(retry_interval_s)

        logger.warning(
            "\n%s",
            format_sdk_error(
                f"Inference deployment not ready after {max_retries} retries",
                "The token-in completions warmup request did not receive HTTP 200 before retries were exhausted.",
                f"Check the deployment state in the Fireworks console: {CONSOLE_URL}\n"
                "  Verify the inference URL and model resource name used by the client.",
                docs_url=DOCS_SDK,
            ),
        )
        return False




# ---------------------------------------------------------------------------
# Backwards-compatible re-exports (these classes moved to sibling modules
# when deployment.py was split). Existing import sites continue to use
# ``fireworks.training.sdk.deployment``.
# ---------------------------------------------------------------------------
from fireworks.training.sdk._sse import (  # noqa: F401,E402
    _SSEEvent,
    _SSEDecoder,
    _SSETruncationError,
)
from fireworks.training.sdk.sampling import (  # noqa: F401,E402
    ServerMetrics,
    DeploymentSampler,
    SampledCompletion,
    FiretitanSamplingClient,
)
from fireworks.training.sdk.concurrency import (  # noqa: F401,E402
    FixedConcurrencyController,
    AdaptiveConcurrencyController,
)
