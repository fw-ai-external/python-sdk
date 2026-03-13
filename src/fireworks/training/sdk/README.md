# SDK (`fireworks.training.sdk`)

`fireworks.training.sdk` is the infrastructure layer for Tinker-style training on Fireworks.
It provides trainer/deployment lifecycle APIs, hotload orchestration, and thin Tinker client extensions.

## Main components

| Component | Purpose |
| --- | --- |
| `TrainerJobManager` + `TrainerJobConfig` | Create/resume/delete RLOR trainer jobs and wait for healthy endpoints. Supports training shape resolution via `resolve_training_profile`. |
| `DeploymentManager` + `DeploymentConfig` | Create/get/delete deployments, hotload snapshots, wait for readiness, warmup. |
| `DeploymentSampler` | Token-in/token-out completions wrapper with client-side tokenizer and routing matrix extraction. |
| `FiretitanServiceClient` + `FiretitanTrainingClient` | Tinker-compatible training clients with Fireworks-specific extensions (sampler weights, cross-job resume). |
| `WeightSyncer` | Save sampler checkpoints and sync them to deployments via delta chain management. |

## Tinker compatibility and extensions

Inherited behavior remains the same (`forward`, `forward_backward_custom`, `optim_step`, `save_state`, `load_state_with_optimizer`).

Fireworks-specific additions:

- `save_weights_for_sampler_ext(name, checkpoint_type=...)` — session-scoped sampler checkpoints with base/delta support.
- `list_checkpoints()`
- cross-job checkpoint references for resume (`resolve_checkpoint_path(...)`)
- automatic model-input patch for router replay (`_tinker_r3_patch.py`)

## Minimal lifecycle example

```python
from fireworks.training.sdk import (
    TrainerJobManager,
    TrainerJobConfig,
    DeploymentManager,
    DeploymentConfig,
    FiretitanServiceClient,
    WeightSyncer,
)

trainer_mgr = TrainerJobManager(api_key="...", account_id="...", base_url="https://api.fireworks.ai")
deploy_mgr = DeploymentManager(api_key="...", account_id="...", base_url="https://api.fireworks.ai")

deploy = deploy_mgr.create_or_get(
    DeploymentConfig(
        deployment_id="my-run",
        base_model="accounts/fireworks/models/qwen3-8b",
        region="US_VIRGINIA_1",
    )
)
deploy_mgr.wait_for_ready(deploy.deployment_id)

endpoint = trainer_mgr.create_and_wait(
    TrainerJobConfig(
        base_model="accounts/fireworks/models/qwen3-8b",
        display_name="my-trainer",
        hot_load_deployment_id=deploy.deployment_id,
        region="US_VIRGINIA_1",
    )
)

service = FiretitanServiceClient(base_url=endpoint.base_url, api_key="tml-local")
policy = service.create_training_client(base_model="accounts/fireworks/models/qwen3-8b")

syncer = WeightSyncer(
    policy_client=policy,
    deploy_mgr=deploy_mgr,
    deployment_id=deploy.deployment_id,
    base_model="accounts/fireworks/models/qwen3-8b",
)
syncer.save_and_hotload("step-1")
syncer.save_dcp("step-1")
```

## Using training shapes

Two launch paths are supported:

### Shape path

Pass `training_shape_ref`. The backend populates accelerator, image tag,
node count, max context length, and sharding from the validated shape.
Do not set infra fields -- the SDK validates this.

```python
profile = trainer_mgr.resolve_training_profile("ts-qwen3-8b-policy")

config = TrainerJobConfig(
    base_model="accounts/fireworks/models/qwen3-8b",
    display_name="my-trainer",
    training_shape_ref=profile.training_shape_version,
)
```

### Manual path

Omit `training_shape_ref` and set all infra fields directly.
The server skips shape validation on this path.

```python
config = TrainerJobConfig(
    base_model="accounts/fireworks/models/qwen3-8b",
    display_name="my-trainer",
    accelerator_type="NVIDIA_A100_80GB",
    accelerator_count=8,
    custom_image_tag="0.33.0",
    node_count=2,
)
```

## Error handling and retries

- `errors.py` provides `request_with_retries`, structured error formatting, and status hints.
- Retry behavior mirrors Tinker-style exponential backoff for retryable HTTP/network errors.
- HTTP 425 (deployment hotloading) is intentionally handled at call sites with longer polling intervals.

## Next step

Use this layer directly when building your own algorithm loop, or use `fireworks.training.cookbook` from the standalone cookbook repo for ready-to-run recipes.
