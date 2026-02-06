#!/usr/bin/env python3
"""
Direct Preference Optimization (DPO) Training via Tinker SDK

This script demonstrates DPO training using the Tinker SDK's forward_backward_custom API.
It's designed as a reference implementation for the Fireworks AI cookbook.

Architecture:
    - Single RLOR trainer server (no separate reference model needed)
    - Reference logprobs cached at initialization (policy = reference initially)
    - Custom loss function computed client-side, gradients sent to server

DPO Algorithm:
    loss = -log(sigmoid(β * margin))
    margin = (π_chosen - π_ref_chosen) - (π_rejected - π_ref_rejected)

    Where π represents sum of log-probabilities over response tokens only.

Checkpointing & Hotload:
    - Supports periodic checkpoint saving during training (--save-interval)
    - Supports delta checkpoints for efficient storage (XOR-based compression)
    - First checkpoint can be base or delta (--first-checkpoint-type), subsequent are delta
    - Automatic hotloading to inference deployment (--hotload-interval)
    - Delta hotloads reference the previous checkpoint (chained deltas)
    - Supports resuming with existing trainers/deployments (--rlor-endpoint)

Usage:
    # Basic training:
    python train_dpo.py \\
        --base-model "Qwen/Qwen3-8B" \\
        --dataset /path/to/preference_data.jsonl

    # With hotload (saves trained weights to inference deployment):
    python train_dpo.py \\
        --base-model "Qwen/Qwen3-8B" \\
        --dataset /path/to/data.jsonl \\
        --create-deployment --hotload-deployment-id "my-dpo-deployment" \\
        --save-sampler --hotload

    # Periodic saves with delta hotloading:
    python train_dpo.py \\
        --base-model "Qwen/Qwen3-8B" \\
        --dataset /path/to/data.jsonl \\
        --hotload-deployment-id "my-deployment" \\
        --save-interval 2 --hotload-interval \\
        --first-checkpoint-type base

Copyright (c) Fireworks AI, Inc. and affiliates.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from typing import Any, Callable, List

import httpx
import tinker
import torch
import torch.nn.functional as F

# Importing fireworks.rl applies the Fireworks compatibility patches to Tinker
# automatically (if Tinker is installed). This adds checkpoint_type support to
# save_weights_for_sampler.
import fireworks.rl  # noqa: F401

# Tinker cookbook helper for datum construction (handles token shifting internally)
from tinker_cookbook.supervised.common import datum_from_tokens_weights

# Import shared utilities
from shared import (
    log,
    warn,
    parse_additional_headers,
    # RLOR
    RlorServiceEndpoint,
    create_rlor_service_job_and_wait,
    delete_rlor_job,
    # Deployment
    DeploymentInfo,
    create_or_get_deployment,
    wait_for_deployment_ready,
    delete_deployment,
    # Hotload
    hotload_load_model,
    hotload_check_status,
    wait_for_hotload_ready,
)

try:
    import wandb

    WANDB_AVAILABLE = True
except ImportError:
    WANDB_AVAILABLE = False


# =============================================================================
# Inference Test
# =============================================================================


def run_inference_test(
    api_key: str,
    base_model: str,
    prompt: str,
    max_tokens: int = 64,
    temperature: float = 0.7,
    api_url: str = "https://api.fireworks.ai",
) -> str | None:
    """Run a quick inference test through the Fireworks API."""
    try:
        url = f"{api_url.rstrip('/')}/inference/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        payload = {
            "model": base_model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        resp = httpx.post(url, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content")
    except Exception as e:
        warn(f"Inference test failed: {e}")
        return None


# =============================================================================
# Dataset Loading
# =============================================================================


def load_preference_dataset(path: str) -> List[dict[str, Any]]:
    """Load preference dataset.

    Supports formats:
    1. {"chosen": {"text": ...}, "rejected": {"text": ...}}
    2. {"chosen": {"messages": [...]}, "rejected": {"messages": [...]}}
    3. {"samples": [...]} with score=1.0 (chosen) and score=0.0 (rejected)
    4. {"input": ..., "preferred_output": ..., "non_preferred_output": ...}
    """
    data = []
    with open(path) as f:
        for line in f:
            row = json.loads(line)

            # Format 1 & 2: Direct chosen/rejected
            if "chosen" in row and "rejected" in row:
                data.append(row)
            # Format 3: Samples with scores
            elif "samples" in row:
                samples = row["samples"]
                chosen = None
                rejected = None
                for s in samples:
                    score = s.get("evals", {}).get("score", s.get("score"))
                    if score == 1.0:
                        chosen = s
                    elif score == 0.0:
                        rejected = s
                if chosen and rejected:
                    data.append({"chosen": chosen, "rejected": rejected})
            # Format 4: input + preferred_output + non_preferred_output (chat messages format)
            elif "preferred_output" in row and "non_preferred_output" in row:
                input_data = row.get("input", {})
                preferred = row["preferred_output"]
                non_preferred = row["non_preferred_output"]

                # Handle input as messages dict or string
                if isinstance(input_data, dict) and "messages" in input_data:
                    input_messages = input_data["messages"]
                elif isinstance(input_data, list):
                    input_messages = input_data
                elif isinstance(input_data, str):
                    input_messages = [{"role": "user", "content": input_data}]
                else:
                    input_messages = []

                # Handle preferred/non_preferred as list of messages or string
                if isinstance(preferred, list):
                    preferred_messages = preferred
                elif isinstance(preferred, str):
                    preferred_messages = [{"role": "assistant", "content": preferred}]
                else:
                    preferred_messages = []

                if isinstance(non_preferred, list):
                    non_preferred_messages = non_preferred
                elif isinstance(non_preferred, str):
                    non_preferred_messages = [{"role": "assistant", "content": non_preferred}]
                else:
                    non_preferred_messages = []

                # Combine into full message sequences
                chosen_messages = input_messages + preferred_messages
                rejected_messages = input_messages + non_preferred_messages

                data.append(
                    {
                        "chosen": {"messages": chosen_messages},
                        "rejected": {"messages": rejected_messages},
                    }
                )

    return data


def extract_text(item: dict[str, Any]) -> str:
    """Extract text from a chosen/rejected item."""
    # Direct text
    if "text" in item:
        return item["text"]

    # Messages format
    if "messages" in item:
        parts = []
        for msg in item["messages"]:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            parts.append(f"<|{role}|>\n{content}")
        return "\n".join(parts)

    return ""


# =============================================================================
# Prompt/Response Detection
# =============================================================================


def find_common_prefix_length(tokens1: List[int], tokens2: List[int]) -> int:
    """Find the length of the longest common prefix between two token lists.

    This identifies the shared prompt between chosen and rejected sequences.
    """
    min_len = min(len(tokens1), len(tokens2))
    for i in range(min_len):
        if tokens1[i] != tokens2[i]:
            return i
    return min_len


# =============================================================================
# DPO Loss Computation
# =============================================================================
#
# DPO (Direct Preference Optimization) loss:
#   loss = -log(sigmoid(β * margin))
#   margin = log_ratio_chosen - log_ratio_rejected
#   log_ratio = sum(policy_logprobs) - sum(reference_logprobs)
#
# Key insight: We only compute loss over RESPONSE tokens (not prompt).
# The reference logprobs are computed once at initialization when policy=reference.
# =============================================================================


def compute_dpo_metrics(
    pi_chosen: float,
    pi_rejected: float,
    ref_chosen: float,
    ref_rejected: float,
    beta: float,
) -> dict[str, float]:
    """Compute DPO metrics (used for printing + WandB)."""
    chosen_log_ratio = pi_chosen - ref_chosen
    rejected_log_ratio = pi_rejected - ref_rejected
    margin = chosen_log_ratio - rejected_log_ratio

    loss = -F.logsigmoid(torch.tensor(beta * margin)).item()
    accuracy = 1.0 if margin > 0 else 0.0

    return {
        "dpo_loss": loss,
        "margin": margin,
        "accuracy": accuracy,
        "chosen_reward": beta * chosen_log_ratio,
        "rejected_reward": beta * rejected_log_ratio,
    }


def make_dpo_loss_fn(
    ref_chosen_logprobs: List[float],
    ref_rejected_logprobs: List[float],
    beta: float,
) -> Callable[[List[tinker.Datum], List[torch.Tensor]], tuple[torch.Tensor, dict[str, float]]]:
    """Create a DPO loss function for forward_backward_custom.

    Uses the tinker-cookbook pattern: weights from datum.loss_fn_inputs["weights"]
    and torch.dot() to compute weighted logprob sums over response tokens only.

    Args:
        ref_chosen_logprobs: Pre-computed reference logprobs for chosen (per-token list)
        ref_rejected_logprobs: Pre-computed reference logprobs for rejected (per-token list)
        beta: DPO temperature parameter
    """
    # Convert reference logprobs to tensors (no grad needed - these are frozen)
    ref_chosen_tensor = torch.tensor(ref_chosen_logprobs, dtype=torch.float32)
    ref_rejected_tensor = torch.tensor(ref_rejected_logprobs, dtype=torch.float32)

    def loss_fn(
        data: List[tinker.Datum],
        logprobs_list: List[torch.Tensor],
    ) -> tuple[torch.Tensor, dict[str, float]]:
        """DPO loss using weights + dot product (tinker-cookbook pattern).

        Args:
            data: List of [chosen_datum, rejected_datum] with loss_fn_inputs["weights"]
            logprobs_list: List of [chosen_logprobs, rejected_logprobs]
        """
        assert len(logprobs_list) == 2, f"Expected 2 sequences, got {len(logprobs_list)}"

        pi_chosen = logprobs_list[0]
        pi_rejected = logprobs_list[1]

        # Get weights from datums (0 for prompt, 1 for response tokens)
        chosen_weights = torch.tensor(data[0].loss_fn_inputs["weights"].data, dtype=torch.float32)
        rejected_weights = torch.tensor(data[1].loss_fn_inputs["weights"].data, dtype=torch.float32)

        # Weighted logprob sums using dot product (response tokens only)
        pi_chosen_sum = torch.dot(pi_chosen.float(), chosen_weights)
        pi_rejected_sum = torch.dot(pi_rejected.float(), rejected_weights)
        ref_chosen_sum = torch.dot(ref_chosen_tensor.float(), chosen_weights)
        ref_rejected_sum = torch.dot(ref_rejected_tensor.float(), rejected_weights)

        # DPO margin and loss
        margin = (pi_chosen_sum - ref_chosen_sum) - (pi_rejected_sum - ref_rejected_sum)
        dpo_loss = -F.logsigmoid(beta * margin)

        # Compute metrics (detached)
        with torch.no_grad():
            margin_val = margin.item()
            loss_val = dpo_loss.item()
            accuracy = 1.0 if margin_val > 0 else 0.0
            chosen_reward = beta * (pi_chosen_sum.item() - ref_chosen_sum.item())
            rejected_reward = beta * (pi_rejected_sum.item() - ref_rejected_sum.item())

        metrics = {
            "dpo_loss": loss_val,
            "margin": margin_val,
            "accuracy": accuracy,
            "chosen_reward": chosen_reward,
            "rejected_reward": rejected_reward,
        }

        return dpo_loss, metrics

    return loss_fn


# =============================================================================
# Main Training
# =============================================================================


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="DPO Training via Tinker SDK")

    # Tinker auth (service endpoint is created via control plane)
    parser.add_argument("--api-key", default="tml-local", help="API key for the trainer's Tinker endpoint")
    parser.add_argument("--base-model", required=True, help="Base model name (e.g., Qwen/Qwen3-8B)")

    # Fireworks control plane
    parser.add_argument("--fireworks-api-key", default=None, help="Defaults to FIREWORKS_API_KEY env var")
    parser.add_argument("--fireworks-account-id", default=None, help="Defaults to FIREWORKS_ACCOUNT_ID env var")
    parser.add_argument("--fireworks-base-url", default=None, help="Defaults to FIREWORKS_BASE_URL env var")
    parser.add_argument(
        "--additional-headers",
        type=str,
        default=None,
        help='Additional HTTP headers as JSON dict, e.g. \'{"X-Custom-Header": "value"}\'. '
        "Defaults to FIREWORKS_ADDITIONAL_HEADERS env var.",
    )
    parser.add_argument("--rlor-node-count", type=int, default=1, help="Trainer node count (default: 1)")
    parser.add_argument(
        "--rlor-display-name", type=str, default=None, help="Optional display name for the trainer job"
    )
    parser.add_argument(
        "--hotload-deployment-id",
        type=str,
        default=None,
        help="Deployment ID for hotload. If --create-deployment is set, this deployment will be created.",
    )
    parser.add_argument(
        "--create-deployment",
        action="store_true",
        help="Create a hotload-enabled deployment before starting the trainer. "
        "Requires --hotload-deployment-id.",
    )
    parser.add_argument(
        "--deployment-shape",
        type=str,
        default=None,
        help="Deployment shape (e.g., accounts/fireworks/deploymentShapes/rft-qwen3-0p6b).",
    )
    parser.add_argument(
        "--deployment-timeout-s",
        type=float,
        default=600,
        help="Timeout for deployment readiness (seconds, default: 600)",
    )
    parser.add_argument(
        "--skip-validations",
        action="store_true",
        help="[RECOMMENDED for hotload] Skip RLOR job validations.",
    )
    parser.add_argument(
        "--custom-image-tag",
        type=str,
        default=None,
        help="Custom trainer image tag.",
    )
    parser.add_argument(
        "--trainer-extra-args",
        type=str,
        default=None,
        help="Extra arguments to pass to the trainer (SUPERUSER_ONLY). "
        'Examples: --trainer-extra-args "--pp 2 --activation-checkpoint full"',
    )
    parser.add_argument(
        "--rlor-timeout-s", type=float, default=15 * 60, help="Timeout for trainer readiness (seconds)"
    )
    parser.add_argument(
        "--rlor-poll-interval-s", type=float, default=5.0, help="Polling interval for trainer readiness (seconds)"
    )
    parser.add_argument(
        "--rlor-endpoint",
        type=str,
        default=None,
        help="Use an existing RLOR trainer endpoint directly. Skips RLOR job creation.",
    )
    parser.add_argument(
        "--region",
        type=str,
        default=None,
        help="Region for trainer (e.g., US_OHIO_1, US_VIRGINIA_1)",
    )
    parser.add_argument(
        "--deployment-region",
        type=str,
        default=None,
        help="Region for the inference deployment (used only with --create-deployment).",
    )
    parser.add_argument(
        "--accelerator-type",
        type=str,
        default=None,
        help="Accelerator type (e.g., NVIDIA_B200_180GB, NVIDIA_H100_80GB)",
    )
    parser.add_argument(
        "--accelerator-count",
        type=int,
        default=None,
        help="Number of accelerators per node (e.g., 8)",
    )
    parser.add_argument(
        "--hot-load-bucket-type",
        type=str,
        default="FW_HOSTED",
        choices=["MINIO", "S3", "NEBIUS", "FW_HOSTED"],
        help="Hotload bucket type (default: FW_HOSTED).",
    )

    # Dataset
    parser.add_argument("--dataset", required=True, help="Path to preference dataset (JSONL)")
    parser.add_argument("--max-examples", type=int, default=None, help="Deprecated, use --max-pairs instead.")
    parser.add_argument("--max-pairs", type=int, default=None, help="Max number of VALID (chosen,rejected) pairs.")
    parser.add_argument("--max-seq-len", type=int, default=4096, help="Max sequence length (default: 4096)")

    # Training hyperparameters
    parser.add_argument("--beta", type=float, default=0.1, help="DPO beta parameter (default: 0.1)")
    parser.add_argument("--lr", type=float, default=1e-5, help="Learning rate (default: 1e-5)")
    parser.add_argument("--epochs", type=int, default=1, help="Number of epochs (default: 1)")
    parser.add_argument("--grad-accum", type=int, default=4, help="Gradient accumulation steps (default: 4)")
    parser.add_argument("--lora-rank", type=int, default=0, help="LoRA rank (default: 0 = full fine-tuning)")

    # Logging
    parser.add_argument("--log-interval", type=int, default=1, help="Log every N optimizer steps (default: 1)")
    parser.add_argument("--wandb-entity", type=str, default=None, help="WandB entity (username or team)")
    parser.add_argument("--wandb-project", type=str, default="dpo-tinker", help="WandB project name")
    parser.add_argument("--wandb-run-name", type=str, default=None, help="WandB run name")

    # Checkpointing and hotload
    parser.add_argument("--save-sampler", action="store_true", help="Save sampler weights at end of training.")
    parser.add_argument("--sampler-name", type=str, default=None, help="Sampler checkpoint name (default: auto)")
    parser.add_argument("--save-interval", type=int, default=0, help="Save checkpoint every N optimizer steps (0 = only at end).")
    parser.add_argument("--hotload-interval", action="store_true", help="Hotload each checkpoint saved by --save-interval.")
    parser.add_argument(
        "--first-checkpoint-type",
        type=str,
        choices=["base", "delta"],
        default="base",
        help="Type for the FIRST checkpoint save. 'base' = full save (default), 'delta' = incremental.",
    )
    parser.add_argument("--hotload", action="store_true", help="After saving sampler weights, hotload them onto the deployment.")
    parser.add_argument("--inference-prompt", type=str, default=None, help="Run a quick inference test after hotload.")
    parser.add_argument("--hotload-api-url", type=str, default="https://api.fireworks.ai", help="Hotload API URL")
    parser.add_argument("--hotload-timeout", type=int, default=120, help="Timeout for hotload to complete (seconds)")
    parser.add_argument("--dry-run", action="store_true", help="Show what checkpoints would be saved, then exit.")

    # Cleanup
    parser.add_argument("--cleanup-rlor-job", action="store_true", help="Delete the RLOR trainer job after training")
    parser.add_argument("--cleanup-deployment", action="store_true", help="Delete the deployment after training")

    return parser.parse_args()


def _cleanup_resources(
    api_key: str | None,
    account_id: str | None,
    base_url: str,
    additional_headers: dict | None,
    rlor_job_id: str | None,
    deployment_id: str | None,
) -> None:
    """Clean up created resources on failure."""
    if not api_key or not account_id:
        warn("Cannot cleanup: missing API key or account ID")
        return

    log("\n[CLEANUP] Cleaning up resources due to failure...")

    if rlor_job_id:
        log(f"  Deleting RLOR trainer job: {rlor_job_id}")
        try:
            delete_rlor_job(api_key, account_id, base_url, additional_headers, rlor_job_id)
            log(f"  Successfully deleted RLOR job: {rlor_job_id}")
        except Exception as e:
            warn(f"  Failed to delete RLOR job {rlor_job_id}: {e}")

    if deployment_id:
        log(f"  Deleting deployment: {deployment_id}")
        try:
            delete_deployment(api_key, account_id, base_url, additional_headers, deployment_id)
            log(f"  Successfully deleted deployment: {deployment_id}")
        except Exception as e:
            warn(f"  Failed to delete deployment {deployment_id}: {e}")


def main():
    """DPO training loop.

    Overall flow:
    1. Load preference dataset (chosen/rejected pairs)
    2. Optionally create a hotload-enabled deployment
    3. Create a single RLOR trainer job
    4. Compute reference logprobs (policy = reference at init, so one forward pass)
    5. Training loop: for each (chosen, rejected) pair:
       a. Create datums with weights (response tokens only)
       b. Compute DPO loss via forward_backward_custom
       c. Accumulate gradients, then optim_step
    6. Save final checkpoint and optionally hotload to deployment

    DPO only needs one trainer (not two like GRPO) because the reference
    logprobs are cached at initialization when policy = reference.
    """
    args = parse_args()

    # Handle --max-examples as deprecated alias for --max-pairs
    if args.max_examples is not None:
        if args.max_pairs is not None:
            warn("Both --max-examples and --max-pairs specified; using --max-pairs")
        else:
            warn("--max-examples is deprecated, use --max-pairs instead")
            args.max_pairs = args.max_examples

    log(f"Starting DPO training: {args}")

    # Validate flag combinations
    if args.hotload or args.save_sampler:
        if not args.hotload_deployment_id:
            raise RuntimeError("--hotload or --save-sampler requires --hotload-deployment-id")
        if not args.skip_validations:
            warn("HINT: --skip-validations is recommended for hotload workflows.")

    if args.hotload_interval:
        if args.save_interval <= 0:
            raise RuntimeError("--hotload-interval requires --save-interval > 0")
        if not args.hotload_deployment_id:
            raise RuntimeError("--hotload-interval requires --hotload-deployment-id")

    # Track created resources for cleanup
    created_rlor_job_id: str | None = None
    created_deployment: bool = False
    resources_ready: bool = False
    training_succeeded: bool = False
    rlor_base_url: str | None = None

    # Initialize WandB
    use_wandb = WANDB_AVAILABLE and args.wandb_entity is not None
    if use_wandb:
        wandb.init(
            entity=args.wandb_entity,
            project=args.wandb_project,
            name=args.wandb_run_name,
            config={
                "beta": args.beta,
                "lr": args.lr,
                "epochs": args.epochs,
                "grad_accum": args.grad_accum,
                "max_seq_len": args.max_seq_len,
                "lora_rank": args.lora_rank,
                "dataset": args.dataset,
            },
        )
        if wandb.run is not None:
            log(f"WandB: {wandb.run.url}")
        else:
            log(f"WandB initialized: {args.wandb_entity}/{args.wandb_project}")
    elif args.wandb_entity:
        warn("WandB requested but not available. Install with: pip install wandb")

    fw_api_key = args.fireworks_api_key or os.environ.get("FIREWORKS_API_KEY")
    fw_account_id = args.fireworks_account_id or os.environ.get("FIREWORKS_ACCOUNT_ID")
    additional_headers_json = args.additional_headers or os.environ.get("FIREWORKS_ADDITIONAL_HEADERS")
    additional_headers = parse_additional_headers(additional_headers_json)
    fw_base_url = args.fireworks_base_url or os.environ.get("FIREWORKS_BASE_URL") or "https://api.fireworks.ai"

    # Validate credentials
    if not args.rlor_endpoint:
        if not fw_api_key or not fw_account_id:
            raise RuntimeError(
                "To create an RLOR trainer job, set FIREWORKS_API_KEY and FIREWORKS_ACCOUNT_ID "
                "(or pass --fireworks-api-key / --fireworks-account-id). "
                "Alternatively, use --rlor-endpoint to connect to an existing trainer."
            )

    # Load and validate dataset
    log("\n[0/4] Loading and validating dataset...")
    raw_data = load_preference_dataset(args.dataset)

    if not raw_data:
        raise RuntimeError(f"No data loaded from {args.dataset}!")

    valid_text_count = 0
    empty_text_count = 0
    for i, example in enumerate(raw_data):
        chosen_text = extract_text(example["chosen"])
        rejected_text = extract_text(example["rejected"])
        if chosen_text and rejected_text:
            valid_text_count += 1
        else:
            empty_text_count += 1
            if empty_text_count <= 3:
                warn(f"  Example {i}: empty chosen or rejected text")

    if valid_text_count == 0:
        raise RuntimeError(f"No valid examples found! All {len(raw_data)} examples have empty text.")

    log(f"  Loaded {len(raw_data)} examples, {valid_text_count} have extractable text")

    # Initialize checkpoint tracking
    hotload_deployment_id = args.hotload_deployment_id
    base_checkpoint_saved = False
    base_checkpoint_identity: str | None = None
    step_offset = 0

    try:
        if args.create_deployment:
            if not hotload_deployment_id:
                raise RuntimeError("--create-deployment requires --hotload-deployment-id")

            log("\n[1/5] Creating hotload-enabled deployment...")
            deployment_region = args.deployment_region or args.region or "US_VIRGINIA_1"
            deployment_info = create_or_get_deployment(
                api_key=fw_api_key,
                account_id=fw_account_id,
                base_url=fw_base_url,
                additional_headers=additional_headers,
                deployment_id=hotload_deployment_id,
                base_model=args.base_model,
                deployment_shape=args.deployment_shape,
                region=deployment_region,
                accelerator_type=args.accelerator_type,
                hot_load_bucket_type=args.hot_load_bucket_type,
            )
            created_deployment = True

            if deployment_info.state != "READY":
                deployment_info = wait_for_deployment_ready(
                    api_key=fw_api_key,
                    account_id=fw_account_id,
                    base_url=fw_base_url,
                    additional_headers=additional_headers,
                    deployment_id=hotload_deployment_id,
                    timeout_s=args.deployment_timeout_s,
                )

            log(f"  Deployment ready: {deployment_info.name}")
            if not deployment_info.hot_load_bucket_url:
                warn("  ⚠️  WARNING: Deployment has no hotLoadBucketUrl configured!")

        # Create or connect to RLOR Trainer
        if args.rlor_endpoint:
            log("\n[2/5] Using existing RLOR trainer endpoint...")
            rlor_base_url = args.rlor_endpoint.rstrip("/")
            if rlor_base_url.startswith("http://"):
                rlor_base_url = "https://" + rlor_base_url[7:]
            elif not rlor_base_url.startswith("https://"):
                rlor_base_url = "https://" + rlor_base_url
            log(f"  Trainer endpoint: {rlor_base_url}")

            try:
                r = httpx.get(f"{rlor_base_url}/api/v1/healthz", timeout=10)
                if r.status_code == 200:
                    log("  Trainer endpoint is healthy")
                else:
                    warn(f"  Trainer endpoint returned status {r.status_code}")
            except Exception as e:
                warn(f"  Could not verify trainer endpoint health: {e}")
        else:
            log("\n[2/5] Creating RLOR trainer job...")
            endpoint = create_rlor_service_job_and_wait(
                api_key=fw_api_key,
                account_id=fw_account_id,
                base_url=fw_base_url,
                additional_headers=additional_headers,
                base_model=args.base_model,
                lora_rank=args.lora_rank,
                max_context_length=args.max_seq_len,
                learning_rate=args.lr,
                gradient_accumulation_steps=args.grad_accum,
                node_count=args.rlor_node_count,
                display_name=args.rlor_display_name,
                hot_load_deployment_id=hotload_deployment_id,
                region=args.region,
                skip_validations=args.skip_validations,
                custom_image_tag=args.custom_image_tag,
                extra_args=args.trainer_extra_args.split() if args.trainer_extra_args else None,
                poll_interval_s=args.rlor_poll_interval_s,
                timeout_s=args.rlor_timeout_s,
            )
            rlor_base_url = endpoint.base_url
            created_rlor_job_id = endpoint.job_id
            log(f"  Trainer ready: {endpoint.job_id}")

        # Create Tinker SDK client
        service = tinker.ServiceClient(base_url=rlor_base_url, api_key=args.api_key)
        training_client = service.create_lora_training_client(
            base_model=args.base_model,
            rank=args.lora_rank,
        )
        resources_ready = True

        log("\n  Note: Using auto checkpoint_type - trainer will save base if none exists")

        # Check current hotload status (for resume scenarios)
        if args.hotload_deployment_id and (args.hotload or args.hotload_interval):
            log("\n  Checking current hotload status on deployment...")
            try:
                current_status = hotload_check_status(
                    api_key=fw_api_key,
                    account_id=fw_account_id,
                    deployment_id=args.hotload_deployment_id,
                    base_model=args.base_model,
                    hotload_api_url=args.hotload_api_url,
                )
                replicas = current_status.get("replicas", [])
                if replicas:
                    replica = replicas[0]
                    current_identity = replica.get("current_snapshot_identity")
                    readiness = replica.get("readiness", False)
                    if current_identity and readiness:
                        log(f"  Deployment has snapshot loaded: {current_identity}")
                        base_checkpoint_identity = current_identity
                        log(f"  Deployment base for delta hotloads: {base_checkpoint_identity}")
                        step_match = re.search(r"checkpoint_step_(\d+)", current_identity)
                        if step_match:
                            step_offset = int(step_match.group(1))
                            log(f"  New checkpoints will start from step {step_offset + 1}")
                    else:
                        log(f"  Deployment ready={readiness}, identity={current_identity}")
                else:
                    log("  No replica status available")
            except Exception as e:
                warn(f"  Could not check hotload status: {e}")
                log("  Will start with base checkpoint saves")

        # Dry-run mode
        if args.dry_run:
            log("\n" + "=" * 70)
            log("DRY RUN MODE - Checkpoint Planning")
            log("=" * 70)
            log(f"\nCurrent state:")
            log(f"  Base checkpoint saved: {base_checkpoint_saved}")
            log(f"  Base checkpoint identity: {base_checkpoint_identity or '(none)'}")
            log(f"  Step offset: {step_offset}")
            log(f"\nTraining configuration:")
            log(f"  Max pairs: {args.max_pairs or 'all'}")
            log(f"  Grad accumulation: {args.grad_accum}")
            log(f"  Save interval: {args.save_interval}")
            log(f"  Hotload interval: {args.hotload_interval}")
            if args.max_pairs:
                estimated_steps = args.max_pairs // args.grad_accum
            else:
                estimated_steps = len(raw_data) // args.grad_accum
            log(f"  Estimated total steps: {estimated_steps}")
            log(f"\nExpected checkpoints (--first-checkpoint-type={args.first_checkpoint_type}):")
            first_save_done = False
            if args.save_interval > 0:
                for s in range(args.save_interval, estimated_steps + 1, args.save_interval):
                    ckpt_name = f"checkpoint_step_{s + step_offset}"
                    if not first_save_done:
                        ckpt_type = args.first_checkpoint_type
                        first_save_done = True
                    else:
                        ckpt_type = "delta"
                    log(f"  Step {s} -> {ckpt_name} (type={ckpt_type})")
            final_name = f"final_sampler_step_{estimated_steps + step_offset}"
            final_type = "delta" if first_save_done else args.first_checkpoint_type
            log(f"\nFinal checkpoint: {final_name} (type={final_type})")
            log("\n" + "=" * 70)
            log("DRY RUN COMPLETE - No training performed")
            log("=" * 70)
            return

        # Use the RLOR trainer's tokenizer endpoint
        log("  Using Fireworks RLOR trainer's tokenizer endpoint")

        def encode_text_fn(text: str) -> list[int]:
            """Encode text using the Fireworks RLOR trainer's tokenizer endpoint."""
            resp = httpx.post(
                f"{rlor_base_url}/api/v1/tokenizer/encode",
                json={"text": text},
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()["tokens"]

        # Compute reference logprobs — since the policy hasn't been trained yet,
        # it's identical to the reference model. We do one forward pass per example
        # to cache the reference logprobs, then use them throughout training.
        log("\n[3/5] Computing reference logprobs...")
        ref_cache: dict[int, dict[str, Any]] = {}
        skipped_empty = 0
        skipped_too_long = 0
        skipped_too_short = 0
        target_pairs = None
        if args.max_pairs is not None:
            if args.max_pairs <= 0:
                raise ValueError("--max-pairs must be > 0")
            target_pairs = args.max_pairs

        for i, example in enumerate(raw_data):
            chosen_text = extract_text(example["chosen"])
            rejected_text = extract_text(example["rejected"])

            if not chosen_text or not rejected_text:
                skipped_empty += 1
                if skipped_empty <= 3:
                    warn(f"  Example {i}: empty text")
                continue

            chosen_tokens = encode_text_fn(chosen_text)
            rejected_tokens = encode_text_fn(rejected_text)

            if len(chosen_tokens) > args.max_seq_len or len(rejected_tokens) > args.max_seq_len:
                skipped_too_long += 1
                if skipped_too_long <= 3:
                    warn(f"  Example {i}: too long")
                continue

            if len(chosen_tokens) < 2 or len(rejected_tokens) < 2:
                skipped_too_short += 1
                if skipped_too_short <= 3:
                    warn(f"  Example {i}: too short")
                continue

            prompt_len = find_common_prefix_length(chosen_tokens, rejected_tokens)

            # Build weights: 0 for prompt, 1 for response (tinker-cookbook pattern)
            chosen_weights = torch.zeros(len(chosen_tokens), dtype=torch.float32)
            chosen_weights[prompt_len:] = 1.0
            rejected_weights = torch.zeros(len(rejected_tokens), dtype=torch.float32)
            rejected_weights[prompt_len:] = 1.0

            # datum_from_tokens_weights handles shifting internally
            chosen_datum = datum_from_tokens_weights(
                torch.tensor(chosen_tokens, dtype=torch.long), chosen_weights, max_length=args.max_seq_len,
            )
            rejected_datum = datum_from_tokens_weights(
                torch.tensor(rejected_tokens, dtype=torch.long), rejected_weights, max_length=args.max_seq_len,
            )

            fwd_result = training_client.forward([chosen_datum, rejected_datum], "cross_entropy").result()
            ref_chosen = fwd_result.loss_fn_outputs[0]["logprobs"].data
            ref_rejected = fwd_result.loss_fn_outputs[1]["logprobs"].data

            ref_cache[i] = {
                "chosen_tokens": chosen_tokens,
                "rejected_tokens": rejected_tokens,
                "ref_chosen": ref_chosen,
                "ref_rejected": ref_rejected,
                "prompt_len": prompt_len,
            }

            if target_pairs is not None and len(ref_cache) >= target_pairs:
                break

        valid_indices = list(ref_cache.keys())
        total_skipped = skipped_empty + skipped_too_long + skipped_too_short
        log(f"  Prepared {len(valid_indices)} preference pairs (skipped {total_skipped})")
        if not valid_indices:
            raise RuntimeError("No valid examples!")

        # Training Loop
        log(f"\n[4/5] Training: {args.epochs} epoch(s), {len(valid_indices)} pairs, β={args.beta}, lr={args.lr}")
        total_steps = len(valid_indices) * args.epochs // args.grad_accum
        step = 0

        # Compute initial loss
        init_metrics = {"dpo_loss": 0.0, "margin": 0.0, "accuracy": 0.0}
        num_eval = min(50, len(valid_indices))
        for idx in valid_indices[:num_eval]:
            cached = ref_cache[idx]
            prompt_len = cached.get("prompt_len", 0)
            chosen_tokens = cached["chosen_tokens"]
            rejected_tokens = cached["rejected_tokens"]

            # Build weights + datums (tinker-cookbook pattern)
            chosen_weights = torch.zeros(len(chosen_tokens), dtype=torch.float32)
            chosen_weights[prompt_len:] = 1.0
            rejected_weights = torch.zeros(len(rejected_tokens), dtype=torch.float32)
            rejected_weights[prompt_len:] = 1.0
            chosen_datum = datum_from_tokens_weights(
                torch.tensor(chosen_tokens, dtype=torch.long), chosen_weights, max_length=args.max_seq_len,
            )
            rejected_datum = datum_from_tokens_weights(
                torch.tensor(rejected_tokens, dtype=torch.long), rejected_weights, max_length=args.max_seq_len,
            )

            fwd_result = training_client.forward([chosen_datum, rejected_datum], "cross_entropy").result()
            pi_chosen_list = fwd_result.loss_fn_outputs[0]["logprobs"].data
            pi_rejected_list = fwd_result.loss_fn_outputs[1]["logprobs"].data

            # Use dot product with weights for response-only sums
            c_w = torch.tensor(chosen_datum.loss_fn_inputs["weights"].data, dtype=torch.float32)
            r_w = torch.tensor(rejected_datum.loss_fn_inputs["weights"].data, dtype=torch.float32)
            pi_chosen = torch.dot(torch.tensor(pi_chosen_list, dtype=torch.float32), c_w).item()
            pi_rejected = torch.dot(torch.tensor(pi_rejected_list, dtype=torch.float32), r_w).item()
            ref_chosen_val = torch.dot(torch.tensor(cached["ref_chosen"], dtype=torch.float32), c_w).item()
            ref_rejected_val = torch.dot(torch.tensor(cached["ref_rejected"], dtype=torch.float32), r_w).item()
            metrics = compute_dpo_metrics(pi_chosen, pi_rejected, ref_chosen_val, ref_rejected_val, args.beta)
            init_metrics["dpo_loss"] += metrics["dpo_loss"]
            init_metrics["margin"] += metrics["margin"]
            init_metrics["accuracy"] += metrics["accuracy"]

        init_loss = init_metrics["dpo_loss"] / num_eval
        init_margin = init_metrics["margin"] / num_eval
        init_acc = init_metrics["accuracy"] / num_eval
        log(f"Step 0 (INITIAL) | Loss: {init_loss:.4f} | Margin: {init_margin:+.4f} | Acc: {init_acc:.2%}")

        if use_wandb:
            wandb.log({"train/dpo_loss": init_loss, "train/margin": init_margin, "train/accuracy": init_acc, "train/step": 0}, step=0)

        for epoch in range(args.epochs):
            epoch_metrics = {"dpo_loss": 0.0, "margin": 0.0, "accuracy": 0.0}
            accum_count = 0

            for idx in valid_indices:
                cached = ref_cache[idx]
                prompt_len = cached["prompt_len"]
                chosen_tokens = cached["chosen_tokens"]
                rejected_tokens = cached["rejected_tokens"]

                # Build weights + datums (tinker-cookbook pattern)
                chosen_weights = torch.zeros(len(chosen_tokens), dtype=torch.float32)
                chosen_weights[prompt_len:] = 1.0
                rejected_weights = torch.zeros(len(rejected_tokens), dtype=torch.float32)
                rejected_weights[prompt_len:] = 1.0
                chosen_datum = datum_from_tokens_weights(
                    torch.tensor(chosen_tokens, dtype=torch.long), chosen_weights, max_length=args.max_seq_len,
                )
                rejected_datum = datum_from_tokens_weights(
                    torch.tensor(rejected_tokens, dtype=torch.long), rejected_weights, max_length=args.max_seq_len,
                )
                data_pair = [chosen_datum, rejected_datum]

                loss_fn = make_dpo_loss_fn(
                    ref_chosen_logprobs=cached["ref_chosen"],
                    ref_rejected_logprobs=cached["ref_rejected"],
                    beta=args.beta,
                )

                result = training_client.forward_backward_custom(data_pair, loss_fn).result()
                metrics = result.metrics
                epoch_metrics["dpo_loss"] += metrics["dpo_loss"]
                epoch_metrics["margin"] += metrics["margin"]
                epoch_metrics["accuracy"] += metrics["accuracy"]
                accum_count += 1

                if accum_count >= args.grad_accum:
                    training_client.optim_step(
                        tinker.AdamParams(learning_rate=args.lr, beta1=0.9, beta2=0.999, eps=1e-8, weight_decay=0.01)
                    ).result()
                    step += 1

                    if step % args.log_interval == 0:
                        avg_loss = epoch_metrics["dpo_loss"] / accum_count
                        avg_margin = epoch_metrics["margin"] / accum_count
                        avg_acc = epoch_metrics["accuracy"] / accum_count
                        log(f"Step {step}/{total_steps} | Loss: {avg_loss:.4f} | Margin: {avg_margin:+.4f} | Acc: {avg_acc:.2%} | LR: {args.lr:.2e}")
                        if use_wandb:
                            wandb.log({"train/dpo_loss": avg_loss, "train/margin": avg_margin, "train/accuracy": avg_acc, "train/step": step}, step=step)

                    # Periodic checkpoint saving
                    if args.save_interval > 0 and step % args.save_interval == 0:
                        ckpt_name = f"checkpoint_step_{step + step_offset}"
                        ckpt_type = "delta" if base_checkpoint_saved else args.first_checkpoint_type
                        log(f"  Saving periodic checkpoint: {ckpt_name} (type={ckpt_type})")
                        try:
                            training_client.save_weights_for_sampler(ckpt_name, checkpoint_type=ckpt_type).result()
                            actual_ckpt_type = ckpt_type
                            if not base_checkpoint_saved:
                                base_checkpoint_saved = True
                                if actual_ckpt_type == "base":
                                    base_checkpoint_identity = ckpt_name
                            log(f"  Checkpoint saved: {ckpt_name} (type={actual_ckpt_type})")

                            if args.hotload_interval and args.hotload_deployment_id:
                                try:
                                    incremental_metadata = None
                                    if actual_ckpt_type == "delta" and base_checkpoint_identity:
                                        incremental_metadata = {
                                            "previous_snapshot_identity": base_checkpoint_identity,
                                            "compression_format": "xor_one_to_one_zstd",
                                            "checksum_format": "alder32",
                                        }
                                    hotload_load_model(
                                        api_key=fw_api_key, account_id=fw_account_id,
                                        deployment_id=args.hotload_deployment_id, base_model=args.base_model,
                                        snapshot_identity=ckpt_name, hotload_api_url=args.hotload_api_url,
                                        incremental_snapshot_metadata=incremental_metadata,
                                    )
                                    hotload_success = wait_for_hotload_ready(
                                        api_key=fw_api_key, account_id=fw_account_id,
                                        deployment_id=args.hotload_deployment_id, base_model=args.base_model,
                                        expected_identity=ckpt_name, hotload_api_url=args.hotload_api_url,
                                        timeout_seconds=args.hotload_timeout,
                                    )
                                    if hotload_success:
                                        base_checkpoint_identity = ckpt_name
                                    else:
                                        warn(f"  Hotload failed for {ckpt_name}")
                                except Exception as e:
                                    warn(f"  Hotload error: {e}")
                        except Exception as e:
                            warn(f"  Failed to save checkpoint: {e}")

                    epoch_metrics = {"dpo_loss": 0.0, "margin": 0.0, "accuracy": 0.0}
                    accum_count = 0

            if accum_count > 0:
                training_client.optim_step(
                    tinker.AdamParams(learning_rate=args.lr, beta1=0.9, beta2=0.999, eps=1e-8, weight_decay=0.01)
                ).result()
                step += 1

        log(f"\nTraining complete: {step} optimizer steps")
        training_succeeded = True

        # Save and hotload
        if args.save_sampler:
            sampler_name = args.sampler_name or f"final_sampler_step_{step + step_offset}"
            final_ckpt_type = "delta" if base_checkpoint_saved else args.first_checkpoint_type
            log(f"\nSaving final weights: {sampler_name} (type={final_ckpt_type})")
            try:
                sampler_result = training_client.save_weights_for_sampler(sampler_name, checkpoint_type=final_ckpt_type).result()
                result_path = sampler_result.path
                log(f"  Saved to: {result_path} (type={final_ckpt_type})")

                if not base_checkpoint_saved:
                    base_checkpoint_saved = True
                    if final_ckpt_type == "base":
                        base_checkpoint_identity = sampler_name

                if args.hotload and args.hotload_deployment_id:
                    try:
                        incremental_metadata: dict[str, Any] | None = None
                        if final_ckpt_type == "delta" and base_checkpoint_identity:
                            incremental_metadata = {
                                "previous_snapshot_identity": base_checkpoint_identity,
                                "compression_format": "xor_one_to_one_zstd",
                                "checksum_format": "alder32",
                            }
                        hotload_load_model(
                            api_key=fw_api_key, account_id=fw_account_id,
                            deployment_id=args.hotload_deployment_id, base_model=args.base_model,
                            snapshot_identity=sampler_name, hotload_api_url=args.hotload_api_url,
                            incremental_snapshot_metadata=incremental_metadata,
                        )
                        hotload_success = wait_for_hotload_ready(
                            api_key=fw_api_key, account_id=fw_account_id,
                            deployment_id=args.hotload_deployment_id, base_model=args.base_model,
                            expected_identity=sampler_name, hotload_api_url=args.hotload_api_url,
                            timeout_seconds=args.hotload_timeout,
                        )
                        if not hotload_success:
                            warn("Hotload did not complete successfully")
                        if args.inference_prompt:
                            log("\nRunning inference test...")
                            result = run_inference_test(
                                api_key=fw_api_key, base_model=args.base_model,
                                prompt=args.inference_prompt, api_url=args.hotload_api_url,
                            )
                            if result:
                                log(f"Response: {result}")
                    except Exception as e:
                        warn(f"Hotload failed: {e}")
            except Exception as e:
                warn(f"Failed to save weights: {e}")

        if use_wandb:
            wandb.finish()

    except Exception as e:
        log(f"\n[ERROR] Training failed: {e}")
        raise
    finally:
        if not resources_ready and (created_rlor_job_id or created_deployment):
            _cleanup_resources(
                api_key=fw_api_key, account_id=fw_account_id, base_url=fw_base_url,
                additional_headers=additional_headers, rlor_job_id=created_rlor_job_id,
                deployment_id=hotload_deployment_id if created_deployment else None,
            )
        elif resources_ready:
            if training_succeeded:
                log("\n" + "=" * 70)
                log("TRAINING COMPLETED SUCCESSFULLY")
                log("=" * 70)
            else:
                log("\n" + "=" * 70)
                log("TRAINING FAILED - Resources kept for retry")
                log("=" * 70)

            log("\n[REUSE] To run again with existing resources, add these flags:")
            if rlor_base_url:
                log(f"  --rlor-endpoint {rlor_base_url}")
            if hotload_deployment_id:
                log(f"  --hotload-deployment-id {hotload_deployment_id}")

    # Cleanup if requested
    if args.cleanup_rlor_job and created_rlor_job_id:
        log(f"\nCleaning up RLOR job: {created_rlor_job_id}")
        try:
            delete_rlor_job(fw_api_key, fw_account_id, fw_base_url, additional_headers, created_rlor_job_id)
            log(f"  Successfully deleted RLOR job: {created_rlor_job_id}")
        except Exception as e:
            warn(f"Failed to delete RLOR job: {e}")

    if args.cleanup_deployment and args.create_deployment and hotload_deployment_id:
        log(f"\nCleaning up deployment: {hotload_deployment_id}")
        try:
            delete_deployment(fw_api_key, fw_account_id, fw_base_url, additional_headers, hotload_deployment_id)
            log(f"  Successfully deleted deployment: {hotload_deployment_id}")
        except Exception as e:
            warn(f"Failed to delete deployment: {e}")


if __name__ == "__main__":
    main()
