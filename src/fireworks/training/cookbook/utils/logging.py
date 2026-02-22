"""WandB and metrics logging utilities."""

from __future__ import annotations

import json
import logging
from typing import Any

from fireworks.training.cookbook.utils.config import WandBConfig

logger = logging.getLogger(__name__)


def setup_wandb(wb: WandBConfig, config: dict[str, Any]) -> bool:
    """Initialize WandB if entity is provided. Returns True if active."""
    if wb.entity is None:
        return False
    try:
        import wandb

        wandb.init(entity=wb.entity, project=wb.project, name=wb.run_name, config=config)
        if wandb.run is not None:
            logger.info("WandB: %s", wandb.run.url)
        return True
    except ImportError:
        logger.warning("wandb not installed; metrics will only be logged to console")
        return False


def wandb_log(metrics: dict[str, Any], step: int) -> None:
    """Log metrics to WandB if available."""
    try:
        import wandb

        if wandb.run is not None:
            wandb.log(metrics, step=step)
    except ImportError:
        pass


def wandb_finish() -> None:
    """Finish WandB run if active."""
    try:
        import wandb

        if wandb.run is not None:
            wandb.finish()
    except ImportError:
        pass


def log_metrics_json(step: int, **kwargs: float) -> None:
    """Print a JSON metrics line to stdout (for structured log parsing)."""
    print(json.dumps({"type": "metrics", "step": step, **kwargs}), flush=True)
