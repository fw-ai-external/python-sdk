#!/usr/bin/env python3
"""Minimal DPO training loop.

A readable, modifiable preference-optimization loop using the Fireworks RLOR API.

Architecture:
    - Policy RLOR job:    forward_backward_custom + optim_step (trainable)
    - Reference RLOR job: forward only (frozen base model, for KL baseline)
    - Reference logprobs cached at initialisation from the frozen reference

Usage:
    export FIREWORKS_API_KEY=...
    export FIREWORKS_ACCOUNT_ID=...
    python cookbook/recipes/dpo_loop.py --dataset /path/to/preference_data.jsonl
"""

from __future__ import annotations

import logging
import os
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any, Dict, List

import tinker

from fireworks.training.sdk import TrainerJobManager, DeploymentManager
from fireworks.training.sdk.deployment import DEFAULT_DELTA_COMPRESSION
from fireworks.training.sdk.weight_syncer import WeightSyncer

from fireworks.training.cookbook.utils import (
    DEFAULT_ADAM,
    DeployConfig,
    HotloadConfig,
    InfraConfig,
    ResumeConfig,
    WandBConfig,
    ReconnectableClient,
    create_trainer_job,
    encode_text,
    extract_text,
    find_common_prefix_length,
    load_preference_dataset,
    log_metrics_json,
    make_dpo_loss_fn,
    setup_deployment,
    setup_resume,
    setup_wandb,
    validate_config,
    wandb_finish,
    wandb_log,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------


@dataclass
class Config:
    base_model: str = "accounts/pyroworks-dev/models/qwen3-1p7b-bf16"
    dataset: str = ""

    beta: float = 0.1
    learning_rate: float = 1e-5
    epochs: int = 1
    grad_accum: int = 4
    max_seq_len: int = 4096
    max_pairs: int | None = None
    lora_rank: int = 0

    infra: InfraConfig = field(default_factory=InfraConfig)
    deployment: DeployConfig = field(default_factory=lambda: DeployConfig(create_deployment=False))
    hotload: HotloadConfig = field(default_factory=lambda: HotloadConfig(hot_load_interval=0))
    wandb: WandBConfig = field(default_factory=lambda: WandBConfig(project="dpo-tinker"))
    resume: ResumeConfig = field(default_factory=ResumeConfig)


# ---------------------------------------------------------------------------
# Main training loop
# ---------------------------------------------------------------------------


def main(
    config: Config,
    rlor_mgr: TrainerJobManager | None = None,
    deploy_mgr: DeploymentManager | None = None,
):
    cfg = config

    validate_config(cfg.base_model, cfg.dataset, cfg.hotload, cfg.deployment, cfg.infra, cfg.resume)
    setup_wandb(cfg.wandb, {"beta": cfg.beta, "lr": cfg.learning_rate, "epochs": cfg.epochs})

    # -- Setup infrastructure ----------------------------------------------

    api_key = os.environ["FIREWORKS_API_KEY"]
    account = os.environ.get("FIREWORKS_ACCOUNT_ID", "")
    base_url = os.environ.get("FIREWORKS_BASE_URL", "https://api.fireworks.ai")

    if rlor_mgr is None:
        rlor_mgr = TrainerJobManager(api_key=api_key, account_id=account, base_url=base_url)
    if deploy_mgr is None:
        deploy_mgr = DeploymentManager(api_key=api_key, account_id=account, base_url=base_url)

    setup_deployment(deploy_mgr, cfg.deployment, cfg.base_model, cfg.infra)

    # Two RLOR jobs (matches GRPO architecture):
    #   - reference: forward-only, frozen at base model weights
    #   - policy:    trainable, resumed from checkpoint if configured
    ref_extra = list(cfg.infra.extra_args or [])
    if "--forward-only" not in ref_extra:
        ref_extra.append("--forward-only")
    if "--no-compile" not in ref_extra:
        ref_extra.append("--no-compile")

    with ThreadPoolExecutor(max_workers=2) as pool:
        pol_fut = pool.submit(
            create_trainer_job,
            rlor_mgr,
            base_model=cfg.base_model,
            infra=cfg.infra,
            lora_rank=cfg.lora_rank,
            max_seq_len=cfg.max_seq_len,
            learning_rate=cfg.learning_rate,
            grad_accum=cfg.grad_accum,
            display_name="dpo-policy",
            hot_load_deployment_id=cfg.deployment.deployment_id,
        )
        ref_fut = pool.submit(
            create_trainer_job,
            rlor_mgr,
            base_model=cfg.base_model,
            infra=cfg.infra,
            lora_rank=cfg.lora_rank,
            max_seq_len=cfg.max_seq_len,
            learning_rate=cfg.learning_rate,
            grad_accum=cfg.grad_accum,
            display_name="dpo-reference",
            extra_args=ref_extra,
        )
        policy_ep = pol_fut.result()
        reference_ep = ref_fut.result()

    policy = ReconnectableClient(rlor_mgr, policy_ep.job_id, cfg.base_model, cfg.lora_rank)
    reference = ReconnectableClient(rlor_mgr, reference_ep.job_id, cfg.base_model, cfg.lora_rank)

    tracker = WeightSyncer(
        policy_client=policy.inner,
        deploy_mgr=deploy_mgr,
        deployment_id=cfg.deployment.deployment_id,
        base_model=cfg.base_model,
        hotload_timeout=cfg.hotload.hot_load_timeout,
        first_checkpoint_type=cfg.hotload.first_checkpoint_type,
        compression_format=DEFAULT_DELTA_COMPRESSION,
    )

    # Resume policy BEFORE any forward() calls (avoids KeyError in optimizer
    # state mapping).  Reference stays frozen at base model weights.
    step_offset, _ = setup_resume(policy, cfg.resume)
    adam_params = tinker.AdamParams(learning_rate=cfg.learning_rate, **DEFAULT_ADAM)

    # -- Cache reference logprobs (from frozen reference model) ------------

    raw_data = load_preference_dataset(cfg.dataset, cfg.max_pairs)
    if not raw_data:
        raise RuntimeError(f"No data loaded from {cfg.dataset}")

    logger.info("Computing reference logprobs for %d pairs...", len(raw_data))
    ref_cache: dict[int, dict[str, Any]] = {}
    tokenizer_url = policy.endpoint.base_url

    for i, example in enumerate(raw_data):
        chosen_text = extract_text(example["chosen"])
        rejected_text = extract_text(example["rejected"])
        if not chosen_text or not rejected_text:
            continue

        chosen_tokens = encode_text(tokenizer_url, chosen_text)
        rejected_tokens = encode_text(tokenizer_url, rejected_text)
        if len(chosen_tokens) > cfg.max_seq_len or len(rejected_tokens) > cfg.max_seq_len:
            continue
        if len(chosen_tokens) < 2 or len(rejected_tokens) < 2:
            continue

        prompt_len = find_common_prefix_length(chosen_tokens, rejected_tokens)
        chosen_datum = tinker.Datum(
            model_input=tinker.ModelInput.from_ints(chosen_tokens[:-1]),
            loss_fn_inputs={
                "target_tokens": tinker.TensorData(
                    data=chosen_tokens[1:], dtype="int64", shape=[len(chosen_tokens) - 1]
                )
            },
        )
        rejected_datum = tinker.Datum(
            model_input=tinker.ModelInput.from_ints(rejected_tokens[:-1]),
            loss_fn_inputs={
                "target_tokens": tinker.TensorData(
                    data=rejected_tokens[1:], dtype="int64", shape=[len(rejected_tokens) - 1]
                )
            },
        )
        fwd = reference.forward([chosen_datum, rejected_datum], "cross_entropy").result()
        ref_cache[i] = {
            "chosen_tokens": chosen_tokens,
            "rejected_tokens": rejected_tokens,
            "ref_chosen": fwd.loss_fn_outputs[0]["logprobs"].data,
            "ref_rejected": fwd.loss_fn_outputs[1]["logprobs"].data,
            "prompt_len": prompt_len,
        }

    valid_indices = list(ref_cache.keys())
    logger.info("Prepared %d preference pairs", len(valid_indices))
    if not valid_indices:
        raise RuntimeError("No valid pairs after tokenization")

    # -- Training loop -----------------------------------------------------

    step = step_offset
    total_steps = len(valid_indices) * cfg.epochs // cfg.grad_accum
    accum_count = 0
    agg = {"dpo_loss": 0.0, "margin": 0.0, "accuracy": 0.0, "count": 0}

    for epoch in range(cfg.epochs):
        for pair_idx, idx in enumerate(valid_indices):
            cached = ref_cache[idx]
            response_start = max(0, cached["prompt_len"] - 1)
            chosen_tokens = cached["chosen_tokens"]
            rejected_tokens = cached["rejected_tokens"]

            chosen_datum = tinker.Datum(
                model_input=tinker.ModelInput.from_ints(chosen_tokens[:-1]),
                loss_fn_inputs={
                    "target_tokens": tinker.TensorData(
                        data=chosen_tokens[1:], dtype="int64", shape=[len(chosen_tokens) - 1]
                    )
                },
            )
            rejected_datum = tinker.Datum(
                model_input=tinker.ModelInput.from_ints(rejected_tokens[:-1]),
                loss_fn_inputs={
                    "target_tokens": tinker.TensorData(
                        data=rejected_tokens[1:], dtype="int64", shape=[len(rejected_tokens) - 1]
                    )
                },
            )

            loss_fn = make_dpo_loss_fn(cached["ref_chosen"], cached["ref_rejected"], response_start, cfg.beta)
            result = policy.forward_backward_custom([chosen_datum, rejected_datum], loss_fn).result()

            metrics = result.metrics
            agg["dpo_loss"] += metrics["dpo_loss"]
            agg["margin"] += metrics["margin"]
            agg["accuracy"] += metrics["accuracy"]
            agg["count"] += 1
            accum_count += 1

            # Optimizer step
            if accum_count >= cfg.grad_accum:
                policy.optim_step(adam_params).result()
                step += 1
                accum_count = 0

                n = agg["count"]
                if n > 0:
                    avg_loss = agg["dpo_loss"] / n
                    avg_margin = agg["margin"] / n
                    avg_acc = agg["accuracy"] / n
                    logger.info(
                        "Step %d/%d | Loss: %.4f | Margin: %+.4f | Acc: %.1f%%",
                        step,
                        total_steps,
                        avg_loss,
                        avg_margin,
                        avg_acc * 100,
                    )
                    log_metrics_json(step, dpo_loss=avg_loss, margin=avg_margin, accuracy=avg_acc)
                    wandb_log(
                        {
                            "train/dpo_loss": avg_loss,
                            "train/margin": avg_margin,
                            "train/accuracy": avg_acc,
                            "train/epoch": epoch + 1,
                        },
                        step,
                    )

                hl = cfg.hotload
                if hl.hot_load_interval > 0 and step % hl.hot_load_interval == 0:
                    tracker.save_and_hotload(f"step-{step}")
                if hl.dcp_save_interval > 0 and step % hl.dcp_save_interval == 0:
                    tracker.save_dcp(f"step-{step}")

                agg = {"dpo_loss": 0.0, "margin": 0.0, "accuracy": 0.0, "count": 0}

        # Flush remaining gradients
        if accum_count > 0:
            policy.optim_step(adam_params).result()
            step += 1
            accum_count = 0

    # -- Final checkpoint --------------------------------------------------

    hl = cfg.hotload
    if step > step_offset and (hl.hot_load_interval > 0 or hl.dcp_save_interval > 0):
        tracker.save_and_hotload(f"final-step-{step}")

    logger.info("Training complete: %d optimizer steps (%d new)", step, step - step_offset)
    wandb_finish()
    return {"steps": step, "policy_job_id": policy.job_id, "reference_job_id": reference.job_id}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    main(Config())
