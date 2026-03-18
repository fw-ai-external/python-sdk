# Fireworks Training SDK (`fireworks.training.sdk`)

Infrastructure and orchestration primitives for training on [Fireworks](https://fireworks.ai):

- **Trainer jobs** -- create, resume, and manage RLOR trainer jobs (`TrainerJobManager`).
- **Deployments** -- create, poll, hotload, and warm up inference deployments (`DeploymentManager`).
- **Sampling** -- client-side tokenized completions (`DeploymentSampler`).
- **Weight sync** -- checkpoint save / hotload pipeline (`WeightSyncer`).

## Install

```bash
pip install -e ".[training]"

export FIREWORKS_API_KEY="..."
```

## Quick start

```python
from training.recipes.rl_loop import Config, main
from training.utils import DeployConfig, HotloadConfig

cfg = Config(
    base_model="accounts/fireworks/models/qwen3-8b",
    policy_loss="grpo",  # or "dapo", "gspo", "cispo"
    deployment=DeployConfig(tokenizer_model="Qwen/Qwen3-8B"),
    hotload=HotloadConfig(hot_load_interval=1),
)

main(cfg)
```

For runnable recipes (GRPO, DPO, SFT, etc.), see the [Training Cookbook](https://github.com/fw-ai/cookbook/blob/main/training/README.md).

## Tests

```bash
pytest src/fireworks/training/sdk/tests
```
