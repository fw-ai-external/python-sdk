"""Trainer Job Management for Fireworks.

Manages the lifecycle of service-mode trainer jobs (called "RLOR jobs" in the
Fireworks REST API) that run the firetitan training backend and expose the
Tinker HTTP protocol.  These jobs are algorithm-agnostic — usable for DPO,
GRPO, SFT, or any Tinker-protocol training.
"""

from __future__ import annotations

import time
import logging
from typing import Any
from dataclasses import dataclass

import urllib3
import requests

from fireworks.training.sdk.errors import (
    DOCS_RLOR,
    HTTP_STATUS_HINTS,
    parse_api_error,
    format_sdk_error,
    request_with_retries,
)
from fireworks.training.sdk.deployment import DeploymentManager

# Suppress SSL warnings for dev/self-signed cert environments
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


@dataclass
class TrainerServiceEndpoint:
    """Info returned after creating/connecting to a service-mode trainer job."""

    job_name: str
    job_id: str
    base_url: str


@dataclass
class TrainerJobConfig:
    """Configuration for creating a trainer job."""

    base_model: str
    lora_rank: int = 0
    max_context_length: int = 4096
    learning_rate: float = 1e-5
    gradient_accumulation_steps: int = 1
    node_count: int = 1
    display_name: str | None = None
    hot_load_deployment_id: str | None = None
    region: str | None = None
    custom_image_tag: str | None = None
    extra_args: list[str] | None = None
    accelerator_type: str | None = None
    accelerator_count: int | None = None
    skip_validations: bool = False
    forward_only: bool = False


class TrainerJobManager:
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
        self.api_key = api_key
        self.account_id = account_id
        self.base_url = base_url
        self.additional_headers = additional_headers
        self._verify_ssl = verify_ssl if verify_ssl is not None else DeploymentManager._should_verify_ssl(base_url)

    def _headers(self) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "X-Api-Key": self.api_key,
        }
        if self.additional_headers:
            headers.update(self.additional_headers)
        return headers

    # -- Low-level REST calls --------------------------------------------------

    def _create(self, config: TrainerJobConfig) -> dict:
        url = f"{self.base_url}/v1/accounts/{self.account_id}/rlorTrainerJobs"
        query_params: list[str] = []
        if config.hot_load_deployment_id:
            query_params.append(f"deploymentId={config.hot_load_deployment_id}")
        if config.skip_validations:
            query_params.append("skipValidations=true")
        if query_params:
            url = f"{url}?{'&'.join(query_params)}"

        payload: dict[str, Any] = {
            "serviceMode": True,
            "keepAlive": False,
            "nodeCount": config.node_count,
            "dataset": "",
            "trainingConfig": {
                "baseModel": config.base_model,
                "loraRank": config.lora_rank,
                "maxContextLength": config.max_context_length,
                "learningRate": config.learning_rate,
                "gradientAccumulationSteps": config.gradient_accumulation_steps,
            },
        }
        if config.display_name:
            payload["displayName"] = config.display_name
        if config.hot_load_deployment_id:
            payload["hotLoadDeploymentId"] = config.hot_load_deployment_id
        if config.region:
            payload["trainingConfig"]["region"] = config.region
        if config.custom_image_tag:
            payload["trainingConfig"]["customImageTag"] = config.custom_image_tag
        if config.extra_args:
            flat = []
            for arg in config.extra_args:
                flat.extend(arg.split()) if " " in arg else flat.append(arg)
            payload["trainingConfig"]["extraArgs"] = flat
        if config.accelerator_type:
            payload["trainingConfig"]["acceleratorType"] = config.accelerator_type
        if config.accelerator_count:
            payload["trainingConfig"]["acceleratorCount"] = config.accelerator_count
        if config.forward_only:
            payload["forwardOnly"] = True

        logger.info("Creating RLOR job: POST %s (model=%s)", url, config.base_model)
        resp = request_with_retries(
            requests.post, url, json=payload, headers=self._headers(), timeout=60, verify=self._verify_ssl
        )
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
                    docs_url=DOCS_RLOR,
                ),
            )
        resp.raise_for_status()
        return resp.json()

    def get(self, job_id: str) -> dict:
        """Get the current state of an RLOR job. Returns raw API response dict."""
        url = f"{self.base_url}/v1/accounts/{self.account_id}/rlorTrainerJobs/{job_id}"
        resp = request_with_retries(requests.get, url, headers=self._headers(), timeout=30, verify=self._verify_ssl)
        resp.raise_for_status()
        return resp.json()

    def _delete(self, job_id: str) -> None:
        url = f"{self.base_url}/v1/accounts/{self.account_id}/rlorTrainerJobs/{job_id}"
        resp = request_with_retries(requests.delete, url, headers=self._headers(), timeout=30, verify=self._verify_ssl)
        resp.raise_for_status()

    def _resume(self, job_id: str) -> dict:
        url = f"{self.base_url}/v1/accounts/{self.account_id}/rlorTrainerJobs/{job_id}:resume"
        resp = request_with_retries(requests.post, url, headers=self._headers(), timeout=60, verify=self._verify_ssl)
        if not resp.ok:
            error_msg = parse_api_error(resp)
            hint = HTTP_STATUS_HINTS.get(resp.status_code, "")
            logger.warning(
                "\n%s",
                format_sdk_error(
                    f"RLOR job resume failed (HTTP {resp.status_code})",
                    error_msg,
                    f"{hint}\n  Check job status in the Fireworks console: "
                    f"https://fireworks.ai/account/rlor-jobs/{job_id}",
                    docs_url=DOCS_RLOR,
                ),
            )
        resp.raise_for_status()
        return resp.json()

    # -- High-level operations -------------------------------------------------

    def _check_healthz(self, base_url: str, timeout: float = 5) -> bool:
        """Probe /api/v1/healthz -- returns True only on HTTP 200."""
        try:
            r = requests.get(f"{base_url}/api/v1/healthz", timeout=timeout, verify=False)
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
        base_url: str = ""

        while time.time() - start < timeout_s:
            job = self.get(job_id)
            state = job.get("state", "")
            endpoint = job.get("directRouteHandle", "")
            elapsed = int(time.time() - start)

            if state == "JOB_STATE_FAILED":
                msg = job.get("status", {}).get("message", "unknown")
                raise RuntimeError(
                    format_sdk_error(
                        f"Trainer job {job_id} failed",
                        msg,
                        "Check the job logs in the Fireworks console for details.\n"
                        f"  Console: https://fireworks.ai/account/rlor-jobs/{job_id}\n"
                        "  Common causes: invalid model name, insufficient quota, or region unavailable.",
                        docs_url=DOCS_RLOR,
                    )
                )

            if endpoint:
                base_url = endpoint.rstrip("/")
                if not base_url.startswith("http://") and not base_url.startswith("https://"):
                    raise RuntimeError(
                        f"Trainer endpoint has no URL scheme: '{endpoint}'. "
                        "Expected a full URL from directRouteHandle."
                    )
                service_ready = self._check_healthz(base_url)

            if service_ready:
                logger.info(
                    "[%ds] Trainer job %s: state=%s, healthz=OK -- service ready",
                    elapsed,
                    job_id,
                    state,
                )
                return TrainerServiceEndpoint(job_name=job_name, job_id=job_id, base_url=base_url)

            # Log current state
            if endpoint:
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
                f"Increase timeout with --rlor-timeout-s (current: {timeout_s}s).\n"
                f"  Check job status: https://fireworks.ai/account/rlor-jobs/{job_id}",
                docs_url=DOCS_RLOR,
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
                    "Failed to query job %s (retrying): %s. " "This is usually transient during pod rescheduling.",
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
                        f"  Console: https://fireworks.ai/account/rlor-jobs/{job_id}",
                        docs_url=DOCS_RLOR,
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
            self._delete(job_id)
            logger.info("Deleted trainer job: %s", job_id)
        except Exception as e:
            logger.warning(
                "Failed to delete trainer job %s: %s. " "You can delete it manually in the Fireworks console.",
                job_id,
                e,
            )
