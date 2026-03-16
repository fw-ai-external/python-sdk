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
from fireworks.training.sdk.client import (
    SaveSamplerResult,
    FiretitanServiceClient,
    FiretitanTrainingClient,
)
from fireworks.training.sdk.trainer import (
    TrainerJobConfig,
    CreatedTrainerJob,
    TrainerJobManager,
    TrainingShapeProfile,
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
    "CreatedTrainerJob",
    "TrainerJobConfig",
    "TrainerJobManager",
    "TrainerServiceEndpoint",
    "TrainingShapeProfile",
]
