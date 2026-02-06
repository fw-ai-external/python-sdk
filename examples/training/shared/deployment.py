"""
Deployment Creation and Management.

A deployment is an inference endpoint that serves your model for sampling
(e.g., chat completions). With hotload enabled, you can update the model's
weights during training without restarting the deployment.

The typical workflow is:
1. Create a hotload-enabled deployment (create_or_get_deployment)
2. Wait for it to be ready (wait_for_deployment_ready)
3. Sample completions from it during training (via chat completions API)
4. After each training step, save weights and hotload them onto the deployment
5. The deployment now serves the updated model for the next round of sampling

Deployments use a "deployment shape" which pre-configures the GPU type and
count for your model. Ask your Fireworks contact for available shapes.

Copyright (c) Fireworks AI, Inc. and affiliates.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

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
class DeploymentInfo:
    """Info about a deployment.

    Attributes:
        deployment_id: Short deployment ID
        name: Full resource name
        state: Current state (e.g., "READY", "CREATING")
        hot_load_bucket_url: Path where the trainer uploads checkpoints
            for this deployment to hotload from
    """

    deployment_id: str
    name: str
    state: str
    hot_load_bucket_url: str | None


def _get_deployment(
    api_key: str,
    account_id: str,
    base_url: str,
    additional_headers: dict | None,
    deployment_id: str,
) -> dict | None:
    """Get deployment status. Returns None if not found."""
    try:
        client = _get_fireworks_client(api_key, base_url)
        deployment = client.deployments.get(
            account_id=account_id,
            deployment_id=deployment_id,
        )
        return deployment.model_dump() if hasattr(deployment, "model_dump") else dict(deployment)
    except Exception as e:
        if "not found" in str(e).lower() or "404" in str(e):
            return None
        raise


def delete_deployment(
    api_key: str,
    account_id: str,
    base_url: str,
    additional_headers: dict | None,
    deployment_id: str,
    ignore_checks: bool = True,
) -> None:
    """Delete a deployment, releasing its resources."""
    client = _get_fireworks_client(api_key, base_url)
    extra_query = {"ignoreChecks": "true"} if ignore_checks else None
    client.deployments.delete(
        account_id=account_id,
        deployment_id=deployment_id,
        extra_query=extra_query,
    )


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
    """Create a hotload-enabled deployment.

    This creates an inference endpoint with hotload enabled, allowing you to
    update the model's weights during training. The deployment will:
    - Serve chat completions at: POST /inference/v1/chat/completions
    - Accept hotload requests to swap in new weights
    - Watch for new checkpoint files

    The deployment_shape determines the GPU configuration. Common shapes:
    - accounts/{account}/deploymentShapes/hotload-qwen3-1p7b-bf16 (1x H200)
    - Ask your Fireworks contact for shapes matching your model

    Equivalent firectl command:
        firectl create deployment <base_model> \\
            --deployment-shape <shape> --region <region> \\
            --enable-hot-load --hot-load-bucket-type FW_HOSTED
    """
    client = _get_fireworks_client(api_key, base_url)

    log(f"Creating hotload-enabled deployment:")
    log(f"  deploymentId={deployment_id}, baseModel={base_model}, region={region}")
    if deployment_shape:
        log(f"  deploymentShape={deployment_shape}")
    if hot_load_bucket_type:
        log(f"  hotLoadBucketType={hot_load_bucket_type}")

    kwargs: dict[str, Any] = {
        "account_id": account_id,
        "deployment_id": deployment_id,
        "base_model": base_model,
        "min_replica_count": min_replica_count,
        "max_replica_count": max_replica_count,
        "enable_hot_load": True,
        "placement": {"region": region},
    }

    if hot_load_bucket_type:
        kwargs["hot_load_bucket_type"] = hot_load_bucket_type
    if deployment_shape:
        kwargs["deployment_shape"] = deployment_shape
    if accelerator_type:
        kwargs["accelerator_type"] = accelerator_type

    try:
        deployment = client.deployments.create(**kwargs)
        return deployment.model_dump() if hasattr(deployment, "model_dump") else dict(deployment)
    except Exception as e:
        warn(f"Deployment creation failed: {e}")
        raise


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
    """Create a new deployment or return info about an existing one.

    If a deployment with the given ID already exists, returns its info without
    modifying it. Otherwise, creates a new hotload-enabled deployment.
    """
    existing = _get_deployment(api_key, account_id, base_url, additional_headers, deployment_id)
    if existing:
        return DeploymentInfo(
            deployment_id=deployment_id,
            name=existing.get("name", ""),
            state=existing.get("state", "UNKNOWN"),
            hot_load_bucket_url=existing.get("hotLoadBucketUrl") or existing.get("hot_load_bucket_url"),
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
    """Wait for a deployment to become READY (model loaded, serving traffic).

    Typical wait time: 2-5 minutes depending on model size and GPU availability.
    """
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
            )
        if state in ("FAILED", "DELETED", "DELETING"):
            raise RuntimeError(f"Deployment entered bad state: {state}")
        time.sleep(poll_interval_s)
    raise TimeoutError(f"Deployment did not become ready within {timeout_s}s")
