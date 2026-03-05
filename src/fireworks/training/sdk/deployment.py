"""Fireworks Deployment, Hotload & Sampling.

Manages inference deployment lifecycle, hotload operations for weight syncing,
and provides a thin wrapper for deployment completions API with client-side
tokenization (token-in, token-out).
"""

from __future__ import annotations

import time
import logging
from typing import TYPE_CHECKING, Any, List
from dataclasses import dataclass

if TYPE_CHECKING:
    from transformers import PreTrainedTokenizerBase

import urllib3
import requests

from fireworks.training.sdk.errors import (
    DOCS_SDK,
    CONSOLE_URL,
    DISCORD_URL,
    HTTP_STATUS_HINTS,
    parse_api_error,
    format_sdk_error,
    request_with_retries,
)

# Suppress SSL warnings for dev/self-signed cert environments
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

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
    """Configuration for creating/managing a Fireworks deployment."""

    deployment_id: str
    base_model: str
    deployment_shape: str | None = None
    region: str = "US_OHIO_1"
    min_replica_count: int = 0
    max_replica_count: int = 1
    accelerator_type: str = "NVIDIA_H200_141GB"
    hot_load_bucket_type: str | None = "FW_HOSTED"
    skip_shape_validation: bool = False
    disable_speculative_decoding: bool = False
    extra_args: list[str] | None = None


class DeploymentManager:
    """Manages Fireworks deployment lifecycle and hotloading.

    Handles deployment creation, readiness polling, hotloading weight snapshots,
    and warmup.  All inference and hotload traffic goes through the gateway.

    Args:
        api_key: Fireworks API key.
        account_id: Fireworks account ID.
        base_url: Control-plane URL for deployment CRUD operations.
        inference_url: Gateway URL for inference completions.  Defaults to *base_url*.
        hotload_api_url: Gateway URL for hotload operations.  Defaults to *base_url*.
        additional_headers: Extra headers added to every request (e.g. gateway secret).

    Example::

        mgr = DeploymentManager(
            api_key="...",
            account_id="...",
            base_url="https://api.fireworks.ai",
        )

        # Example with separate control-plane and gateway endpoints:
        mgr = DeploymentManager(
            api_key="...",
            account_id="...",
            base_url="http://GATEWAY_IP:8083",
            inference_url="https://api.fireworks.ai",
            hotload_api_url="https://api.fireworks.ai",
        )
    """

    def __init__(
        self,
        api_key: str,
        account_id: str,
        base_url: str = "https://api.fireworks.ai",
        inference_url: str | None = None,
        hotload_api_url: str | None = None,
        additional_headers: dict[str, str] | None = None,
        verify_ssl: bool | None = None,
    ):
        self.api_key = api_key
        self.account_id = account_id
        self.base_url = base_url
        self.inference_url = inference_url or base_url
        self.hotload_api_url = hotload_api_url or base_url
        self.additional_headers = additional_headers
        self._verify_ssl = verify_ssl if verify_ssl is not None else self._should_verify_ssl(base_url)
        self.boot_time_s: float | None = None
        """Wall-clock seconds spent in the most recent ``wait_for_ready`` call."""

    @staticmethod
    def _should_verify_ssl(url: str) -> bool:
        """Verify SSL for https URLs with real domain names; skip for http or IPs."""
        import ipaddress
        from urllib.parse import urlparse

        parsed = urlparse(url)
        if parsed.scheme != "https":
            return False
        try:
            ipaddress.ip_address(parsed.hostname)
            return False
        except (ValueError, TypeError):
            return True

    def _headers(self) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "X-Api-Key": self.api_key,
        }
        if self.additional_headers:
            headers.update(self.additional_headers)
        return headers

    # -- Deployment CRUD -------------------------------------------------------

    def _get_deployment(self, deployment_id: str) -> dict | None:
        url = f"{self.base_url}/v1/accounts/{self.account_id}/deployments/{deployment_id}"
        resp = request_with_retries(requests.get, url, headers=self._headers(), timeout=30, verify=self._verify_ssl)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()

    def _delete_deployment(self, deployment_id: str, ignore_checks: bool = True, hard: bool = True) -> None:
        url = f"{self.base_url}/v1/accounts/{self.account_id}/deployments/{deployment_id}"
        params = []
        if ignore_checks:
            params.append("ignoreChecks=true")
        if hard:
            params.append("hard=true")
        if params:
            url = f"{url}?{'&'.join(params)}"
        resp = request_with_retries(requests.delete, url, headers=self._headers(), timeout=60, verify=self._verify_ssl)
        resp.raise_for_status()

    def _create_deployment(self, config: DeploymentConfig) -> dict:
        url = f"{self.base_url}/v1/accounts/{self.account_id}/deployments?deploymentId={config.deployment_id}"
        if config.skip_shape_validation:
            url = f"{url}&skipShapeValidation=true"
        if config.disable_speculative_decoding:
            url = f"{url}&disableSpeculativeDecoding=true"

        body: dict[str, Any] = {
            "baseModel": config.base_model,
            "minReplicaCount": config.min_replica_count,
            "maxReplicaCount": config.max_replica_count,
            "enableHotLoad": True,
            "placement": {"region": config.region},
        }
        if config.hot_load_bucket_type:
            body["hotLoadBucketType"] = config.hot_load_bucket_type
        if config.deployment_shape:
            body["deploymentShape"] = config.deployment_shape
        if config.accelerator_type:
            body["acceleratorType"] = config.accelerator_type
        if config.extra_args:
            flat = []
            for arg in config.extra_args:
                flat.extend(arg.split()) if " " in arg else flat.append(arg)
            body["extraArgs"] = flat

        logger.info("Creating deployment: %s", config.deployment_id)
        resp = request_with_retries(
            requests.post, url, headers=self._headers(), json=body, timeout=60, verify=self._verify_ssl
        )
        if resp.status_code == 409:
            logger.info(
                "Deployment %s already exists (409 Conflict), fetching existing deployment",
                config.deployment_id,
            )
            existing = self._get_deployment(config.deployment_id)
            if existing:
                return existing
        if not resp.ok:
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
                "Failed to delete deployment %s: %s. "
                "You can delete it manually in the Fireworks console: %s",
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
        url = f"{self.base_url}/v1/accounts/{self.account_id}/deployments/{deployment_id}"
        body = {"maxReplicaCount": 0, "minReplicaCount": 0}
        try:
            resp = request_with_retries(
                requests.patch,
                url,
                headers=self._headers(),
                json=body,
                timeout=60,
                verify=self._verify_ssl,
            )
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
        timeout: int = 60,
    ) -> dict[str, Any]:
        """Load a weight snapshot onto a deployment via the gateway.

        Args:
            deployment_id: Target deployment ID.
            base_model: Model name (e.g., accounts/fireworks/models/qwen3-8b).
            snapshot_identity: Snapshot identity to load.
            incremental_snapshot_metadata: For delta loads — must include
                previous_snapshot_identity, compression_format, checksum_format.
            timeout: Request timeout in seconds.
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "X-Api-Key": self.api_key,
            "fireworks-model": base_model,
            "fireworks-deployment": f"accounts/{self.account_id}/deployments/{deployment_id}",
        }
        url = f"{self.hotload_api_url}/hot_load/v1/models/hot_load"

        payload: dict[str, Any] = {"identity": snapshot_identity}
        if incremental_snapshot_metadata:
            payload["incremental_snapshot_metadata"] = incremental_snapshot_metadata

        ckpt_type = "DELTA" if incremental_snapshot_metadata else "FULL"
        logger.info("Hotloading %s snapshot '%s' to deployment '%s'", ckpt_type, snapshot_identity, deployment_id)

        verify = self._should_verify_ssl(self.hotload_api_url)
        resp = request_with_retries(
            requests.post,
            url,
            headers=headers,
            json=payload,
            timeout=timeout,
            verify=verify,
        )
        if not resp.ok:
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
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "X-Api-Key": self.api_key,
            "fireworks-model": base_model,
            "fireworks-deployment": f"accounts/{self.account_id}/deployments/{deployment_id}",
        }
        url = f"{self.hotload_api_url}/hot_load/v1/models/hot_load"

        verify = self._should_verify_ssl(self.hotload_api_url)
        resp = request_with_retries(requests.get, url, headers=headers, timeout=timeout, verify=verify)
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
                            "This may indicate an API version mismatch. "
                            f"Reach out on Discord for help: {DISCORD_URL}",
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
                        "Hotload: stage=%s, identity=%s, ready=%s (%ds)",
                        stage,
                        current_identity,
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
        timeout_seconds: int = 400,
    ) -> bool:
        """Hotload a snapshot and wait for it to complete. Returns True on success."""
        self.hotload(
            deployment_id=deployment_id,
            base_model=base_model,
            snapshot_identity=snapshot_identity,
            incremental_snapshot_metadata=incremental_snapshot_metadata,
        )
        return self.wait_for_hotload(
            deployment_id=deployment_id,
            base_model=base_model,
            expected_identity=snapshot_identity,
            timeout_seconds=timeout_seconds,
        )

    def _probe_inference(self, model: str) -> bool:
        """Silent single-shot probe: returns True if deployment responds HTTP 200."""
        base = self.inference_url.rstrip("/")
        url = f"{base}/inference/v1/completions"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}
        payload = {"model": model, "prompt": [1, 2], "max_tokens": 4, "temperature": 0.0}
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=10,
                                 verify=self._should_verify_ssl(self.inference_url))
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
        base = self.inference_url.rstrip("/")
        completions_url = f"{base}/inference/v1/completions"
        verify = self._should_verify_ssl(self.inference_url)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "X-Api-Key": self.api_key,
        }
        payload = {
            "model": model,
            # Keep warmup on the same token-in path as training sampling.
            "prompt": [1, 2],
            "max_tokens": 4,
            "temperature": 0.0,
        }

        logger.info("Warming up inference deployment (%d retries)...", max_retries)
        for attempt in range(1, max_retries + 1):
            try:
                resp = requests.post(completions_url, headers=headers, json=payload, timeout=30, verify=verify)
                if resp.status_code == 200:
                    logger.info("Inference deployment ready after %d attempt(s)", attempt)
                    return True
                logger.info("Warmup attempt %d/%d: HTTP %d", attempt, max_retries, resp.status_code)
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


class DeploymentSampler:
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

        completions = sampler.sample_with_tokens(messages=[...], n=4)
        for c in completions:
            print(c.text, len(c.full_tokens), c.finish_reason)
    """

    def __init__(
        self,
        inference_url: str,
        model: str,
        api_key: str,
        tokenizer: PreTrainedTokenizerBase,
    ):
        self.model = model
        self.api_key = api_key
        self.tokenizer = tokenizer

        base = inference_url.rstrip("/")
        self._completions_url = f"{base}/inference/v1/completions"
        self._verify_ssl = DeploymentManager._should_verify_ssl(inference_url)

    def completions(
        self,
        prompt: list[int],
        n: int = 1,
        max_tokens: int = 1024,
        temperature: float = 1.0,
        hotload_retry_interval: float = 30.0,
        hotload_max_retries: int = 10,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Send a completions request with token IDs to the deployment.

        Automatically retries on HTTP 425 (deployment is hot-loading weights).

        Args:
            prompt: Prompt as a list of token IDs (client-side tokenized).
            n: Number of completions to sample.
                In cookbook GRPO, this maps to ``completions_per_prompt``.
            max_tokens: Max tokens per completion.
            temperature: Sampling temperature.
            hotload_retry_interval: Seconds between retries when deployment
                is hot-loading (HTTP 425).  Default 30s.
            hotload_max_retries: Max retries for hot-loading.  Default 10
                (= ~5 min total wait).
            **kwargs: Extra fields passed directly to the API payload
                (e.g., raw_output=True, logprobs=True, reasoning_effort="none").

        Returns:
            Raw JSON response dict from the completions API.

        Raises:
            requests.HTTPError: On non-2xx responses after retries exhausted.
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "X-Api-Key": self.api_key,
        }
        http_timeout = kwargs.pop("http_timeout", 600)
        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "n": n,
            "max_tokens": max_tokens,
            "temperature": temperature,
            **kwargs,
        }
        for hotload_attempt in range(hotload_max_retries + 1):
            resp = request_with_retries(
                requests.post,
                self._completions_url,
                headers=headers,
                json=payload,
                timeout=http_timeout,
                verify=self._verify_ssl,
                max_wait_time=60,
            )

            if resp.status_code in (404, 425) and hotload_attempt < hotload_max_retries:
                logger.info(
                    "Deployment not ready (HTTP %d), retry %d/%d in %ds...",
                    resp.status_code,
                    hotload_attempt + 1,
                    hotload_max_retries,
                    int(hotload_retry_interval),
                )
                time.sleep(hotload_retry_interval)
                continue

            if not resp.ok:
                error_msg = parse_api_error(resp)
                hint = HTTP_STATUS_HINTS.get(resp.status_code, "")
                extra = ""
                if resp.status_code == 404:
                    extra = "\n  Verify the model name is correct and the deployment is running."
                elif resp.status_code == 401:
                    extra = "\n  Check that your API key is valid and has access to this deployment."
                logger.warning(
                    "\n%s",
                    format_sdk_error(
                        f"Completions error (HTTP {resp.status_code})",
                        error_msg,
                        f"{hint}{extra}",
                        docs_url=DOCS_SDK,
                    ),
                )
            resp.raise_for_status()
            return resp.json()

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

    def sample_with_tokens(
        self,
        messages: list[dict[str, str]],
        n: int = 1,
        max_tokens: int = 1024,
        temperature: float = 1.0,
        max_seq_len: int | None = None,
        **kwargs: Any,
    ) -> List[SampledCompletion]:
        """Sample completions and return structured results with token IDs.

        Tokenizes the chat messages client-side using the local tokenizer,
        sends token IDs to ``/inference/v1/completions``, and returns
        structured completions with the full token sequence.

        BOS and special tokens are handled by the tokenizer's chat template.

        When ``max_seq_len`` is set, two levels of filtering are applied:

        1. **Prompt pre-filter**: If the tokenized prompt already meets or
           exceeds ``max_seq_len``, the method returns an empty list
           immediately — no inference call is made.
        2. **Completion post-filter**: After sampling, any completion whose
           full token sequence (prompt + completion) exceeds ``max_seq_len``
           is silently dropped from the returned list.

        To retrieve per-token inference logprobs (needed for GRPO importance
        sampling), pass ``logprobs=True``::

            completions = sampler.sample_with_tokens(
                messages, n=8, logprobs=True, top_logprobs=1,
            )
            for c in completions:
                print(c.inference_logprobs)  # List[float] or None

        Args:
            messages: Chat messages (role + content).
            n: Number of completions to sample.
                In cookbook GRPO, this is usually ``completions_per_prompt``.
            max_tokens: Max tokens per completion.
            temperature: Sampling temperature.
            max_seq_len: If set, filter out sequences that exceed this length.
                Prompts that already meet or exceed the limit are rejected
                before calling the inference API.
            **kwargs: Extra fields passed to the API (e.g., ``logprobs=True``,
                ``top_logprobs=1``, ``reasoning_effort="none"``).

        Returns:
            List of :class:`SampledCompletion` with token IDs.  Prompt tokens
            come from client-side tokenization; completion tokens from the
            deployment's ``raw_output``.

        Raises:
            RuntimeError: If the deployment does not return ``raw_output``
                token IDs.
            requests.HTTPError: On non-2xx responses.
        """
        user_requested_logprobs = kwargs.get("logprobs", False)
        routing_requested = kwargs.get("include_routing_matrix", False)
        echo_mode = kwargs.get("echo", False)
        num_completions = n

        prompt_ids: list[int] = self.tokenizer.apply_chat_template(
            messages, tokenize=True, add_generation_prompt=True, return_dict=False,
        )

        if max_seq_len is not None and len(prompt_ids) >= max_seq_len:
            logger.info(
                "Prompt pre-filtered: %d prompt tokens >= max_seq_len %d, skipping inference",
                len(prompt_ids), max_seq_len,
            )
            return []

        result = self.completions(
            prompt=prompt_ids,
            n=num_completions,
            max_tokens=max_tokens,
            temperature=temperature,
            raw_output=True,
            **kwargs,
        )

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
                        f"The API response is missing completion_token_ids. "
                        f"Got choice keys: {list(choice.keys())}",
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

                completion_ids = completion_ids[len(prompt_ids):]
                if token_logprobs is not None:
                    token_logprobs = token_logprobs[1:]
                    lp_is_echo = True
                if routing_matrices is not None:
                    routing_matrices = routing_matrices[1:]

            full_tokens = list(prompt_ids) + list(completion_ids)
            if max_seq_len is not None and len(full_tokens) > max_seq_len:
                logger.debug(
                    "Completion post-filtered: %d tokens > max_seq_len %d",
                    len(full_tokens), max_seq_len,
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
