# Fireworks Training (`fireworks.training`)

`fireworks.training` is the training layer built on top of the Fireworks Python SDK and the Tinker protocol.
It is split into two layers:

- `sdk/`: infrastructure + orchestration primitives (trainer jobs, deployments, hotload, sampling).
- `cookbook/`: compact, runnable training loops (GRPO, DPO, SFT) you can fork and modify.

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
from fireworks.training.cookbook.recipes.grpo_loop import Config, main
from fireworks.training.cookbook.utils import (
    InfraConfig,
    DeployConfig,
    HotloadConfig,
    ISConfig,
)

cfg = Config(
    base_model="accounts/fireworks/models/qwen3-8b",
    max_rows=20,
    epochs=1,
    group_size=4,
    infra=InfraConfig(region="US_OHIO_1"),
    deployment=DeployConfig(
        deployment_id="my-grpo-run",
        create_deployment=True,
        tokenizer_model="Qwen/Qwen3-1.7B",
    ),
    hotload=HotloadConfig(hot_load_interval=1),
    importance_sampling=ISConfig(enabled=True),
)

main(cfg)
```

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

## Tests

```bash
pytest src/fireworks/training/sdk/tests
pytest src/fireworks/training/cookbook/tests
```

