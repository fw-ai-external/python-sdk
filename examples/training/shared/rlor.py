"""
RLOR (Reinforcement Learning Orchestrator) Trainer Job Management.

An RLOR trainer job is a GPU-backed training server managed by Fireworks.
When created in "service mode", it exposes a Tinker API endpoint that your
client-side script uses for:
  - forward passes (get logprobs)
  - forward_backward_custom (compute custom loss + backprop)
  - optim_step (apply optimizer update)
  - save_weights_for_sampler (save checkpoints for hotloading)

The trainer runs on dedicated hardware (e.g., H100/H200) and handles all
GPU computation. Your script runs on a CPU machine and orchestrates the
training loop.

Typical usage:
    endpoint = create_rlor_service_job_and_wait(
        api_key=api_key,
        account_id=account_id,
        base_model="accounts/fireworks/models/qwen3-8b",
        lora_rank=0,
        max_context_length=2048,
        learning_rate=1e-5,
        gradient_accumulation_steps=4,
    )
    # endpoint.base_url is the Tinker API endpoint for this trainer

Copyright (c) Fireworks AI, Inc. and affiliates.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import httpx

try:
    from fireworks import Fireworks

    FIREWORKS_SDK_AVAILABLE = True
except ImportError:
    FIREWORKS_SDK_AVAILABLE = False

from . import log, warn


def _get_fireworks_client(api_key: str, base_url: str) -> "Fireworks":
    """Get a Fireworks SDK client."""
    if not FIREWORKS_SDK_AVAILABLE:
        raise RuntimeError("Fireworks SDK not available. Install with: pip install fireworks-ai")
    return Fireworks(api_key=api_key, base_url=base_url)


@dataclass
class RlorServiceEndpoint:
    """Connection info for a running RLOR trainer job.

    Attributes:
        job_name: Full resource name (e.g., accounts/myaccount/rlorTrainerJobs/abc123)
        job_id: Short job ID (e.g., abc123)
        base_url: HTTPS endpoint for the Tinker API (e.g., https://trainer-...:30443)
    """

    job_name: str
    job_id: str
    base_url: str


def _build_headers(api_key: str, additional_headers: dict | None = None) -> dict:
    """Build headers for REST API requests."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    if additional_headers:
        headers.update(additional_headers)
    return headers


def _create_rlor_job(
    api_key: str,
    account_id: str,
    base_url: str,
    additional_headers: dict | None,
    base_model: str,
    lora_rank: int,
    max_context_length: int,
    learning_rate: float,
    gradient_accumulation_steps: int,
    node_count: int,
    display_name: str | None = None,
    hot_load_deployment_id: str | None = None,
    region: str | None = None,
    skip_validations: bool = False,
    custom_image_tag: str | None = None,
    extra_args: list[str] | None = None,
) -> dict:
    """Create an RLOR trainer job via the Fireworks SDK.

    The job is created in "service mode" (serviceMode=True) which means it
    stays running and exposes a Tinker API endpoint, rather than running a
    fixed training job to completion.

    If hot_load_deployment_id is provided, the trainer is linked to that
    deployment. This tells the trainer where to upload checkpoints
    so the deployment can hotload them.
    """
    client = _get_fireworks_client(api_key, base_url)

    log(f"Creating RLOR job via SDK:")
    log(f"  serviceMode=True, keepAlive=False, baseModel={base_model}")
    if hot_load_deployment_id:
        log(f"  hotLoadDeploymentId={hot_load_deployment_id}")
        log(f"  deploymentId (query param)={hot_load_deployment_id}")

    # serviceMode: keeps the trainer running as a service (vs. one-shot training)
    # keepAlive: False means the job auto-terminates when idle
    extra_body: dict[str, Any] = {
        "serviceMode": True,
        "keepAlive": False,
        "nodeCount": node_count,
        "dataset": "",  # Empty for service mode (data is sent via Tinker API)
    }
    if display_name:
        extra_body["displayName"] = display_name
    if hot_load_deployment_id:
        # Links trainer to deployment for checkpoint upload path resolution
        extra_body["hotLoadDeploymentId"] = hot_load_deployment_id

    # Training config: use the SDK's typed parameter for fields it supports
    # (this ensures proper proto enum serialization, e.g. region)
    typed_training_config: dict[str, Any] = {
        "base_model": base_model,
        "lora_rank": lora_rank,
        "max_context_length": max_context_length,
        "learning_rate": learning_rate,
        "gradient_accumulation_steps": gradient_accumulation_steps,
    }
    if region:
        typed_training_config["region"] = region
    if custom_image_tag:
        typed_training_config["custom_image_tag"] = custom_image_tag
        log(f"  customImageTag={custom_image_tag}")

    # Fields not in the SDK's typed TrainingConfig go via extra_body
    if extra_args:
        flat_extra_args = []
        for arg in extra_args:
            if " " in arg:
                flat_extra_args.extend(arg.split())
            else:
                flat_extra_args.append(arg)
        # extraArgs is not in the SDK's typed params, so pass via extra_body
        extra_body["trainingConfig"] = {"extraArgs": flat_extra_args}
        log(f"  extraArgs={flat_extra_args}")

    # skipValidations: bypasses control plane checks and auto-constructs the
    # Required for FW_HOSTED bucket type.
    extra_query: dict[str, str] = {}
    if skip_validations:
        extra_query["skipValidations"] = "true"
        log(f"  skipValidations=true")
    if hot_load_deployment_id:
        extra_query["deploymentId"] = hot_load_deployment_id

    try:
        job = client.reinforcement_fine_tuning_steps.create(
            account_id=account_id,
            training_config=typed_training_config,
            extra_body=extra_body,
            extra_query=extra_query if extra_query else None,
        )
        return job.model_dump() if hasattr(job, "model_dump") else dict(job)
    except Exception as e:
        warn(f"RLOR job creation failed: {e}")
        raise


def _get_rlor_job(
    api_key: str,
    account_id: str,
    base_url: str,
    additional_headers: dict | None,
    job_id: str,
) -> dict:
    """Get RLOR trainer job status."""
    client = _get_fireworks_client(api_key, base_url)
    job = client.reinforcement_fine_tuning_steps.get(
        account_id=account_id,
        rlor_trainer_job_id=job_id,
    )
    return job.model_dump() if hasattr(job, "model_dump") else dict(job)


def delete_rlor_job(
    api_key: str,
    account_id: str,
    base_url: str,
    additional_headers: dict | None,
    job_id: str,
) -> None:
    """Delete an RLOR trainer job, releasing its GPU resources."""
    client = _get_fireworks_client(api_key, base_url)
    client.reinforcement_fine_tuning_steps.delete(
        account_id=account_id,
        rlor_trainer_job_id=job_id,
    )


def create_rlor_service_job_and_wait(
    *,
    api_key: str,
    account_id: str,
    base_model: str,
    lora_rank: int,
    max_context_length: int,
    learning_rate: float,
    gradient_accumulation_steps: int,
    node_count: int = 1,
    display_name: str | None = None,
    hot_load_deployment_id: str | None = None,
    region: str | None = None,
    skip_validations: bool = False,
    custom_image_tag: str | None = None,
    extra_args: list[str] | None = None,
    base_url: str | None = None,
    additional_headers: dict | None = None,
    poll_interval_s: float = 5.0,
    timeout_s: float = 15 * 60,
) -> RlorServiceEndpoint:
    """Create an RLOR trainer job and wait for it to be ready.

    This is the main entry point for creating a trainer. It:
    1. Creates the job via the Fireworks API
    2. Polls until the trainer is running and its endpoint is reachable
    3. Returns the endpoint URL for use with tinker.ServiceClient

    Typical wait time: 1-3 minutes for the trainer to start and load the model.

    Args:
        api_key: Fireworks API key
        account_id: Fireworks account ID
        base_model: Model to load (e.g., "accounts/fireworks/models/qwen3-8b")
        lora_rank: LoRA rank (0 = full fine-tuning)
        max_context_length: Maximum sequence length
        learning_rate: Learning rate for the optimizer
        gradient_accumulation_steps: Number of forward_backward calls before optim_step
        node_count: Number of GPU nodes (default: 1)
        display_name: Human-readable name for the job
        hot_load_deployment_id: Link trainer to this deployment for checkpoint uploads
        region: GPU region (e.g., "US_VIRGINIA_1", "EU_ICELAND_2")
        skip_validations: Skip control plane validations (recommended for hotload)
        timeout_s: Max wait time in seconds (default: 15 minutes)

    Returns:
        RlorServiceEndpoint with the trainer's API URL
    """
    if base_url is None:
        base_url = "https://api.fireworks.ai"

    job = _create_rlor_job(
        api_key=api_key,
        account_id=account_id,
        base_url=base_url,
        additional_headers=additional_headers,
        base_model=base_model,
        lora_rank=lora_rank,
        max_context_length=max_context_length,
        learning_rate=learning_rate,
        gradient_accumulation_steps=gradient_accumulation_steps,
        node_count=node_count,
        display_name=display_name,
        hot_load_deployment_id=hot_load_deployment_id,
        region=region,
        skip_validations=skip_validations,
        custom_image_tag=custom_image_tag,
        extra_args=extra_args,
    )

    job_name = job.get("name", "")
    job_id = job_name.split("/")[-1] if "/" in job_name else job_name
    log(f"Created RLOR job: {job_id}")

    # Poll until the trainer is running and its endpoint is reachable
    start = time.time()
    while time.time() - start < timeout_s:
        job = _get_rlor_job(api_key, account_id, base_url, additional_headers, job_id)
        state = job.get("state", "")
        endpoint = job.get("directRouteHandle", "")

        elapsed = int(time.time() - start)
        log(
            f"  [{elapsed}s] State: {state}, Endpoint: {endpoint[:50]}..."
            if endpoint
            else f"  [{elapsed}s] State: {state}"
        )

        if state == "JOB_STATE_FAILED":
            msg = job.get("status", {}).get("message", "unknown")
            raise RuntimeError(f"RLOR job failed: {msg}")

        if state == "JOB_STATE_RUNNING" and endpoint:
            if endpoint.startswith("http://"):
                endpoint = "https://" + endpoint[7:]
            elif not endpoint.startswith("https://"):
                endpoint = "https://" + endpoint
            endpoint = endpoint.rstrip("/")
            return RlorServiceEndpoint(job_name=job_name, job_id=job_id, base_url=endpoint)

        # Even before state=RUNNING, try healthcheck if endpoint is available
        if endpoint:
            try:
                check_url = endpoint.rstrip("/")
                if check_url.startswith("http://"):
                    check_url = "https://" + check_url[7:]
                elif not check_url.startswith("https://"):
                    check_url = "https://" + check_url
                r = httpx.get(f"{check_url}/api/v1/healthz", timeout=5)
                if r.status_code == 200:
                    return RlorServiceEndpoint(job_name=job_name, job_id=job_id, base_url=check_url)
            except Exception:
                pass

        time.sleep(poll_interval_s)

    raise TimeoutError(f"RLOR job did not become ready within {timeout_s}s")
