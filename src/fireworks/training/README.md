# Fireworks Training (`fireworks.training`)

`fireworks.training` is the training layer built on top of the Fireworks Python SDK and the Tinker protocol.
This repo now contains the SDK/orchestration layer:

- `sdk/`: infrastructure + orchestration primitives (trainer jobs, deployments, hotload, sampling).

Runnable recipe loops (GRPO, DAPO, GSPO, CISPO, DPO, ORPO, SFT) now live in the standalone cookbook repo under `../cookbook/training`.

## Install

```bash
pip install -e ".[training]"

export FIREWORKS_API_KEY="..."
export FIREWORKS_ACCOUNT_ID="..."
export FIREWORKS_BASE_URL="https://api.fireworks.ai"  # optional
```

## Quick start

After installing the standalone cookbook package/code, you can run recipe loops with:

```python
from fireworks.training.cookbook.recipes.rl_loop import Config, main
from fireworks.training.cookbook.utils import InfraConfig, DeployConfig, HotloadConfig

cfg = Config(
    base_model="accounts/fireworks/models/qwen3-8b",
    max_rows=20,
    epochs=1,
    policy_loss="grpo",  # or "dapo", "gspo", "cispo"
    infra=InfraConfig(region="US_OHIO_1"),
    deployment=DeployConfig(
        deployment_id="my-grpo-run",
        create_deployment=True,
        tokenizer_model="Qwen/Qwen3-8B",
    ),
    hotload=HotloadConfig(hot_load_interval=1),
)

main(cfg)
```

## Where to start

- Want a runnable baseline: start with `../cookbook/training/src/fireworks/training/cookbook/README.md`.
- Want low-level lifecycle control: start with `sdk/README.md`.
- Want a full worked example: see `../cookbook/training/src/fireworks/training/cookbook/examples/deepmath`.

## Tests

```bash
pytest src/fireworks/training/sdk/tests
```
