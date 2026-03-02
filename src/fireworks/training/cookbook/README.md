# Cookbook (`fireworks.training.cookbook`)

The cookbook contains compact training loops that are easy to run, read, and customize.
Think of it like a Fireworks-adapted `tinker-cookbook`: same client-side loss pattern, plus Fireworks deployment/hotload orchestration.

## Included recipes

| Recipe | File | Notes |
| --- | --- | --- |
| GRPO / DAPO / GSPO | `recipes/rl_loop.py` | Streaming RL loop with greedy rollout batching, pluggable policy loss, optional TIS and R3 router replay. |
| DPO | `recipes/dpo_loop.py` | Policy + reference trainers; reference logprobs are cached concurrently, then DPO loss is optimized. |
| ORPO | `recipes/orpo_loop.py` | Odds-ratio preference optimization — no reference model needed. Combined SFT + odds-ratio loss. |
| SFT | `recipes/sft_loop.py` | Single trainer with response-only cross-entropy loss. |

## Streaming RL loop

`rl_loop.py` uses a fully async, streaming architecture for maximum GPU utilization:

1. Sampling coroutines run concurrently (capped by `max_concurrent`).
2. Completions arrive into an `asyncio.Queue` as they finish.
3. A dynamic filter rejects zero-variance reward groups (pluggable via `dynamic_filter_fn`).
4. Valid groups accumulate in a greedy-batching buffer.
5. When the buffer reaches `min_samples_per_fwd_bwd`, a micro-batch fires `ref_forward_batch` + `forward_backward_custom`.
6. After `prompt_groups_per_step` groups are consumed, `optim_step` runs, followed by hotload/DCP save if scheduled.

### Rollout scheduling parameters

| Parameter | Default | Description |
| --- | --- | --- |
| `prompt_groups_per_step` | `1` | Prompt groups per optimizer step. |
| `min_samples_per_fwd_bwd` | `None` (= max) | Minimum samples to trigger a `fwd_bwd` call. |
| `max_samples_per_fwd_bwd` | `256` | Cap on samples per `fwd_bwd` call. |
| `max_concurrent` | `32` | Max concurrent in-flight sampling requests. |

The loop automatically computes `server_grad_accum_steps = ceil(prompt_groups_per_step / min_prompt_groups_per_fwd_bwd)`.

## Policy loss variants

All RL losses are set via `Config(policy_loss="...")` and are composable with TIS:

| Loss | `policy_loss` value | Key config | Description |
| --- | --- | --- | --- |
| GRPO | `"grpo"` | `kl_beta` | REINFORCE with group-relative advantages and KL penalty. |
| DAPO | `"dapo"` | `DAPOConfig` | PPO-style clipped surrogate with asymmetric clip bounds. No explicit KL penalty. |
| GSPO | `"gspo"` | `GSPOConfig` | PPO clipping with a sequence-level importance ratio (geometric mean of per-token ratios). |

CISPO (`make_cispo_loss_fn`) is also available as a standalone loss function via `fireworks.training.cookbook.utils.rl` but is not yet wired into the `policy_loss` dispatch. Use it directly when building a custom loop.

### DAPO config (`DAPOConfig`)

| Field | Default | Description |
| --- | --- | --- |
| `eps_clip` | `0.2` | Lower clipping bound. |
| `eps_clip_high` | `0.28` | Upper clipping bound. |
| `eps_clip_c` | `None` | Optional dual-clip for negative-advantage tokens (must be > 1.0). |
| `ratio_log_cap` | `20.0` | Clamp log-ratio before `exp()` for stability. |

### GSPO config (`GSPOConfig`)

| Field | Default | Description |
| --- | --- | --- |
| `clip_ratio` | `0.2` | Symmetric fallback clip epsilon. |
| `clip_ratio_low` | `None` | Asymmetric lower bound (overrides `clip_ratio`). |
| `clip_ratio_high` | `None` | Asymmetric upper bound (overrides `clip_ratio`). |
| `seq_ratio_log_cap` | `10.0` | Clamp sequence-level log-ratio. |
| `kl_beta` | `0.001` | KL coefficient (metrics only). |

### TIS — Truncated Importance Sampling (`ISConfig`)

Orthogonal modifier composable with any policy loss. Enabled via `Config(tis_enabled=True)`.

| Field | Default | Description |
| --- | --- | --- |
| `clip_high` | `2.0` | Upper importance ratio clamp. |
| `clip_low` | `0.0` | Lower importance ratio clamp. |

## Shared config blocks

All recipes compose these dataclasses from `utils/config.py`:

- `InfraConfig`: region, accelerators, image tag, extra args, node count. Supports `training_shape_id` for auto-config from control-plane training shapes.
- `DeployConfig`: deployment lifecycle, sampling/hotload settings, `tokenizer_model` (required for GRPO).
- `HotloadConfig`: hotload cadence, base/delta behavior, timeout.
- `ResumeConfig`: checkpoint source + optional step offset.
- `WandBConfig`: optional experiment logging.

## Minimal usage — RL (GRPO)

```python
from fireworks.training.cookbook.recipes.rl_loop import Config, main
from fireworks.training.cookbook.utils import (
    InfraConfig,
    DeployConfig,
    HotloadConfig,
)
from fireworks.training.cookbook.utils.rl import ISConfig

cfg = Config(
    base_model="accounts/fireworks/models/qwen3-8b",
    max_rows=20,
    epochs=1,
    completions_per_prompt=4,
    prompt_groups_per_step=4,
    min_samples_per_fwd_bwd=16,
    max_samples_per_fwd_bwd=64,
    policy_loss="grpo",  # or "dapo", "gspo"
    infra=InfraConfig(region="US_OHIO_1"),
    deployment=DeployConfig(
        deployment_id="my-grpo-run",
        create_deployment=True,
        tokenizer_model="Qwen/Qwen3-8B",
    ),
    hotload=HotloadConfig(hot_load_interval=1),
    tis_enabled=True,
    tis=ISConfig(clip_high=2.0, clip_low=0.0),
)

main(cfg)
```

## Minimal usage — DPO

```python
from fireworks.training.cookbook.recipes.dpo_loop import Config, main
from fireworks.training.cookbook.utils import InfraConfig, ResumeConfig

cfg = Config(
    base_model="accounts/fireworks/models/qwen3-8b",
    dataset="/path/to/preferences.jsonl",
    epochs=1,
    infra=InfraConfig(region="US_OHIO_1"),
    resume=ResumeConfig(resume_from="step-10", resume_job_id="old-job-id"),
)

main(cfg)
```

## Minimal usage — ORPO

```python
from fireworks.training.cookbook.recipes.orpo_loop import Config, main
from fireworks.training.cookbook.utils import InfraConfig

cfg = Config(
    base_model="accounts/fireworks/models/qwen3-8b",
    dataset="/path/to/preferences.jsonl",
    tokenizer_model="Qwen/Qwen3-8B",
    orpo_lambda=1.0,
    epochs=1,
    infra=InfraConfig(region="US_OHIO_1"),
)

main(cfg)
```

## Router Replay (R3) for MoE models

Enable R3 to replay expert routing decisions from inference during training:

```python
cfg = Config(
    ...,
    router_replay=True,
    router_replay_completion_only=True,  # default; replay only completion tokens
)
```

Routing matrices from the deployment are aligned to training positions and injected into policy datums. Reference datums are token-only (no routing matrices).

## Pipeline-parallel batch recommendation

When using `InfraConfig(training_shape_id="...")` with a PP-enabled shape, the loop auto-computes and logs a `PPBatchRecommendation`:

- `local_batch_size` — server-side PP batch size.
- `bubble_ratio` — expected PP bubble fraction.
- `recommended_group_size` — ideal `completions_per_prompt` to fill one PP batch.
- `recommended_prompts_per_step` — optimal `prompt_groups_per_step`.

## What to customize first

- Reward logic in `recipes/rl_loop.py` (`reward_fn`).
- Loss functions in `utils/rl/` — `grpo.py`, `dapo.py`, `gspo.py`, `cispo.py`, `importance_sampling.py`.
- Data adapters in `utils/data.py` for your JSONL schema.
- Rollout filter via `dynamic_filter_fn` parameter to `run_rl_loop`.
- Resume behavior in `utils/resume.py`.

## Relationship to SDK

The cookbook does not replace the SDK; it composes it:

- lifecycle: `TrainerJobManager`, `DeploymentManager`
- training clients: `FiretitanServiceClient`, `ReconnectableClient`
- checkpoint/hotload chain: `WeightSyncer`
- token-in/token-out sampling: `DeploymentSampler`

If you need a custom algorithm loop, copy the closest recipe and keep using the same SDK primitives.
