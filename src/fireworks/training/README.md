# Fireworks Training (`fireworks.training`)

`fireworks.training` is the training layer built on top of the Fireworks Python SDK and the Tinker protocol.
It is split into two layers:

- `sdk/`: infrastructure + orchestration primitives (trainer jobs, deployments, hotload, sampling).
- `cookbook/`: compact, runnable training loops (GRPO, DAPO, GSPO, CISPO, DPO, ORPO, SFT) you can fork and modify.

## Install

```bash
pip install -e ".[training]"

export FIREWORKS_API_KEY="..."
export FIREWORKS_ACCOUNT_ID="..."
export FIREWORKS_BASE_URL="https://api.fireworks.ai"  # optional
```

## Quick start

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

- Want a runnable baseline: start with `cookbook/README.md`.
- Want low-level lifecycle control: start with `sdk/README.md`.
- Want a full worked example: see `cookbook/examples/deepmath/RUNBOOK.md`.

## Tests

```bash
pytest src/fireworks/training/sdk/tests
pytest src/fireworks/training/cookbook/tests
```
