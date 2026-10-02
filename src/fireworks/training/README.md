# Fireworks Training SDK (`fireworks.training.sdk`)

Infrastructure and orchestration primitives for training on [Fireworks](https://fireworks.ai):

- **Trainer jobs** -- create, resume, and manage RLOR trainer jobs (`TrainerJobManager`).
- **Deployments** -- create, poll, hotload, and warm up inference deployments (`DeploymentManager`).
- **Sampling** -- client-side tokenized completions (`DeploymentSampler`).
- **Weight sync** -- checkpoint save / hotload pipeline (`WeightSyncer`).

## Install

Use **Python 3.11+**:

```bash
python -m pip install --upgrade 'fireworks-ai[training]>=1.2.11,<2'
export FIREWORKS_API_KEY="..."  # Training-scoped API key
```

The legacy `0.19.20` package has no `fireworks.training` module; upgrade with
the command above. Stable training releases do not require `--pre`.

Verify the installation:

```bash
python - <<'PYTHON'
import fireworks
from fireworks.training.sdk import FiretitanServiceClient

print(f"Fireworks SDK {fireworks.__version__}: {FiretitanServiceClient.__name__} is available")
PYTHON
```

For runnable recipes, follow the [Training Cookbook setup](https://github.com/fw-ai/cookbook/blob/main/training/README.md#getting-started).
Advanced: API-only environments can use the smaller `[training-sdk]` extra,
which omits local ML dependencies such as PyTorch and W&B.

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

## Weight sync transport

The managed SDK and cookbook select RDMA automatically only
for dedicated full-parameter training when the trainer and every inference
replica advertise `supports_rdma_weight_sync=true`. It reads the existing
create-model response and hotload status response; no capability endpoint or
image-tag comparison is needed. Missing or unknown fields mean unsupported.

RDMA readiness comes from platform-managed runtime/shape configuration. The
SDK does not add superuser-only `extraArgs` or `extraValues` to enable RDMA.
Runtimes without RDMA configured use FILE, including with the compatibility
option below. Explicit admin overrides remain available for superuser callers.

| Training mode | Trainer supports RDMA | Inference supports RDMA | Selected path |
| --- | --- | --- | --- |
| Full parameter | No | No | Save → file hotload |
| Full parameter | No | Yes | Save → file hotload |
| Full parameter | Yes | No | Save → file hotload |
| Full parameter | Yes | Yes | RDMA |
| LoRA | No | No | Save → file hotload |
| LoRA | No | Yes | Save → file hotload |
| LoRA | Yes | No | Save → file hotload |
| LoRA | Yes | Yes | Save → file hotload |

`training_client.supports_rdma_weight_sync` reports the negotiated result.
The older `weight_sync_transport="RDMA"` setup option remains accepted but
does not bypass capability checks. `weight_sync()` rechecks inference support
before each publication and uses the existing sampler-save/hotload operations
when support disappears. Callers do not need to branch or reconnect. Its future
covers negotiation through rollout activation; FILE results have
`optimizer_version=None` because legacy saves do not report an optimizer version.
Explicit `save_weights_for_sampler()` / `create_sampling_client()` calls remain
available.

Reused deployments retain their runtime configuration and advertise false if
RDMA is disabled. A trainer that no longer implements the weight-sync route
(HTTP 404/405 before acceptance) also uses FILE. Errors after an RDMA publication
is accepted are surfaced; they do not trigger an unsafe FILE retry.

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
from training.renderer.supervised import datum_from_model_input_weights

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
