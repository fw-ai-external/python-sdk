#!/usr/bin/env python3
"""
Supervised Fine-Tuning (SFT) via Fireworks' Tinker SDK.

This script runs LoRA SFT training using the Tinker SDK. It supports two modes:
  1. Direct Tinker endpoint: --base-url points to any Tinker service
  2. RLOR mode (--use-rlor): creates a Fireworks-managed GPU trainer job

The training loop uses cross-entropy loss on assistant messages only, with a
linear learning rate decay schedule.

Usage (direct Tinker endpoint):
    python examples/training/train_sft.py \\
        --base-url https://trainer-...:30443 \\
        --model-name "accounts/fireworks/models/qwen3-8b" \\
        --dataset-path /path/to/train.jsonl \\
        --lora-rank 32 --epochs 1

Usage (RLOR mode):
    python examples/training/train_sft.py \\
        --use-rlor \\
        --model-name "accounts/fireworks/models/qwen3-8b" \\
        --dataset-path /path/to/train.jsonl \\
        --lora-rank 32 --epochs 1 \\
        --region EU_ICELAND_2

Copyright (c) Fireworks AI, Inc. and affiliates.
"""

from __future__ import annotations

import argparse
import atexit
import json
import logging
import os
import time
from typing import List

import tinker
# Import shared utilities
from shared import (RlorServiceEndpoint, create_rlor_service_job_and_wait,
                    delete_rlor_job, log, parse_additional_headers, warn)
from tinker_cookbook import model_info, renderers
from tinker_cookbook.supervised.common import compute_mean_nll
from tinker_cookbook.supervised.data import conversation_to_datum
from tinker_cookbook.tokenizer_utils import get_tokenizer

# Importing fireworks.training applies Fireworks compatibility patches to Tinker
# (e.g., checkpoint_type support for save_weights_for_sampler).
# This is optional for SFT since we don't use hotloading.
try:
    import fireworks.training  # noqa: F401
except ImportError:
    pass

try:
    import wandb

    WANDB_AVAILABLE = True
except ImportError:
    WANDB_AVAILABLE = False

logger = logging.getLogger(__name__)


# =============================================================================
# Dataset loading
# =============================================================================


def load_jsonl_dataset(path: str, max_rows: int | None = None) -> list[dict]:
    """Load a JSONL file where each line has a 'messages' field.

    Args:
        path: Path to the JSONL file.
        max_rows: Maximum number of rows to load (None = all).

    Returns:
        List of dicts, each containing at least a 'messages' key.
    """
    rows = []
    with open(path) as f:
        for i, line in enumerate(f):
            if max_rows is not None and i >= max_rows:
                break
            row = json.loads(line)
            if "messages" not in row:
                warn(f"Row {i} missing 'messages' field, skipping")
                continue
            rows.append(row)
    log(f"Loaded {len(rows)} rows from {path}")
    return rows


def load_hf_dataset(dataset_name: str, split: str = "train", max_rows: int | None = None) -> list[dict]:
    """Load a HuggingFace dataset (e.g., HuggingFaceH4/no_robots).

    Args:
        dataset_name: HuggingFace dataset name.
        split: Dataset split to load.
        max_rows: Maximum number of rows (None = all).

    Returns:
        List of dicts with 'messages' field.
    """
    import datasets

    ds = datasets.load_dataset(dataset_name)
    assert isinstance(ds, datasets.DatasetDict)

    # Handle split name variations (e.g., train_sft vs train)
    if split in ds:
        data = ds[split]
    elif f"{split}_sft" in ds:
        data = ds[f"{split}_sft"]
    else:
        available = list(ds.keys())
        raise ValueError(f"Split '{split}' not found. Available: {available}")

    rows = []
    for i, row in enumerate(data):
        if max_rows is not None and i >= max_rows:
            break
        rows.append(dict(row))
    log(f"Loaded {len(rows)} rows from {dataset_name} ({split})")
    return rows


# =============================================================================
# CLI
# =============================================================================


def parse_args():
    parser = argparse.ArgumentParser(
        description="Supervised Fine-Tuning via Tinker SDK (LoRA or full param)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Connection mode
    conn_group = parser.add_argument_group("Connection")
    conn_group.add_argument(
        "--base-url",
        type=str,
        default=None,
        help="Direct Tinker endpoint URL (mutually exclusive with --use-rlor)",
    )
    conn_group.add_argument("--use-rlor", action="store_true", help="Create an RLOR trainer job on Fireworks")
    conn_group.add_argument("--api-key", default="tml-local", help="API key for Tinker endpoint")

    # Fireworks API (for RLOR mode)
    api_group = parser.add_argument_group("Fireworks API (RLOR mode)")
    api_group.add_argument("--fireworks-api-key", default=None, help="Fireworks API key (or FIREWORKS_API_KEY)")
    api_group.add_argument("--fireworks-account-id", default=None, help="Account ID (or FIREWORKS_ACCOUNT_ID)")
    api_group.add_argument("--fireworks-base-url", default=None, help="Fireworks API base URL")
    api_group.add_argument("--additional-headers", type=str, default=None, help="Additional headers as JSON")
    api_group.add_argument("--region", type=str, default=None, help="GPU region (e.g., EU_ICELAND_2)")
    api_group.add_argument("--skip-validations", action="store_true", help="Skip control plane validations")
    api_group.add_argument("--custom-image-tag", type=str, default=None, help="Custom trainer image tag")
    api_group.add_argument("--rlor-node-count", type=int, default=1, help="Number of trainer nodes")
    api_group.add_argument("--rlor-display-name", type=str, default=None, help="RLOR job display name")
    api_group.add_argument("--rlor-timeout-s", type=float, default=15 * 60, help="RLOR ready timeout (seconds)")

    # Model and dataset
    model_group = parser.add_argument_group("Model and Dataset")
    model_group.add_argument(
        "--model-name",
        type=str,
        default="accounts/fireworks/models/qwen3-8b",
        help="Model name (HF-style or Fireworks account path)",
    )
    model_group.add_argument(
        "--dataset-path",
        type=str,
        default=None,
        help="Path to local JSONL dataset (each line has 'messages' field)",
    )
    model_group.add_argument(
        "--dataset-name",
        type=str,
        default=None,
        help="HuggingFace dataset name (e.g., HuggingFaceH4/no_robots)",
    )
    model_group.add_argument("--max-rows", type=int, default=None, help="Max dataset rows (None = all)")

    # Training hyperparameters
    train_group = parser.add_argument_group("Training")
    train_group.add_argument("--lora-rank", type=int, default=32, help="LoRA rank")
    train_group.add_argument("--batch-size", type=int, default=128, help="Batch size (sequences per step)")
    train_group.add_argument("--learning-rate", type=float, default=1e-4, help="Peak learning rate")
    train_group.add_argument("--max-length", type=int, default=32768, help="Maximum sequence length")
    train_group.add_argument("--epochs", type=int, default=1, help="Number of training epochs")
    train_group.add_argument(
        "--train-on-what",
        type=str,
        default="ALL_ASSISTANT_MESSAGES",
        choices=["ALL_ASSISTANT_MESSAGES", "LAST_ASSISTANT_MESSAGE"],
        help="Which assistant messages to compute loss on",
    )
    train_group.add_argument("--grad-accum", type=int, default=1, help="Gradient accumulation steps")

    # Checkpointing
    ckpt_group = parser.add_argument_group("Checkpointing")
    ckpt_group.add_argument("--save-every", type=int, default=0, help="Save checkpoint every N steps (0=disabled)")
    ckpt_group.add_argument("--log-path", type=str, default="/tmp/tinker-sft", help="Log and checkpoint directory")
    ckpt_group.add_argument(
        "--ttl-seconds", type=int, default=604800, help="Checkpoint TTL in seconds (default: 7 days)"
    )

    # Logging
    log_group = parser.add_argument_group("Logging")
    log_group.add_argument("--wandb-entity", type=str, default=None, help="W&B entity (enables W&B)")
    log_group.add_argument("--wandb-project", type=str, default="sft-tinker", help="W&B project name")
    log_group.add_argument("--wandb-run-name", type=str, default=None, help="W&B run name")
    log_group.add_argument("--log-interval", type=int, default=1, help="Log metrics every N steps")

    # Cleanup
    parser.add_argument("--cleanup-rlor-job", action="store_true", help="Delete RLOR job after training")

    return parser.parse_args()


# =============================================================================
# Main
# =============================================================================


def main():
    args = parse_args()

    # Validate connection mode
    if not args.base_url and not args.use_rlor:
        raise RuntimeError("Specify either --base-url (direct endpoint) or --use-rlor (Fireworks managed)")

    # Validate dataset source
    if not args.dataset_path and not args.dataset_name:
        raise RuntimeError("Specify either --dataset-path (local JSONL) or --dataset-name (HuggingFace)")

    log("Starting SFT training")

    # =========================================================================
    # Setup W&B
    # =========================================================================
    use_wandb = WANDB_AVAILABLE and args.wandb_entity is not None
    if use_wandb:
        wandb.init(
            entity=args.wandb_entity,
            project=args.wandb_project,
            name=args.wandb_run_name,
            config={
                "model_name": args.model_name,
                "lora_rank": args.lora_rank,
                "batch_size": args.batch_size,
                "learning_rate": args.learning_rate,
                "max_length": args.max_length,
                "epochs": args.epochs,
                "train_on_what": args.train_on_what,
            },
        )

    # =========================================================================
    # Create or connect to trainer
    # =========================================================================
    trainer_endpoint: RlorServiceEndpoint | None = None
    cleanup_done = False

    def cleanup_resources():
        nonlocal cleanup_done
        if cleanup_done:
            return
        cleanup_done = True
        if args.cleanup_rlor_job and trainer_endpoint is not None:
            log(f"Cleaning up RLOR job: {trainer_endpoint.job_id}")
            fw_api_key = args.fireworks_api_key or os.environ.get("FIREWORKS_API_KEY")
            fw_account_id = args.fireworks_account_id or os.environ.get("FIREWORKS_ACCOUNT_ID")
            fw_base_url = args.fireworks_base_url or os.environ.get("FIREWORKS_BASE_URL") or "https://api.fireworks.ai"
            fw_additional_headers = parse_additional_headers(
                args.additional_headers or os.environ.get("FIREWORKS_ADDITIONAL_HEADERS")
            )
            try:
                delete_rlor_job(
                    api_key=fw_api_key,
                    account_id=fw_account_id,
                    base_url=fw_base_url,
                    additional_headers=fw_additional_headers,
                    job_id=trainer_endpoint.job_id,
                )
                log(f"  Deleted {trainer_endpoint.job_id}")
            except Exception as e:
                warn(f"Failed to delete RLOR job: {e}")

    atexit.register(cleanup_resources)

    if args.use_rlor:
        fw_api_key = args.fireworks_api_key or os.environ.get("FIREWORKS_API_KEY")
        fw_account_id = args.fireworks_account_id or os.environ.get("FIREWORKS_ACCOUNT_ID")
        fw_base_url = args.fireworks_base_url or os.environ.get("FIREWORKS_BASE_URL") or "https://api.fireworks.ai"
        fw_additional_headers = parse_additional_headers(
            args.additional_headers or os.environ.get("FIREWORKS_ADDITIONAL_HEADERS")
        )
        if not fw_api_key or not fw_account_id:
            raise RuntimeError("RLOR mode requires FIREWORKS_API_KEY and FIREWORKS_ACCOUNT_ID")

        log("[1/3] Creating RLOR trainer job...")
        trainer_endpoint = create_rlor_service_job_and_wait(
            api_key=fw_api_key,
            account_id=fw_account_id,
            base_url=fw_base_url,
            additional_headers=fw_additional_headers,
            base_model=args.model_name,
            lora_rank=args.lora_rank,
            max_context_length=args.max_length,
            learning_rate=args.learning_rate,
            gradient_accumulation_steps=args.grad_accum,
            node_count=args.rlor_node_count,
            display_name=args.rlor_display_name or "sft-training",
            region=args.region,
            skip_validations=args.skip_validations,
            custom_image_tag=args.custom_image_tag,
            timeout_s=args.rlor_timeout_s,
        )
        base_url = trainer_endpoint.base_url
        log(f"  Trainer ready: {trainer_endpoint.job_id} at {base_url}")
    else:
        base_url = args.base_url
        log(f"[1/3] Using direct endpoint: {base_url}")

    # =========================================================================
    # Setup tokenizer, renderer, and training client
    # =========================================================================
    log("[2/3] Setting up tokenizer and training client...")

    tokenizer = get_tokenizer(args.model_name)
    renderer_name = model_info.get_recommended_renderer_name(args.model_name)
    renderer = renderers.get_renderer(renderer_name, tokenizer)
    log(f"  Renderer: {renderer_name}")

    train_on_what = renderers.TrainOnWhat[args.train_on_what]

    service_client = tinker.ServiceClient(base_url=base_url, api_key=args.api_key)
    training_client = service_client.create_lora_training_client(
        base_model=args.model_name,
        rank=args.lora_rank,
    )
    log(f"  Training client created (lora_rank={args.lora_rank})")

    # =========================================================================
    # Load dataset
    # =========================================================================
    log("[3/3] Loading dataset...")

    if args.dataset_path:
        dataset = load_jsonl_dataset(args.dataset_path, max_rows=args.max_rows)
    else:
        dataset = load_hf_dataset(args.dataset_name, max_rows=args.max_rows)

    n_train_batches = max(1, len(dataset) // args.batch_size)
    log(f"  {len(dataset)} rows, batch_size={args.batch_size}, batches={n_train_batches}")

    # =========================================================================
    # Training loop
    # =========================================================================
    grad_accum = args.grad_accum
    total_optim_steps = max(1, (args.epochs * n_train_batches + grad_accum - 1) // grad_accum)
    log(
        f"Training for {args.epochs} epoch(s), {n_train_batches} batches/epoch, "
        f"grad_accum={grad_accum}, ~{total_optim_steps} optimizer steps"
    )

    global_step = 0
    accum_count = 0
    accum_nll_sum = 0.0
    accum_nll_weight = 0
    accum_tokens = 0
    accum_seqs = 0

    for epoch in range(args.epochs):
        log(f"\n=== Epoch {epoch + 1}/{args.epochs} ===")

        for batch_idx in range(n_train_batches):
            start_time = time.time()
            step = epoch * n_train_batches + batch_idx
            metrics = {}

            # Save checkpoint (if enabled) -- only at optimizer step boundaries
            if args.save_every > 0 and global_step > 0 and global_step % args.save_every == 0 and accum_count == 0:
                try:
                    from tinker_cookbook import checkpoint_utils

                    checkpoint_utils.save_checkpoint(
                        training_client=training_client,
                        name=f"{global_step:06d}",
                        log_path=args.log_path,
                        kind="state",
                        loop_state={"batch": batch_idx, "epoch": epoch},
                        ttl_seconds=args.ttl_seconds,
                    )
                    log(f"  Saved checkpoint at step {global_step}")
                except Exception as e:
                    warn(f"  Checkpoint save failed: {e}")

            # Get batch rows
            batch_start = batch_idx * args.batch_size
            batch_end = min((batch_idx + 1) * args.batch_size, len(dataset))
            batch_rows = dataset[batch_start:batch_end]

            # Convert to datums
            batch = []
            skipped = 0
            for row in batch_rows:
                try:
                    datum = conversation_to_datum(
                        row["messages"],
                        renderer,
                        args.max_length,
                        train_on_what,
                    )
                    batch.append(datum)
                except Exception as e:
                    skipped += 1
                    if skipped <= 3:
                        warn(f"  Skipped row: {e}")

            if not batch:
                warn(f"  Batch {batch_idx}: all rows skipped, continuing")
                continue

            if skipped > 0:
                log(f"  Batch {batch_idx}: {skipped}/{len(batch_rows)} rows skipped")

            # Forward + backward (accumulates gradients on the server)
            fwd_bwd_future = training_client.forward_backward(batch, loss_fn="cross_entropy")
            fwd_bwd_result = fwd_bwd_future.result()

            # Track NLL across accumulation window
            num_tokens = sum(d.model_input.length for d in batch)
            if fwd_bwd_result.loss_fn_outputs:
                train_logprobs = [x["logprobs"] for x in fwd_bwd_result.loss_fn_outputs]
                train_weights = [d.loss_fn_inputs["weights"] for d in batch]
                batch_nll = compute_mean_nll(train_logprobs, train_weights)
            elif fwd_bwd_result.metrics:
                # Batched path returns aggregate loss in metrics (no per-datum logprobs)
                batch_nll = float(fwd_bwd_result.metrics.get("loss:sum", 0.0)) / max(num_tokens, 1)
            else:
                batch_nll = float("nan")

            accum_nll_sum += batch_nll * len(batch)
            accum_nll_weight += len(batch)
            accum_tokens += num_tokens
            accum_seqs += len(batch)
            accum_count += 1

            # Optimizer step: after grad_accum batches or at end of epoch
            is_last_batch_in_epoch = (batch_idx == n_train_batches - 1)
            should_step = (accum_count >= grad_accum) or is_last_batch_in_epoch

            if should_step:
                # Linear learning rate decay based on optimizer step count
                lr_mult = max(0.0, 1.0 - global_step / total_optim_steps)
                current_lr = args.learning_rate * lr_mult
                adam_params = tinker.AdamParams(
                    learning_rate=current_lr,
                    beta1=0.9,
                    beta2=0.95,
                    eps=1e-8,
                )

                optim_step_future = training_client.optim_step(adam_params)
                optim_result = optim_step_future.result()

                if optim_result.metrics:
                    metrics.update(optim_result.metrics)

                train_nll = accum_nll_sum / accum_nll_weight if accum_nll_weight > 0 else float("nan")
                elapsed = time.time() - start_time

                metrics.update(
                    num_sequences=accum_seqs,
                    num_tokens=accum_tokens,
                    learning_rate=current_lr,
                    train_mean_nll=train_nll,
                    progress=global_step / total_optim_steps,
                    time_total=elapsed,
                    grad_accum_batches=accum_count,
                )

                global_step += 1

                # Log metrics
                if global_step % args.log_interval == 0:
                    log(
                        f"  Step {global_step}/{total_optim_steps} | "
                        f"NLL: {train_nll:.4f} | "
                        f"LR: {current_lr:.2e} | "
                        f"Seqs: {accum_seqs} | "
                        f"Tokens: {accum_tokens} | "
                        f"AccumBatches: {accum_count} | "
                        f"Time: {elapsed:.1f}s"
                    )
                    log(json.dumps({
                        "type": "metrics",
                        "step": global_step,
                        "train_nll": train_nll,
                        "lr": current_lr,
                    }))

                if use_wandb:
                    wandb.log(
                        {
                            "train/nll": train_nll,
                            "train/lr": current_lr,
                            "train/num_tokens": accum_tokens,
                            "train/step": global_step,
                        },
                        step=global_step,
                    )

                # Reset accumulation counters
                accum_count = 0
                accum_nll_sum = 0.0
                accum_nll_weight = 0
                accum_tokens = 0
                accum_seqs = 0

    # =========================================================================
    # Save final checkpoint
    # =========================================================================
    try:
        from tinker_cookbook import checkpoint_utils

        log("\nSaving final checkpoint...")
        checkpoint_utils.save_checkpoint(
            training_client=training_client,
            name="final",
            log_path=args.log_path,
            kind="both",
            loop_state={"batch": n_train_batches, "epoch": args.epochs},
            ttl_seconds=args.ttl_seconds,
        )
        log(f"  Final checkpoint saved to {args.log_path}")
    except Exception as e:
        warn(f"Final checkpoint save failed: {e}")

    log(f"\nTraining complete: {global_step} optimizer steps over {args.epochs} epoch(s) (grad_accum={grad_accum})")

    if use_wandb:
        wandb.finish()

    # Cleanup
    cleanup_resources()


if __name__ == "__main__":
    main()
