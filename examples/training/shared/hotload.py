"""
Hotload (Weight Hot-Swapping) Helpers.

Hotloading lets you update a deployed model's weights without restarting the
deployment. This is essential for RL training where the sampling policy needs
to stay in sync with the training policy.

How it works:
1. Trainer saves a checkpoint (via save_weights_for_sampler)
2. You call hotload_load_model to tell the deployment to load that checkpoint
3. The deployment downloads the checkpoint and swaps the weights in-place
4. wait_for_hotload_ready polls until the swap is complete

Checkpoint types:
- **Base (full)**: Complete model weights. First checkpoint must be base.
- **Delta (incremental)**: Only the diff from a previous base checkpoint.
  Much smaller and faster to transfer. Uses XOR compression + zstd.

For delta hotloads, you must provide incremental_snapshot_metadata:
    {
        "previous_snapshot_identity": "name-of-base-checkpoint",
        "compression_format": "arc_v2",
        "checksum_format": "alder32"
    }

Copyright (c) Fireworks AI, Inc. and affiliates.
"""

from __future__ import annotations

import time
from typing import Any

import httpx

from . import log, warn


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
    """Tell a deployment to load a new model snapshot (checkpoint).

    This triggers the deployment to download and load the specified checkpoint.
    The checkpoint must already be saved (done by save_weights_for_sampler).

    For base (full) checkpoints: just pass the snapshot_identity.
    For delta (incremental) checkpoints: also pass incremental_snapshot_metadata
    with the previous base checkpoint's identity.

    Args:
        snapshot_identity: Name of the checkpoint to load (e.g., "online-step-5")
        incremental_snapshot_metadata: Required for delta checkpoints. Must include
            previous_snapshot_identity, compression_format, and checksum_format.

    Returns:
        API response dict
    """
    url = f"{hotload_api_url}/hot_load/v1/models/hot_load"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "fireworks-model": base_model,
        "fireworks-deployment": f"accounts/{account_id}/deployments/{deployment_id}",
    }
    payload: dict[str, Any] = {"identity": snapshot_identity}

    if incremental_snapshot_metadata:
        payload["incremental_snapshot_metadata"] = incremental_snapshot_metadata
        log(
            f"Hotload: loading DELTA snapshot '{snapshot_identity}' "
            f"(base: {incremental_snapshot_metadata.get('previous_snapshot_identity')}) "
            f"onto deployment '{deployment_id}'..."
        )
    else:
        log(f"Hotload: loading FULL snapshot '{snapshot_identity}' onto deployment '{deployment_id}'...")

    resp = httpx.post(url, headers=headers, json=payload, timeout=timeout)
    if not resp.is_success:
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
    timeout: int = 30,
) -> dict[str, Any]:
    """Check the current hotload status for a deployment.

    Returns replica info including current snapshot identity, loading stage,
    and readiness status.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    url = f"{hotload_api_url}/hot_load/v1/models/hot_load"
    headers["fireworks-model"] = base_model
    headers["fireworks-deployment"] = f"accounts/{account_id}/deployments/{deployment_id}"

    resp = httpx.get(url, headers=headers, timeout=timeout, verify=False)
    resp.raise_for_status()
    return resp.json()


def wait_for_hotload_ready(
    api_key: str,
    account_id: str,
    deployment_id: str,
    base_model: str,
    expected_identity: str,
    hotload_api_url: str = "https://api.fireworks.ai",
    timeout_seconds: int = 400,
    poll_interval: int = 5,
) -> bool:
    """Wait for hotload to complete and verify the correct snapshot is loaded.

    Polls the hotload status API until:
    - The deployment reports readiness=True with the expected snapshot identity
    - An error occurs (returns False)
    - Timeout is reached (returns False)

    Typical hotload times:
    - Base (full) checkpoint: 20-60 seconds depending on model size
    - Delta (incremental) checkpoint: 5-15 seconds

    Returns:
        True if hotload completed successfully, False otherwise
    """
    log(f"Waiting for hotload to complete (identity={expected_identity})...")
    start_time = time.time()

    while time.time() - start_time < timeout_seconds:
        try:
            status = hotload_check_status(api_key, account_id, deployment_id, base_model, hotload_api_url)

            # Response format: {"replicas": [{"current_snapshot_identity": ...,
            #   "loading_state": {"stage": ...}, "readiness": ...}]}
            replicas = status.get("replicas", [])
            if replicas:
                replica = replicas[0]
                current_identity = replica.get("current_snapshot_identity")
                loading_state = replica.get("loading_state", {})
                stage = loading_state.get("stage", "unknown")
                readiness = replica.get("readiness", False)
            else:
                current_identity = status.get("identity") or status.get("current_identity")
                stage = status.get("state", "UNKNOWN")
                readiness = status.get("readiness", False)

            elapsed = int(time.time() - start_time)

            # Hotload complete when readiness=True and identity matches
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
