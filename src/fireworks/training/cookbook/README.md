# Cookbook (`fireworks.training.cookbook`)

The cookbook contains compact training loops that are easy to run, read, and customize.
Think of it like a Fireworks-adapted `tinker-cookbook`: same client-side loss pattern, plus Fireworks deployment/hotload orchestration.

## Included recipes

| Recipe | File | Notes |
| --- | --- | --- |
| GRPO | `recipes/grpo_loop.py` | Policy + reference trainers, deployment sampling, optional router replay (R3), optional truncated importance sampling (TIS). |
| DPO | `recipes/dpo_loop.py` | Policy + reference trainers; reference logprobs are cached, then DPO loss is optimized. |
| SFT | `recipes/sft_loop.py` | Single trainer with response-only cross-entropy loss. |

## Shared config blocks

All recipes compose these dataclasses from `utils/config.py`:

- `InfraConfig`: region, accelerators, image tag, extra args, node count.
- `DeployConfig`: deployment lifecycle and sampling/hotload settings.
- `HotloadConfig`: hotload cadence, base/delta behavior, timeout.
- `ResumeConfig`: checkpoint source + optional step offset.
- `WandBConfig`: optional experiment logging.
- `ISConfig`: GRPO importance sampling controls.

## Minimal usage

```python
from fireworks.training.cookbook.recipes.dpo_loop import Config, main
from fireworks.training.cookbook.utils import InfraConfig, ResumeConfig

cfg = Config(
    base_model="accounts/pyroworks-dev/models/qwen3-1p7b-bf16",
    dataset="/path/to/preferences.jsonl",
    epochs=1,
    infra=InfraConfig(region="US_OHIO_1"),
    resume=ResumeConfig(resume_from="step-10", resume_job_id="old-job-id"),
)

main(cfg)
```

## What to customize first

- Reward logic in `recipes/grpo_loop.py` (`reward_fn`).
- Loss functions in `utils/losses.py` and `utils/importance_sampling.py`.
- Data adapters in `utils/data.py` for your JSONL schema.
- Resume behavior in `utils/resume.py`.

## Numerics verification

Use `scripts/verify_logprobs.py` to compare inference logprobs (deployment) vs training logprobs (forward-only reference trainer), including token-level diagnostics.

## Relationship to SDK

The cookbook does not replace the SDK; it composes it:

- lifecycle: `TrainerJobManager`, `DeploymentManager`
- training clients: `FiretitanServiceClient`, `ReconnectableClient`
- checkpoint/hotload chain: `WeightSyncer`
- token-in/token-out sampling: `DeploymentSampler`

If you need a custom algorithm loop, copy the closest recipe and keep using the same SDK primitives.

