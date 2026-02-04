#!/usr/bin/env python3
"""
GRPO (Group Relative Policy Optimization) Training via Tinker SDK

This script runs GRPO training using the Tinker SDK and control plane with
two RLOR trainer jobs: policy (trainable) and reference (frozen, logprobs only).
Sampling uses the deployment's chat completions API.

Architecture:
    - Policy RLOR job: forward_backward + optim_step (trainable)
    - Reference RLOR job: forward only (frozen, for KL)
    - Deployment: sampling (chat completions) and hotload

GRPO Algorithm (On-Policy when using hotload):
    advantage = (r - mean_r) / (std_r + eps)
    loss = -advantage * sum(response_logprobs) + kl_beta * KL(policy || reference)
    
    On-policy: hotload at every step so sampling policy = current policy.
    No importance sampling needed (rho = 1).

Usage:
    python examples/rl/train_grpo.py \\
        --base-model "accounts/fireworks/models/qwen3-8b" \\
        --dataset /path/to/gsm8k.jsonl \\
        --create-deployment --hotload-deployment-id "grpo-test" \\
        --save-sampler --hotload --skip-validations

Copyright (c) Fireworks AI, Inc. and affiliates.
"""

from __future__ import annotations

import argparse
import atexit
import json
import math
import os
import re
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

import requests
import tinker
import torch
import torch.nn.functional as F
import urllib3

# Importing fireworks.rl applies the Fireworks compatibility patches to Tinker
# automatically (if Tinker is installed). This adds checkpoint_type support to
# save_weights_for_sampler.
import fireworks.rl  # noqa: F401

# Suppress SSL warnings for direct route requests (self-signed certs)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    import wandb

    WANDB_AVAILABLE = True
except ImportError:
    WANDB_AVAILABLE = False


# =============================================================================
# RLOR Trainer Job Creation (REST API) - same as DPO
# =============================================================================


@dataclass
class RlorServiceEndpoint:
    """Info returned after creating an RLOR service-mode trainer job."""

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
) -> dict:
    """Create RLOR trainer job via REST API."""
    url = f"{base_url}/v1/accounts/{account_id}/rlorTrainerJobs"
    query_params: list[str] = []
    if hot_load_deployment_id:
        query_params.append(f"deploymentId={hot_load_deployment_id}")
    if skip_validations:
        query_params.append("skipValidations=true")
    if query_params:
        url = f"{url}?{'&'.join(query_params)}"

    headers = _build_headers(api_key, additional_headers)

    payload: dict[str, Any] = {
        "serviceMode": True,
        "keepAlive": False,
        "nodeCount": node_count,
        "dataset": "",
        "trainingConfig": {
            "baseModel": base_model,
            "loraRank": lora_rank,
            "maxContextLength": max_context_length,
            "learningRate": learning_rate,
            "gradientAccumulationSteps": gradient_accumulation_steps,
        },
    }

    if display_name:
        payload["displayName"] = display_name
    if hot_load_deployment_id:
        payload["hotLoadDeploymentId"] = hot_load_deployment_id
    if region:
        payload["trainingConfig"]["region"] = region
    if custom_image_tag:
        payload["trainingConfig"]["customImageTag"] = custom_image_tag

    log(f"Creating RLOR job: POST {url}")
    log(f"  serviceMode=True, keepAlive=False, baseModel={base_model}")
    if hot_load_deployment_id:
        log(f"  deploymentId (query param)={hot_load_deployment_id}")

    resp = requests.post(url, json=payload, headers=headers, timeout=60)
    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        body = resp.text.strip()
        if body:
            warn(f"RLOR job creation failed ({resp.status_code}). Response body:\n{body}")
        raise
    return resp.json()


def _get_rlor_job(
    api_key: str,
    account_id: str,
    base_url: str,
    additional_headers: dict | None,
    job_id: str,
) -> dict:
    """Get RLOR trainer job status via REST API."""
    url = f"{base_url}/v1/accounts/{account_id}/rlorTrainerJobs/{job_id}"
    headers = _build_headers(api_key, additional_headers)
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _delete_rlor_job(
    api_key: str,
    account_id: str,
    base_url: str,
    additional_headers: dict | None,
    job_id: str,
) -> None:
    """Delete RLOR trainer job via REST API."""
    url = f"{base_url}/v1/accounts/{account_id}/rlorTrainerJobs/{job_id}"
    headers = _build_headers(api_key, additional_headers)
    resp = requests.delete(url, headers=headers, timeout=30)
    resp.raise_for_status()


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
    base_url: str | None = None,
    additional_headers: dict | None = None,
    poll_interval_s: float = 5.0,
    timeout_s: float = 15 * 60,
) -> RlorServiceEndpoint:
    """Create an RLOR service-mode trainer job and wait for it to be ready."""
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
    )

    job_name = job.get("name", "")
    job_id = job_name.split("/")[-1] if "/" in job_name else job_name
    log(f"Created RLOR job: {job_id}")

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

        if endpoint:
            try:
                check_url = endpoint.rstrip("/")
                if check_url.startswith("http://"):
                    check_url = "https://" + check_url[7:]
                elif not check_url.startswith("https://"):
                    check_url = "https://" + check_url
                r = requests.get(f"{check_url}/api/v1/healthz", timeout=5)
                if r.status_code == 200:
                    return RlorServiceEndpoint(job_name=job_name, job_id=job_id, base_url=check_url)
            except Exception:
                pass

        time.sleep(poll_interval_s)

    raise TimeoutError(f"RLOR job did not become ready within {timeout_s}s")


def log(msg: str) -> None:
    print(msg, flush=True)


def warn(msg: str) -> None:
    print(f"[warn] {msg}", flush=True)


def _parse_additional_headers(additional_headers_json: str | None) -> dict | None:
    if not additional_headers_json:
        return None
    try:
        return json.loads(additional_headers_json)
    except json.JSONDecodeError:
        warn(f"Invalid JSON for additional headers: {additional_headers_json}")
        return None


# =============================================================================
# Tokenizer
# =============================================================================


def encode_text(base_url: str, text: str) -> list[int]:
    """Encode text to token IDs via trainer's tokenizer endpoint."""
    resp = requests.post(
        f"{base_url}/api/v1/tokenizer/encode",
        json={"text": text},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["tokens"]


# =============================================================================
# Deployment Creation - same as DPO
# =============================================================================


@dataclass
class DeploymentInfo:
    deployment_id: str
    name: str
    state: str
    hot_load_bucket_url: str | None
    direct_route_handle: str | None = None


def _get_deployment(
    api_key: str,
    account_id: str,
    base_url: str,
    additional_headers: dict | None,
    deployment_id: str,
) -> dict | None:
    url = f"{base_url}/v1/accounts/{account_id}/deployments/{deployment_id}"
    headers = _build_headers(api_key, additional_headers)
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            return None
        raise


def _delete_deployment(
    api_key: str,
    account_id: str,
    base_url: str,
    additional_headers: dict | None,
    deployment_id: str,
    ignore_checks: bool = True,
) -> None:
    url = f"{base_url}/v1/accounts/{account_id}/deployments/{deployment_id}"
    if ignore_checks:
        url = f"{url}?ignoreChecks=true"
    headers = _build_headers(api_key, additional_headers)
    resp = requests.delete(url, headers=headers, timeout=60)
    resp.raise_for_status()


def _create_deployment(
    api_key: str,
    account_id: str,
    base_url: str,
    additional_headers: dict | None,
    deployment_id: str,
    base_model: str,
    deployment_shape: str | None = None,
    region: str = "US_VIRGINIA_1",
    min_replica_count: int = 0,
    max_replica_count: int = 1,
    accelerator_type: str | None = None,
    hot_load_bucket_type: str | None = None,
) -> dict:
    url = f"{base_url}/v1/accounts/{account_id}/deployments?deploymentId={deployment_id}"
    headers = _build_headers(api_key, additional_headers)
    body: dict[str, Any] = {
        "baseModel": base_model,
        "minReplicaCount": min_replica_count,
        "maxReplicaCount": max_replica_count,
        "enableHotLoad": True,
        "directRouteType": "INTERNET",
        "directRouteApiKeys": [api_key],
        "placement": {"region": region},
        "enableMultiRegionSharding": False,
    }
    if hot_load_bucket_type:
        body["hotLoadBucketType"] = hot_load_bucket_type
    if deployment_shape:
        body["deploymentShape"] = deployment_shape
    if accelerator_type:
        body["acceleratorType"] = accelerator_type
    resp = requests.post(url, headers=headers, json=body, timeout=60)
    resp.raise_for_status()
    return resp.json()


def create_or_get_deployment(
    api_key: str,
    account_id: str,
    base_url: str,
    additional_headers: dict | None,
    deployment_id: str,
    base_model: str,
    deployment_shape: str | None = None,
    region: str = "US_VIRGINIA_1",
    accelerator_type: str | None = None,
    hot_load_bucket_type: str | None = None,
) -> DeploymentInfo:
    existing = _get_deployment(api_key, account_id, base_url, additional_headers, deployment_id)
    if existing:
        return DeploymentInfo(
            deployment_id=deployment_id,
            name=existing.get("name", ""),
            state=existing.get("state", "UNKNOWN"),
            hot_load_bucket_url=existing.get("hotLoadBucketUrl") or existing.get("hot_load_bucket_url"),
            direct_route_handle=existing.get("directRouteHandle") or existing.get("direct_route_handle"),
        )
    log("Deployment not found, creating new one...")
    created = _create_deployment(
        api_key=api_key,
        account_id=account_id,
        base_url=base_url,
        additional_headers=additional_headers,
        deployment_id=deployment_id,
        base_model=base_model,
        deployment_shape=deployment_shape,
        region=region,
        accelerator_type=accelerator_type,
        hot_load_bucket_type=hot_load_bucket_type,
    )
    return DeploymentInfo(
        deployment_id=deployment_id,
        name=created.get("name", ""),
        state=created.get("state", "UNKNOWN"),
        hot_load_bucket_url=created.get("hotLoadBucketUrl") or created.get("hot_load_bucket_url"),
        direct_route_handle=created.get("directRouteHandle") or created.get("direct_route_handle"),
    )


def wait_for_deployment_ready(
    api_key: str,
    account_id: str,
    base_url: str,
    additional_headers: dict | None,
    deployment_id: str,
    timeout_s: float = 600,
    poll_interval_s: float = 15,
) -> DeploymentInfo:
    start = time.time()
    while time.time() - start < timeout_s:
        deployment = _get_deployment(api_key, account_id, base_url, additional_headers, deployment_id)
        if not deployment:
            raise RuntimeError(f"Deployment {deployment_id} not found")
        state = deployment.get("state", "UNKNOWN")
        elapsed = int(time.time() - start)
        log(f"  [{elapsed}s] Deployment state: {state}")
        if state == "READY":
            return DeploymentInfo(
                deployment_id=deployment_id,
                name=deployment.get("name", ""),
                state=state,
                hot_load_bucket_url=deployment.get("hotLoadBucketUrl") or deployment.get("hot_load_bucket_url"),
                direct_route_handle=deployment.get("directRouteHandle") or deployment.get("direct_route_handle"),
            )
        if state in ("FAILED", "DELETED", "DELETING"):
            raise RuntimeError(f"Deployment entered bad state: {state}")
        time.sleep(poll_interval_s)
    raise TimeoutError(f"Deployment did not become ready within {timeout_s}s")


# =============================================================================
# Hotload Helpers
# =============================================================================


def hotload_load_model(
    api_key: str,
    account_id: str,
    deployment_id: str,
    base_model: str,
    snapshot_identity: str,
    hotload_api_url: str = "https://api.fireworks.ai",
    incremental_snapshot_metadata: dict[str, Any] | None = None,
    timeout: int = 60,
) -> dict[str, Any]:
    """Load a model snapshot onto a deployment via the hotload API.

    Args:
        api_key: Fireworks API key
        account_id: Account ID
        deployment_id: Target deployment ID
        base_model: Model name (e.g., accounts/fireworks/models/qwen3-8b)
        snapshot_identity: Snapshot identity to load
        hotload_api_url: Hotload API URL
        incremental_snapshot_metadata: For delta loads, must include:
            - previous_snapshot_identity: The full checkpoint snapshot to diff against
            - compression_format: e.g., "arc_v2"
            - checksum_format: "alder32" (NOTE: server expects this misspelling of "adler32")
        timeout: Request timeout in seconds

    Returns:
        Response from hotload API
    """
    url = f"{hotload_api_url}/hot_load/v1/models/hot_load"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "fireworks-model": base_model,
        "fireworks-deployment": f"accounts/{account_id}/deployments/{deployment_id}",
    }
    payload: dict[str, Any] = {"identity": snapshot_identity}

    # For delta checkpoints, include incremental_snapshot_metadata
    if incremental_snapshot_metadata:
        payload["incremental_snapshot_metadata"] = incremental_snapshot_metadata
        log(
            f"Hotload: loading DELTA snapshot '{snapshot_identity}' "
            f"(base: {incremental_snapshot_metadata.get('previous_snapshot_identity')}) "
            f"onto deployment '{deployment_id}'..."
        )
    else:
        log(f"Hotload: loading FULL snapshot '{snapshot_identity}' onto deployment '{deployment_id}'...")

    resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
    if not resp.ok:
        # Log the full error response for debugging
        try:
            error_body = resp.json()
        except Exception:
            error_body = resp.text
        warn(f"  Hotload API error: {resp.status_code} - {error_body}")
    resp.raise_for_status()
    return resp.json()


def hotload_check_status(
    api_key: str,
    account_id: str,
    deployment_id: str,
    base_model: str,
    hotload_api_url: str = "https://api.fireworks.ai",
    direct_route_handle: str | None = None,
    timeout: int = 30,
) -> dict[str, Any]:
    """Check current hotload status for a deployment.

    If direct_route_handle is provided, uses direct route (more reliable).
    Otherwise falls back to gateway API.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    if direct_route_handle:
        # Direct route - hit the deployment directly (bypasses gateway)
        # Ensure proper URL format
        if not direct_route_handle.startswith("https://"):
            direct_route_handle = f"https://{direct_route_handle}"
        url = f"{direct_route_handle}/v1/models/hot_load"
    else:
        # Gateway route
        url = f"{hotload_api_url}/hot_load/v1/models/hot_load"
        headers["fireworks-model"] = base_model
        headers["fireworks-deployment"] = f"accounts/{account_id}/deployments/{deployment_id}"

    resp = requests.get(url, headers=headers, timeout=timeout, verify=False)
    resp.raise_for_status()
    return resp.json()


def wait_for_hotload_ready(
    api_key: str,
    account_id: str,
    deployment_id: str,
    base_model: str,
    expected_identity: str,
    hotload_api_url: str = "https://api.fireworks.ai",
    direct_route_handle: str | None = None,
    timeout_seconds: int = 400,
    poll_interval: int = 5,
) -> bool:
    """Wait for hotload to complete and return True if successful.

    PAPERCUT: The gateway hotload status API (GET /hot_load/v1/models/hot_load) is
    unreliable and often returns internal_server_error. The direct route is much
    more stable. Always prefer passing direct_route_handle when available.
    """
    log(f"Waiting for hotload to complete (identity={expected_identity})...")
    if direct_route_handle:
        log(f"  Using direct route: {direct_route_handle}")
    start_time = time.time()

    while time.time() - start_time < timeout_seconds:
        try:
            status = hotload_check_status(
                api_key, account_id, deployment_id, base_model, hotload_api_url, direct_route_handle
            )

            # Parse the actual response format: {"replicas": [{"current_snapshot_identity": ..., "loading_state": {"stage": ...}, "readiness": ...}]}
            replicas = status.get("replicas", [])
            if replicas:
                replica = replicas[0]
                current_identity = replica.get("current_snapshot_identity")
                loading_state = replica.get("loading_state", {})
                stage = loading_state.get("stage", "unknown")
                readiness = replica.get("readiness", False)
            else:
                # Fallback for legacy/different response format
                current_identity = status.get("identity") or status.get("current_identity")
                stage = status.get("state", "UNKNOWN")
                readiness = status.get("readiness", False)

            elapsed = int(time.time() - start_time)

            # Check if hotload is complete:
            # - readiness is True AND current_snapshot_identity matches expected
            # - stage can be "idle" (after completion) or "completed" (during completion)
            if readiness and current_identity == expected_identity:
                log(f"Hotload complete! Identity: {expected_identity} (took {elapsed}s)")
                return True
            elif stage == "error":
                warn("Hotload failed (stage=error)!")
                return False
            else:
                log(
                    f"  Hotload stage: {stage}, identity: {current_identity}, ready: {readiness} (elapsed: {elapsed}s)"
                )

        except Exception as e:
            warn(f"Error checking hotload status: {e}")

        time.sleep(poll_interval)

    warn(f"Hotload did not complete within {timeout_seconds}s")
    return False


# =============================================================================
# GSM8K Evaluator and Dataset
# =============================================================================


def extract_answer_digits(text: str) -> Optional[str]:
    match = re.search(r"<answer>(.*?)</answer>", text, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    digits = re.search(r"(-?\d+)", match.group(1))
    return digits.group(1) if digits else None


def evaluate_gsm8k_response(response: str, ground_truth: str) -> Tuple[float, str]:
    predicted = extract_answer_digits(response)
    truth = extract_answer_digits(str(ground_truth))
    if predicted is None or truth is None:
        return 0.0, f"Missing <answer> tags. Predicted: {predicted}, Truth: {truth}"
    if predicted == truth:
        return 1.0, f"Correct! Predicted: {predicted}, Truth: {truth}"
    return 0.0, f"Incorrect. Predicted: {predicted}, Truth: {truth}"


def load_gsm8k_dataset(path_or_url: str, max_rows: int) -> List[Dict[str, Any]]:
    """Load GSM8K-style dataset from path or URL. Format: messages + ground_truth per line."""
    if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
        resp = requests.get(path_or_url, timeout=30)
        resp.raise_for_status()
        lines = resp.text.strip().split("\n")
    else:
        with open(path_or_url) as f:
            lines = f.readlines()

    rows = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        rows.append(row)
        if len(rows) >= max_rows:
            break
    log(f"Loaded {len(rows)} examples from dataset")
    return rows


# =============================================================================
# GRPO Loss Function for forward_backward_custom
# =============================================================================


def make_grpo_loss_fn(
    rewards: List[float],
    ref_logprobs_list: List[List[float]],
    prompt_len: int,
    kl_beta: float = 0.001,
    eps: float = 1e-8,
) -> Callable[[List[tinker.Datum], List[torch.Tensor]], Tuple[torch.Tensor, Dict[str, float]]]:
    """Create a GRPO loss function for forward_backward_custom.

    GRPO (Group Relative Policy Optimization) uses reward centering within a group:
        advantage = (reward - mean_reward) / (std_reward + eps)

    On-policy loss (no importance sampling since we hotload before sampling):
        loss = -advantage * sum(response_logprobs) + kl_beta * KL(policy || reference)

    Args:
        rewards: List of K rewards, one per completion in the group
        ref_logprobs_list: Reference model logprobs for each completion (frozen, for KL)
        prompt_len: Number of prompt tokens (response starts at prompt_len - 1 in logprobs)
        kl_beta: KL regularization coefficient
        eps: Epsilon for numerical stability in advantage normalization

    Returns:
        Loss function compatible with training_client.forward_backward_custom()
    """
    K = len(rewards)
    if K == 0:
        raise ValueError("Cannot create GRPO loss with empty rewards")

    # Compute normalized advantages (GRPO-style reward centering)
    rewards_tensor = torch.tensor(rewards, dtype=torch.float32)
    mean_r = rewards_tensor.mean()
    std_r = rewards_tensor.std()
    if std_r < eps:
        std_r = torch.tensor(1.0)
    advantages = ((rewards_tensor - mean_r) / (std_r + eps)).tolist()

    # Convert reference logprobs to tensors (no grad needed - frozen)
    ref_tensors = [torch.tensor(ref_lp, dtype=torch.float32) for ref_lp in ref_logprobs_list]

    # Response tokens start at index (prompt_len - 1) in the logprobs array
    # because logprobs[i] = log P(token[i+1] | token[0:i+1])
    response_start_idx = max(0, prompt_len - 1)

    def loss_fn(
        data: List[tinker.Datum],
        logprobs_list: List[torch.Tensor],
    ) -> Tuple[torch.Tensor, Dict[str, float]]:
        """GRPO loss function.

        Args:
            data: List of K Datum objects (one per completion)
            logprobs_list: List of K logprob tensors from policy model (requires_grad=True)
                           Each tensor has shape [seq_len - 1] (logprobs for tokens[1:])

        Returns:
            (loss, metrics) tuple
        """
        assert len(logprobs_list) == K, f"Expected {K} sequences, got {len(logprobs_list)}"

        total_loss = torch.tensor(0.0)
        total_kl = 0.0
        total_policy_lp = 0.0
        total_ref_lp = 0.0
        num_response_tokens = 0

        for i in range(K):
            adv = advantages[i]
            pi_lp = logprobs_list[i]  # Policy logprobs (requires_grad=True)
            ref_lp = ref_tensors[i]  # Reference logprobs (frozen)

            # Get response-only logprobs (skip prompt tokens)
            # Handle case where sequences may have different lengths
            pi_response = pi_lp[response_start_idx:]
            ref_response = ref_lp[response_start_idx:] if len(ref_lp) > response_start_idx else torch.tensor([])

            # Ensure same length (truncate to shorter)
            min_len = min(len(pi_response), len(ref_response))
            if min_len == 0:
                continue

            pi_response = pi_response[:min_len]
            ref_response = ref_response[:min_len]

            # Policy gradient loss: -advantage * sum(logprobs)
            # On-policy: no importance ratio needed (rho = 1)
            pg_loss = -adv * pi_response.sum()

            # KL penalty: beta * sum(pi - ref) = beta * KL(pi || ref)
            # KL(pi || ref) ≈ sum(pi_logprob - ref_logprob) for same tokens
            kl_term = (pi_response - ref_response).sum()

            total_loss = total_loss + pg_loss + kl_beta * kl_term

            # Metrics (detached)
            with torch.no_grad():
                total_kl += kl_term.item()
                total_policy_lp += pi_response.sum().item()
                total_ref_lp += ref_response.sum().item()
                num_response_tokens += min_len

        # Average loss over group
        loss = total_loss / K

        # Compute metrics
        metrics = {
            "grpo_loss": loss.item(),
            "mean_reward": mean_r.item(),
            "std_reward": std_r.item() if isinstance(std_r, torch.Tensor) else std_r,
            "mean_advantage": sum(advantages) / K,
            "mean_kl": total_kl / K if K > 0 else 0.0,
            "mean_policy_lp": total_policy_lp / num_response_tokens if num_response_tokens > 0 else 0.0,
            "mean_ref_lp": total_ref_lp / num_response_tokens if num_response_tokens > 0 else 0.0,
            "num_response_tokens": num_response_tokens,
        }

        return loss, metrics

    return loss_fn


# =============================================================================
# Sampling from deployment
# =============================================================================


@dataclass
class SampledCompletion:
    text: str
    full_tokens: List[int]
    prompt_len: int


def sample_completions_from_deployment(
    inference_url: str,
    model: str,
    api_key: str,
    messages: List[Dict[str, str]],
    n: int,
    max_tokens: int = 1024,
    temperature: float = 0.7,
    policy_encode_url: str | None = None,
) -> List[SampledCompletion]:
    """Sample n completions from deployment. If raw_output not available, encode via policy tokenizer."""
    base = inference_url.rstrip("/")
    # Gateway (api.fireworks.ai): .../inference/v1/chat/completions; direct route: .../v1/chat/completions
    if "api.fireworks" in base:
        chat_url = f"{base}/inference/v1/chat/completions"
    else:
        chat_url = f"{base}/v1/chat/completions"

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    payload: Dict[str, Any] = {
        "model": model,
        "messages": messages,
        "n": n,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    payload["raw_output"] = True

    resp = requests.post(chat_url, headers=headers, json=payload, timeout=180)
    resp.raise_for_status()
    result = resp.json()
    completions = []

    for choice in result.get("choices", []):
        text = choice.get("message", {}).get("content", "")
        raw_output = choice.get("raw_output", {})
        prompt_token_ids = raw_output.get("prompt_token_ids", [])
        completion_token_ids = raw_output.get("completion_token_ids", [])

        if prompt_token_ids or completion_token_ids:
            full_tokens = prompt_token_ids + completion_token_ids
            prompt_len = len(prompt_token_ids)
        elif policy_encode_url:
            # Fallback: build prompt text and encode with policy tokenizer
            parts = []
            for m in messages:
                role = m.get("role", "user")
                content = m.get("content", "")
                parts.append(f"<|{role}|>\n{content}")
            prompt_text = "\n".join(parts) + "\n<|assistant|>\n"
            response_text = text
            full_prompt_tokens = encode_text(policy_encode_url, prompt_text)
            full_text = prompt_text + response_text
            full_tokens = encode_text(policy_encode_url, full_text)
            prompt_len = len(full_prompt_tokens)
        else:
            continue

        completions.append(SampledCompletion(text=text, full_tokens=full_tokens, prompt_len=prompt_len))

    return completions


# =============================================================================
# CLI and main
# =============================================================================


def parse_args():
    parser = argparse.ArgumentParser(description="GRPO Training via Tinker SDK (two RLOR jobs)")

    parser.add_argument("--api-key", default="tml-local", help="API key for trainer Tinker endpoint")
    parser.add_argument("--base-model", required=True, help="Base model name")

    parser.add_argument("--fireworks-api-key", default=None)
    parser.add_argument("--fireworks-account-id", default=None)
    parser.add_argument("--fireworks-base-url", default=None)
    parser.add_argument("--additional-headers", type=str, default=None)

    parser.add_argument("--rlor-node-count", type=int, default=1)
    parser.add_argument("--rlor-display-name", type=str, default=None)
    parser.add_argument("--hotload-deployment-id", type=str, default=None)
    parser.add_argument("--create-deployment", action="store_true")
    parser.add_argument("--deployment-shape", type=str, default=None)
    parser.add_argument("--deployment-timeout-s", type=float, default=600)
    parser.add_argument("--skip-validations", action="store_true")
    parser.add_argument("--custom-image-tag", type=str, default=None)
    parser.add_argument("--rlor-timeout-s", type=float, default=15 * 60)
    parser.add_argument("--rlor-poll-interval-s", type=float, default=5.0)
    parser.add_argument("--region", type=str, default=None)
    parser.add_argument("--deployment-region", type=str, default=None)
    parser.add_argument("--accelerator-type", type=str, default=None)
    parser.add_argument("--hot-load-bucket-type", type=str, default="FW_HOSTED")

    parser.add_argument("--dataset", required=True, help="Path or URL to GSM8K-style JSONL")
    parser.add_argument("--max-rows", type=int, default=100, help="Max dataset rows")
    parser.add_argument("--max-seq-len", type=int, default=4096)

    parser.add_argument("--group-size", type=int, default=4, help="GRPO K completions per prompt")
    parser.add_argument("--kl-beta", type=float, default=0.001)
    parser.add_argument("--lr", type=float, default=1e-5)
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--grad-accum", type=int, default=4)
    parser.add_argument("--lora-rank", type=int, default=0)
    parser.add_argument("--max-new-tokens", type=int, default=512)
    parser.add_argument("--temperature", type=float, default=0.7)

    parser.add_argument("--log-interval", type=int, default=1)
    parser.add_argument("--wandb-entity", type=str, default=None)
    parser.add_argument("--wandb-project", type=str, default="grpo-tinker")
    parser.add_argument("--wandb-run-name", type=str, default=None)

    parser.add_argument("--save-sampler", action="store_true")
    parser.add_argument("--sampler-name", type=str, default=None)
    parser.add_argument(
        "--save-interval",
        type=int,
        default=0,
        help="Save checkpoint every N optimizer steps (0 = only at end). "
        "First save is always full (base), subsequent saves are delta.",
    )
    parser.add_argument(
        "--hotload-interval",
        action="store_true",
        help="Hotload each checkpoint saved by --save-interval. "
        "Requires --save-interval > 0 and --hotload-deployment-id. "
        "First hotload is base, subsequent are delta.",
    )
    parser.add_argument(
        "--first-checkpoint-type",
        type=str,
        choices=["base", "delta"],
        default="base",
        help="Type for the FIRST checkpoint save. 'base' = full save (default), 'delta' = incremental. "
        "Subsequent saves are always delta. Use 'delta' when restarting script with existing trainer "
        "that already has a base checkpoint saved.",
    )
    parser.add_argument("--hotload", action="store_true")
    parser.add_argument("--hotload-api-url", type=str, default="https://api.fireworks.ai")
    parser.add_argument("--hotload-timeout", type=int, default=120)
    parser.add_argument("--direct-route-handle", type=str, default=None)

    parser.add_argument("--cleanup-rlor-job", action="store_true", help="Delete both RLOR jobs after training")
    parser.add_argument("--cleanup-deployment", action="store_true")

    return parser.parse_args()


def main():
    args = parse_args()
    log(f"Starting GRPO training: two RLOR jobs (policy + reference)")

    if args.hotload or args.save_sampler:
        if not args.hotload_deployment_id:
            raise RuntimeError("--hotload or --save-sampler requires --hotload-deployment-id")

    # Validate hotload-interval requirements
    if args.hotload_interval:
        if args.save_interval <= 0:
            raise RuntimeError("--hotload-interval requires --save-interval > 0")
        if not args.hotload_deployment_id:
            raise RuntimeError("--hotload-interval requires --hotload-deployment-id")

    use_wandb = WANDB_AVAILABLE and args.wandb_entity is not None
    if use_wandb:
        wandb.init(
            entity=args.wandb_entity,
            project=args.wandb_project,
            name=args.wandb_run_name,
            config={
                "group_size": args.group_size,
                "kl_beta": args.kl_beta,
                "lr": args.lr,
                "epochs": args.epochs,
                "grad_accum": args.grad_accum,
                "max_rows": args.max_rows,
            },
        )

    fw_api_key = args.fireworks_api_key or os.environ.get("FIREWORKS_API_KEY")
    fw_account_id = args.fireworks_account_id or os.environ.get("FIREWORKS_ACCOUNT_ID")
    fw_additional_headers = _parse_additional_headers(
        args.additional_headers or os.environ.get("FIREWORKS_ADDITIONAL_HEADERS")
    )
    fw_base_url = args.fireworks_base_url or os.environ.get("FIREWORKS_BASE_URL") or "https://api.fireworks.ai"
    if not fw_api_key or not fw_account_id:
        raise RuntimeError(
            "Set FIREWORKS_API_KEY and FIREWORKS_ACCOUNT_ID (or --fireworks-api-key / --fireworks-account-id)"
        )

    hotload_deployment_id = args.hotload_deployment_id
    direct_route_handle = args.direct_route_handle

    # Optional: create deployment
    if args.create_deployment:
        if not hotload_deployment_id:
            raise RuntimeError("--create-deployment requires --hotload-deployment-id")
        log("\n[1/5] Creating hotload-enabled deployment...")
        deployment_region = args.deployment_region or args.region or "US_VIRGINIA_1"
        deployment_info = create_or_get_deployment(
            api_key=fw_api_key,
            account_id=fw_account_id,
            base_url=fw_base_url,
            additional_headers=fw_additional_headers,
            deployment_id=hotload_deployment_id,
            base_model=args.base_model,
            deployment_shape=args.deployment_shape,
            region=deployment_region,
            accelerator_type=args.accelerator_type,
            hot_load_bucket_type=args.hot_load_bucket_type,
        )
        if deployment_info.state != "READY":
            deployment_info = wait_for_deployment_ready(
                api_key=fw_api_key,
                account_id=fw_account_id,
                base_url=fw_base_url,
                additional_headers=fw_additional_headers,
                deployment_id=hotload_deployment_id,
                timeout_s=args.deployment_timeout_s,
            )
        log(f"  Deployment ready: {deployment_info.name}")
        if deployment_info.direct_route_handle:
            direct_route_handle = deployment_info.direct_route_handle

    # Track created resources for cleanup on failure
    policy_endpoint = None
    reference_endpoint = None
    cleanup_done = False

    def cleanup_resources():
        """Clean up RLOR jobs and deployment. Called on success or failure."""
        nonlocal cleanup_done
        if cleanup_done:
            return
        cleanup_done = True

        if args.cleanup_rlor_job:
            for label, endpoint in [("policy", policy_endpoint), ("reference", reference_endpoint)]:
                if endpoint is None:
                    continue
                log(f"\nCleaning up RLOR job ({label}): {endpoint.job_id}")
                try:
                    _delete_rlor_job(
                        api_key=fw_api_key,
                        account_id=fw_account_id,
                        base_url=fw_base_url,
                        additional_headers=fw_additional_headers,
                        job_id=endpoint.job_id,
                    )
                    log(f"  Deleted {endpoint.job_id}")
                except Exception as e:
                    warn(f"Failed to delete {endpoint.job_id}: {e}")

        if args.cleanup_deployment and args.create_deployment and hotload_deployment_id:
            log(f"\nCleaning up deployment: {hotload_deployment_id}")
            try:
                _delete_deployment(
                    api_key=fw_api_key,
                    account_id=fw_account_id,
                    base_url=fw_base_url,
                    additional_headers=fw_additional_headers,
                    deployment_id=hotload_deployment_id,
                )
                log(f"  Deleted {hotload_deployment_id}")
            except Exception as e:
                warn(f"Failed to delete deployment: {e}")

    # Register cleanup to run on exit (handles exceptions, Ctrl+C, etc.)
    atexit.register(cleanup_resources)

    # Create policy RLOR job (with hotload)
    log("\n[2/5] Creating policy RLOR trainer job...")
    policy_endpoint = create_rlor_service_job_and_wait(
        api_key=fw_api_key,
        account_id=fw_account_id,
        base_url=fw_base_url,
        additional_headers=fw_additional_headers,
        base_model=args.base_model,
        lora_rank=args.lora_rank,
        max_context_length=args.max_seq_len,
        learning_rate=args.lr,
        gradient_accumulation_steps=args.grad_accum,
        node_count=args.rlor_node_count,
        display_name=(args.rlor_display_name or "grpo-policy"),
        hot_load_deployment_id=hotload_deployment_id,
        region=args.region,
        skip_validations=args.skip_validations,
        custom_image_tag=args.custom_image_tag,
        poll_interval_s=args.rlor_poll_interval_s,
        timeout_s=args.rlor_timeout_s,
    )
    log(f"  Policy trainer ready: {policy_endpoint.job_id}")

    # Create reference RLOR job (no hotload)
    log("\n[3/5] Creating reference RLOR trainer job...")
    reference_endpoint = create_rlor_service_job_and_wait(
        api_key=fw_api_key,
        account_id=fw_account_id,
        base_url=fw_base_url,
        additional_headers=fw_additional_headers,
        base_model=args.base_model,
        lora_rank=args.lora_rank,
        max_context_length=args.max_seq_len,
        learning_rate=args.lr,
        gradient_accumulation_steps=args.grad_accum,
        node_count=args.rlor_node_count,
        display_name="grpo-reference",
        hot_load_deployment_id=None,
        region=args.region,
        skip_validations=args.skip_validations,
        custom_image_tag=args.custom_image_tag,
        poll_interval_s=args.rlor_poll_interval_s,
        timeout_s=args.rlor_timeout_s,
    )
    log(f"  Reference trainer ready: {reference_endpoint.job_id}")

    # Create Tinker SDK clients for policy and reference trainers
    policy_service = tinker.ServiceClient(base_url=policy_endpoint.base_url, api_key=args.api_key)
    policy_client = policy_service.create_lora_training_client(
        base_model=args.base_model,
        rank=args.lora_rank,
    )
    log(f"  Policy Tinker client created: {policy_endpoint.base_url}")

    reference_service = tinker.ServiceClient(base_url=reference_endpoint.base_url, api_key=args.api_key)
    reference_client = reference_service.create_lora_training_client(
        base_model=args.base_model,
        rank=args.lora_rank,
    )
    log(f"  Reference Tinker client created: {reference_endpoint.base_url}")

    # Keep URLs for tokenizer endpoint
    policy_url = policy_endpoint.base_url

    # Inference URL for sampling (deployment direct route or base URL)
    inference_url = direct_route_handle or fw_base_url
    if not inference_url.startswith("http"):
        inference_url = f"https://{inference_url}"
    inference_model = args.base_model

    # Load dataset
    log("\n[4/5] Loading dataset...")
    dataset = load_gsm8k_dataset(args.dataset, args.max_rows)
    if not dataset:
        raise RuntimeError("No data loaded!")

    # Training loop
    log("\n[5/5] GRPO training loop...")
    global_step = 0
    accum_count = 0
    epoch_metrics = {"reward": 0.0, "accuracy": 0.0, "kl": 0.0, "grpo_loss": 0.0, "num_prompts": 0}
    skipped = 0

    # Periodic checkpoint tracking:
    # - base_checkpoint_saved: Has THIS TRAINER SESSION saved a full (base) checkpoint?
    #   Controls whether next save is full vs delta.
    # - base_checkpoint_identity: What checkpoint should delta HOTLOADS reference?
    #   For chained deltas, this is the most recently hotloaded checkpoint.
    base_checkpoint_saved = False  # True once a full checkpoint has been saved
    base_checkpoint_identity: str | None = None  # Identity of current full checkpoint for delta reference

    # Print initial (step 0) metrics for e2e test
    print(json.dumps({"type": "metrics", "step": 0, "reward": 0.0, "accuracy": 0.0, "kl": 0.0}))

    for epoch in range(args.epochs):
        for prompt_idx, row in enumerate(dataset):
            messages = row.get("messages", [])
            ground_truth = row.get("ground_truth", "")
            if not messages or not ground_truth:
                continue

            input_messages = [m for m in messages if m.get("role") != "assistant"]
            if not input_messages:
                continue

            # =========================================================================
            # On-Policy: Hotload current weights before sampling
            # This ensures sampling policy = current policy (no importance sampling needed)
            # =========================================================================
            if global_step > 0 and hotload_deployment_id:
                try:
                    sampler_name = f"online-step-{global_step}"
                    ckpt_type = "delta" if base_checkpoint_saved else "base"
                    log(f"  Hotloading weights before sampling (step {global_step}, type={ckpt_type})...")

                    # Save current weights (patched API accepts checkpoint_type)
                    policy_client.save_weights_for_sampler(
                        sampler_name,
                        checkpoint_type=ckpt_type,
                    ).result()

                    # Track checkpoint for delta chaining
                    if not base_checkpoint_saved:
                        base_checkpoint_saved = True
                        if ckpt_type == "base":
                            base_checkpoint_identity = sampler_name

                    # Build incremental metadata for delta hotloads
                    incremental_metadata: dict[str, Any] | None = None
                    if ckpt_type == "delta" and base_checkpoint_identity:
                        incremental_metadata = {
                            "previous_snapshot_identity": base_checkpoint_identity,
                            "compression_format": "arc_v2",
                            "checksum_format": "alder32",
                        }

                    # Trigger hotload
                    hotload_load_model(
                        api_key=fw_api_key,
                        account_id=fw_account_id,
                        deployment_id=hotload_deployment_id,
                        base_model=args.base_model,
                        snapshot_identity=sampler_name,
                        hotload_api_url=args.hotload_api_url,
                        incremental_snapshot_metadata=incremental_metadata,
                    )

                    # Wait for hotload to complete
                    hotload_success = wait_for_hotload_ready(
                        api_key=fw_api_key,
                        account_id=fw_account_id,
                        deployment_id=hotload_deployment_id,
                        base_model=args.base_model,
                        expected_identity=sampler_name,
                        hotload_api_url=args.hotload_api_url,
                        direct_route_handle=direct_route_handle,
                        timeout_seconds=args.hotload_timeout,
                    )

                    if hotload_success:
                        # Update base identity for next delta
                        base_checkpoint_identity = sampler_name
                    else:
                        warn(f"  Hotload failed for step {global_step}, continuing with stale weights")

                except Exception as e:
                    warn(f"  Hotload error at step {global_step}: {e}")

            # =========================================================================
            # Sample completions from deployment
            # =========================================================================
            try:
                sampled = sample_completions_from_deployment(
                    inference_url=inference_url,
                    model=inference_model,
                    api_key=fw_api_key,
                    messages=input_messages,
                    n=args.group_size,
                    max_tokens=args.max_new_tokens,
                    temperature=args.temperature,
                    policy_encode_url=policy_url,
                )
            except Exception as e:
                warn(f"Sampling failed for prompt {prompt_idx}: {e}")
                continue

            if len(sampled) < args.group_size:
                warn(f"Got {len(sampled)} completions, expected {args.group_size}")
                continue

            # =========================================================================
            # Compute rewards
            # =========================================================================
            rewards = []
            for s in sampled:
                score, _ = evaluate_gsm8k_response(s.text, ground_truth)
                rewards.append(score)

            # Skip if all rewards are the same (no learning signal)
            if len(set(rewards)) == 1:
                skipped += 1
                continue

            # =========================================================================
            # Get reference logprobs (frozen model, for KL penalty)
            # =========================================================================
            ref_logprobs_list: List[List[float]] = []
            datums: List[tinker.Datum] = []
            prompt_len = 0

            for s in sampled:
                full_tokens = s.full_tokens
                if prompt_len == 0:
                    prompt_len = s.prompt_len

                if len(full_tokens) < 2:
                    continue

                # Create Datum for forward pass
                # Client-side shifting: model_input = tokens[:-1], target_tokens = tokens[1:]
                datum = tinker.Datum(
                    model_input=tinker.ModelInput.from_ints(full_tokens[:-1]),
                    loss_fn_inputs={
                        "target_tokens": tinker.TensorData(
                            data=full_tokens[1:],
                            dtype="int64",
                            shape=[len(full_tokens) - 1],
                        ),
                    },
                )
                datums.append(datum)

                # Get reference logprobs via forward on frozen reference trainer
                ref_fwd = reference_client.forward([datum], "cross_entropy").result()
                ref_lp = list(ref_fwd.loss_fn_outputs[0]["logprobs"].data)
                ref_logprobs_list.append(ref_lp)

            if not datums:
                continue

            # =========================================================================
            # Create GRPO loss function and run forward_backward_custom
            # =========================================================================
            grpo_loss_fn = make_grpo_loss_fn(
                rewards=rewards,
                ref_logprobs_list=ref_logprobs_list,
                prompt_len=prompt_len,
                kl_beta=args.kl_beta,
            )

            # forward_backward_custom:
            # 1. Does forward pass on policy trainer to get logprobs
            # 2. Converts to PyTorch tensors with requires_grad=True
            # 3. Calls our grpo_loss_fn to compute loss
            # 4. Calls loss.backward() to get per-token gradients d_loss/d_logprob
            # 5. Sends gradients back to server for backward pass
            result = policy_client.forward_backward_custom(datums, grpo_loss_fn).result()
            metrics = result.metrics

            # =========================================================================
            # Accumulate metrics
            # =========================================================================
            epoch_metrics["reward"] += sum(rewards) / len(rewards)
            epoch_metrics["accuracy"] += sum(1 for r in rewards if r > 0.5) / len(rewards)
            epoch_metrics["kl"] += metrics.get("mean_kl", 0.0)
            epoch_metrics["grpo_loss"] += metrics.get("grpo_loss", 0.0)
            epoch_metrics["num_prompts"] += 1
            accum_count += 1

            if accum_count >= args.grad_accum:
                policy_client.optim_step(
                    tinker.AdamParams(
                        learning_rate=args.lr,
                        beta1=0.9,
                        beta2=0.999,
                        eps=1e-8,
                        weight_decay=0.01,
                    )
                ).result()
                global_step += 1

                n = epoch_metrics["num_prompts"]
                avg_reward = epoch_metrics["reward"] / n if n > 0 else 0
                avg_acc = epoch_metrics["accuracy"] / n if n > 0 else 0
                avg_kl = epoch_metrics["kl"] / n if n > 0 else 0
                avg_loss = epoch_metrics["grpo_loss"] / n if n > 0 else 0

                log(
                    f"Step {global_step} | Loss: {avg_loss:.4f} | Reward: {avg_reward:.3f} | Acc: {avg_acc:.2%} | KL: {avg_kl:.4f} | LR: {args.lr:.2e}"
                )
                print(
                    json.dumps(
                        {
                            "type": "metrics",
                            "step": global_step,
                            "grpo_loss": avg_loss,
                            "reward": avg_reward,
                            "accuracy": avg_acc,
                            "kl": avg_kl,
                        }
                    )
                )

                if use_wandb:
                    wandb.log(
                        {
                            "train/grpo_loss": avg_loss,
                            "train/reward": avg_reward,
                            "train/accuracy": avg_acc,
                            "train/kl": avg_kl,
                            "train/step": global_step,
                        },
                        step=global_step,
                    )

                # Periodic checkpoint saving (first uses --first-checkpoint-type, subsequent are delta)
                if args.save_interval > 0 and global_step % args.save_interval == 0:
                    ckpt_name = f"step-{global_step}"
                    # First save uses --first-checkpoint-type, subsequent are always delta
                    if base_checkpoint_saved:
                        ckpt_type = "delta"
                    else:
                        ckpt_type = args.first_checkpoint_type  # "base" or "delta"
                    log(f"  Saving periodic checkpoint: {ckpt_name} (type={ckpt_type})")
                    try:
                        # Patched API accepts checkpoint_type
                        ckpt_result = policy_client.save_weights_for_sampler(
                            ckpt_name,
                            checkpoint_type=ckpt_type,
                        ).result()
                        ckpt_snapshot_id = ckpt_name  # snapshot_id is the path/name
                        actual_ckpt_type = ckpt_type

                        # Track that we've saved (subsequent saves will be delta)
                        if not base_checkpoint_saved:
                            base_checkpoint_saved = True
                            if actual_ckpt_type == "base":
                                base_checkpoint_identity = ckpt_snapshot_id
                        log(f"  Checkpoint saved: {ckpt_name} (type={actual_ckpt_type})")

                        # Hotload this checkpoint if --hotload-interval is set
                        if args.hotload_interval and hotload_deployment_id:
                            try:
                                # For delta checkpoints, include incremental_snapshot_metadata
                                # For base checkpoints, send without incremental metadata
                                incremental_metadata: dict[str, Any] | None = None
                                if actual_ckpt_type == "delta":
                                    log(f"  Hotloading DELTA checkpoint to {hotload_deployment_id}...")
                                    # Construct metadata from known full checkpoint
                                    if base_checkpoint_identity:
                                        incremental_metadata = {
                                            "previous_snapshot_identity": base_checkpoint_identity,
                                            "compression_format": "arc_v2",
                                            # NOTE: "alder32" is intentional - server expects this misspelling
                                            "checksum_format": "alder32",
                                        }
                                        log(f"  Delta base: {incremental_metadata.get('previous_snapshot_identity')}")
                                    else:
                                        warn("  Delta checkpoint but no base identity found - hotload may fail")
                                else:
                                    log(f"  Hotloading FULL checkpoint to {hotload_deployment_id}...")

                                # Trigger hotload
                                hotload_load_model(
                                    api_key=fw_api_key,
                                    account_id=fw_account_id,
                                    deployment_id=hotload_deployment_id,
                                    base_model=args.base_model,
                                    snapshot_identity=ckpt_snapshot_id,
                                    hotload_api_url=args.hotload_api_url,
                                    incremental_snapshot_metadata=incremental_metadata,
                                )

                                # Wait for hotload to complete
                                hotload_success = wait_for_hotload_ready(
                                    api_key=fw_api_key,
                                    account_id=fw_account_id,
                                    deployment_id=hotload_deployment_id,
                                    base_model=args.base_model,
                                    expected_identity=ckpt_snapshot_id,
                                    hotload_api_url=args.hotload_api_url,
                                    direct_route_handle=direct_route_handle,
                                    timeout_seconds=args.hotload_timeout,
                                )
                                if hotload_success:
                                    log(f"  Hotload complete: {ckpt_name}")
                                    # After successful hotload, update the base identity.
                                    # The trainer chains deltas (each delta is relative to previous),
                                    # so the next delta hotload must reference this checkpoint.
                                    base_checkpoint_identity = ckpt_snapshot_id
                                else:
                                    warn(f"  Hotload failed for {ckpt_name}")
                            except Exception as e:
                                warn(f"  Hotload error: {e}")
                    except Exception as e:
                        warn(f"  Failed to save checkpoint: {e}")

                epoch_metrics = {"reward": 0.0, "accuracy": 0.0, "kl": 0.0, "grpo_loss": 0.0, "num_prompts": 0}
                accum_count = 0

        if accum_count > 0:
            policy_client.optim_step(
                tinker.AdamParams(
                    learning_rate=args.lr,
                    beta1=0.9,
                    beta2=0.999,
                    eps=1e-8,
                    weight_decay=0.01,
                )
            ).result()
            global_step += 1

            # Log end-of-epoch step (same as main loop)
            n = epoch_metrics["num_prompts"]
            avg_reward = epoch_metrics["reward"] / n if n > 0 else 0
            avg_acc = epoch_metrics["accuracy"] / n if n > 0 else 0
            avg_kl = epoch_metrics["kl"] / n if n > 0 else 0
            avg_loss = epoch_metrics["grpo_loss"] / n if n > 0 else 0

            log(
                f"Step {global_step} | Loss: {avg_loss:.4f} | Reward: {avg_reward:.3f} | Acc: {avg_acc:.2%} | KL: {avg_kl:.4f} | LR: {args.lr:.2e}"
            )
            print(
                json.dumps(
                    {
                        "type": "metrics",
                        "step": global_step,
                        "grpo_loss": avg_loss,
                        "reward": avg_reward,
                        "accuracy": avg_acc,
                        "kl": avg_kl,
                    }
                )
            )

            if use_wandb:
                wandb.log(
                    {
                        "train/grpo_loss": avg_loss,
                        "train/reward": avg_reward,
                        "train/accuracy": avg_acc,
                        "train/kl": avg_kl,
                        "train/step": global_step,
                    },
                    step=global_step,
                )

            # Periodic checkpoint saving for end-of-epoch step
            if args.save_interval > 0 and global_step % args.save_interval == 0:
                ckpt_name = f"step-{global_step}"
                if base_checkpoint_saved:
                    ckpt_type = "delta"
                else:
                    ckpt_type = args.first_checkpoint_type
                log(f"  Saving periodic checkpoint: {ckpt_name} (type={ckpt_type})")
                try:
                    # Patched API accepts checkpoint_type
                    ckpt_result = policy_client.save_weights_for_sampler(
                        ckpt_name,
                        checkpoint_type=ckpt_type,
                    ).result()
                    ckpt_snapshot_id = ckpt_name
                    actual_ckpt_type = ckpt_type

                    if not base_checkpoint_saved:
                        base_checkpoint_saved = True
                        if actual_ckpt_type == "base":
                            base_checkpoint_identity = ckpt_snapshot_id
                    log(f"  Checkpoint saved: {ckpt_name} (type={actual_ckpt_type})")

                    # Hotload this checkpoint if --hotload-interval is set
                    if args.hotload_interval and hotload_deployment_id:
                        try:
                            incremental_metadata: dict[str, Any] | None = None
                            if actual_ckpt_type == "delta":
                                log(f"  Hotloading DELTA checkpoint to {hotload_deployment_id}...")
                                if base_checkpoint_identity:
                                    incremental_metadata = {
                                        "previous_snapshot_identity": base_checkpoint_identity,
                                        "compression_format": "arc_v2",
                                        # NOTE: "alder32" is intentional - server expects this misspelling
                                        "checksum_format": "alder32",
                                    }
                                    log(
                                        f"  Delta base (full checkpoint): {incremental_metadata.get('previous_snapshot_identity')}"
                                    )
                            else:
                                log(f"  Hotloading FULL checkpoint to {hotload_deployment_id}...")

                            hotload_load_model(
                                api_key=fw_api_key,
                                account_id=fw_account_id,
                                deployment_id=hotload_deployment_id,
                                base_model=args.base_model,
                                snapshot_identity=ckpt_snapshot_id,
                                hotload_api_url=args.hotload_api_url,
                                incremental_snapshot_metadata=incremental_metadata,
                            )

                            hotload_success = wait_for_hotload_ready(
                                api_key=fw_api_key,
                                account_id=fw_account_id,
                                deployment_id=hotload_deployment_id,
                                base_model=args.base_model,
                                expected_identity=ckpt_snapshot_id,
                                hotload_api_url=args.hotload_api_url,
                                direct_route_handle=direct_route_handle,
                                timeout_seconds=args.hotload_timeout,
                            )
                            if hotload_success:
                                log(f"  Hotload complete: {ckpt_name}")
                                base_checkpoint_identity = ckpt_snapshot_id
                            else:
                                warn(f"  Hotload failed for {ckpt_name}")
                        except Exception as e:
                            warn(f"  Hotload error: {e}")
                except Exception as e:
                    warn(f"  Failed to save checkpoint: {e}")

            epoch_metrics = {"reward": 0.0, "accuracy": 0.0, "kl": 0.0, "grpo_loss": 0.0, "num_prompts": 0}
            accum_count = 0

    log(f"\nTraining complete: {global_step} optimizer steps (skipped {skipped} prompts with uniform rewards)")

    # Save and hotload
    if args.save_sampler:
        sampler_name = args.sampler_name or f"grpo_sampler_step_{global_step}"
        # First save uses --first-checkpoint-type, subsequent are always delta
        if base_checkpoint_saved:
            final_ckpt_type = "delta"
        else:
            final_ckpt_type = args.first_checkpoint_type  # "base" or "delta"
        log(f"\nSaving final weights: {sampler_name} (type={final_ckpt_type})")
        try:
            # Patched API accepts checkpoint_type
            sampler_result = policy_client.save_weights_for_sampler(
                sampler_name,
                checkpoint_type=final_ckpt_type,
            ).result()
            result_path = sampler_result.path
            actual_final_type = final_ckpt_type
            log(f"  Saved to: {result_path} (type={actual_final_type})")

            # Track that we've saved
            if not base_checkpoint_saved:
                base_checkpoint_saved = True
                if actual_final_type == "base":
                    base_checkpoint_identity = sampler_name

            # Hotload: load trained weights onto inference deployment
            if args.hotload and hotload_deployment_id:
                try:
                    # For delta checkpoints, include incremental_snapshot_metadata
                    # For base checkpoints, send without incremental metadata
                    incremental_metadata: dict[str, Any] | None = None
                    if actual_final_type == "delta":
                        log(f"\nHotloading DELTA weights to deployment: {hotload_deployment_id}")
                        # Construct metadata from known full checkpoint
                        if base_checkpoint_identity:
                            incremental_metadata = {
                                "previous_snapshot_identity": base_checkpoint_identity,
                                "compression_format": "arc_v2",
                                # NOTE: "alder32" is intentional - server expects this misspelling
                                "checksum_format": "alder32",
                            }
                            log(
                                f"  Delta base (full checkpoint): {incremental_metadata.get('previous_snapshot_identity')}"
                            )
                        else:
                            warn("  Delta checkpoint but no full checkpoint identity found - hotload may fail")
                    else:
                        log(f"\nHotloading FULL weights to deployment: {hotload_deployment_id}")

                    hotload_load_model(
                        api_key=fw_api_key,
                        account_id=fw_account_id,
                        deployment_id=hotload_deployment_id,
                        base_model=args.base_model,
                        snapshot_identity=sampler_name,
                        hotload_api_url=args.hotload_api_url,
                        incremental_snapshot_metadata=incremental_metadata,
                    )

                    hotload_success = wait_for_hotload_ready(
                        api_key=fw_api_key,
                        account_id=fw_account_id,
                        deployment_id=hotload_deployment_id,
                        base_model=args.base_model,
                        expected_identity=sampler_name,
                        hotload_api_url=args.hotload_api_url,
                        direct_route_handle=direct_route_handle,
                        timeout_seconds=args.hotload_timeout,
                    )
                    if not hotload_success:
                        warn("Hotload did not complete successfully")

                except Exception as e:
                    warn(f"Hotload failed: {e}")

            elif args.hotload and not hotload_deployment_id:
                warn("--hotload requires --hotload-deployment-id")

        except Exception as e:
            warn(f"Failed to save weights: {e}")

    if use_wandb:
        wandb.finish()

    # Cleanup (also registered via atexit for exception handling)
    cleanup_resources()


if __name__ == "__main__":
    main()
