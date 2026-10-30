# Fireworks Training SDK (`fireworks.training.sdk`)

Infrastructure and orchestration primitives for training on [Fireworks](https://fireworks.ai):

- **Trainer jobs** -- create, resume, and manage RLOR trainer jobs (`TrainerJobManager`).
- **Deployments** -- create, poll, hotload, and warm up inference deployments (`DeploymentManager`).
- **Sampling** -- client-side tokenized completions (`DeploymentSampler`).
- **Weight sync** -- checkpoint save / hotload pipeline (`WeightSyncer`).

Both native entrypoints are available:

```python
from fireworks.training import sdk
from fireworks.training import tinker
```

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

## Recovering sampling concurrency

`DeploymentSampler` uses `AdaptiveConcurrencyController` by default. Its request
window is separate from a recipe's number of active questions or trajectories.
Dedicated deployments provide prefill queue duration; serverless deployments
use HTTP 429/503 and transport failures instead. A large window cannot create
serving capacity that the deployment does not have.

Dedicated feedback is evaluated after at most `min(adjustment_interval, window_size)`
accepted fresh queue observations. Status-only responses and missing metrics do
not advance this interval. Feedback from attempts admitted before the latest window
reduction is ignored, and healthy feedback clears a previously congested average.
A transport-driven reduction also clears buffered pre-cut queue feedback, even
when the window is already at its minimum.
This allows recovery during a long rollout, without waiting for an optimizer
step. Persistent fresh congestion still reduces the window. Explicit
`adjustment_interval=0` retains step-only adjustment; serverless retry behavior
and the default window bounds are unchanged.

## Weight sync transport

The managed SDK and cookbook select RDMA automatically only
for dedicated full-parameter training when the trainer and every inference
replica advertise `supports_rdma_weight_sync=true`. It reads the existing
create-model response and hotload status response; no capability endpoint or
image-tag comparison is needed. Missing or unknown support fields mean unsupported; an enabled flag still requires RDMA.

RDMA readiness comes from platform-managed runtime/shape configuration. The
SDK does not add superuser-only `extraArgs` or `extraValues` to enable RDMA.
Runtimes without RDMA configured use FILE. Explicit admin overrides remain available for superuser callers.

| Training mode | Trainer supports RDMA | Inference supports RDMA | Selected path |
| --- | --- | --- | --- |
| Full parameter | No | No | Save → file hotload |
| Full parameter | No | Yes | Capability mismatch error |
| Full parameter | Yes | No | Capability mismatch error |
| Full parameter | Yes | Yes | RDMA |
| LoRA | No | No | Save → file hotload |
| LoRA | No | Yes | Rollout rejects FILE publication when RDMA is enabled |
| LoRA | Yes | No | Configuration error |
| LoRA | Yes | Yes | Configuration error |

`training_client.supports_rdma_weight_sync` reports the negotiated result.
Enabling the trainer or rollout RDMA flag makes RDMA mandatory. Both runtimes
fail startup if their enabled RDMA checks fail. Their existing runtime responses
also expose `rdma_weight_sync_enabled`, separately from `supports_rdma_weight_sync`.
The SDK checks both fields before every publication: both enabled and supported
uses RDMA; both disabled uses FILE; mismatches or enabled-but-unavailable RDMA raise.
A trainer requiring RDMA cannot use unsupported session modes or gateway shard fan-out.
Legacy LoRA/session clients retain their FILE flow without a base-model status probe;
an RDMA-enabled rollout rejects that FILE publication server-side. HTTP 404/405 from the RDMA operation also raises.

Legacy FILE runtimes without these fields remain supported when neither side
advertises RDMA. Once RDMA has been selected, losing support cannot downgrade the
session. Old runtimes cannot expose an enabled flag when their first probe fails;
upgrade trainer and serving images as well as the SDK for the full startup contract.
The rollout also rejects FILE weight-sync requests when its RDMA flag is on,
including requests from older clients. Explicit checkpoint exports remain available;
loading them as FILE weight sync requires a FILE-configured rollout. Initial model
loading and durable checkpoint storage are separate from this transport requirement.

When model creation or initial transport attachment fails after managed resources
are ready, the SDK closes its client holder and applies the configured cleanup
policies to resources it created, including a separate reference trainer. Reused
resources are preserved. Cleanup errors do not replace the original setup error.

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
from fireworks.training.sdk.types import ModelInput
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

Run the optional training suite from the repository root on Python 3.11+.
It is separate from the base SDK's `tests/` suite, which supports Python 3.9
and Pydantic v1.

```bash
pip install -e '.[training-sdk]' torch numpy openai transformers pytest pytest-asyncio pytest-timeout
pytest tests_training
```

Generic trainer/deployment argument and value overrides are opt-in testing
interfaces. They forward opaque caller-provided data, require authorized
credentials, and are left unset by normal managed flows. Prefer typed options
and validated shapes in recipes. A projection-head model handle requires a
training shape that already configures the requested topology.
