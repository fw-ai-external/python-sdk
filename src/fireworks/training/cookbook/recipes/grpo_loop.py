#!/usr/bin/env python3
"""Minimal GRPO training loop.

A readable, modifiable RL training loop using the Fireworks RLOR API.
Fork this script and customise the reward function, loss, or sampling
strategy to fit your task.

Architecture:
    - Policy RLOR job:    forward_backward_custom + optim_step (trainable)
    - Reference RLOR job: forward only (frozen, for KL divergence)
    - Deployment:         sampling (completions, token-in/token-out) + hotload

Each optimizer step collects ``prompts_per_step`` prompts, batches all
datums into one ``forward_backward_custom`` call, then calls ``optim_step``
once (1:1 pattern).  This minimizes pipeline-parallel bubble overhead.

Usage:
    export FIREWORKS_API_KEY=...
    export FIREWORKS_ACCOUNT_ID=...
    python cookbook/recipes/grpo_loop.py
"""

from __future__ import annotations

import os
import re
import logging
from typing import List, Optional
from dataclasses import field, dataclass
from concurrent.futures import ThreadPoolExecutor

import tinker
import transformers

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
    setup_deployment,
    compute_advantages,
    create_trainer_job,
    load_jsonl_dataset,
    resolve_and_apply_shape,
)
from fireworks.training.sdk.deployment import DeploymentSampler
from fireworks.training.cookbook.utils.rl import (
    ISConfig,
    PromptGroup,
    make_grpo_loss_fn,
    make_tis_weights_fn,
)
from fireworks.training.sdk.weight_syncer import WeightSyncer
from fireworks.training.cookbook.utils.rl.pp import compute_pp_recommendation
from fireworks.training.cookbook.utils.rl.dapo import DAPOConfig, make_dapo_loss_fn
from fireworks.training.cookbook.utils.rl.gspo import GSPOConfig, make_gspo_loss_fn
from fireworks.training.cookbook.utils.rl.router_replay import build_r3_routing_matrices

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------


@dataclass
class Config:
    base_model: str = "accounts/fireworks/models/qwen3-8b"
    dataset: str = "https://raw.githubusercontent.com/eval-protocol/python-sdk/main/development/gsm8k_sample.jsonl"

    learning_rate: float = 1e-5
    kl_beta: float = 0.001
    group_size: int = 4
    max_completion_tokens: int = 1024
    temperature: float = 1.0
    epochs: int = 1
    max_rows: int = 100
    max_seq_len: int = 4096
    lora_rank: int = 0

    prompts_per_step: int | None = None
    """Number of prompts per optimizer step. All prompts are batched into one
    ``forward_backward_custom`` call (1:1 pattern). Auto-derived from the
    training shape when ``None`` and PP > 1. Defaults to 1 otherwise."""

    router_replay: bool = False
    router_replay_completion_only: bool = True

    policy_loss: str = "grpo"
    """Base policy gradient loss: ``"grpo"`` (vanilla REINFORCE + KL),
    ``"dapo"`` (token-level PPO clipping), or ``"gspo"`` (sequence-level clipped PPO)."""

    tis_enabled: bool = False
    """Enable TIS (Truncated Importance Sampling) correction on top of the
    base ``policy_loss``.  Orthogonal -- composes with any loss type."""

    tis: ISConfig = field(default_factory=ISConfig)
    dapo: DAPOConfig = field(default_factory=DAPOConfig)
    gspo: GSPOConfig = field(default_factory=GSPOConfig)

    infra: InfraConfig = field(default_factory=InfraConfig)
    deployment: DeployConfig = field(default_factory=DeployConfig)
    hotload: HotloadConfig = field(default_factory=HotloadConfig)
    wandb: WandBConfig = field(default_factory=lambda: WandBConfig(project="grpo-tinker"))
    resume: ResumeConfig = field(default_factory=ResumeConfig)


# ---------------------------------------------------------------------------
# Reward function -- customise this for your task
# ---------------------------------------------------------------------------


def extract_answer(text: str) -> Optional[str]:
    match = re.search(r"<answer>(.*?)</answer>", text, re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    digits = re.search(r"(-?\d+)", match.group(1))
    return digits.group(1) if digits else None


def reward_fn(completion: str, row: dict) -> float:
    """Return 1.0 if the model's numeric answer matches the ground truth."""
    predicted = extract_answer(completion)
    truth = extract_answer(str(row.get("ground_truth", "")))
    if predicted is None or truth is None:
        return 0.0
    return 1.0 if predicted == truth else 0.0


# ---------------------------------------------------------------------------
# Loss builder
# ---------------------------------------------------------------------------


def _build_loss_fn(cfg: Config):
    """Return a loss-builder callback for :func:`train_step`."""

    def build(
        advantages: List[float],
        ref_logprobs: List[List[float]],
        prompt_lens: List[int],
        inf_logprobs: List[List[float]],
    ):
        tis_wf = None
        if cfg.tis_enabled:
            tis_wf = make_tis_weights_fn(inf_logprobs, prompt_lens, cfg.tis)

        if cfg.policy_loss == "dapo":
            return make_dapo_loss_fn(
                advantages, ref_logprobs, inf_logprobs,
                prompt_lens, cfg.dapo, tis_weights_fn=tis_wf,
            )
        elif cfg.policy_loss == "gspo":
            return make_gspo_loss_fn(
                advantages, ref_logprobs, inf_logprobs,
                prompt_lens, cfg.gspo, tis_weights_fn=tis_wf,
            )
        else:
            return make_grpo_loss_fn(
                advantages, ref_logprobs,
                prompt_lens, cfg.kl_beta, tis_weights_fn=tis_wf,
            )

    return build


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
    if not cfg.deployment.tokenizer_model:
        raise ValueError(
            "deployment.tokenizer_model is required for client-side tokenization. "
            "Set it to the HuggingFace model name (e.g. 'Qwen/Qwen3-1.7B')."
        )
    setup_wandb(cfg.wandb, {"group_size": cfg.group_size, "kl_beta": cfg.kl_beta, "lr": cfg.learning_rate})

    # -- Setup infrastructure -----------------------------------------------

    api_key = os.environ["FIREWORKS_API_KEY"]
    account = os.environ.get("FIREWORKS_ACCOUNT_ID", "")
    base_url = os.environ.get("FIREWORKS_BASE_URL", "https://api.fireworks.ai")

    if rlor_mgr is None:
        rlor_mgr = TrainerJobManager(api_key=api_key, account_id=account, base_url=base_url)
    if deploy_mgr is None:
        deploy_mgr = DeploymentManager(api_key=api_key, account_id=account, base_url=base_url)

    profile = None
    if cfg.infra.training_shape_id:
        profile = resolve_and_apply_shape(rlor_mgr, cfg.base_model, cfg.infra, cfg.deployment)

    prompts_per_step = cfg.prompts_per_step or 1

    if profile and profile.pipeline_parallelism > 1:
        pp_rec = compute_pp_recommendation(profile, cfg.group_size)
        logger.info(
            "PP recommendation: set prompts_per_step=%d for optimal efficiency (current=%d)",
            pp_rec.recommended_prompts_per_step, prompts_per_step,
        )

    ref_extra = list(cfg.infra.extra_args or [])
    if "--forward-only" not in ref_extra:
        ref_extra.append("--forward-only")
    if "--no-compile" not in ref_extra:
        ref_extra.append("--no-compile")

    dep_info = setup_deployment(deploy_mgr, cfg.deployment, cfg.base_model, cfg.infra)

    with ThreadPoolExecutor(max_workers=2) as pool:
        pol_fut = pool.submit(
            create_trainer_job, rlor_mgr,
            base_model=cfg.base_model, infra=cfg.infra,
            lora_rank=cfg.lora_rank, max_seq_len=cfg.max_seq_len,
            learning_rate=cfg.learning_rate, grad_accum=1,
            display_name="grpo-policy",
            hot_load_deployment_id=cfg.deployment.deployment_id,
        )
        ref_fut = pool.submit(
            create_trainer_job, rlor_mgr,
            base_model=cfg.base_model, infra=cfg.infra,
            lora_rank=cfg.lora_rank, max_seq_len=cfg.max_seq_len,
            learning_rate=cfg.learning_rate, grad_accum=1,
            display_name="grpo-reference", extra_args=ref_extra,
        )
        policy_ep = pol_fut.result()
        reference_ep = ref_fut.result()

    policy = ReconnectableClient(rlor_mgr, policy_ep.job_id, cfg.base_model, cfg.lora_rank)
    reference = ReconnectableClient(rlor_mgr, reference_ep.job_id, cfg.base_model, cfg.lora_rank)

    inference_model = dep_info.inference_model if dep_info else cfg.base_model
    tokenizer = transformers.AutoTokenizer.from_pretrained(cfg.deployment.tokenizer_model, trust_remote_code=True)
    sampler = DeploymentSampler(
        inference_url=deploy_mgr.inference_url,
        model=inference_model, api_key=api_key, tokenizer=tokenizer,
    )
    weight_syncer = WeightSyncer(
        policy_client=policy.inner, deploy_mgr=deploy_mgr,
        deployment_id=cfg.deployment.deployment_id, base_model=cfg.base_model,
        hotload_timeout=cfg.hotload.hot_load_timeout,
        first_checkpoint_type=cfg.hotload.first_checkpoint_type,
    )

    step_offset, _ = setup_resume(policy, cfg.resume)
    if cfg.hotload.hot_load_before_training and cfg.deployment.deployment_id:
        name = f"resume-{step_offset}-base" if step_offset > 0 else "step-0-base"
        weight_syncer.save_and_hotload(name, checkpoint_type="base")

    # -- Load data -----------------------------------------------------------

    dataset = load_jsonl_dataset(cfg.dataset, cfg.max_rows)
    adam_params = tinker.AdamParams(learning_rate=cfg.learning_rate, **DEFAULT_ADAM)
    build_loss = _build_loss_fn(cfg)
    needs_inf_lp = cfg.policy_loss in {"dapo", "gspo"} or cfg.tis_enabled

    # -- Training loop -------------------------------------------------------
    #
    # 1. Collect: sample + reward + ref forward for prompts_per_step prompts
    # 2. Train:   one forward_backward_custom + one optim_step on all datums
    # 3. Log + hotload

    global_step = step_offset
    agg = {"reward": 0.0, "accuracy": 0.0, "kl": 0.0, "count": 0}
    seq_filter_stats = {"prompts_filtered": 0, "completions_filtered": 0, "total_prompts": 0}
    prompt_buffer: List[PromptGroup] = []

    def _do_train_step():
        """Train on buffered prompts: forward_backward + optim_step + log + hotload."""
        nonlocal global_step, agg, prompt_buffer

        # -- Concatenate all prompt groups into one batch ---
        combined_data: List[tinker.Datum] = []
        combined_adv: List[float] = []
        combined_ref: List[List[float]] = []
        combined_prompt_lens: List[int] = []
        combined_inf_lp: List[List[float]] = []

        for pg in prompt_buffer:
            combined_data.extend(pg.data)
            combined_adv.extend(pg.advantages)
            combined_ref.extend(pg.ref_logprobs)
            combined_prompt_lens.extend([pg.prompt_len] * len(pg.data))
            combined_inf_lp.extend(pg.inf_logprobs)

        loss_fn = build_loss(combined_adv, combined_ref, combined_prompt_lens, combined_inf_lp)

        # -- One forward_backward + one optim_step (1:1 pattern) ---
        fwd_bwd = policy.forward_backward_custom(combined_data, loss_fn).result()
        policy.optim_step(adam_params).result()
        global_step += 1

        # -- Aggregate metrics ---
        for pg in prompt_buffer:
            agg["reward"] += sum(pg.rewards) / len(pg.rewards)
            agg["accuracy"] += sum(1 for r in pg.rewards if r > 0.5) / len(pg.rewards)
        agg["kl"] += fwd_bwd.metrics.get("mean_kl", 0.0)
        agg["count"] += len(prompt_buffer)
        prompt_buffer = []

        n = agg["count"]
        if n > 0:
            avg_reward = agg["reward"] / n
            avg_acc = agg["accuracy"] / n
            avg_kl = agg["kl"] / n
            logger.info(
                "Step %d | Reward: %.3f | Acc: %.1f%% | KL: %.4f",
                global_step, avg_reward, avg_acc * 100, avg_kl,
            )
            log_metrics_json(global_step, reward=avg_reward, accuracy=avg_acc, kl=avg_kl)
            wandb_log({"train/reward": avg_reward, "train/accuracy": avg_acc, "train/kl": avg_kl}, global_step)

        # -- Hotload ---
        if cfg.hotload.hot_load_interval > 0 and global_step % cfg.hotload.hot_load_interval == 0:
            weight_syncer.save_and_hotload(f"step-{global_step}")
        if cfg.hotload.dcp_save_interval > 0 and global_step % cfg.hotload.dcp_save_interval == 0:
            weight_syncer.save_dcp(f"step-{global_step}")

        agg = {"reward": 0.0, "accuracy": 0.0, "kl": 0.0, "count": 0}

    for _epoch in range(cfg.epochs):
        for prompt_idx, row in enumerate(dataset):
            messages = row.get("messages", [])
            input_messages = [m for m in messages if m.get("role") != "assistant"]
            if not input_messages:
                continue
            seq_filter_stats["total_prompts"] += 1

            # -- Sample completions from deployment ---
            sample_kwargs: dict = dict(
                messages=input_messages, n=cfg.group_size,
                max_tokens=cfg.max_completion_tokens, temperature=cfg.temperature,
                max_seq_len=cfg.max_seq_len,
            )
            if cfg.router_replay:
                sample_kwargs.update(include_routing_matrix=True, echo=True, logprobs=True)
            if needs_inf_lp:
                sample_kwargs["logprobs"] = True
            try:
                sampled = sampler.sample_with_tokens(**sample_kwargs)
            except Exception as e:
                logger.warning("Sampling failed for prompt %d: %s", prompt_idx, e)
                continue
            if not sampled:
                seq_filter_stats["prompts_filtered"] += 1
                continue
            if len(sampled) < cfg.group_size:
                seq_filter_stats["completions_filtered"] += cfg.group_size - len(sampled)
                continue

            # -- Compute rewards & advantages ---
            ground_truth = row.get("ground_truth", "")
            rewards = [reward_fn(s.text, {"ground_truth": ground_truth}) for s in sampled]
            if len(set(rewards)) == 1:
                continue
            advantages = compute_advantages(rewards)

            # -- Build datums ---
            prompt_len = sampled[0].prompt_len
            data: List[tinker.Datum] = []
            ref_data: List[tinker.Datum] = []
            adv_filtered: List[float] = []
            inf_logprobs_aligned: List[List[float]] = []

            for idx, s in enumerate(sampled):
                tokens = s.full_tokens
                if len(tokens) < 2:
                    continue
                model_input_len = len(tokens) - 1

                rm = None
                if cfg.router_replay:
                    rm = build_r3_routing_matrices(
                        s.routing_matrices, s.prompt_len, model_input_len,
                        completion_only=cfg.router_replay_completion_only,
                    )

                policy_datum = tinker.Datum(
                    model_input=tinker.ModelInput.from_ints(tokens[:-1], routing_matrices=rm),
                    loss_fn_inputs={
                        "target_tokens": tinker.TensorData(data=tokens[1:], dtype="int64", shape=[model_input_len]),
                    },
                )
                # Reference should not replay
                ref_datum = tinker.Datum(
                    model_input=tinker.ModelInput.from_ints(tokens[:-1]),
                    loss_fn_inputs={
                        "target_tokens": tinker.TensorData(data=tokens[1:], dtype="int64", shape=[model_input_len]),
                    },
                )
                data.append(policy_datum)
                ref_data.append(ref_datum)
                adv_filtered.append(advantages[idx])

                if needs_inf_lp:
                    if not s.inference_logprobs:
                        raise RuntimeError(
                            f"Inference logprobs required (policy_loss='{cfg.policy_loss}', "
                            f"tis_enabled={cfg.tis_enabled}) but sample {idx} has none. "
                            f"Ensure the deployment returns logprobs."
                        )
                    response_start = max(0, prompt_len - 1)
                    echoed = getattr(s, "logprobs_echoed", False)
                    aligned = (
                        list(s.inference_logprobs) if echoed else [0.0] * response_start + list(s.inference_logprobs)
                    )
                    inf_logprobs_aligned.append(aligned)
                else:
                    inf_logprobs_aligned.append([])

            if not data:
                continue

            # -- Reference forward ---
            ref_fwd = reference.forward(ref_data, "cross_entropy").result()
            ref_logprobs = [out["logprobs"].data for out in ref_fwd.loss_fn_outputs]

            # -- Collect into buffer ---
            prompt_buffer.append(PromptGroup(
                data=data, advantages=adv_filtered, ref_logprobs=ref_logprobs,
                prompt_len=prompt_len, rewards=rewards, inf_logprobs=inf_logprobs_aligned,
            ))

            # -- Train when buffer is full ---
            if len(prompt_buffer) >= prompts_per_step:
                _do_train_step()

        # End of epoch: train on remaining prompts
        if prompt_buffer:
            _do_train_step()

    # -- Final checkpoint ----------------------------------------------------

    if global_step > step_offset:
        try:
            policy.save_state(f"step-{global_step}").result(timeout=1800)
        except Exception as e:
            logger.warning("Failed to save final checkpoint: %s", e)

    if seq_filter_stats["prompts_filtered"] > 0 or seq_filter_stats["completions_filtered"] > 0:
        logger.info(
            "Seq-length filter stats: %d/%d prompts skipped (prompt >= max_seq_len), "
            "%d completions dropped (prompt+completion > max_seq_len)",
            seq_filter_stats["prompts_filtered"],
            seq_filter_stats["total_prompts"],
            seq_filter_stats["completions_filtered"],
        )
    logger.info("Training complete: %d steps", global_step)
    wandb_finish()
    return {"steps": global_step, "policy_job_id": policy.job_id, "reference_job_id": reference.job_id}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    main(Config())
