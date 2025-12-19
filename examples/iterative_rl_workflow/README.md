# Iterative RL Workflow Example

## Usage

Run `train.py` to start the iterative reinforcement learning workflow. Use `--help` to see all available flags and options:

```bash
python train.py --help
```

## Important Notes

- **No data splitting**: We do not split train/validation/test sets. We use the entire dataset for training. You should handle data splitting in your own code if needed.

- **Direct route**: We use direct route to minimize network latency and keep-alive to save on job creation/teardown time.

- **Cleanup**: Use `cleanup.py` to delete orphaned trainer jobs that `train.py` does not delete.

- **Throughput**: You can increase `--replica-count` to increase throughput of your rollouts.
