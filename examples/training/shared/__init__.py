"""
Shared utilities for Fireworks RL training scripts.

This module provides common infrastructure for training scripts that use the
Fireworks platform for RL (GRPO, DPO, etc.):

- **RLOR jobs**: GPU trainer instances managed by Fireworks. Each job runs on
  dedicated hardware and exposes a Tinker API endpoint for forward/backward passes.
  You typically create two: a policy trainer (trainable) and a reference trainer (frozen).

- **Deployments**: Inference endpoints for sampling model completions. With hotload
  enabled, you can update the deployed model's weights during training without
  restarting the deployment.

- **Hotload**: The mechanism for updating deployed model weights in-place. After each
  training step (or at intervals), you save a checkpoint and tell the deployment to
  load it. Supports full (base) and incremental (delta) checkpoints.

- **Dataset**: Utilities for loading training data (GSM8K format for GRPO).

- **Tokenizer**: Encode text to tokens via the trainer's tokenizer endpoint.

Copyright (c) Fireworks AI, Inc. and affiliates.
"""

from __future__ import annotations

import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def log(msg: str) -> None:
    """Log an info message."""
    logger.info(msg)


def warn(msg: str) -> None:
    """Log a warning message."""
    logger.warning(msg)


def parse_additional_headers(additional_headers_json: str | None) -> dict | None:
    """Parse JSON string to dict for additional HTTP headers."""
    if not additional_headers_json:
        return None
    try:
        return json.loads(additional_headers_json)
    except json.JSONDecodeError:
        warn(f"Invalid JSON for additional headers: {additional_headers_json}")
        return None


# Re-export from submodules for convenience
from .rlor import (
    RlorServiceEndpoint,
    create_rlor_service_job_and_wait,
    delete_rlor_job,
)
from .deployment import (
    DeploymentInfo,
    create_or_get_deployment,
    wait_for_deployment_ready,
    delete_deployment,
)
from .hotload import (
    hotload_load_model,
    hotload_check_status,
    wait_for_hotload_ready,
)
from .dataset import (
    extract_answer_digits,
    evaluate_gsm8k_response,
    load_gsm8k_dataset,
)
from .tokenizer import encode_text

__all__ = [
    "log",
    "warn",
    "parse_additional_headers",
    "RlorServiceEndpoint",
    "create_rlor_service_job_and_wait",
    "delete_rlor_job",
    "DeploymentInfo",
    "create_or_get_deployment",
    "wait_for_deployment_ready",
    "delete_deployment",
    "hotload_load_model",
    "hotload_check_status",
    "wait_for_hotload_ready",
    "extract_answer_digits",
    "evaluate_gsm8k_response",
    "load_gsm8k_dataset",
    "encode_text",
]
