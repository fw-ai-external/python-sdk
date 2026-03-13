"""Trainer Job Management for Fireworks.

Manages the lifecycle of service-mode trainer jobs (called "RLOR jobs" in the
Fireworks REST API) that run the firetitan training backend and expose the
Tinker HTTP protocol.  These jobs are algorithm-agnostic — usable for DPO,
GRPO, SFT, or any Tinker-protocol training.
"""

from __future__ import annotations

import re
import time
import logging
from typing import Any
from dataclasses import dataclass
from urllib.parse import urlencode

from fireworks.training.sdk.errors import (
    DOCS_SDK,
    CONSOLE_URL,
    HTTP_STATUS_HINTS,
    parse_api_error,
    format_sdk_error,
)
from fireworks.training.sdk._rest_client import _RestClient

logger = logging.getLogger(__name__)


@dataclass
class TrainerServiceEndpoint:
    """Info returned after creating/connecting to a service-mode trainer job."""

    job_name: str
    job_id: str
    base_url: str


@dataclass
class TrainingShapeProfile:
    """Resolved training shape profile from the control plane.

    Contains all shape-derived config: region, accelerator, image tag,
    sharding, deployment shape, etc.  Returned by
    :meth:`TrainerJobManager.resolve_training_profile`.
    """

    training_shape_version: str
    """Versioned training-shape resource name.

    Example:
    ``accounts/fw/trainingShapes/ts-x/versions/abc123``.
    """
    trainer_image_tag: str
    max_supported_context_length: int
    node_count: int
    deployment_shape_version: str
    deployment_image_tag: str
    accelerator_type: str
    accelerator_count: int
    base_model_weight_precision: str
    pipeline_parallelism: int = 1
    """Pipeline parallelism degree from the training shape's sharding scheme."""

    @property
    def training_shape(self) -> str | None:
        """Training shape name derived from ``training_shape_version``.

        Strips the ``/versions/...`` suffix, e.g.
        ``"accounts/fw/trainingShapes/ts-x/versions/1"`` becomes
        ``"accounts/fw/trainingShapes/ts-x"``.
        """
        if not self.training_shape_version:
            return None
        return re.sub(r"/versions/[^/]+$", "", self.training_shape_version)

    @property
    def deployment_shape(self) -> str | None:
        """Deployment shape name derived from ``deployment_shape_version``.

        Strips the ``/versions/...`` suffix, e.g.
        ``"accounts/fw/deploymentShapes/ds-x/versions/1"`` becomes
        ``"accounts/fw/deploymentShapes/ds-x"``.
        """
        if not self.deployment_shape_version:
            return None
        return re.sub(r"/versions/[^/]+$", "", self.deployment_shape_version)


@dataclass
class TrainerJobConfig:
    """Configuration for creating a trainer job."""

    base_model: str
    lora_rank: int = 0
    max_context_length: int | None = None
    """Max context length for the trainer.

    Omitted from the request on validated-shape launches (the backend
    populates it from the training shape).  On ``skip_validations`` or
    manual launches it is sent as-is.
    """
    learning_rate: float = 1e-5
    gradient_accumulation_steps: int = 1
    node_count: int | None = None
    """Number of trainer nodes.

    Omitted from the request on validated-shape launches (the backend
    populates it from the training shape).  Defaults to ``1`` when sent.
    """
    display_name: str | None = None
    hot_load_deployment_id: str | None = None
    region: str | None = None
    custom_image_tag: str | None = None
    """Trainer container image tag.

    Omitted from the request on validated-shape launches (the backend
    populates it from the training shape).
    """
    extra_args: list[str] | None = None
    """Additional trainer arguments passed through to the backend."""
    accelerator_type: str | None = None
    """Accelerator type override.

    Omitted from the request on validated-shape launches (the backend
    populates it from the training shape).  On ``skip_validations``
    launches, explicit values are sent as user overrides.
    """
    accelerator_count: int | None = None
    """Accelerator count override.

    Omitted from the request on validated-shape launches (the backend
    populates it from the training shape).  On ``skip_validations``
    launches, explicit values are sent as user overrides.
    """
    training_shape_ref: str | None = None
    """Training-shape selector resource reference.

    Sent as the top-level ``trainingShape`` request parameter so the backend can
    select and apply the validated launch profile. Accepts either an
    unversioned training-shape resource or an exact training-shape version.
    """
    skip_validations: bool = False
    forward_only: bool = False

    def apply_shape(self, profile: TrainingShapeProfile) -> None:
        """Populate request fields from a resolved training shape.

        This copies the resolved shape-derived launch settings onto the config,
        including accelerators. For validated launches the SDK still omits
        accelerator fields from the outgoing request when ``training_shape_ref``
        is set, so the control plane uses the validated shape directly.

        By default the shape values always win. When ``skip_validations`` is
        True, any config field the user already set (non-None) is kept as an
        override and the shape value is skipped for that field.
        """
        _SHAPE_FIELD_MAP: list[tuple[str, str, Any]] = [
            # (config_field, profile_field, sentinel_to_skip)
            ("accelerator_type", "accelerator_type", ""),
            ("accelerator_count", "accelerator_count", 0),
            ("custom_image_tag", "trainer_image_tag", ""),
            ("node_count", "node_count", 0),
            ("max_context_length", "max_supported_context_length", 0),
        ]

        for cfg_field, profile_field, sentinel in _SHAPE_FIELD_MAP:
            shape_val = getattr(profile, profile_field)
            if shape_val is None or shape_val == sentinel:
                continue
            current = getattr(self, cfg_field)
            if self.skip_validations and current is not None:
                logger.info(
                    "Keeping user override %s=%s (shape: %s)",
                    cfg_field,
                    current,
                    shape_val,
                )
                continue
            setattr(self, cfg_field, shape_val)

        logger.info(
            "Applied training shape: %s (accel=%s, image=%s, nodes=%s, max_ctx=%s, pp=%d)",
            profile.training_shape_version,
            profile.accelerator_type,
            profile.trainer_image_tag,
            profile.node_count,
            profile.max_supported_context_length,
            profile.pipeline_parallelism,
        )


class TrainerJobManager(_RestClient):
    """Manages trainer job lifecycle via Fireworks REST API.

    The Fireworks API calls these "RLOR trainer jobs", but they are
    algorithm-agnostic — usable for DPO, GRPO, SFT, or any training
    that speaks the Tinker protocol.

    Example::

        manager = TrainerJobManager(
            api_key="...",
            account_id="...",
        )

        # Create and wait for a new job
        endpoint = manager.create_and_wait(config)

        # Or reuse an existing job
        endpoint = manager.wait_for_existing(job_id="...")

        # Clean up when done
        manager.delete(endpoint.job_id)
    """

    def __init__(
        self,
        api_key: str,
        account_id: str,
        base_url: str = "https://api.fireworks.ai",
        additional_headers: dict[str, str] | None = None,
        verify_ssl: bool | None = None,
    ):
        super().__init__(
            api_key=api_key,
            account_id=account_id,
            base_url=base_url,
            additional_headers=additional_headers,
            verify_ssl=verify_ssl,
        )
        self.boot_time_s: float | None = None
        """Wall-clock seconds spent in the most recent ``_poll_until_ready`` call."""

    # -- Training shape resolution ------------------------------------------------

    def resolve_training_profile(
        self,
        training_shape_id: str,
        **_kwargs,
    ) -> TrainingShapeProfile:
        """Fetch the latest validated version of a training shape.

        Reads the latest validated training-shape version and extracts all
        shape-derived config (region, accelerator, image tag, deployment
        shape, etc.) from its embedded snapshot. This gives callers a pinned
        versioned training-shape reference they can pass back when launching
        validated service-mode jobs.

        Args:
            training_shape_id: Shape ID (e.g. ``ts-qwen3-8b-policy``) or full
                training shape name (e.g.
                ``accounts/fw/trainingShapes/ts-qwen3-8b-policy``).

        Returns:
            :class:`TrainingShapeProfile` with all shape-derived fields.
        """
        training_shape_name = training_shape_id
        if not training_shape_name.startswith("accounts/"):
            training_shape_name = (
                f"accounts/{self.account_id}/trainingShapes/{training_shape_id}"
            )
        path = (
            f"/v1/{training_shape_name}/versions?"
            f"{urlencode({'filter': 'latest_validated=true', 'pageSize': 1})}"
        )
        resp = self._get(path, timeout=30)
        if not resp.ok:
            error_msg = parse_api_error(resp)
            show_support = False
            if resp.status_code == 404:
                if training_shape_id.startswith("accounts/"):
                    solution = (
                        f"Training shape '{training_shape_id}' was not found. "
                        "Verify the training_shape_id is correct and the shape exists."
                    )
                else:
                    solution = (
                        f"Training shape '{training_shape_id}' was not found under account '{self.account_id}'. "
                        "Verify the training_shape_id is correct and the shape exists."
                    )
            elif resp.status_code == 403:
                solution = (
                    f"Permission denied for training shape '{training_shape_id}'. "
                    f"Ensure your account owns or has access to this shape."
                )
            else:
                solution = "Verify the training_shape_id and account have the shape registered."
                show_support = True
            raise RuntimeError(
                format_sdk_error(
                    f"Failed to fetch training shape '{training_shape_id}' (HTTP {resp.status_code})",
                    error_msg,
                    solution,
                    docs_url=DOCS_SDK,
                    show_support=show_support,
                )
            )
        data = resp.json()
        versions = data.get("trainingShapeVersions", []) or []
        if not versions:
            raise RuntimeError(
                format_sdk_error(
                    f"Failed to resolve latest validated training shape for '{training_shape_id}'",
                    "No latest validated training-shape version was returned.",
                    (
                        "Validate a training-shape version first, or check that the "
                        "training_shape_id is correct and visible to your account."
                    ),
                    docs_url=DOCS_SDK,
                    show_support=False,
                )
            )
        version = versions[0]
        snapshot = version.get("snapshot", {}) or {}
        sharding = snapshot.get("trainerShardingScheme", {}) or {}
        pp = int(sharding.get("pipelineParallelism", 1) or 1)
        return TrainingShapeProfile(
            training_shape_version=version.get("name", ""),
            trainer_image_tag=snapshot.get("trainerImageTag", ""),
            max_supported_context_length=snapshot.get("maxSupportedContextLength", 0),
            node_count=snapshot.get("nodeCount", 1),
            deployment_shape_version=snapshot.get("deploymentShapeVersion", ""),
            deployment_image_tag=snapshot.get("deploymentImageTag", ""),
            accelerator_type=snapshot.get("acceleratorType", ""),
            accelerator_count=snapshot.get("acceleratorCount", 0),
            base_model_weight_precision=snapshot.get("baseModelWeightPrecision", ""),
            pipeline_parallelism=pp,
        )

    # -- Low-level REST calls --------------------------------------------------

    def _create(self, config: TrainerJobConfig) -> dict:
        path = f"/v1/accounts/{self.account_id}/rlorTrainerJobs"
        query_params: list[tuple[str, str]] = []
        if config.hot_load_deployment_id:
            query_params.append(("deploymentId", config.hot_load_deployment_id))
        if config.skip_validations:
            query_params.append(("skipValidations", "true"))
        if config.training_shape_ref:
            query_params.append(("trainingShape", config.training_shape_ref))
        if query_params:
            path = f"{path}?{urlencode(query_params)}"

        is_validated_shape = bool(config.training_shape_ref) and not config.skip_validations

        training_config: dict[str, Any] = {
            "baseModel": config.base_model,
            "loraRank": config.lora_rank,
            "learningRate": config.learning_rate,
            "gradientAccumulationSteps": config.gradient_accumulation_steps,
        }
        if not is_validated_shape and config.max_context_length is not None:
            training_config["maxContextLength"] = config.max_context_length

        payload: dict[str, Any] = {
            "serviceMode": True,
            "keepAlive": False,
            "dataset": "",
            "trainingConfig": training_config,
        }
        if not is_validated_shape:
            payload["nodeCount"] = config.node_count if config.node_count is not None else 1
        if config.display_name:
            payload["displayName"] = config.display_name
        if config.hot_load_deployment_id:
            payload["hotLoadDeploymentId"] = config.hot_load_deployment_id
        if config.region:
            payload["trainingConfig"]["region"] = config.region
        if not is_validated_shape and config.custom_image_tag:
            payload["trainingConfig"]["customImageTag"] = config.custom_image_tag
        if config.extra_args:
            flat = []
            for arg in config.extra_args:
                flat.extend(arg.split()) if " " in arg else flat.append(arg)
            payload["trainingConfig"]["extraArgs"] = flat
        if not is_validated_shape and config.accelerator_type:
            payload["trainingConfig"]["acceleratorType"] = config.accelerator_type
        if not is_validated_shape and config.accelerator_count:
            payload["trainingConfig"]["acceleratorCount"] = config.accelerator_count
        if config.forward_only:
            payload["forwardOnly"] = True

        logger.info("Creating RLOR job: POST %s (model=%s)", f"{self.base_url}{path}", config.base_model)
        resp = self._post(path, json=payload, timeout=60)
        if not resp.ok:
            error_msg = parse_api_error(resp)
            hint = HTTP_STATUS_HINTS.get(resp.status_code, "")
            extra = ""
            if resp.status_code == 400:
                extra = (
                    "\n  Verify the request parameters are correct."
                    "\n  If using hotload, ensure the deployment has hotLoadBucketUrl configured."
                    "\n  Use --skip-validations to bypass server-side validation."
                )
            logger.warning(
                "\n%s",
                format_sdk_error(
                    f"RLOR job creation failed (HTTP {resp.status_code})",
                    error_msg,
                    f"{hint}{extra}",
                    docs_url=DOCS_SDK,
                ),
            )
        resp.raise_for_status()
        return resp.json()

    def get(self, job_id: str) -> dict:
        """Get the current state of an RLOR job. Returns raw API response dict."""
        path = f"/v1/accounts/{self.account_id}/rlorTrainerJobs/{job_id}"
        resp = self._get(path, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def _delete_job(self, job_id: str) -> None:
        path = f"/v1/accounts/{self.account_id}/rlorTrainerJobs/{job_id}"
        resp = self._delete(path, timeout=30)
        resp.raise_for_status()

    def _resume(self, job_id: str) -> dict:
        path = f"/v1/accounts/{self.account_id}/rlorTrainerJobs/{job_id}:resume"
        resp = self._post(path, timeout=60)
        if not resp.ok:
            error_msg = parse_api_error(resp)
            hint = HTTP_STATUS_HINTS.get(resp.status_code, "")
            logger.warning(
                "\n%s",
                format_sdk_error(
                    f"RLOR job resume failed (HTTP {resp.status_code})",
                    error_msg,
                    f"{hint}\n  Check job status in the Fireworks console: {CONSOLE_URL}",
                    docs_url=DOCS_SDK,
                ),
            )
        resp.raise_for_status()
        return resp.json()

    # -- High-level operations -------------------------------------------------

    def _get_trainer_gateway_url(self, job_id: str) -> str:
        """Build the gateway proxy URL for a trainer job.

        The API gateway routes requests matching
        ``/training/v1/rlorTrainerJobs/{accountId}/{jobId}/*`` to the
        trainer pod via DynamoDB route lookup and the ``FIREWORKS-TRAINER``
        header.  The gateway strips the prefix so the trainer receives
        the original path (e.g. ``/api/v1/healthz``).

        This replaces the previous ``directRouteHandle`` approach, which
        resolved to a GCP-specific hostname and did not work for non-GCP
        clusters (e.g. OCI).
        """
        return f"{self.base_url}/training/v1/rlorTrainerJobs/{self.account_id}/{job_id}"

    def _check_healthz(self, base_url: str, timeout: float = 5) -> bool:
        """Probe /api/v1/healthz -- returns True only on HTTP 200."""
        try:
            r = self._session.get(
                f"{base_url}/api/v1/healthz",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=timeout,
                verify=False,
            )
            return r.status_code == 200
        except Exception:
            return False

    def _poll_until_ready(
        self,
        job_id: str,
        job_name: str,
        poll_interval_s: float = 5.0,
        timeout_s: float = 15 * 60,
    ) -> TrainerServiceEndpoint:
        start = time.time()
        service_ready = False
        base_url = self._get_trainer_gateway_url(job_id)

        while time.time() - start < timeout_s:
            job = self.get(job_id)
            state = job.get("state", "")
            elapsed = int(time.time() - start)

            if state == "JOB_STATE_FAILED":
                msg = job.get("status", {}).get("message", "unknown")
                raise RuntimeError(
                    format_sdk_error(
                        f"Trainer job {job_id} failed",
                        msg,
                        "Check the job logs in the Fireworks console for details.\n"
                        f"  Console: {CONSOLE_URL}\n"
                        "  Common causes: invalid model name, insufficient quota, or region unavailable.",
                        docs_url=DOCS_SDK,
                        show_support=True,
                    )
                )

            if state == "JOB_STATE_RUNNING":
                service_ready = self._check_healthz(base_url)

            if service_ready:
                self.boot_time_s = time.time() - start
                logger.info(
                    "[%ds] Trainer job %s: state=%s, healthz=OK -- service ready",
                    elapsed,
                    job_id,
                    state,
                )
                return TrainerServiceEndpoint(job_name=job_name, job_id=job_id, base_url=base_url)

            if state == "JOB_STATE_RUNNING":
                logger.info(
                    "[%ds] Trainer job %s: state=%s, healthz=waiting",
                    elapsed,
                    job_id,
                    state,
                )
            else:
                logger.info(
                    "[%ds] Trainer job %s: state=%s",
                    elapsed,
                    job_id,
                    state,
                )

            time.sleep(poll_interval_s)

        raise TimeoutError(
            format_sdk_error(
                f"Trainer job {job_id} did not become ready within {timeout_s}s",
                "The job is still provisioning or waiting for GPU resources.",
                f"Increase timeout with --rlor-timeout-s (current: {timeout_s}s).\n  Check job status: {CONSOLE_URL}",
                docs_url=DOCS_SDK,
            )
        )

    def create_and_wait(
        self,
        config: TrainerJobConfig,
        poll_interval_s: float = 5.0,
        timeout_s: float = 15 * 60,
    ) -> TrainerServiceEndpoint:
        """Create a service-mode trainer job and wait for it to be ready."""
        job = self._create(config)
        job_name = job.get("name", "")
        job_id = job_name.split("/")[-1] if "/" in job_name else job_name
        logger.info("Created trainer job: %s", job_id)
        return self._poll_until_ready(job_id, job_name, poll_interval_s, timeout_s)

    def wait_for_existing(
        self,
        job_id: str,
        poll_interval_s: float = 5.0,
        timeout_s: float = 15 * 60,
    ) -> TrainerServiceEndpoint:
        """Wait for an already-existing trainer job to reach RUNNING state."""
        job_name = f"accounts/{self.account_id}/rlorTrainerJobs/{job_id}"
        return self._poll_until_ready(job_id, job_name, poll_interval_s, timeout_s)

    def resume_and_wait(
        self,
        job_id: str,
        poll_interval_s: float = 5.0,
        timeout_s: float = 15 * 60,
    ) -> TrainerServiceEndpoint:
        """Resume a failed/cancelled/paused trainer job and wait for it to be ready."""
        self._resume(job_id)
        logger.info("Resumed trainer job: %s", job_id)
        return self.wait_for_existing(job_id, poll_interval_s, timeout_s)

    def reconnect_and_wait(
        self,
        job_id: str,
        poll_interval_s: float = 5.0,
        timeout_s: float = 600.0,
        max_wait_for_resumable_s: float = 120.0,
    ) -> TrainerServiceEndpoint:
        """Reconnect to a preempted/failed trainer job.

        Handles pod preemption: waits for the job to reach a resumable state
        (tolerates transitional states like CREATING/DELETING), resumes it,
        then polls until RUNNING with a healthy endpoint.

        This is more robust than ``resume_if_needed_and_wait()`` because it
        retries when the job is in a transitional state (e.g. the control plane
        is still processing the pod death) instead of failing immediately.

        Args:
            job_id: The RLOR job ID to reconnect.
            poll_interval_s: Seconds between health checks after resume.
            timeout_s: Overall timeout for the job to become RUNNING.
            max_wait_for_resumable_s: Max seconds to wait for the job to
                reach a resumable state (FAILED/CANCELLED/PAUSED/COMPLETED).
        """
        start = time.time()
        while True:
            try:
                job = self.get(job_id)
            except Exception as e:
                if time.time() - start > max_wait_for_resumable_s:
                    raise
                logger.warning(
                    "Failed to query job %s (retrying): %s. This is usually transient during pod rescheduling.",
                    job_id,
                    e,
                )
                time.sleep(5)
                continue

            state = job.get("state", "")
            logger.info("Reconnect: job %s state=%s", job_id, state)

            if state == "JOB_STATE_RUNNING":
                # Already running (maybe it recovered on its own)
                return self.wait_for_existing(job_id, poll_interval_s, timeout_s)

            resumable = (
                "JOB_STATE_FAILED",
                "JOB_STATE_CANCELLED",
                "JOB_STATE_PAUSED",
                "JOB_STATE_COMPLETED",
            )
            if state in resumable:
                logger.info("Reconnect: resuming job %s from %s...", job_id, state)
                return self.resume_and_wait(job_id, poll_interval_s, timeout_s)

            # Job might be in a transitional state (CREATING, DELETING, etc.)
            if time.time() - start > max_wait_for_resumable_s:
                raise RuntimeError(
                    format_sdk_error(
                        f"Trainer job {job_id} stuck in {state}",
                        f"Job has been in '{state}' state for {max_wait_for_resumable_s}s "
                        "without transitioning to a resumable state.",
                        "1. Check the Fireworks console for job details\n"
                        "  2. Try cancelling the job and creating a new one\n"
                        f"  Console: {CONSOLE_URL}",
                        docs_url=DOCS_SDK,
                        show_support=True,
                    )
                )
            logger.info(
                "Reconnect: job %s in %s, waiting for resumable state...",
                job_id,
                state,
            )
            time.sleep(10)

    def delete(self, job_id: str) -> None:
        """Delete a trainer job."""
        try:
            self._delete_job(job_id)
            logger.info("Deleted trainer job: %s", job_id)
        except Exception as e:
            logger.warning(
                "Failed to delete trainer job %s: %s. You can delete it manually in the Fireworks console: %s",
                job_id,
                e,
                CONSOLE_URL,
            )
