# Iterative RL Workflow Example

## Setup

This example uses `uv` for dependency management. Install dependencies with:

```bash
uv sync
```

Activate the virtual environment:

```bash
source .venv/bin/activate
```

**Note**: This source code uses the local `fireworks-ai` package from the parent directory. If you copy this script elsewhere, you can install the latest version of `fireworks-ai` externally:

```bash
pip install fireworks-ai
```

## Usage

Run [`train.py`](./train.py) to start the iterative reinforcement learning workflow. Use `--help` to see all available flags and options:

```bash
python train.py --help
```

### Basic Example

```bash
python train.py \
    --run-prefix gsm8k-rlor \
    --deployment-id gsm8k-rlor \
    --base-model accounts/fireworks/models/qwen3-32b \
    --direct-route-api-key <your-direct-route-api-key>
```

The script will use the provided `--deployment-id` to get an existing deployment or create a new one if it doesn't exist. Both `--run-prefix` and `--deployment-id` are required to ensure explicit naming and deployment selection.

## Important Notes

- **No data splitting**: We do not split train/validation/test sets. We use the entire dataset for training. You should handle data splitting in your own code if needed.

- **Direct route**: We use direct route to minimize network latency and keep-alive to save on job creation/teardown time.

- **Cleanup**: Use [`cleanup.py`](./cleanup.py) to delete orphaned trainer jobs that [`train.py`](./train.py) does not delete.

- **Throughput**: You can increase `--replica-count` to increase throughput of your rollouts.
