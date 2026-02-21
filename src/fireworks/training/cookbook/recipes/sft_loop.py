#!/usr/bin/env python3
"""Minimal SFT (Supervised Fine-Tuning) training loop.

A readable, modifiable fine-tuning loop using the Fireworks RLOR API.
Uses a single RLOR trainer job with cross-entropy loss on response tokens.

Dataset format (JSONL, OpenAI chat format):
    {"messages": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}

Usage:
    export FIREWORKS_API_KEY=...
    export FIREWORKS_ACCOUNT_ID=...
    python cookbook/recipes/sft_loop.py --dataset /path/to/chat_data.jsonl
"""

from __future__ import annotations

import logging
import os
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
    log_metrics_json,
    make_sft_loss_fn,
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
    tokenizer_model: str = ""  # HuggingFace model name for chat template, e.g. "Qwen/Qwen3-1.7B"

    learning_rate: float = 1e-4
    epochs: int = 3
    grad_accum: int = 4
    max_seq_len: int = 4096
    max_examples: int | None = None
    lora_rank: int = 0

    infra: InfraConfig = field(default_factory=InfraConfig)
    deployment: DeployConfig = field(default_factory=lambda: DeployConfig(create_deployment=False))
    hotload: HotloadConfig = field(default_factory=lambda: HotloadConfig(hot_load_interval=0))
    wandb: WandBConfig = field(default_factory=lambda: WandBConfig(project="sft-tinker"))
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
    setup_wandb(cfg.wandb, {"lr": cfg.learning_rate, "epochs": cfg.epochs, "grad_accum": cfg.grad_accum})

    if not cfg.tokenizer_model:
        raise ValueError(
            "Config.tokenizer_model is required for chat template formatting. "
            "Set it to the HuggingFace model name (e.g. 'Qwen/Qwen3-1.7B')."
        )

    # -- Setup infrastructure ----------------------------------------------

    api_key = os.environ["FIREWORKS_API_KEY"]
    account = os.environ.get("FIREWORKS_ACCOUNT_ID", "")
    base_url = os.environ.get("FIREWORKS_BASE_URL", "https://api.fireworks.ai")

    if rlor_mgr is None:
        rlor_mgr = TrainerJobManager(api_key=api_key, account_id=account, base_url=base_url)
    if deploy_mgr is None:
        deploy_mgr = DeploymentManager(api_key=api_key, account_id=account, base_url=base_url)

    setup_deployment(deploy_mgr, cfg.deployment, cfg.base_model, cfg.infra)

    endpoint = create_trainer_job(
        rlor_mgr,
        base_model=cfg.base_model,
        infra=cfg.infra,
        lora_rank=cfg.lora_rank,
        max_seq_len=cfg.max_seq_len,
        learning_rate=cfg.learning_rate,
        grad_accum=cfg.grad_accum,
        display_name="sft-trainer",
        hot_load_deployment_id=cfg.deployment.deployment_id,
    )
    client = ReconnectableClient(rlor_mgr, endpoint.job_id, cfg.base_model, cfg.lora_rank)

    tracker = WeightSyncer(
        policy_client=client.inner,
        deploy_mgr=deploy_mgr,
        deployment_id=cfg.deployment.deployment_id,
        base_model=cfg.base_model,
        hotload_timeout=cfg.hotload.hot_load_timeout,
        first_checkpoint_type=cfg.hotload.first_checkpoint_type,
        compression_format=DEFAULT_DELTA_COMPRESSION,
    )

    # -- Prepare data ------------------------------------------------------

    import json
    import transformers

    tokenizer = transformers.AutoTokenizer.from_pretrained(cfg.tokenizer_model)
    tokenizer_url = client.endpoint.base_url

    raw_data: List[Dict[str, Any]] = []
    with open(cfg.dataset) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            raw_data.append(json.loads(line))
            if cfg.max_examples and len(raw_data) >= cfg.max_examples:
                break
    logger.info("Loaded %d examples from %s", len(raw_data), cfg.dataset)

    training_data: List[Dict[str, Any]] = []
    for row in raw_data:
        messages = row.get("messages", [])
        if not messages:
            continue

        full_text = tokenizer.apply_chat_template(messages, tokenize=False)
        prompt_messages = [m for m in messages if m.get("role") != "assistant"]
        prompt_text = tokenizer.apply_chat_template(prompt_messages, tokenize=False, add_generation_prompt=True)

        full_tokens = encode_text(tokenizer_url, full_text)
        prompt_tokens = encode_text(tokenizer_url, prompt_text)

        if len(full_tokens) > cfg.max_seq_len or len(full_tokens) < 2:
            continue
        training_data.append({"tokens": full_tokens, "prompt_len": len(prompt_tokens)})

    logger.info("Prepared %d training examples", len(training_data))
    if not training_data:
        raise RuntimeError("No valid training examples after tokenization")

    step_offset, _ = setup_resume(client, cfg.resume)
    adam_params = tinker.AdamParams(learning_rate=cfg.learning_rate, **DEFAULT_ADAM)

    # -- Training loop -----------------------------------------------------

    step = step_offset
    total_steps = len(training_data) * cfg.epochs // cfg.grad_accum
    accum = 0
    agg_loss = 0.0
    agg_ppl = 0.0
    agg_count = 0

    for epoch in range(cfg.epochs):
        for ex in training_data:
            tokens = ex["tokens"]
            prompt_len = ex["prompt_len"]

            datum = tinker.Datum(
                model_input=tinker.ModelInput.from_ints(tokens[:-1]),
                loss_fn_inputs={
                    "target_tokens": tinker.TensorData(data=tokens[1:], dtype="int64", shape=[len(tokens) - 1]),
                },
            )
            loss_fn = make_sft_loss_fn(response_start=max(0, prompt_len - 1), target_tokens=tokens[1:])
            result = client.forward_backward_custom([datum], loss_fn).result()

            agg_loss += result.metrics["ce_loss"]
            agg_ppl += result.metrics["ppl"]
            agg_count += 1
            accum += 1

            # Optimizer step
            if accum >= cfg.grad_accum:
                client.optim_step(adam_params).result()
                step += 1
                accum = 0

                if agg_count > 0:
                    avg_loss = agg_loss / agg_count
                    avg_ppl = agg_ppl / agg_count
                    logger.info("Step %d/%d | Loss: %.4f | PPL: %.2f", step, total_steps, avg_loss, avg_ppl)
                    log_metrics_json(step, ce_loss=avg_loss, ppl=avg_ppl)
                    wandb_log({"train/ce_loss": avg_loss, "train/ppl": avg_ppl}, step)

                hl = cfg.hotload
                if hl.hot_load_interval > 0 and step % hl.hot_load_interval == 0:
                    tracker.save_and_hotload(f"step-{step}")
                if hl.dcp_save_interval > 0 and step % hl.dcp_save_interval == 0:
                    tracker.save_dcp(f"step-{step}")

                agg_loss = agg_ppl = agg_count = 0

        # Flush remaining gradients
        if accum > 0:
            client.optim_step(adam_params).result()
            step += 1
            accum = 0

    # -- Final checkpoint --------------------------------------------------

    if step > step_offset:
        tracker.save_dcp(f"step-{step}")
    if cfg.hotload.hot_load_interval > 0 or cfg.deployment.deployment_id:
        tracker.save_and_hotload(f"final-step-{step}")

    logger.info("Training complete: %d optimizer steps", step)
    wandb_finish()
    return {"steps": step, "job_id": client.job_id}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    main(Config())
