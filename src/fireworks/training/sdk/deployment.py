"""Fireworks Deployment, Hotload & Sampling.

Manages inference deployment lifecycle, hotload operations for weight syncing,
and provides a thin wrapper for deployment completions API with client-side
tokenization (token-in, token-out).
"""

from __future__ import annotations

import time
import asyncio
import logging
from typing import TYPE_CHECKING, Any, List
from dataclasses import dataclass

if TYPE_CHECKING:
    from transformers import PreTrainedTokenizerBase

from fireworks.training.sdk.errors import (
    DOCS_SDK,
    CONSOLE_URL,
    DISCORD_URL,
    HTTP_STATUS_HINTS,
    parse_api_error,
    format_sdk_error,
    async_request_with_retries,
)
from fireworks.training.sdk._rest_client import _RestClient, _should_verify_ssl

logger = logging.getLogger(__name__)


# =============================================================================
# SSE decoder for streaming completions
# =============================================================================


class _SSEEvent:
    """A single Server-Sent Event."""

    __slots__ = ("data", "event")

    def __init__(self, data: str = "", event: str | None = None):
        self.data = data
        self.event = event


class _SSEDecoder:
    """Minimal async SSE decoder for ``httpx.Response.aiter_bytes``.

    Implements the subset of the `SSE spec`_ used by the Fireworks
    completions endpoint:

    * ``data:`` fields (single- and multi-line)
    * ``event:`` fields
    * Comment lines (``:…``) are skipped
    * ``[DONE]`` sentinel terminates the stream

    .. _SSE spec: https://html.spec.whatwg.org/multipage/server-sent-events.html
    """

    def __init__(self) -> None:
        self._event: str | None = None
        self._data: list[str] = []

    @staticmethod
    async def _aiter_chunks(stream: Any) -> Any:
        """Reassemble raw bytes into SSE chunks (delimited by blank lines)."""
        buf = b""
        async for raw in stream.aiter_bytes():
            for line in raw.splitlines(keepends=True):
                buf += line
                if buf.endswith((b"\r\r", b"\n\n", b"\r\n\r\n")):
                    yield buf
                    buf = b""
        if buf:
            yield buf

    async def aiter_events(self, response: Any) -> Any:
        """Yield :class:`_SSEEvent` objects from an ``httpx.Response``."""
        async for chunk in self._aiter_chunks(response):
            for raw_line in chunk.splitlines():
                line = raw_line.decode("utf-8")
                event = self._decode_line(line)
                if event is not None:
                    yield event

    def _decode_line(self, line: str) -> _SSEEvent | None:
        # Blank line → dispatch accumulated event.
        if not line:
            if not self._data and self._event is None:
                return None
            event = _SSEEvent(data="\n".join(self._data), event=self._event)
            self._data = []
            self._event = None
            return event

        # Comment line.
        if line.startswith(":"):
            return None

        field, _, value = line.partition(":")
        if value.startswith(" "):
            value = value[1:]

        if field == "data":
            self._data.append(value)
        elif field == "event":
            self._event = value

        return None


DEFAULT_DELTA_COMPRESSION = "arc_v2"
DEFAULT_CHECKSUM_FORMAT = "alder32"


@dataclass
class DeploymentInfo:
    """Metadata about a Fireworks deployment."""

    deployment_id: str
    name: str
    state: str
    hot_load_bucket_url: str | None = None
    inference_model: str | None = None
    """Model string for completions API (``accounts/{account}/deployments/{id}``)."""


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
    skip_shape_validation: bool = False
    disable_speculative_decoding: bool = False
    extra_args: list[str] | None = None
    extra_values: dict[str, str] | None = None


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
        self.boot_time_s: float | None = None
        """Wall-clock seconds spent in the most recent ``wait_for_ready`` call."""

    def _hotload_headers(self, deployment_id: str, base_model: str) -> dict[str, str]:
        """Construct headers for hotload API requests."""
        return self._headers(
            Authorization=f"Bearer {self.api_key}",
            **{
                "fireworks-model": base_model,
                "fireworks-deployment": f"accounts/{self.account_id}/deployments/{deployment_id}",
            },
        )

    # -- Deployment CRUD -------------------------------------------------------

    def _get_deployment(self, deployment_id: str) -> dict | None:
        path = f"/v1/accounts/{self.account_id}/deployments/{deployment_id}"
        resp = self._get(path)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()

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

        body: dict[str, Any] = {
            "baseModel": config.base_model,
            "minReplicaCount": config.min_replica_count,
            "maxReplicaCount": config.max_replica_count,
            "enableHotLoad": True,
        }
        if config.region:
            body["placement"] = {"region": config.region}
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
                flat.extend(arg.split()) if " " in arg else flat.append(arg)
            body["extraArgs"] = flat
        if config.extra_values:
            body["extraValues"] = config.extra_values

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
                    "\n  Check region, deployment shape, and model name are valid."
                    "\n  Try --skip-shape-validation if the shape version is unsupported."
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

    def _parse_deployment_info(self, deployment_id: str, data: dict) -> DeploymentInfo:
        return DeploymentInfo(
            deployment_id=deployment_id,
            name=data.get("name", ""),
            state=data.get("state", "UNKNOWN"),
            hot_load_bucket_url=data.get("hotLoadBucketUrl"),
            inference_model=f"accounts/{self.account_id}/deployments/{deployment_id}",
        )

    def _wait_for_deletion(
        self,
        deployment_id: str,
        timeout_s: float = 60,
        poll_interval_s: float = 2,
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
        timeout_s: float = 600,
        poll_interval_s: float = 15,
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
                        "The deployment does not exist or was deleted.",
                        "Verify the deployment ID is correct, or use --create-deployment to create a new one.",
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
                        "The deployment failed to start or was deleted externally.",
                        f"1. Check deployment logs in the Fireworks console: {CONSOLE_URL}\n"
                        "  2. Try recreating with --create-deployment\n"
                        "  3. Verify your model name and region are valid",
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
                "The deployment is still provisioning or waiting for GPU resources.",
                f"Increase timeout with --deployment-timeout-s (current: {timeout_s}s).\n"
                f"  Check deployment status in the Fireworks console: {CONSOLE_URL}",
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

    # -- Hotload operations ----------------------------------------------------

    def hotload(
        self,
        deployment_id: str,
        base_model: str,
        snapshot_identity: str,
        incremental_snapshot_metadata: dict[str, Any] | None = None,
        reset_prompt_cache: bool = True,
        timeout: int = 60,
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
        """
        headers = self._hotload_headers(deployment_id, base_model)
        url = f"{self.hotload_api_url}/hot_load/v1/models/hot_load"

        payload: dict[str, Any] = {"identity": snapshot_identity, "reset_prompt_cache": reset_prompt_cache}
        if incremental_snapshot_metadata:
            payload["incremental_snapshot_metadata"] = incremental_snapshot_metadata

        ckpt_type = "DELTA" if incremental_snapshot_metadata else "FULL"
        logger.info(
            "Hotloading %s snapshot '%s' to deployment '%s'",
            ckpt_type,
            snapshot_identity,
            deployment_id,
        )

        resp = self._sync_request(
            url,
            method="POST",
            headers=headers,
            json=payload,
            timeout=timeout,
        )
        if not resp.is_success:
            error_msg = parse_api_error(resp)
            hint = HTTP_STATUS_HINTS.get(resp.status_code, "")
            logger.warning(
                "\n%s",
                format_sdk_error(
                    f"Hotload API error (HTTP {resp.status_code})",
                    error_msg,
                    f"{hint}\n"
                    "  1. Verify the deployment has hotLoadBucketUrl configured\n"
                    "  2. Ensure the base model matches between trainer and deployment\n"
                    "  3. Check that the snapshot identity exists",
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
        timeout_seconds: int = 400,
        poll_interval: int = 5,
    ) -> bool:
        """Wait for hotload to complete. Returns True on success."""
        logger.info("Waiting for hotload (identity=%s)...", expected_identity)
        start = time.time()

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
                            f"This may indicate an API version mismatch. Reach out on Discord for help: {DISCORD_URL}",
                            docs_url=DOCS_SDK,
                            show_support=True,
                        )
                    )
                if replicas:
                    replica = replicas[0]
                    current_identity = replica.get("current_snapshot_identity")
                    stage = replica.get("loading_state", {}).get("stage", "unknown")
                    readiness = replica.get("readiness", False)
                else:
                    current_identity = None
                    stage = "pending"
                    readiness = False

                elapsed = int(time.time() - start)

                if readiness and current_identity == expected_identity:
                    logger.info("Hotload complete: %s (took %ds)", expected_identity, elapsed)
                    return True
                elif stage == "error":
                    logger.warning(
                        "\n%s",
                        format_sdk_error(
                            f"Hotload failed for snapshot '{expected_identity}'",
                            "The deployment reported an error loading the weight snapshot.",
                            "1. Check that hotLoadBucketUrl is configured on the deployment\n"
                            "  2. Verify the snapshot was saved successfully by the trainer\n"
                            "  3. Ensure the base model matches between trainer and deployment",
                            docs_url=DOCS_SDK,
                            show_support=True,
                        ),
                    )
                    return False
                else:
                    logger.info(
                        "Hotload: stage=%s, current=%s, loading=%s, ready=%s (%ds)",
                        stage,
                        current_identity,
                        expected_identity,
                        readiness,
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
            format_sdk_error(
                f"Hotload did not complete within {timeout_seconds}s",
                "The deployment is still loading the snapshot or may be unhealthy.",
                f"1. Increase timeout with --hotload-timeout (current: {timeout_seconds}s)\n"
                f"  2. Check deployment health in the Fireworks console: {CONSOLE_URL}\n"
                "  3. Verify the snapshot identity is correct",
                docs_url=DOCS_SDK,
            ),
        )
        return False

    def hotload_and_wait(
        self,
        deployment_id: str,
        base_model: str,
        snapshot_identity: str,
        incremental_snapshot_metadata: dict[str, Any] | None = None,
        reset_prompt_cache: bool = True,
        timeout_seconds: int = 400,
    ) -> bool:
        """Hotload a snapshot and wait for it to complete. Returns True on success."""
        self.hotload(
            deployment_id=deployment_id,
            base_model=base_model,
            snapshot_identity=snapshot_identity,
            incremental_snapshot_metadata=incremental_snapshot_metadata,
            reset_prompt_cache=reset_prompt_cache,
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
                timeout=10,
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
                    timeout=30,
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
                "The deployment is not responding to inference requests.",
                f"1. Check the deployment state in the Fireworks console: {CONSOLE_URL}\n"
                "  2. Verify the inference URL and model name are correct\n"
                "  3. The deployment may be scaling up — try increasing retry count",
                docs_url=DOCS_SDK,
            ),
        )
        return False


# =============================================================================
# DeploymentSampler — completions API with client-side tokenization
# =============================================================================


@dataclass
class ServerMetrics:
    """Server-side metrics extracted from response headers.

    Available on dedicated deployments.  Fields are ``None`` when the
    header is absent (e.g. serverless deployments).
    """

    num_concurrent_requests: int | None = None
    prefill_queue_duration: float | None = None
    generation_queue_duration: float | None = None
    server_ttft: float | None = None
    cached_prompt_tokens: int | None = None
    prompt_tokens: int | None = None
    server_processing_time: float | None = None
    client_ttft: float | None = None
    """Client-measured time-to-first-token (seconds).  Only set for streaming."""

    @staticmethod
    def from_headers(headers: dict[str, str], client_ttft: float | None = None) -> "ServerMetrics":
        """Parse server metrics from HTTP response headers."""

        def _float(key: str) -> float | None:
            v = headers.get(key)
            if v is None:
                return None
            try:
                return float(v)
            except (ValueError, TypeError):
                return None

        def _int(key: str) -> int | None:
            v = headers.get(key)
            if v is None:
                return None
            try:
                return int(v)
            except (ValueError, TypeError):
                return None

        return ServerMetrics(
            num_concurrent_requests=_int("num-concurrent-requests"),
            prefill_queue_duration=_float("prefill-queue-duration"),
            generation_queue_duration=_float("generation-queue-duration"),
            server_ttft=_float("server-time-to-first-token"),
            cached_prompt_tokens=_int("cached-prompt-tokens"),
            prompt_tokens=_int("prompt-tokens"),
            server_processing_time=_float("server-processing-time"),
            client_ttft=client_ttft,
        )


@dataclass
class SampledCompletion:
    """A single sampled completion with tokenized representation.

    Contains the full token sequence (prompt + completion) needed for training,
    with prompt tokens from client-side tokenization and completion tokens from
    the deployment's ``raw_output`` response.
    """

    text: str
    full_tokens: List[int]  # prompt_token_ids + completion_token_ids
    prompt_len: int
    finish_reason: str = "unknown"
    completion_len: int = 0
    inference_logprobs: List[float] | None = None
    logprobs_echoed: bool = False
    """True when echo=True was used: inference_logprobs has P+C-1 entries
    (training-aligned).  False: completion-only."""
    routing_matrices: List[str] | None = None


class DeploymentSampler(_RestClient):
    """Wraps Fireworks deployment completions API with client-side tokenization.

    Uses a local HuggingFace tokenizer to apply chat templates and tokenize
    prompts, then sends token IDs to the ``/inference/v1/completions`` endpoint
    (token-in, token-out).  Completion token IDs come back via ``raw_output``.

    BOS and special tokens are handled by the tokenizer's chat template --
    no manual prepend is needed.

    Handles URL construction, auth headers, SSL verification, and basic
    retries -- so training scripts never do raw HTTP for sampling.

    Example::

        from transformers import AutoTokenizer

        tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-1.7B")
        sampler = DeploymentSampler(
            inference_url="https://api.fireworks.ai",
            model="accounts/your-account/deployments/my-deploy",
            api_key="...",
            tokenizer=tokenizer,
        )

        completions = await sampler.sample_with_tokens(messages=[...], n=4)
        for c in completions:
            print(c.text, len(c.full_tokens), c.finish_reason)
    """

    def __init__(
        self,
        inference_url: str,
        model: str,
        api_key: str,
        tokenizer: PreTrainedTokenizerBase | None = None,
        concurrency_controller: "AdaptiveConcurrencyController | FixedConcurrencyController | None" = None,
        max_concurrency: int | None = None,  # TODO: remove after deprecation period
    ):
        super().__init__(api_key=api_key, base_url=inference_url)
        self.model = model
        self.tokenizer = tokenizer
        self._recent_metrics: list[ServerMetrics] = []

        if max_concurrency is not None:
            import warnings
            warnings.warn(
                "max_concurrency is deprecated and will be removed in a future release. "
                "Use concurrency_controller=FixedConcurrencyController(max_concurrency) "
                "or AdaptiveConcurrencyController() instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            if concurrency_controller is None:
                concurrency_controller = FixedConcurrencyController(max_concurrency)

        self._concurrency_controller = concurrency_controller

    def _inference_headers(self) -> dict[str, str]:
        """Headers for inference completions requests."""
        return self._headers(Authorization=f"Bearer {self.api_key}")

    _HOTLOAD_RETRY_INTERVAL_S = 5.0
    _HOTLOAD_MAX_RETRIES = 10

    async def async_completions_stream(
        self,
        prompt: list[int],
        max_tokens: int = 1024,
        temperature: float = 1.0,
        hotload_retry_interval: float = _HOTLOAD_RETRY_INTERVAL_S,
        hotload_max_retries: int = _HOTLOAD_MAX_RETRIES,
        **kwargs: Any,
    ) -> tuple[dict[str, Any], ServerMetrics]:
        """Streaming n=1 async completions request.

        Opens an SSE stream, accumulates chunks into the same response
        format that ``async_completions`` returns, and extracts
        ``ServerMetrics`` from both:

        * **HTTP response headers** -- available immediately (partial:
          ``prompt-tokens``, ``cached-prompt-tokens``, ``server-time-to-first-token``).
        * **``perf_metrics`` in the final SSE chunk** -- available after
          completion (full timing: ``prefill-queue-duration``,
          ``generation-queue-duration``, ``num-concurrent-requests``, etc.).

        The request automatically sets ``perf_metrics_in_response=True``
        so the server includes complete metrics in the last chunk.
        """
        import json as _json

        http_timeout = kwargs.pop("http_timeout", 600)
        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "n": 1,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True,
            "perf_metrics_in_response": True,
            **kwargs,
        }
        url = f"{self.base_url}/inference/v1/completions"
        headers = self._inference_headers()
        client = self._get_async_client()
        prompt_len = len(prompt)

        for hotload_attempt in range(hotload_max_retries + 1):
            t0 = time.time()
            resp = await async_request_with_retries(
                client.post,
                url,
                headers=headers,
                json=payload,
                timeout=http_timeout,
            )

            if resp.status_code in (404, 425) and hotload_attempt < hotload_max_retries:
                logger.info(
                    "Deployment not ready (HTTP %d), retry %d/%d in %ds...",
                    resp.status_code,
                    hotload_attempt + 1,
                    hotload_max_retries,
                    int(hotload_retry_interval),
                )
                await asyncio.sleep(hotload_retry_interval)
                continue

            resp.raise_for_status()

            accumulated_text = ""
            accumulated_logprobs: list[dict] = []
            finish_reason = None
            usage_info = None
            raw_output = None
            perf_metrics_dict: dict[str, str] | None = None
            first_token_time: float | None = None

            decoder = _SSEDecoder()
            async for sse in decoder.aiter_events(resp):
                if sse.data.startswith("[DONE]"):
                    break

                try:
                    chunk = _json.loads(sse.data)
                except (ValueError, TypeError):
                    continue

                for choice in chunk.get("choices", []):
                    text_delta = choice.get("text", "")
                    if text_delta:
                        if first_token_time is None:
                            first_token_time = time.time()
                        accumulated_text += text_delta

                    lp = choice.get("logprobs")
                    if lp and isinstance(lp, dict):
                        content = lp.get("content")
                        if isinstance(content, list):
                            accumulated_logprobs.extend(content)

                    fr = choice.get("finish_reason")
                    if fr:
                        finish_reason = fr

                    ro = choice.get("raw_output")
                    if ro:
                        raw_output = ro

                if "usage" in chunk:
                    usage_info = chunk["usage"]

                # perf_metrics is patched into the final chunk by the server
                # (with is_completed=True, so it has full timing data).
                if "perf_metrics" in chunk:
                    perf_metrics_dict = chunk["perf_metrics"]

            client_ttft = (first_token_time - t0) if first_token_time else None

            # Build ServerMetrics: prefer perf_metrics from final chunk
            # (has complete timing), fall back to HTTP headers (partial).
            metrics_source = perf_metrics_dict or dict(resp.headers)
            server_metrics = ServerMetrics.from_headers(metrics_source, client_ttft=client_ttft)

            assembled_choice: dict[str, Any] = {
                "text": accumulated_text,
                "finish_reason": finish_reason or "stop",
            }
            if accumulated_logprobs:
                assembled_choice["logprobs"] = {"content": accumulated_logprobs}
            if raw_output:
                assembled_choice["raw_output"] = raw_output
            result: dict[str, Any] = {"choices": [assembled_choice]}
            if usage_info:
                result["usage"] = usage_info

            elapsed = time.time() - t0
            logger.debug(
                "Stream completions: prompt=%d, text_len=%d, %.1fs",
                prompt_len,
                len(accumulated_text),
                elapsed,
            )
            return result, server_metrics

        raise RuntimeError("Exhausted hotload retries in streaming mode")

    @staticmethod
    def _extract_logprobs(choice: dict[str, Any]) -> List[float] | None:
        """Extract per-token logprobs from a completions response.

        Expects modern structured logprobs format:
        ``choice.logprobs.content[].logprob``.

        Returns:
            List of per-token logprobs, or ``None`` if absent/empty.
        """
        lp_data = choice.get("logprobs")
        if not lp_data or not isinstance(lp_data, dict):
            return None
        content = lp_data.get("content")
        if isinstance(content, list) and content:
            return [tok.get("logprob", 0.0) for tok in content]
        return None

    @staticmethod
    def _extract_routing_matrices(choice: dict[str, Any]) -> List[str] | None:
        """Extract per-token routing matrices from logprobs content.

        When ``include_routing_matrix=True`` is passed to the API, each token
        in ``choice.logprobs.content`` may contain a ``routing_matrix`` field
        with a base64-encoded expert-index array for Router Replay (R3).

        Returns:
            List of base64-encoded routing matrix strings (one per completion
            token), or ``None`` if no routing matrices are present.
        """
        lp_data = choice.get("logprobs")
        if lp_data and isinstance(lp_data, dict):
            content = lp_data.get("content", [])
            if content:
                matrices = [tok.get("routing_matrix", "") for tok in content]
                if any(m for m in matrices):
                    return matrices
        return None

    async def sample_with_tokens(
        self,
        messages: list[dict[str, str]],
        n: int = 1,
        max_tokens: int = 1024,
        temperature: float = 1.0,
        max_seq_len: int | None = None,
        **kwargs: Any,
    ) -> List[SampledCompletion]:
        """Sample n completions via streaming, firing n individual requests concurrently.

        Each completion is an independent async streaming request.
        Server metrics from response headers are fed into the
        ``AdaptiveConcurrencyController`` (if one was provided).
        """
        if self.tokenizer is None:
            raise ValueError("Tokenizer is required for sample_with_tokens")
        user_requested_logprobs = kwargs.get("logprobs", False)
        routing_requested = kwargs.get("include_routing_matrix", False)
        echo_mode = kwargs.get("echo", False)

        prompt_ids: list[int] = self.tokenizer.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_dict=False,
        )

        if max_seq_len is not None and len(prompt_ids) >= max_seq_len:
            return []

        async def _one(idx: int) -> List[SampledCompletion]:
            return await self._do_one_completion(
                prompt_ids,
                max_tokens,
                temperature,
                max_seq_len,
                user_requested_logprobs,
                routing_requested,
                echo_mode,
                **kwargs,
            )

        results = await asyncio.gather(*[_one(i) for i in range(n)])
        return [c for batch in results for c in batch]

    async def _acquire_concurrency(self) -> None:
        """Acquire a concurrency slot from the controller."""
        if self._concurrency_controller is not None:
            await self._concurrency_controller.acquire()

    def _release_concurrency(self, server_metrics: ServerMetrics | None = None) -> None:
        """Release a concurrency slot, feeding metrics to the controller."""
        if server_metrics is not None:
            self._recent_metrics.append(server_metrics)
        if self._concurrency_controller is not None:
            self._concurrency_controller.release(server_metrics)

    def drain_metrics(self) -> list[ServerMetrics]:
        """Return and clear all collected ServerMetrics since last drain."""
        out = list(self._recent_metrics)
        self._recent_metrics.clear()
        return out

    async def _do_one_completion(
        self,
        prompt_ids: list[int],
        max_tokens: int,
        temperature: float,
        max_seq_len: int | None,
        user_requested_logprobs: bool,
        routing_requested: bool,
        echo_mode: bool,
        **kwargs: Any,
    ) -> List[SampledCompletion]:
        await self._acquire_concurrency()
        server_metrics: ServerMetrics | None = None
        try:
            result, server_metrics = await self.async_completions_stream(
                prompt=prompt_ids,
                max_tokens=max_tokens,
                temperature=temperature,
                raw_output=True,
                **kwargs,
            )
        finally:
            self._release_concurrency(server_metrics)
        return self._parse_completions_result(
            result,
            prompt_ids,
            max_seq_len,
            user_requested_logprobs,
            routing_requested,
            echo_mode,
        )

    def _parse_completions_result(
        self,
        result: dict[str, Any],
        prompt_ids: list[int],
        max_seq_len: int | None,
        user_requested_logprobs: bool,
        routing_requested: bool,
        echo_mode: bool,
    ) -> List[SampledCompletion]:
        """Parse a completions API response into SampledCompletion objects."""
        completions: List[SampledCompletion] = []
        for choice in result.get("choices", []):
            text = choice.get("text", "")
            finish_reason = choice.get("finish_reason", "unknown")
            raw = choice.get("raw_output") or {}
            completion_ids = raw.get("completion_token_ids")

            if completion_ids is None:
                raise RuntimeError(
                    format_sdk_error(
                        "Deployment did not return raw_output token IDs",
                        f"The API response is missing completion_token_ids. Got choice keys: {list(choice.keys())}",
                        "Ensure the deployment supports raw_output=True.\n"
                        "  This requires a deployment running a compatible model version.\n"
                        "  Check that the deployment base model matches your training model.",
                        docs_url=DOCS_SDK,
                        show_support=True,
                    )
                )

            token_logprobs = self._extract_logprobs(choice) if user_requested_logprobs else None
            routing_matrices = self._extract_routing_matrices(choice) if routing_requested else None

            # With echo=True the API returns P+C tokens in
            # completion_token_ids and logprobs cover all P+C positions.
            # Strip the prompt prefix (verified by actual content match)
            # and drop the unconditional first-token logprob to get
            # P+C-1 training-aligned entries.
            lp_is_echo = False
            if echo_mode:
                if len(completion_ids) < len(prompt_ids) or completion_ids[: len(prompt_ids)] != list(prompt_ids):
                    raise RuntimeError(
                        format_sdk_error(
                            "Echo response format mismatch",
                            "echo=True was requested but completion_token_ids do not include the prompt prefix.",
                            "Ensure the deployment supports token echo with raw_output=True.",
                            docs_url=DOCS_SDK,
                            show_support=True,
                        )
                    )

                completion_ids = completion_ids[len(prompt_ids) :]
                if token_logprobs is not None:
                    token_logprobs = token_logprobs[1:]
                    lp_is_echo = True
                if routing_matrices is not None:
                    routing_matrices = routing_matrices[1:]

            full_tokens = list(prompt_ids) + list(completion_ids)
            if max_seq_len is not None and len(full_tokens) > max_seq_len:
                logger.debug(
                    "Completion post-filtered: %d tokens > max_seq_len %d",
                    len(full_tokens),
                    max_seq_len,
                )
                continue

            completions.append(
                SampledCompletion(
                    text=text,
                    full_tokens=full_tokens,
                    prompt_len=len(prompt_ids),
                    finish_reason=finish_reason,
                    completion_len=len(completion_ids),
                    inference_logprobs=token_logprobs,
                    logprobs_echoed=lp_is_echo,
                    routing_matrices=routing_matrices,
                )
            )

        return completions


# =============================================================================
# FixedConcurrencyController — static semaphore
# =============================================================================


class FixedConcurrencyController:
    """Fixed concurrency controller backed by an asyncio.Semaphore.

    Same interface as ``AdaptiveConcurrencyController`` so ``DeploymentSampler``
    can use either interchangeably.
    """

    def __init__(self, max_concurrency: int):
        self._max_concurrency = max_concurrency
        self._semaphore = asyncio.Semaphore(max_concurrency)

    @property
    def window_size(self) -> int:
        return self._max_concurrency

    async def acquire(self) -> None:
        await self._semaphore.acquire()

    def release(self, metrics: "ServerMetrics | None" = None) -> None:
        self._semaphore.release()

    def step_completed(self) -> dict[str, float]:
        return {"window": float(self._max_concurrency)}


# =============================================================================
# AdaptiveConcurrencyController — AIMD-based dynamic concurrency
# =============================================================================


class AdaptiveConcurrencyController:
    """AIMD concurrency controller with proportional increase.

    Uses ``prefill_queue_duration`` from server response headers as the
    congestion signal.  When the prefill queue is above the target, the
    window shrinks (multiplicative decrease).  When below, the window
    grows proportionally to the headroom (further below target = faster
    growth), capped at ``_MAX_INCREASE_FACTOR``.

    Compatible with ``DeploymentSampler`` -- pass as ``concurrency_controller``.
    """

    # -- Internal constants (not user-configurable) --
    _MAX_INCREASE_FACTOR = 4.0   # Cap proportional increase at 4x base rate.
    _MIN_PQ_FLOOR = 0.001        # Avoid division by zero in headroom calc.
    _DEFAULT_INITIAL_WINDOW = 16
    _DEFAULT_MIN_WINDOW = 1
    _DEFAULT_MAX_WINDOW = 256
    _DEFAULT_PQ_TARGET = 0.5     # Prefill queue target in seconds.
    _DEFAULT_ADDITIVE_INCREASE = 1.0
    _DEFAULT_MULTIPLICATIVE_DECREASE = 0.5
    _DEFAULT_EMA_ALPHA = 0.3

    def __init__(
        self,
        initial_window: int = _DEFAULT_INITIAL_WINDOW,
        min_window: int = _DEFAULT_MIN_WINDOW,
        max_window: int = _DEFAULT_MAX_WINDOW,
        prefill_queue_target: float = _DEFAULT_PQ_TARGET,
        additive_increase: float = _DEFAULT_ADDITIVE_INCREASE,
        multiplicative_decrease: float = _DEFAULT_MULTIPLICATIVE_DECREASE,
        ema_alpha: float = _DEFAULT_EMA_ALPHA,
    ):
        self._window: float = float(initial_window)
        self._min_window = min_window
        self._max_window = max_window
        self._prefill_queue_target = prefill_queue_target
        self._additive_increase = additive_increase
        self._multiplicative_decrease = multiplicative_decrease
        self._ema_alpha = ema_alpha

        self._ema_prefill_queue: float | None = None
        self._semaphore = asyncio.Semaphore(initial_window)

        self._completed_requests: int = 0
        self._last_logged_window: int = initial_window

        # Batch-level metrics: collected per-request, aggregated at step boundary.
        self._step_prefill_queues: list[float] = []
        self._step_metrics_count: int = 0
        self._step_cache_hits: int = 0
        self._step_cache_total: int = 0

    @property
    def window_size(self) -> int:
        return max(self._min_window, min(self._max_window, int(self._window)))

    @property
    def ema_prefill_queue(self) -> float | None:
        return self._ema_prefill_queue

    async def acquire(self) -> None:
        await self._semaphore.acquire()

    def release(self, metrics: ServerMetrics | None = None) -> None:
        """Release a slot and collect metrics.  Window is NOT adjusted here.

        Call :meth:`step_completed` between RL steps to trigger the AIMD
        adjustment based on the average prefill queue across the step.
        """
        self._semaphore.release()
        self._completed_requests += 1
        if metrics is None:
            return
        if metrics.prefill_queue_duration is not None:
            self._step_prefill_queues.append(metrics.prefill_queue_duration)
        self._step_metrics_count += 1
        if metrics.cached_prompt_tokens is not None:
            self._step_cache_hits += metrics.cached_prompt_tokens
        if metrics.prompt_tokens is not None:
            self._step_cache_total += metrics.prompt_tokens

    def step_completed(self) -> dict[str, float]:
        """Called between RL steps.  Adjusts window based on the step's
        average prefill queue duration and returns a summary dict for logging.

        Returns:
            Dict with step-level metrics (``avg_pq``, ``window``, ``cache_hit_rate``, etc.).
        """
        summary: dict[str, float] = {
            "window": float(self.window_size),
            "requests": float(self._step_metrics_count),
        }

        # Compute step-level average prefill queue.
        if self._step_prefill_queues:
            avg_pq = sum(self._step_prefill_queues) / len(self._step_prefill_queues)
            summary["avg_pq"] = avg_pq
            self._update_window(avg_pq)
            summary["window_after"] = float(self.window_size)

        if self._step_cache_total > 0:
            summary["cache_hit_rate"] = self._step_cache_hits / self._step_cache_total

        if self._ema_prefill_queue is not None:
            summary["ema_pq"] = self._ema_prefill_queue

        logger.info(
            "AdaptiveConcurrency step: window=%d, reqs=%d, avg_pq=%.3fs, ema_pq=%s, cache=%.1f%%",
            self.window_size,
            self._step_metrics_count,
            summary.get("avg_pq", 0.0),
            f"{self._ema_prefill_queue:.3f}" if self._ema_prefill_queue is not None else "N/A",
            summary.get("cache_hit_rate", 0.0) * 100,
        )

        # Reset per-step accumulators.
        self._step_prefill_queues.clear()
        self._step_metrics_count = 0
        self._step_cache_hits = 0
        self._step_cache_total = 0

        return summary

    def _update_window(self, avg_prefill_queue: float) -> None:
        """AIMD adjustment based on step-averaged prefill queue."""
        if self._ema_prefill_queue is None:
            self._ema_prefill_queue = avg_prefill_queue
        else:
            a = self._ema_alpha
            self._ema_prefill_queue = a * avg_prefill_queue + (1 - a) * self._ema_prefill_queue

        old_int_window = self.window_size

        if self._ema_prefill_queue > self._prefill_queue_target:
            self._window *= self._multiplicative_decrease
        else:
            # Proportional increase: grow faster when far below target.
            headroom = self._prefill_queue_target / max(self._ema_prefill_queue, self._MIN_PQ_FLOOR)
            increase = self._additive_increase * min(headroom, self._MAX_INCREASE_FACTOR)
            self._window += increase

        self._window = max(float(self._min_window), min(float(self._max_window), self._window))
        new_int_window = self.window_size

        if new_int_window != old_int_window:
            self._resize_semaphore(old_int_window, new_int_window)

    def _resize_semaphore(self, old_size: int, new_size: int) -> None:
        delta = new_size - old_size
        if delta > 0:
            for _ in range(delta):
                self._semaphore.release()
        elif delta < 0:
            for _ in range(-delta):
                if self._semaphore._value > 0:
                    self._semaphore._value -= 1
