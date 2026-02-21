"""Firetitan SDK — Tinker-compatible training interface + Fireworks orchestration.

Training (tinker protocol):
  - FiretitanServiceClient: creates full-param or LoRA training clients
  - FiretitanTrainingClient: adds checkpoint_type and list_checkpoints

Orchestration (Fireworks platform):
  - TrainerJobManager: trainer job lifecycle (algorithm-agnostic)
  - DeploymentManager: deployment creation, hotloading, warmup

Algorithms live in ``cookbook.algorithms`` (separate from the SDK):
  - cookbook.algorithms.grpo: GRPOTrainer, GRPOConfig
  - cookbook.algorithms.dpo:  DPOTrainer, DPOConfig
"""

import fireworks.training.sdk._tinker_r3_patch  # noqa: F401
from fireworks.training.sdk.client import SaveSamplerResult, FiretitanServiceClient, FiretitanTrainingClient
from fireworks.training.sdk.errors import (
    DOCS_RLOR,
    DOCS_HOTLOAD,
    DOCS_API_KEYS,
    DOCS_DEPLOYMENTS,
    HTTP_STATUS_HINTS,
    parse_api_error,
    format_sdk_error,
    request_with_retries,
)
from fireworks.training.sdk.trainer import (
    TrainerJobConfig,
    TrainerJobManager,
    TrainerServiceEndpoint,
)
from fireworks.training.sdk.deployment import (
    DEFAULT_CHECKSUM_FORMAT,
    DEFAULT_DELTA_COMPRESSION,
    DeploymentInfo,
    DeploymentConfig,
    DeploymentManager,
    DeploymentSampler,
    SampledCompletion,
)
from fireworks.training.sdk.weight_syncer import WeightSyncer

__all__ = [
    # Training (tinker protocol)
    "FiretitanServiceClient",
    "FiretitanTrainingClient",
    "SaveSamplerResult",
    "WeightSyncer",
    # Orchestration (Fireworks platform)
    "DEFAULT_CHECKSUM_FORMAT",
    "DEFAULT_DELTA_COMPRESSION",
    "DeploymentConfig",
    "DeploymentInfo",
    "DeploymentManager",
    "DeploymentSampler",
    "SampledCompletion",
    "TrainerJobConfig",
    "TrainerJobManager",
    "TrainerServiceEndpoint",
    # Error formatting
    "format_sdk_error",
    "parse_api_error",
    "request_with_retries",
    "HTTP_STATUS_HINTS",
    "DOCS_HOTLOAD",
    "DOCS_API_KEYS",
    "DOCS_RLOR",
    "DOCS_DEPLOYMENTS",
]
