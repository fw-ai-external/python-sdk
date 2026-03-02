# Fireworks Training (`fireworks.training`)

`fireworks.training` is the training layer built on top of the Fireworks Python SDK and the Tinker protocol.
It is split into two layers:

- `sdk/`: infrastructure + orchestration primitives (trainer jobs, deployments, hotload, sampling).
- `cookbook/`: compact, runnable training loops (GRPO, DAPO, GSPO, DPO, ORPO, SFT) you can fork and modify.

## Install

```bash
# from this repo (recommended for SDK + cookbook development)
pip install -e ".[training]"

# from PyPI (works once a release includes sdk/cookbook modules)
# pip install --pre "fireworks-ai[training]"

export FIREWORKS_API_KEY="..."
export FIREWORKS_ACCOUNT_ID="..."
# optional for dev gateways
export FIREWORKS_BASE_URL="https://api.fireworks.ai"
```

## Quick start (recipe-first)

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

## Supported algorithms

| Algorithm | Recipe | Reference model? | Description |
| --- | --- | --- | --- |
| GRPO | `rl_loop.py` | Yes | REINFORCE with group-relative advantages and KL penalty. |
| DAPO | `rl_loop.py` | Yes | Asymmetric PPO clipping, no explicit KL penalty. |
| GSPO | `rl_loop.py` | Yes | Sequence-level PPO clipping (geometric-mean ratio). |
| DPO | `dpo_loop.py` | Yes (cached) | Direct preference optimization with concurrent reference caching. |
| ORPO | `orpo_loop.py` | No | Odds-ratio preference optimization — combined SFT + odds-ratio loss. |
| SFT | `sft_loop.py` | No | Supervised fine-tuning with response-only cross-entropy loss. |

## Key features

- **Streaming RL loop** — async rollout scheduling with greedy batching for maximum GPU utilization. Sampling, reference forward, and training overlap automatically.
- **Pluggable policy losses** — swap between GRPO, DAPO, and GSPO via a single `policy_loss` string. CISPO available as a standalone loss function.
- **TIS (Truncated Importance Sampling)** — orthogonal importance weighting composable with any policy loss.
- **Router Replay (R3)** — replay MoE expert routing decisions from inference during training for MoE models.
- **Training shape auto-config** — set `InfraConfig(training_shape_id="...")` to auto-derive region, accelerator, image tag, and node count from the control plane.
- **Pipeline-parallel batch recommendation** — auto-computes optimal batch sizes for PP-enabled shapes.
- **Pre-flight validation** — catches misconfiguration before GPU provisioning.
- **Pluggable reward and filter** — customize `reward_fn` and `dynamic_filter_fn` without modifying the loop.

## Tinker mapping (mental model)

| Tinker concept | Fireworks training equivalent |
| --- | --- |
| `ServiceClient` / `TrainingClient` | `FiretitanServiceClient` / `FiretitanTrainingClient` |
| `forward_backward_custom()` with client-side loss | Same pattern used by `cookbook/recipes/*.py` |
| Checkpoint save/load | DCP via `save_state()/load_state_with_optimizer()` |
| Sampler checkpoint for inference | `save_weights_for_sampler_ext()` + deployment hotload |

The key design is unchanged from Tinker: loss is computed on the client, while forward/backward/optimizer work runs on trainer GPUs.

## Where to start

- Want a runnable baseline: start with `cookbook/README.md`.
- Want low-level lifecycle control: start with `sdk/README.md`.
- Want a full worked example: see `cookbook/examples/deepmath/RUNBOOK.md`.

## Tests

```bash
pytest src/fireworks/training/sdk/tests
pytest src/fireworks/training/cookbook/tests
```
