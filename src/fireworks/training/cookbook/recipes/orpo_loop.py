#!/usr/bin/env python3
"""Minimal ORPO (Odds Ratio Preference Optimization) training loop.

A readable, modifiable preference-optimization loop using the Fireworks RLOR API.
Unlike DPO, ORPO does *not* require a reference model -- it combines SFT loss on
the chosen response with an odds-ratio loss contrasting chosen vs rejected, all
from a single policy model.

Architecture:
    - Single RLOR job: forward_backward_custom + optim_step (trainable)
    - No reference model needed (key advantage over DPO)

Loss:
    L_ORPO = L_SFT(chosen) + lambda * L_OR
    L_SFT  = -mean(logprobs_chosen)   (cross-entropy on chosen response)
    L_OR   = -log(sigmoid(log(odds_chosen / odds_rejected)))

Dataset format (JSONL, preference pairs -- same as DPO):
    {"chosen": {"messages": [...]}, "rejected": {"messages": [...]}}

Usage:
    export FIREWORKS_API_KEY=...
    export FIREWORKS_ACCOUNT_ID=...
    python cookbook/recipes/orpo_loop.py --dataset /path/to/preference_data.jsonl

Default config targets Qwen3-235B on 2 nodes (16 GPUs) with expert parallelism.
Adjust Config below for other models/setups.
"""

from __future__ import annotations

import os
import random
import logging
from dataclasses import field, dataclass

import tinker

from fireworks.training.sdk import DeploymentManager, TrainerJobManager
from fireworks.training.cookbook.utils import (
    DEFAULT_ADAM,
    InfraConfig,
    WandBConfig,
    DeployConfig,
    ResumeConfig,
    HotloadConfig,
    ReconnectableClient,
    wandb_log,
    setup_wandb,
    setup_resume,
    wandb_finish,
    validate_config,
    log_metrics_json,
    make_orpo_loss_fn,
    setup_deployment,
    create_trainer_job,
    load_preference_dataset,
    find_common_prefix_length,
)
from fireworks.training.sdk.deployment import DEFAULT_DELTA_COMPRESSION
from fireworks.training.sdk.weight_syncer import WeightSyncer

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------


@dataclass
class Config:
    # -- Model ---------------------------------------------------------------
    base_model: str = "accounts/fireworks/models/qwen3-235b-a22b-instruct-2507"
    dataset: str = ""
    tokenizer_model: str = ""  # HuggingFace model name, e.g. "Qwen/Qwen3-235B-A22B-Instruct-2507"

    # -- ORPO hyper-parameters -----------------------------------------------
    orpo_lambda: float = 1.0  # weight for the odds-ratio loss term
    learning_rate: float = 1e-5
    epochs: int = 1
    grad_accum: int = 4
    max_seq_len: int = 128_000
    max_pairs: int | None = None
    lora_rank: int = 0

    # -- Infrastructure (Qwen3-235B defaults from firectl) -------------------
    infra: InfraConfig = field(
        default_factory=lambda: InfraConfig(
            region="US_VIRGINIA_1",
            node_count=2,
            skip_validations=True,
            extra_args=[
                "--cp=16",
                "--ep-comm-backend=deepep",
                "--ep=8",
                "--no-compile",
                "--profile",
                "--enable-optimizer-offload",
                "--profile-active-ops=2",
            ],
        )
    )
    deployment: DeployConfig = field(
        default_factory=lambda: DeployConfig(create_deployment=False)
    )
    hotload: HotloadConfig = field(
        default_factory=lambda: HotloadConfig(hot_load_interval=0)
    )
    wandb: WandBConfig = field(
        default_factory=lambda: WandBConfig(
            project="dsv3-training",
            entity="myh97",
        )
    )
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

    validate_config(
        cfg.base_model, cfg.dataset, cfg.hotload, cfg.deployment, cfg.infra, cfg.resume
    )
    if not cfg.tokenizer_model:
        raise ValueError(
            "Config.tokenizer_model is required for client-side tokenization. "
            "Set it to the HuggingFace model name "
            "(e.g. 'Qwen/Qwen3-235B-A22B-Instruct-2507')."
        )
    setup_wandb(
        cfg.wandb,
        {
            "orpo_lambda": cfg.orpo_lambda,
            "lr": cfg.learning_rate,
            "epochs": cfg.epochs,
        },
    )

    # -- Setup infrastructure ------------------------------------------------

    api_key = os.environ["FIREWORKS_API_KEY"]
    account = os.environ.get("FIREWORKS_ACCOUNT_ID", "")
    base_url = os.environ.get("FIREWORKS_BASE_URL", "https://api.fireworks.ai")

    if rlor_mgr is None:
        rlor_mgr = TrainerJobManager(
            api_key=api_key, account_id=account, base_url=base_url
        )
    if deploy_mgr is None:
        deploy_mgr = DeploymentManager(
            api_key=api_key, account_id=account, base_url=base_url
        )

    setup_deployment(deploy_mgr, cfg.deployment, cfg.base_model, cfg.infra)

    # Single RLOR job -- ORPO needs no reference model
    endpoint = create_trainer_job(
        rlor_mgr,
        base_model=cfg.base_model,
        infra=cfg.infra,
        lora_rank=cfg.lora_rank,
        max_seq_len=cfg.max_seq_len,
        learning_rate=cfg.learning_rate,
        grad_accum=cfg.grad_accum,
        display_name="orpo-trainer",
        hot_load_deployment_id=cfg.deployment.deployment_id,
    )
    client = ReconnectableClient(
        rlor_mgr, endpoint.job_id, cfg.base_model, cfg.lora_rank
    )

    weight_syncer = WeightSyncer(
        policy_client=client.inner,
        deploy_mgr=deploy_mgr,
        deployment_id=cfg.deployment.deployment_id,
        base_model=cfg.base_model,
        hotload_timeout=cfg.hotload.hot_load_timeout,
        first_checkpoint_type=cfg.hotload.first_checkpoint_type,
        compression_format=DEFAULT_DELTA_COMPRESSION,
    )

    step_offset, _ = setup_resume(client, cfg.resume)
    adam_params = tinker.AdamParams(learning_rate=cfg.learning_rate, **DEFAULT_ADAM)

    # -- Prepare data --------------------------------------------------------

    import transformers

    tokenizer = transformers.AutoTokenizer.from_pretrained(
        cfg.tokenizer_model, trust_remote_code=True
    )

    raw_data = load_preference_dataset(cfg.dataset, cfg.max_pairs)
    if not raw_data:
        raise RuntimeError(f"No data loaded from {cfg.dataset}")

    logger.info("Tokenizing %d preference pairs...", len(raw_data))
    pair_cache: list[dict] = []
    filtered_count = 0

    for example in raw_data:
        chosen_msgs = example["chosen"].get("messages", [])
        rejected_msgs = example["rejected"].get("messages", [])
        if not chosen_msgs or not rejected_msgs:
            continue

        chosen_tokens = tokenizer.apply_chat_template(
            chosen_msgs, tokenize=True, return_dict=False
        )
        rejected_tokens = tokenizer.apply_chat_template(
            rejected_msgs, tokenize=True, return_dict=False
        )

        if (
            len(chosen_tokens) > cfg.max_seq_len
            or len(rejected_tokens) > cfg.max_seq_len
        ):
            filtered_count += 1
            continue
        if len(chosen_tokens) < 2 or len(rejected_tokens) < 2:
            continue

        # Prompt = common prefix between chosen/rejected token sequences
        prompt_len = find_common_prefix_length(chosen_tokens, rejected_tokens)

        pair_cache.append(
            {
                "chosen_tokens": chosen_tokens,
                "rejected_tokens": rejected_tokens,
                "prompt_len": prompt_len,
            }
        )

    if filtered_count > 0:
        logger.info(
            "Seq-length filter: %d/%d pairs filtered (chosen or rejected > %d tokens)",
            filtered_count,
            len(raw_data),
            cfg.max_seq_len,
        )
    logger.info("Prepared %d preference pairs", len(pair_cache))
    if not pair_cache:
        raise RuntimeError("No valid pairs after tokenization")

    # -- Training loop -------------------------------------------------------

    step = step_offset
    total_steps = len(pair_cache) * cfg.epochs // cfg.grad_accum
    accum_count = 0
    agg = {
        "orpo_loss": 0.0,
        "sft_loss": 0.0,
        "or_loss": 0.0,
        "log_odds_ratio": 0.0,
        "accuracy": 0.0,
        "count": 0,
    }

    for epoch in range(cfg.epochs):
        random.shuffle(pair_cache)
        for pair in pair_cache:
            chosen_tokens = pair["chosen_tokens"]
            rejected_tokens = pair["rejected_tokens"]
            response_start = max(0, pair["prompt_len"] - 1)

            chosen_datum = tinker.Datum(
                model_input=tinker.ModelInput.from_ints(chosen_tokens[:-1]),
                loss_fn_inputs={
                    "target_tokens": tinker.TensorData(
                        data=chosen_tokens[1:],
                        dtype="int64",
                        shape=[len(chosen_tokens) - 1],
                    )
                },
            )
            rejected_datum = tinker.Datum(
                model_input=tinker.ModelInput.from_ints(rejected_tokens[:-1]),
                loss_fn_inputs={
                    "target_tokens": tinker.TensorData(
                        data=rejected_tokens[1:],
                        dtype="int64",
                        shape=[len(rejected_tokens) - 1],
                    )
                },
            )

            loss_fn = make_orpo_loss_fn(response_start, cfg.orpo_lambda)
            result = client.forward_backward_custom(
                [chosen_datum, rejected_datum], loss_fn
            ).result()

            metrics = result.metrics
            agg["orpo_loss"] += metrics["orpo_loss"]
            agg["sft_loss"] += metrics["sft_loss"]
            agg["or_loss"] += metrics["or_loss"]
            agg["log_odds_ratio"] += metrics["log_odds_ratio"]
            agg["accuracy"] += metrics["accuracy"]
            agg["count"] += 1
            accum_count += 1

            # Optimizer step
            if accum_count >= cfg.grad_accum:
                client.optim_step(adam_params).result()
                step += 1
                accum_count = 0

                n = agg["count"]
                if n > 0:
                    avg = {k: agg[k] / n for k in agg if k != "count"}
                    logger.info(
                        "Step %d/%d | ORPO: %.4f | SFT: %.4f | OR: %.4f | "
                        "LogOR: %+.4f | Acc: %.1f%%",
                        step,
                        total_steps,
                        avg["orpo_loss"],
                        avg["sft_loss"],
                        avg["or_loss"],
                        avg["log_odds_ratio"],
                        avg["accuracy"] * 100,
                    )
                    log_metrics_json(step, **avg)
                    wandb_log(
                        {
                            "train/orpo_loss": avg["orpo_loss"],
                            "train/sft_loss": avg["sft_loss"],
                            "train/or_loss": avg["or_loss"],
                            "train/log_odds_ratio": avg["log_odds_ratio"],
                            "train/accuracy": avg["accuracy"],
                            "train/epoch": epoch + 1,
                        },
                        step,
                    )

                hl = cfg.hotload
                if hl.hot_load_interval > 0 and step % hl.hot_load_interval == 0:
                    weight_syncer.save_and_hotload(f"step-{step}")
                if hl.dcp_save_interval > 0 and step % hl.dcp_save_interval == 0:
                    weight_syncer.save_dcp(f"step-{step}")

                agg = {k: 0.0 for k in agg}

        # Flush remaining gradients at end of epoch
        if accum_count > 0:
            client.optim_step(adam_params).result()
            step += 1
            accum_count = 0

    # -- Final checkpoint ----------------------------------------------------

    hl = cfg.hotload
    if step > step_offset and (hl.hot_load_interval > 0 or hl.dcp_save_interval > 0):
        weight_syncer.save_and_hotload(f"final-step-{step}")

    # Always save a full base checkpoint so the trained weights are persisted
    # on the trainer's GCS storage (HF safetensors format).
    if step > step_offset:
        logger.info("Saving final base checkpoint (step %d)...", step)
        client.inner.save_weights_for_sampler_ext(
            f"final-step-{step}", checkpoint_type="base"
        ).result(timeout=1800)
        logger.info("Final base checkpoint saved.")

    logger.info(
        "Training complete: %d optimizer steps (%d new)", step, step - step_offset
    )
    wandb_finish()
    return {"steps": step, "job_id": client.job_id}


if __name__ == "__main__":
    import os
    import pathlib

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )

    # Default dataset: sample_orpo_data.jsonl next to this script
    default_dataset = str(pathlib.Path(__file__).parent / "sample_orpo_data.jsonl")
    cfg = Config(
        dataset=os.environ.get("ORPO_DATASET", default_dataset),
        tokenizer_model=os.environ.get("ORPO_TOKENIZER", "Qwen/Qwen3-235B-A22B-Instruct-2507"),
    )
    main(cfg)
