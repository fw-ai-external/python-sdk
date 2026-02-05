#!/usr/bin/env python3
"""
GRPO (Group Relative Policy Optimization) Training via Tinker SDK - OFF-POLICY

This script runs OFF-POLICY GRPO training using the Tinker SDK and control plane.
Unlike the on-policy version, this hotloads at intervals (not every step) and uses
importance sampling to correct for the mismatch between sampling and training policies.

Architecture:
    - Policy RLOR job: forward_backward + optim_step (trainable)
    - Reference RLOR job: forward only (frozen, for KL)
    - Deployment: sampling (chat completions) and hotload at intervals

GRPO Algorithm (Off-Policy with Importance Sampling):
    advantage = (r - mean_r) / (std_r + eps)
    rho = exp(log_pi_current - log_pi_behavior)  # importance ratio
    loss = rho * (-advantage * sum(response_logprobs) + kl_beta * KL(policy || reference))
    
    Off-policy: hotload at intervals (e.g., every 10 steps).
    Uses importance sampling to correct for stale samples.

Usage:
    python examples/rl/train_grpo_off_policy.py \\
        --base-model "accounts/fireworks/models/qwen3-8b" \\
        --dataset /path/to/gsm8k.jsonl \\
        --create-deployment --hotload-deployment-id "grpo-test" \\
        --hotload-interval 10 \\
        --save-sampler --hotload --skip-validations

Copyright (c) Fireworks AI, Inc. and affiliates.
"""

from __future__ import annotations

import argparse
import atexit
import json
import os
import pdb
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Tuple

import httpx
import tinker
import torch

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
    wait_for_hotload_ready,
    # Dataset
    evaluate_gsm8k_response,
    load_gsm8k_dataset,
    # Tokenizer
    encode_text,
)

try:
    import wandb

    WANDB_AVAILABLE = True
except ImportError:
    WANDB_AVAILABLE = False


# =============================================================================
# GRPO Loss Function for forward_backward_custom (Off-Policy with Importance Sampling)
# =============================================================================


def make_grpo_loss_fn(
    rewards: List[float],
    ref_logprobs_list: List[List[float]],
    behavior_logprobs_list: List[List[float]],
    kl_beta: float = 0.001,
    clip_rho: float = 10.0,
    eps: float = 1e-8,
    debug: bool = False,
) -> Callable[[List[tinker.Datum], List[torch.Tensor]], Tuple[torch.Tensor, Dict[str, float]]]:
    """Create an OFF-POLICY GRPO loss function with importance sampling.

    Uses the tinker-cookbook pattern: weights from datum.loss_fn_inputs["weights"]
    and torch.dot() to compute weighted logprob sums over response tokens only.

    Off-policy loss with importance sampling correction:
        rho = exp(dot(log_pi_current - log_pi_behavior, weights) / n_response)
        loss = rho * (-advantage * dot(logprobs, weights) + kl_beta * dot(pi - ref, weights))

    Args:
        rewards: List of K rewards, one per completion in the group
        ref_logprobs_list: Reference model logprobs for each completion (frozen, for KL)
        behavior_logprobs_list: Behavior policy logprobs (from deployment at time of sampling)
        kl_beta: KL regularization coefficient
        clip_rho: Clip importance ratio for stability
        eps: Epsilon for numerical stability in advantage normalization
        debug: Enable pdb breakpoints inside loss function

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

    if debug:
        log(f"\n[DEBUG GRPO OFF-POLICY] === Advantage Computation ===")
        log(f"[DEBUG GRPO] rewards_tensor: {rewards_tensor}")
        log(f"[DEBUG GRPO] mean_r: {mean_r.item():.4f}, std_r: {std_r.item() if isinstance(std_r, torch.Tensor) else std_r:.4f}")
        log(f"[DEBUG GRPO] advantages: {advantages}")

    # Convert reference and behavior logprobs to tensors (no grad needed - frozen)
    ref_tensors = [torch.tensor(ref_lp, dtype=torch.float32) for ref_lp in ref_logprobs_list]
    behavior_tensors = [torch.tensor(b_lp, dtype=torch.float32) for b_lp in behavior_logprobs_list]

    def loss_fn(
        data: List[tinker.Datum],
        logprobs_list: List[torch.Tensor],
    ) -> Tuple[torch.Tensor, Dict[str, float]]:
        """Off-policy GRPO loss using weights + dot product (tinker-cookbook pattern).

        Args:
            data: List of K Datum objects with loss_fn_inputs["weights"]
            logprobs_list: List of K logprob tensors from CURRENT policy (requires_grad=True)

        Returns:
            (loss, metrics) tuple
        """
        assert len(logprobs_list) == K, f"Expected {K} sequences, got {len(logprobs_list)}"

        total_loss = torch.tensor(0.0)
        total_kl = 0.0
        total_policy_lp = 0.0
        total_ref_lp = 0.0
        total_behavior_lp = 0.0
        total_rho = 0.0
        num_response_tokens = 0

        for i in range(K):
            adv = advantages[i]
            pi_lp = logprobs_list[i]  # Current policy logprobs (requires_grad=True)
            ref_lp = ref_tensors[i]  # Reference logprobs (frozen)
            behavior_lp = behavior_tensors[i]  # Behavior policy logprobs (frozen)

            # Get weights from datum (0 for prompt, 1 for response tokens)
            weights = torch.tensor(data[i].loss_fn_inputs["weights"].data, dtype=torch.float32)

            # Truncate to min length
            min_len = min(len(pi_lp), len(ref_lp), len(behavior_lp), len(weights))
            if min_len == 0:
                continue
            pi_lp_t = pi_lp[:min_len]
            ref_lp_t = ref_lp[:min_len]
            behavior_lp_t = behavior_lp[:min_len]
            weights_t = weights[:min_len]

            n_response = int(weights_t.sum().item())
            if n_response == 0:
                continue

            # Weighted logprob sums using dot product
            pi_sum = torch.dot(pi_lp_t.float(), weights_t)
            ref_sum = torch.dot(ref_lp_t.float(), weights_t)
            behavior_sum = torch.dot(behavior_lp_t.float(), weights_t)

            # Importance ratio: rho = exp(mean per-token log ratio over response)
            log_rho = torch.dot((pi_lp_t - behavior_lp_t).float(), weights_t)
            rho = torch.clamp(torch.exp(log_rho / n_response), max=clip_rho)

            # Policy gradient loss with importance sampling
            pg_loss = rho * (-adv * pi_sum)

            # KL penalty
            kl_term = torch.dot((pi_lp_t - ref_lp_t).float(), weights_t)

            total_loss = total_loss + pg_loss + rho * kl_beta * kl_term

            # Metrics (detached)
            with torch.no_grad():
                total_kl += kl_term.item()
                total_policy_lp += pi_sum.item()
                total_ref_lp += ref_sum.item()
                total_behavior_lp += behavior_sum.item()
                total_rho += rho.item()
                num_response_tokens += n_response

        # Average loss over group
        loss = total_loss / K

        metrics = {
            "grpo_loss": loss.item(),
            "mean_reward": mean_r.item(),
            "std_reward": std_r.item() if isinstance(std_r, torch.Tensor) else std_r,
            "mean_advantage": sum(advantages) / K,
            "mean_kl": total_kl / K if K > 0 else 0.0,
            "mean_policy_lp": total_policy_lp / num_response_tokens if num_response_tokens > 0 else 0.0,
            "mean_ref_lp": total_ref_lp / num_response_tokens if num_response_tokens > 0 else 0.0,
            "mean_behavior_lp": total_behavior_lp / num_response_tokens if num_response_tokens > 0 else 0.0,
            "mean_importance_ratio": total_rho / K if K > 0 else 1.0,
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
    # Fireworks API gateway: .../inference/v1/chat/completions
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

    resp = httpx.post(chat_url, headers=headers, json=payload, timeout=180)
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


def get_prefill_logprobs_from_deployment(
    inference_url: str,
    api_key: str,
    model: str,
    tokens: List[int],
    timeout: int = 120,
) -> List[float]:
    """Get logprobs for a token sequence by running prefill on the deployment.

    This is used for OFF-POLICY training to get the "behavior policy" logprobs
    (the logprobs at the time of sampling, before subsequent training updates).

    Uses /v1/completions with echo=True to get logprobs for the input tokens.

    IMPORTANT: Alignment with Tinker API (trainer's /forward):
    - Trainer returns: logprobs[i] = P(tokens[i+1] | tokens[0:i+1])  (N-1 values for N tokens)
    - Inference returns: logprobs[i] = P(tokens[i] | tokens[0:i])    (N values, first=None)
    - To align: use inference[1:] which matches trainer[0:]

    Args:
        inference_url: Base URL of the inference server/deployment
        api_key: Fireworks API key
        model: Model name (e.g., accounts/{account}/deployments/{deployment_id})
        tokens: Full token sequence (prompt + completion)
        timeout: Request timeout in seconds

    Returns:
        List of per-token logprobs aligned with trainer convention (N-1 values for N tokens).
    """
    if not tokens or len(tokens) < 2:
        return [0.0] * (len(tokens) - 1) if tokens else []

    base = inference_url.rstrip("/")
    # Fireworks API gateway URL handling
    if "api.fireworks" in base:
        completions_url = f"{base}/inference/v1/completions"
    else:
        completions_url = f"{base}/v1/completions"

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    payload = {
        "model": model,
        "prompt": tokens,  # Pass token IDs directly
        "max_tokens": 1,  # Minimal generation, we only want prefill logprobs
        "echo": True,  # Include input in output to get logprobs for input tokens
        "logprobs": 1,  # Request logprobs
        "prompt_cache_max_len": 0,  # Disable prompt caching for accurate logprobs
    }

    resp = httpx.post(completions_url, headers=headers, json=payload, timeout=timeout)
    resp.raise_for_status()

    result = resp.json()
    choices = result.get("choices", [])

    if not choices:
        return [0.0] * (len(tokens) - 1)

    logprobs_data = choices[0].get("logprobs", {})
    token_logprobs = logprobs_data.get("token_logprobs", [])

    # Inference returns: logprobs[i] = P(tokens[i] | tokens[0:i])
    # - logprobs[0] = None (first token has no context)
    # - logprobs[1] = P(tokens[1] | tokens[0])
    # - logprobs[2] = P(tokens[2] | tokens[0:2])
    #
    # Trainer returns: logprobs[i] = P(tokens[i+1] | tokens[0:i+1])
    # - logprobs[0] = P(tokens[1] | tokens[0])
    # - logprobs[1] = P(tokens[2] | tokens[0:2])
    #
    # So inference[1:] aligns with trainer[0:]
    aligned_logprobs = token_logprobs[1 : len(tokens)]  # Skip first (None), take up to len(tokens)-1

    # Replace None with 0.0 and pad if needed
    logprobs = [lp if lp is not None else 0.0 for lp in aligned_logprobs]
    expected_len = len(tokens) - 1  # Trainer returns N-1 logprobs for N tokens
    while len(logprobs) < expected_len:
        logprobs.append(0.0)

    return logprobs


# =============================================================================
# CLI and main
# =============================================================================


def parse_args():
    parser = argparse.ArgumentParser(
        description="OFF-POLICY GRPO Training via Tinker SDK with Importance Sampling",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Fireworks API configuration
    api_group = parser.add_argument_group("Fireworks API")
    api_group.add_argument("--api-key", default="tml-local", help="API key for trainer Tinker endpoint")
    api_group.add_argument("--base-model", required=True, help="Base model name (e.g., accounts/fireworks/models/qwen3-8b)")
    api_group.add_argument("--fireworks-api-key", default=None, help="Fireworks API key (or set FIREWORKS_API_KEY env var)")
    api_group.add_argument("--fireworks-account-id", default=None, help="Fireworks account ID (or set FIREWORKS_ACCOUNT_ID env var)")
    api_group.add_argument("--fireworks-base-url", default=None, help="Fireworks API base URL (default: https://api.fireworks.ai)")
    api_group.add_argument("--additional-headers", type=str, default=None, help="Additional HTTP headers as JSON string")

    # RLOR trainer configuration
    rlor_group = parser.add_argument_group("RLOR Trainer")
    rlor_group.add_argument("--rlor-node-count", type=int, default=1, help="Number of trainer nodes")
    rlor_group.add_argument("--rlor-display-name", type=str, default=None, help="Display name for RLOR job")
    rlor_group.add_argument("--rlor-timeout-s", type=float, default=15 * 60, help="Timeout for RLOR job to become ready (seconds)")
    rlor_group.add_argument("--rlor-poll-interval-s", type=float, default=5.0, help="Poll interval for RLOR job status (seconds)")
    rlor_group.add_argument("--custom-image-tag", type=str, default=None, help="Custom trainer image tag (e.g., /train:0.20.14)")
    rlor_group.add_argument("--region", type=str, default=None, help="Region for RLOR trainer (e.g., EU_ICELAND_2)")
    rlor_group.add_argument("--skip-validations", action="store_true", help="Skip control plane validations (required for FW_HOSTED bucket)")

    # Deployment configuration
    deploy_group = parser.add_argument_group("Deployment")
    deploy_group.add_argument("--hotload-deployment-id", type=str, default=None, help="Deployment ID for hotload and inference")
    deploy_group.add_argument("--create-deployment", action="store_true", help="Create deployment if it doesn't exist")
    deploy_group.add_argument("--deployment-shape", type=str, default=None, help="Deployment shape (e.g., 1xH100)")
    deploy_group.add_argument("--deployment-region", type=str, default=None, help="Region for deployment (defaults to --region)")
    deploy_group.add_argument("--deployment-timeout-s", type=float, default=600, help="Timeout for deployment to become ready (seconds)")
    deploy_group.add_argument("--accelerator-type", type=str, default=None, help="Accelerator type (e.g., NVIDIA_H100_80GB)")
    deploy_group.add_argument("--hot-load-bucket-type", type=str, default="FW_HOSTED", help="Hotload bucket type: FW_HOSTED, MINIO, S3, NEBIUS")
    # Dataset configuration
    data_group = parser.add_argument_group("Dataset")
    data_group.add_argument("--dataset", required=True, help="Path or URL to GSM8K-style JSONL dataset")
    data_group.add_argument("--max-rows", type=int, default=100, help="Maximum number of dataset rows to use")
    data_group.add_argument("--max-seq-len", type=int, default=4096, help="Maximum sequence length for training")

    # Training hyperparameters
    train_group = parser.add_argument_group("Training")
    train_group.add_argument("--group-size", type=int, default=4, help="GRPO group size (K completions per prompt)")
    train_group.add_argument("--kl-beta", type=float, default=0.001, help="KL divergence penalty coefficient")
    train_group.add_argument("--lr", type=float, default=1e-5, help="Learning rate")
    train_group.add_argument("--epochs", type=int, default=1, help="Number of training epochs")
    train_group.add_argument("--grad-accum", type=int, default=4, help="Gradient accumulation steps (prompts per optimizer step)")
    train_group.add_argument("--lora-rank", type=int, default=0, help="LoRA rank (0 = full fine-tuning)")
    train_group.add_argument("--max-new-tokens", type=int, default=512, help="Maximum new tokens for sampling")
    train_group.add_argument("--temperature", type=float, default=0.7, help="Sampling temperature")

    # Logging and monitoring
    log_group = parser.add_argument_group("Logging")
    log_group.add_argument("--log-interval", type=int, default=1, help="Log metrics every N optimizer steps")
    log_group.add_argument("--wandb-entity", type=str, default=None, help="W&B entity (enables W&B logging if set)")
    log_group.add_argument("--wandb-project", type=str, default="grpo-tinker", help="W&B project name")
    log_group.add_argument("--wandb-run-name", type=str, default=None, help="W&B run name")

    # Checkpointing and hotload
    ckpt_group = parser.add_argument_group("Checkpointing")
    ckpt_group.add_argument("--save-sampler", action="store_true", help="Save final checkpoint for sampler")
    ckpt_group.add_argument("--sampler-name", type=str, default=None, help="Name for saved sampler checkpoint")
    ckpt_group.add_argument("--hotload", action="store_true", help="Enable hotloading at intervals")
    ckpt_group.add_argument(
        "--hotload-interval",
        type=int,
        default=10,
        help="Hotload every N optimizer steps. Uses importance sampling between hotloads.",
    )
    ckpt_group.add_argument(
        "--clip-rho",
        type=float,
        default=10.0,
        help="Clip importance ratio for stability",
    )
    ckpt_group.add_argument("--hotload-api-url", type=str, default="https://api.fireworks.ai", help="API URL for hotload requests")
    ckpt_group.add_argument("--hotload-timeout", type=int, default=120, help="Timeout for hotload to complete (seconds)")

    # Cleanup
    cleanup_group = parser.add_argument_group("Cleanup")
    cleanup_group.add_argument("--cleanup-rlor-job", action="store_true", help="Delete both RLOR jobs after training")
    cleanup_group.add_argument("--cleanup-deployment", action="store_true", help="Delete deployment after training (only if --create-deployment)")

    # Debug
    parser.add_argument("--debug", action="store_true", help="Enable pdb breakpoints at key training steps")

    return parser.parse_args()


def main():
    """GRPO off-policy training loop with importance sampling.

    Same architecture as on-policy, but hotloads at intervals (not every step).
    Between hotloads, uses importance sampling to correct for the mismatch
    between the deployment's weights (behavior policy) and the trainer's
    current weights (target policy).

    Key difference from on-policy:
    - Hotload every N steps instead of every step (--hotload-interval)
    - Computes behavior policy logprobs via deployment prefill
    - Loss includes importance ratio: rho = exp(pi_current - pi_behavior)
    """
    args = parse_args()
    log(f"Starting GRPO training: two RLOR jobs (policy + reference)")

    if args.hotload or args.save_sampler:
        if not args.hotload_deployment_id:
            raise RuntimeError("--hotload or --save-sampler requires --hotload-deployment-id")

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
    fw_additional_headers = parse_additional_headers(
        args.additional_headers or os.environ.get("FIREWORKS_ADDITIONAL_HEADERS")
    )
    fw_base_url = args.fireworks_base_url or os.environ.get("FIREWORKS_BASE_URL") or "https://api.fireworks.ai"
    if not fw_api_key or not fw_account_id:
        raise RuntimeError(
            "Set FIREWORKS_API_KEY and FIREWORKS_ACCOUNT_ID (or --fireworks-api-key / --fireworks-account-id)"
        )

    hotload_deployment_id = args.hotload_deployment_id

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

    # Track created resources for cleanup on failure
    policy_endpoint: RlorServiceEndpoint | None = None
    reference_endpoint: RlorServiceEndpoint | None = None
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
                    delete_rlor_job(
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
                delete_deployment(
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

    # Inference URL and model for sampling via Fireworks API gateway
    inference_url = fw_base_url
    if hotload_deployment_id:
        inference_model = f"accounts/{fw_account_id}/deployments/{hotload_deployment_id}"
        log(f"  Sampling via deployment: {inference_model}")
    else:
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
    epoch_metrics = {"reward": 0.0, "accuracy": 0.0, "kl": 0.0, "grpo_loss": 0.0, "importance_ratio": 0.0, "num_prompts": 0}
    skipped = 0

    # Checkpoint tracking for delta hotloads:
    # First save is "base" (full weights). Subsequent saves are "delta" (diff only,
    # ~10x smaller). See on-policy script for detailed explanation.
    base_checkpoint_saved = False
    base_checkpoint_identity: str | None = None
    last_hotloaded_step = -1

    # Print initial (step 0) metrics for e2e test
    log(json.dumps({"type": "metrics", "step": 0, "reward": 0.0, "accuracy": 0.0, "kl": 0.0}))

    for epoch in range(args.epochs):
        for prompt_idx, row in enumerate(dataset):
            messages = row.get("messages", [])
            ground_truth = row.get("ground_truth", "")
            if not messages or not ground_truth:
                continue

            input_messages = [m for m in messages if m.get("role") != "assistant"]
            if not input_messages:
                continue

            # Progress logging (always shown — important for long runs)
            user_msg = input_messages[0].get("content", "")[:60]
            log(f"  Prompt {prompt_idx}/{len(dataset)}: {user_msg}...")

            # =========================================================================
            # Off-Policy: Hotload at intervals (not every step)
            # Between hotloads, use importance sampling to correct for stale samples
            # =========================================================================
            should_hotload = (
                args.hotload
                and hotload_deployment_id
                and global_step > 0
                and last_hotloaded_step < global_step
                and (global_step % args.hotload_interval == 0)
            )
            if should_hotload:
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
                        timeout_seconds=args.hotload_timeout,
                    )

                    if hotload_success:
                        # Update base identity for next delta
                        base_checkpoint_identity = sampler_name
                        last_hotloaded_step = global_step  # Mark this step as hotloaded
                    else:
                        warn(f"  Hotload failed for step {global_step}, continuing with stale weights")
                        last_hotloaded_step = global_step  # Still mark to avoid retry loop

                except Exception as e:
                    warn(f"  Hotload error at step {global_step}: {e}")
                    last_hotloaded_step = global_step  # Avoid retry loop on error

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

            # Log sampling results: token counts and response lengths
            response_lens = [len(s.full_tokens) - s.prompt_len for s in sampled]
            log(f"    Sampled {len(sampled)} completions, response lengths: {min(response_lens)}-{max(response_lens)} tokens")

            # =========================================================================
            # Compute rewards
            # =========================================================================
            rewards = []
            eval_details = []
            for s in sampled:
                score, detail = evaluate_gsm8k_response(s.text, ground_truth)
                rewards.append(score)
                eval_details.append(detail)

            correct_count = sum(1 for r in rewards if r > 0.5)
            log(f"    Rewards: {correct_count}/{len(rewards)} correct ({rewards})")

            # Show extracted answers for debugging
            if args.debug:
                for i, (r, d, s) in enumerate(zip(rewards, eval_details, sampled)):
                    if i < 2 or r == 1.0:
                        response_preview = s.text[-80:].replace('\n', ' ')
                        log(f"      [{i}] {d} | ...{response_preview}")

            # Skip if all rewards are the same (no learning signal)
            if len(set(rewards)) == 1:
                skipped += 1
                uniform_type = "all correct" if rewards[0] == 1.0 else "all wrong"
                log(f"    SKIPPED ({uniform_type}) | total skipped: {skipped}, valid: {accum_count}, steps: {global_step}")
                continue
            
            log(f"    TRAINING on this prompt (accum {accum_count+1}/{args.grad_accum})")

            # =========================================================================
            # Build datums with weights and get reference + behavior logprobs
            # Uses datum_from_model_input_weights (tinker-cookbook pattern):
            #   - Handles token shifting internally (no manual [:-1] / [1:])
            #   - weights[i]=0 for prompt, weights[i]=1 for response
            # =========================================================================
            ref_logprobs_list: List[List[float]] = []
            behavior_logprobs_list: List[List[float]] = []
            datums: List[tinker.Datum] = []

            for s in sampled:
                full_tokens = s.full_tokens
                if len(full_tokens) < 2:
                    continue

                # Build weights: 0 for prompt tokens, 1 for response tokens
                weights = torch.zeros(len(full_tokens), dtype=torch.float32)
                weights[s.prompt_len:] = 1.0

                # datum_from_tokens_weights handles shifting internally
                datum = datum_from_tokens_weights(
                    torch.tensor(full_tokens, dtype=torch.long),
                    weights,
                    max_length=args.max_seq_len,
                )
                datums.append(datum)

                # Get reference logprobs via forward on frozen reference trainer
                ref_fwd = reference_client.forward([datum], "cross_entropy").result()
                ref_lp = list(ref_fwd.loss_fn_outputs[0]["logprobs"].data)
                ref_logprobs_list.append(ref_lp)

                # Get behavior policy logprobs via deployment prefill.
                # These are the logprobs from the model that GENERATED the samples
                # (may be stale if we haven't hotloaded recently). Used for
                # importance sampling correction: rho = pi_current / pi_behavior
                behavior_lp = get_prefill_logprobs_from_deployment(
                    inference_url=inference_url,
                    api_key=fw_api_key,
                    model=inference_model,
                    tokens=full_tokens,
                )
                behavior_logprobs_list.append(behavior_lp)

            if not datums:
                continue

            # =========================================================================
            # Create off-policy GRPO loss function and run forward_backward_custom
            # Loss fn uses torch.dot(logprobs, weights) for weighted response-only sums
            # =========================================================================
            grpo_loss_fn = make_grpo_loss_fn(
                rewards=rewards,
                ref_logprobs_list=ref_logprobs_list,
                behavior_logprobs_list=behavior_logprobs_list,
                kl_beta=args.kl_beta,
                clip_rho=args.clip_rho,
                debug=args.debug,
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
            epoch_metrics["importance_ratio"] += metrics.get("mean_importance_ratio", 1.0)
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
                avg_rho = epoch_metrics["importance_ratio"] / n if n > 0 else 1.0

                log(
                    f"Step {global_step} | Loss: {avg_loss:.4f} | Reward: {avg_reward:.3f} | Acc: {avg_acc:.2%} | KL: {avg_kl:.4f} | ρ: {avg_rho:.3f} | LR: {args.lr:.2e}"
                )
                log(json.dumps({"type": "metrics", "step": global_step, "grpo_loss": avg_loss, "reward": avg_reward, "accuracy": avg_acc, "kl": avg_kl}))

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

                epoch_metrics = {"reward": 0.0, "accuracy": 0.0, "kl": 0.0, "grpo_loss": 0.0, "importance_ratio": 0.0, "num_prompts": 0}
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
            avg_rho = epoch_metrics["importance_ratio"] / n if n > 0 else 1.0

            log(
                f"Step {global_step} | Loss: {avg_loss:.4f} | Reward: {avg_reward:.3f} | Acc: {avg_acc:.2%} | KL: {avg_kl:.4f} | ρ: {avg_rho:.3f} | LR: {args.lr:.2e}"
            )
            log(json.dumps({"type": "metrics", "step": global_step, "grpo_loss": avg_loss, "reward": avg_reward, "accuracy": avg_acc, "kl": avg_kl}))

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

            epoch_metrics = {"reward": 0.0, "accuracy": 0.0, "kl": 0.0, "grpo_loss": 0.0, "importance_ratio": 0.0, "num_prompts": 0}
            accum_count = 0

    log(f"\nTraining complete: {global_step} optimizer steps (skipped {skipped} prompts with uniform rewards)")

    # Save and hotload
    if args.save_sampler:
        sampler_name = args.sampler_name or f"grpo_sampler_step_{global_step}"
        # First save is always base, subsequent are delta
        final_ckpt_type = "delta" if base_checkpoint_saved else "base"
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
