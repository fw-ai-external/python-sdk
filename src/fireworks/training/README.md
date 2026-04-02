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

Training APIs require a training-scoped Fireworks API key. Inference-only keys
can still work for deployment inference, but they will return HTTP 401 for
trainer lifecycle and training-shape calls.

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

## Account resolution

`TrainerJobManager`, `DeploymentManager`, and `FireworksClient` resolve the
account from your API key automatically. You do not need to pass `account_id`
to these classes. `FIREWORKS_ACCOUNT_ID` remains an optional override for other
SDK surfaces that still accept it.

## SFT datum construction

The training SDK expects token sequences to be wrapped in `ModelInput`, not raw
`torch.Tensor` token lists. For supervised fine-tuning, build a full-sequence
`ModelInput`, align a weights tensor to that same sequence, then convert them
into a `Datum`:

```python
import torch
from tinker.types.model_input import ModelInput
from tinker_cookbook.supervised.common import datum_from_model_input_weights

tokens = [151644, 8948, 198, 151645]
weights = torch.tensor([0.0, 0.0, 1.0, 1.0], dtype=torch.float32)

datum = datum_from_model_input_weights(
    model_input=ModelInput.from_ints(tokens),
    weights=weights,
)
```

`datum_from_model_input_weights(...)` handles the right-shifted input /
left-shifted target construction for next-token prediction. The `weights`
tensor should be aligned to the original full token sequence before that shift.

For `forward_backward(..., "cross_entropy")`, the Fireworks training SDK adds a
`response_tokens` metric so you can compute a per-token mean loss directly:

```python
result = policy.forward_backward([datum], "cross_entropy").result()
mean_nll = result.metrics["loss:sum"] / max(result.metrics["response_tokens"], 1.0)
```

## Checking training-shape capabilities

`resolve_training_profile()` now exposes the validated trainer mode for a shape,
including whether it supports LoRA launches:

```python
profile = trainer_mgr.resolve_training_profile(
    "accounts/fireworks/trainingShapes/ts-qwen3-8b-policy"
)

print(profile.trainer_mode)   # e.g. "POLICY_TRAINER" or "LORA_TRAINER"
print(profile.supports_lora)  # bool
```

## Tests

```bash
pytest src/fireworks/training/sdk/tests
```
