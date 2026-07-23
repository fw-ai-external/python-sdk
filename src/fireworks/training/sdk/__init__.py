"""Firetitan SDK — Tinker-compatible training interface + Fireworks orchestration.

Training (tinker protocol):
  - FiretitanServiceClient: creates full-param or LoRA training clients
  - FiretitanTrainingClient: adds checkpoint_type and list_checkpoints

Orchestration (Fireworks platform):
  - FireworksClient: trainer-free operations (promotion, shape resolution)
  - TrainerJobManager: trainer job lifecycle (extends FireworksClient)
  - DeploymentManager: deployment creation, hotloading, warmup

Algorithms live in ``cookbook.algorithms`` (separate from the SDK):
  - cookbook.algorithms.grpo: GRPOTrainer, GRPOConfig
  - cookbook.algorithms.dpo:  DPOTrainer, DPOConfig
"""

import fireworks.training.sdk.patches  # noqa: F401
from fireworks.training.sdk.client import (
    SaveSamplerResult,
    GradNormMetricsMode,
    GradAccNormalization,
    FiretitanServiceClient,
    FiretitanSampleResponse,
    FiretitanSamplingClient,
    FiretitanSamplingParams,
    FiretitanTrainingClient,
    FiretitanSampledSequence,
)
from fireworks.training.sdk.errors import TrainingAPIError
from fireworks.training.sdk.managed import FiretitanProvisioningConfig
from fireworks.training.sdk.trainer import (
    TrainerJobConfig,
    CreatedTrainerJob,
    TrainerJobManager,
    TrainerServiceEndpoint,
)
from fireworks.training.sdk._constants import (
    CLEANUP_DEPLOYMENT_ON_CLOSE_DELETE,
    CLEANUP_DEPLOYMENT_ON_CLOSE_SCALE_TO_ZERO,
    DeploymentCleanupOnClose,
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
    SamplingRequestError,
    FixedConcurrencyController,
    AdaptiveConcurrencyController,
    DeploymentSamplerTimeoutError,
    SamplingConcurrencyController,
)
from fireworks.training.sdk.tinker_compat import (
    install_tinker_service_client,
    patched_tinker_service_client,
    restore_tinker_service_client,
)
from fireworks.training.sdk.training_spec import (
    WSDSchedule,
    CosineSchedule,
    LinearSchedule,
    LRSchedulerSpec,
    ConstantSchedule,
    compute_lr,
    has_v1_scheduler_fields,
    parse_lr_scheduler_spec,
    default_constant_schedule,
    normalize_lr_scheduler_spec,
)
from fireworks.training.sdk.weight_syncer import WeightSyncer
from fireworks.training.sdk.fireworks_client import (
    FireworksClient,
    TrainingShapeProfile,
    validate_output_model_id,
)

__all__ = [
    # Training (tinker protocol)
    "FiretitanServiceClient",
    "FiretitanTrainingClient",
    "FiretitanSamplingParams",
    "FiretitanSampledSequence",
    "FiretitanSampleResponse",
    "CLEANUP_DEPLOYMENT_ON_CLOSE_DELETE",
    "CLEANUP_DEPLOYMENT_ON_CLOSE_SCALE_TO_ZERO",
    "DeploymentCleanupOnClose",
    "FiretitanProvisioningConfig",
    "TrainingAPIError",
    "GradAccNormalization",
    "GradNormMetricsMode",
    "SaveSamplerResult",
    "WeightSyncer",
    "install_tinker_service_client",
    "patched_tinker_service_client",
    "restore_tinker_service_client",
    # Orchestration (Fireworks platform) — trainer-free
    "FireworksClient",
    "TrainingShapeProfile",
    "validate_output_model_id",
    # Orchestration (Fireworks platform) — trainer lifecycle
    "CreatedTrainerJob",
    "TrainerJobConfig",
    "TrainerJobManager",
    "TrainerServiceEndpoint",
    # Orchestration (Fireworks platform) — deployment
    "DEFAULT_CHECKSUM_FORMAT",
    "DEFAULT_DELTA_COMPRESSION",
    "DeploymentConfig",
    "DeploymentInfo",
    "DeploymentManager",
    "DeploymentSampler",
    "FiretitanSamplingClient",
    "SamplingConcurrencyController",
    "AdaptiveConcurrencyController",
    "FixedConcurrencyController",
    "SampledCompletion",
    "SamplingRequestError",
    "DeploymentSamplerTimeoutError",
    "ServerMetrics",
    # LR scheduler shared schema
    "ConstantSchedule",
    "LinearSchedule",
    "CosineSchedule",
    "WSDSchedule",
    "LRSchedulerSpec",
    "default_constant_schedule",
    "parse_lr_scheduler_spec",
    "normalize_lr_scheduler_spec",
    "compute_lr",
    "has_v1_scheduler_fields",
]
