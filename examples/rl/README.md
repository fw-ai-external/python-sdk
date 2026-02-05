# Fireworks RL Training Examples

RL training scripts using the Tinker SDK with Fireworks infrastructure.

## What We Use vs. Don't Use from Tinker

These scripts use a subset of the Tinker SDK and replace other parts with Fireworks-specific APIs.

### What We Use from Tinker

| Component | Usage |
|-----------|-------|
| `ServiceClient` | Connect to RLOR trainer endpoints |
| `TrainingClient` | `forward_backward_custom()`, `optim_step()` |
| `save_weights_for_sampler()` | Save checkpoints (with patched `checkpoint_type`) |
| `Datum`, `ModelInput`, `TensorData` | Data structures for training |

### What We Don't Use from Tinker

| Component | What We Use Instead |
|-----------|---------------------|
| `SamplingClient` | Fireworks Chat Completions API with `raw_output=True` |
| Built-in loss functions (`importance_sampling`, `ppo`) | `forward_backward_custom()` with custom loss |
| Tinker's checkpoint management | Fireworks hotload API |

## Fireworks-Specific Components

### 1. Deployment Management

We create and manage hotload-enabled deployments via the Fireworks SDK:

```python
from fireworks import Fireworks

client = Fireworks(api_key=api_key, base_url="https://api.fireworks.ai")

# Create deployment
client.deployments.create(
    account_id=account_id,
    deployment_id="my-deployment",
    base_model="accounts/fireworks/models/qwen3-8b",
    enable_hot_load=True,
    hot_load_bucket_type="FW_HOSTED",
    deployment_shape="accounts/{account}/deploymentShapes/{shape}",
    placement={"region": "US_VIRGINIA_1"},
)
```

### 2. RLOR Trainer Job Creation

RLOR (Reinforcement Learning Optimization Runtime) trainer jobs are created via the Fireworks SDK:

```python
# Create trainer job linked to deployment for hotloading
client.reinforcement_fine_tuning_steps.create(
    account_id=account_id,
    extra_body={
        "serviceMode": True,
        "keepAlive": False,
        "hotLoadDeploymentId": deployment_id,  # Links trainer to deployment
        "trainingConfig": {
            "baseModel": base_model,
            "loraRank": 0,
            "maxContextLength": 4096,
            "learningRate": 1e-5,
        },
    },
    extra_query={"deploymentId": deployment_id},
)
```

The `hotLoadDeploymentId` and `deploymentId` query param link the trainer to the deployment, allowing `save_weights_for_sampler()` to write checkpoints that the deployment can load.

### 3. Sampling via Chat Completions API

Instead of Tinker's `SamplingClient`, we sample from the deployed model:

```python
import httpx

response = httpx.post(
    f"{api_url}/inference/v1/chat/completions",
    headers={"Authorization": f"Bearer {api_key}"},
    json={
        "model": f"accounts/{account_id}/deployments/{deployment_id}",
        "messages": messages,
        "n": 8,  # Group size
        "max_tokens": 512,
        "temperature": 1.0,
        "raw_output": True,  # Get token IDs
    },
)

for choice in response.json()["choices"]:
    prompt_tokens = choice["raw_output"]["prompt_token_ids"]
    completion_tokens = choice["raw_output"]["completion_token_ids"]
```

The `raw_output=True` flag returns token IDs needed to construct `Datum` objects for training.

### 4. Hotload API

To load trained weights onto the deployment:

```python
# Trigger hotload
httpx.post(
    f"{api_url}/hot_load/v1/models/hot_load",
    headers={
        "Authorization": f"Bearer {api_key}",
        "fireworks-model": base_model,
        "fireworks-deployment": f"accounts/{account_id}/deployments/{deployment_id}",
    },
    json={
        "identity": snapshot_name,
        # For delta checkpoints only:
        "incremental_snapshot_metadata": {
            "previous_snapshot_identity": base_snapshot_name,
            "compression_format": "xor_one_to_one_zstd",
            "checksum_format": "alder32",
        },
    },
)

# Check status
status = httpx.get(
    f"{api_url}/hot_load/v1/models/hot_load",
    headers={
        "Authorization": f"Bearer {api_key}",
        "fireworks-model": base_model,
        "fireworks-deployment": f"accounts/{account_id}/deployments/{deployment_id}",
    },
)
# status.json()["replicas"][0]["current_snapshot_identity"]
# status.json()["replicas"][0]["readiness"]
```

### 5. `checkpoint_type` Parameter

The Tinker SDK's `save_weights_for_sampler()` doesn't natively support `checkpoint_type`. We patch it:

```python
import fireworks.rl  # Auto-patches Tinker on import

# Now checkpoint_type is available
policy_client.save_weights_for_sampler(
    "step-10",
    checkpoint_type="base",  # Full checkpoint
).result()

policy_client.save_weights_for_sampler(
    "step-20",
    checkpoint_type="delta",  # Incremental checkpoint (~10x smaller)
).result()
```

The patch adds `checkpoint_type` to `extra_body` in the API request.

## Checkpoint Types and Hotloading

### Base Checkpoint

Full model weights. Load without metadata:

```python
hotload_load_model(snapshot_identity="step-10")
```

### Delta Checkpoint

XOR-compressed difference from previous checkpoint. Requires metadata:

```python
hotload_load_model(
    snapshot_identity="step-20",
    incremental_snapshot_metadata={
        "previous_snapshot_identity": "step-10",
        "compression_format": "xor_one_to_one_zstd",
        "checksum_format": "alder32",
    },
)
```

### Chained Deltas

Each delta references the immediately previous checkpoint:

```
step-10 (base) → step-20 (delta, refs step-10) → step-30 (delta, refs step-20)
```

To load step-30, you must first have step-20 loaded (which requires step-10).

## Usage

```bash
# Install
pip install fireworks-ai[rl]

# Set credentials
export FIREWORKS_API_KEY="..."
export FIREWORKS_ACCOUNT_ID="..."

# Run training (on-policy: saves + hotloads after each optimizer step)
python examples/rl/train_grpo.py \
    --base-model "accounts/fireworks/models/qwen3-8b" \
    --dataset /path/to/dataset.jsonl \
    --create-deployment \
    --hotload-deployment-id "my-training-run" \
    --deployment-shape "accounts/{account}/deploymentShapes/{shape}" \
    --hotload \
    --cleanup-rlor-job \
    --cleanup-deployment
```

## Files

- `train_grpo.py` - On-policy GRPO training (hotload every step, no importance sampling)
- `train_grpo_off_policy.py` - Off-policy GRPO training (hotload at intervals, with importance sampling)
- `train_dpo.py` - DPO training
