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

import fireworks.training.sdk.patches  # noqa: F401
from fireworks.training.sdk.client import (
    SaveSamplerResult,
    GradAccNormalization,
    FiretitanServiceClient,
    FiretitanTrainingClient,
)
from fireworks.training.sdk.trainer import (
    TrainerJobConfig,
    CreatedTrainerJob,
    TrainerJobManager,
    TrainingShapeProfile,
    TrainerServiceEndpoint,
    validate_output_model_id,
)
from fireworks.training.sdk.deployment import (
    DEFAULT_CHECKSUM_FORMAT,
    DEFAULT_DELTA_COMPRESSION,
    ServerMetrics,
    DeploymentInfo,
    DeploymentConfig,
    DeploymentManager,
    DeploymentSampler,
    SampledCompletion,
    FixedConcurrencyController,
    AdaptiveConcurrencyController,
)
from fireworks.training.sdk.weight_syncer import WeightSyncer

__all__ = [
    # Training (tinker protocol)
    "FiretitanServiceClient",
    "FiretitanTrainingClient",
    "GradAccNormalization",
    "SaveSamplerResult",
    "WeightSyncer",
    # Orchestration (Fireworks platform)
    "DEFAULT_CHECKSUM_FORMAT",
    "DEFAULT_DELTA_COMPRESSION",
    "DeploymentConfig",
    "DeploymentInfo",
    "DeploymentManager",
    "DeploymentSampler",
    "AdaptiveConcurrencyController",
    "FixedConcurrencyController",
    "SampledCompletion",
    "ServerMetrics",
    "CreatedTrainerJob",
    "TrainerJobConfig",
    "TrainerJobManager",
    "TrainerServiceEndpoint",
    "TrainingShapeProfile",
    "validate_output_model_id",
]
