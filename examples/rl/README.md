# Fireworks RL Training Examples

RL training scripts using the Tinker SDK with Fireworks infrastructure.

## Scripts

| Script | Algorithm | Hotload Frequency | Importance Sampling |
|--------|-----------|-------------------|---------------------|
| `train_grpo.py` | GRPO (on-policy) | Every optimizer step | No (ρ=1) |
| `train_grpo_off_policy.py` | GRPO (off-policy) | Every N steps | Yes (ρ = π_current / π_behavior) |
| `train_dpo.py` | DPO | End of training only | No |

Shared infrastructure code lives in `shared/`:

```
shared/
├── rlor.py         # Create, poll, delete RLOR trainer jobs
├── deployment.py   # Create, poll, delete hotload-enabled deployments
├── hotload.py      # Trigger hotload + wait for completion
├── dataset.py      # Load GSM8K dataset + evaluate responses
└── tokenizer.py    # Encode text via trainer's tokenizer endpoint
```

## How It Works (Step by Step)

### Step 1: Create a Deployment

A deployment is an inference endpoint that serves your model for sampling completions.
With hotload enabled, you can update its weights during training without restarting.

```
--create-deployment --hotload-deployment-id "my-run"
--deployment-shape "accounts/{account}/deploymentShapes/{shape}"
--deployment-region "US_VIRGINIA_1"
```

→ See `shared/deployment.py`: `create_or_get_deployment()`, `wait_for_deployment_ready()`

### Step 2: Create RLOR Trainer Jobs

RLOR jobs are GPU-backed training servers managed by Fireworks. Each job loads the model
onto dedicated hardware and exposes a Tinker API for forward/backward/optim_step calls.

- **Policy trainer**: Trainable. Linked to the deployment so it can upload checkpoints for hotloading.
- **Reference trainer** (GRPO only): Frozen copy of the initial model. Used for KL regularization.
  DPO doesn't need this — it caches reference logprobs at initialization.

→ See `shared/rlor.py`: `create_rlor_service_job_and_wait()`

### Step 3: Connect Tinker SDK Clients

After RLOR jobs are running, create Tinker SDK clients to talk to them:

```python
service = tinker.ServiceClient(base_url=trainer_endpoint.base_url)
training_client = service.create_lora_training_client(base_model=model, rank=lora_rank)
```

These clients provide `forward()`, `forward_backward_custom()`, `optim_step()`, and
`save_weights_for_sampler()`.

### Step 4: Training Loop

For each prompt in the dataset:

1. **Hotload** (on-policy: every step; off-policy: every N steps)
   - Save current trainer weights to GCS: `save_weights_for_sampler(name, checkpoint_type="delta")`
   - Tell deployment to load them: `hotload_load_model(snapshot_identity=name)`
   - Wait for completion: `wait_for_hotload_ready(expected_identity=name)`

2. **Sample** K completions from the deployment via the Fireworks Chat Completions API
   with `raw_output=True` to get token IDs back.

3. **Score** each completion with a reward function (e.g., GSM8K accuracy check).
   Skip prompts where all completions have the same reward (no learning signal).

4. **Build datums** using `datum_from_tokens_weights()` from tinker-cookbook. This handles
   token shifting internally. Weights mark which tokens to train on (0=prompt, 1=response).

5. **Get reference logprobs** via `forward()` on the frozen reference trainer.

6. **Compute loss** via `forward_backward_custom()`. The custom loss function uses
   `torch.dot(logprobs, weights)` for response-only computation:
   - GRPO: `-advantage * dot(logprobs, weights) + kl_beta * dot(pi - ref, weights)`
   - Off-policy adds importance ratio: `rho * loss` where `rho = exp(pi_current - pi_behavior)`
   - DPO: `-log(sigmoid(beta * (margin_chosen - margin_rejected)))`

7. **Accumulate gradients** over `grad_accum` prompts, then call `optim_step()`.

→ See `shared/hotload.py`: `hotload_load_model()`, `wait_for_hotload_ready()`

### Step 5: Save Final Checkpoint + Hotload

After training completes, save the final weights and hotload them so the deployment
serves the trained model.

### Step 6: Cleanup

Delete RLOR jobs and deployment to release GPU resources.

→ See `shared/rlor.py`: `delete_rlor_job()`, `shared/deployment.py`: `delete_deployment()`

## Checkpoint Types

- **Base**: Full model weights. The first checkpoint must be base.
- **Delta**: XOR diff from the previous checkpoint (~10x smaller, ~5x faster).
  Each delta references the previous save (chained, not all relative to the original base).

```
step-1 (base) → step-2 (delta vs step-1) → step-3 (delta vs step-2)
```

The deployment validates that `previous_snapshot_identity` matches its currently loaded
snapshot before applying a delta.

## Install & Run

```bash
pip install fireworks-ai[rl]

export FIREWORKS_API_KEY="..."
export FIREWORKS_ACCOUNT_ID="..."
```

### GRPO On-Policy

```bash
python examples/rl/train_grpo.py \
    --base-model "accounts/fireworks/models/qwen3-8b" \
    --dataset /path/to/gsm8k.jsonl \
    --lora-rank 0 \
    --max-seq-len 4096 \
    --max-new-tokens 1024 \
    --epochs 1 \
    --max-rows 200 \
    --group-size 8 \
    --temperature 1.0 \
    --kl-beta 0.001 \
    --lr 1e-5 \
    --grad-accum 4 \
    --region "US_VIRGINIA_1" \
    --create-deployment \
    --hotload-deployment-id "grpo-run" \
    --deployment-shape "accounts/{account}/deploymentShapes/{shape}" \
    --deployment-region "US_VIRGINIA_1" \
    --skip-validations \
    --save-sampler \
    --hotload \
    --cleanup-rlor-job \
    --cleanup-deployment
```

### GRPO Off-Policy

```bash
python examples/rl/train_grpo_off_policy.py \
    --base-model "accounts/fireworks/models/qwen3-8b" \
    --dataset /path/to/gsm8k.jsonl \
    --lora-rank 0 \
    --max-seq-len 4096 \
    --max-new-tokens 1024 \
    --epochs 1 \
    --max-rows 200 \
    --group-size 8 \
    --temperature 1.0 \
    --kl-beta 0.001 \
    --lr 1e-5 \
    --grad-accum 4 \
    --hotload-interval 5 \
    --region "US_VIRGINIA_1" \
    --create-deployment \
    --hotload-deployment-id "grpo-offpolicy-run" \
    --deployment-shape "accounts/{account}/deploymentShapes/{shape}" \
    --deployment-region "US_VIRGINIA_1" \
    --skip-validations \
    --save-sampler \
    --hotload \
    --cleanup-rlor-job \
    --cleanup-deployment
```

### DPO

```bash
python examples/rl/train_dpo.py \
    --base-model "accounts/fireworks/models/qwen3-8b" \
    --dataset /path/to/preference_data.jsonl \
    --lora-rank 0 \
    --max-seq-len 4096 \
    --epochs 1 \
    --max-pairs 200 \
    --beta 0.1 \
    --lr 1e-5 \
    --grad-accum 4 \
    --region "US_VIRGINIA_1" \
    --create-deployment \
    --hotload-deployment-id "dpo-run" \
    --deployment-shape "accounts/{account}/deploymentShapes/{shape}" \
    --deployment-region "US_VIRGINIA_1" \
    --skip-validations \
    --save-sampler \
    --hotload \
    --cleanup-rlor-job \
    --cleanup-deployment
```

## What We Use from Tinker SDK

| Component | Usage |
|-----------|-------|
| `ServiceClient` | Connect to RLOR trainer endpoints |
| `TrainingClient` | `forward_backward_custom()`, `optim_step()`, `forward()` |
| `save_weights_for_sampler()` | Save checkpoints (with `checkpoint_type` via `import fireworks.rl`) |
| `Datum`, `ModelInput`, `TensorData` | Data structures for training |
| `datum_from_tokens_weights()` | Datum construction with weights (from `tinker-cookbook`) |

### What We Replace

| Tinker Component | Our Replacement |
|------------------|-----------------|
| `SamplingClient` | Fireworks Chat Completions API with `raw_output=True` |
| Built-in loss functions | `forward_backward_custom()` with custom GRPO/DPO loss |
| Checkpoint management | Fireworks hotload API for live weight swapping |
