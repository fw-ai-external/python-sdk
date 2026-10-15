"""Fireworks training SDK public exports.

The package root is intentionally lazy. Lightweight runtimes such as the TITO
agent sidecar must not import trainer, Torch, or orchestration modules
just to reach sampling and exact-token trajectory types. Importing any public
name below loads only that name's owning module.

Native training types and clients do not require an external training SDK.

"""

from __future__ import annotations

import sys

if sys.version_info < (3, 11):
    raise ImportError(
        "The Fireworks training SDK requires Python 3.11 or newer; the inference SDK supports Python 3.9+."
    )

from typing import Any
from importlib import import_module

# The Cookbook's immutable sidecar bundle copies this module with a deliberately
# small module allowlist. Keep root import side-effect-free, and update that
# allowlist whenever a sidecar-visible export gains a new runtime dependency.
_EXPORTS = {
    "APIFuture": ("fireworks.training.sdk._core.lib.public_interfaces.api_future", "APIFuture"),
    "APIError": ("fireworks.training.sdk._core._exceptions", "APIError"),
    "APIStatusError": ("fireworks.training.sdk._core._exceptions", "APIStatusError"),
    "APIConnectionError": ("fireworks.training.sdk._core._exceptions", "APIConnectionError"),
    "APITimeoutError": ("fireworks.training.sdk._core._exceptions", "APITimeoutError"),
    "RequestFailedError": ("fireworks.training.sdk._core._exceptions", "RequestFailedError"),
    "TrainingError": ("fireworks.training.sdk._core._exceptions", "TrainingError"),
    "Datum": ("fireworks.training.sdk.types", "Datum"),
    "ModelInput": ("fireworks.training.sdk.types", "ModelInput"),
    "TensorData": ("fireworks.training.sdk.types", "TensorData"),
    "AdamParams": ("fireworks.training.sdk.types", "AdamParams"),
    "EncodedTextChunk": ("fireworks.training.sdk.types", "EncodedTextChunk"),
    "ModelInputChunk": ("fireworks.training.sdk.types", "ModelInputChunk"),
    "ForwardBackwardOutput": ("fireworks.training.sdk.types", "ForwardBackwardOutput"),
    "OptimStepResponse": ("fireworks.training.sdk.types", "OptimStepResponse"),
    "SamplingParams": ("fireworks.training.sdk.types", "SamplingParams"),
    "StopReason": ("fireworks.training.sdk.types", "StopReason"),
    "LoraConfig": ("fireworks.training.sdk.types", "LoraConfig"),
    # Training clients and orchestration.
    "WeightSyncResponse": ("fireworks.training.sdk.client", "WeightSyncResponse"),
    "SaveSamplerResult": ("fireworks.training.sdk.client", "SaveSamplerResult"),
    "GradNormMetricsMode": ("fireworks.training.sdk.client", "GradNormMetricsMode"),
    "GradAccNormalization": ("fireworks.training.sdk.client", "GradAccNormalization"),
    "FiretitanServiceClient": ("fireworks.training.sdk.client", "FiretitanServiceClient"),
    "FiretitanSampleResponse": ("fireworks.training.sdk.client", "FiretitanSampleResponse"),
    "FiretitanSamplingClient": ("fireworks.training.sdk.client", "FiretitanSamplingClient"),
    "SamplingClientClosedError": ("fireworks.training.sdk.client", "SamplingClientClosedError"),
    "FiretitanSamplingParams": ("fireworks.training.sdk.client", "FiretitanSamplingParams"),
    "FiretitanTrainingClient": ("fireworks.training.sdk.client", "FiretitanTrainingClient"),
    "ServiceClient": ("fireworks.training.sdk.client", "FiretitanServiceClient"),
    "TrainingClient": ("fireworks.training.sdk.client", "FiretitanTrainingClient"),
    "SamplingClient": ("fireworks.training.sdk.client", "FiretitanSamplingClient"),
    "FiretitanSampledSequence": ("fireworks.training.sdk.client", "FiretitanSampledSequence"),
    "TrainingAPIError": ("fireworks.training.sdk.errors", "TrainingAPIError"),
    "FiretitanProvisioningConfig": ("fireworks.training.sdk.managed", "FiretitanProvisioningConfig"),
    # Trainer and deployment orchestration.
    "TrainerJobConfig": ("fireworks.training.sdk.trainer", "TrainerJobConfig"),
    "CreatedTrainerJob": ("fireworks.training.sdk.trainer", "CreatedTrainerJob"),
    "TrainerJobManager": ("fireworks.training.sdk.trainer", "TrainerJobManager"),
    "TrainerServiceEndpoint": ("fireworks.training.sdk.trainer", "TrainerServiceEndpoint"),
    "CLEANUP_DEPLOYMENT_ON_CLOSE_DELETE": (
        "fireworks.training.sdk._constants",
        "CLEANUP_DEPLOYMENT_ON_CLOSE_DELETE",
    ),
    "CLEANUP_DEPLOYMENT_ON_CLOSE_SCALE_TO_ZERO": (
        "fireworks.training.sdk._constants",
        "CLEANUP_DEPLOYMENT_ON_CLOSE_SCALE_TO_ZERO",
    ),
    "DeploymentCleanupOnClose": ("fireworks.training.sdk._constants", "DeploymentCleanupOnClose"),
    "DEFAULT_CHECKSUM_FORMAT": ("fireworks.training.sdk.deployment", "DEFAULT_CHECKSUM_FORMAT"),
    "DEFAULT_DELTA_COMPRESSION": ("fireworks.training.sdk.deployment", "DEFAULT_DELTA_COMPRESSION"),
    "DeploymentInfo": ("fireworks.training.sdk.deployment", "DeploymentInfo"),
    "DeploymentConfig": ("fireworks.training.sdk.deployment", "DeploymentConfig"),
    "DeploymentManager": ("fireworks.training.sdk.deployment", "DeploymentManager"),
    # Lightweight deployment sampling.
    "ServerMetrics": ("fireworks.training.sdk.sampling", "ServerMetrics"),
    "DeploymentSampler": ("fireworks.training.sdk.sampling", "DeploymentSampler"),
    "SampledCompletion": ("fireworks.training.sdk.sampling", "SampledCompletion"),
    "SamplingRequestError": (
        "fireworks.training.sdk.sampling_observability",
        "SamplingRequestError",
    ),
    "DeploymentSamplerTimeoutError": (
        "fireworks.training.sdk.sampling_observability",
        "DeploymentSamplerTimeoutError",
    ),
    "SamplingConcurrencyController": (
        "fireworks.training.sdk.concurrency",
        "SamplingConcurrencyController",
    ),
    "AdaptiveConcurrencyController": (
        "fireworks.training.sdk.concurrency",
        "AdaptiveConcurrencyController",
    ),
    "FixedConcurrencyController": (
        "fireworks.training.sdk.concurrency",
        "FixedConcurrencyController",
    ),
    # Exact-token multi-turn sidecar.
    "TITOCallRecord": ("fireworks.training.sdk.tito", "TITOCallRecord"),
    "TITOCallResult": ("fireworks.training.sdk.tito", "TITOCallResult"),
    "TITOChatRequest": ("fireworks.training.sdk.tito", "TITOChatRequest"),
    "TITODistribution": ("fireworks.training.sdk.tito", "TITODistribution"),
    "TITOError": ("fireworks.training.sdk.tito", "TITOError"),
    "TITOIncrementalPrompt": ("fireworks.training.sdk.tito", "TITOIncrementalPrompt"),
    "TITOIncrementalRenderer": ("fireworks.training.sdk.tito", "TITOIncrementalRenderer"),
    "TITOMetricSummary": ("fireworks.training.sdk.tito", "TITOMetricSummary"),
    "TITOParsedAssistant": ("fireworks.training.sdk.tito", "TITOParsedAssistant"),
    "TITOPromptMode": ("fireworks.training.sdk.tito", "TITOPromptMode"),
    "TITOResponseAttempt": ("fireworks.training.sdk.tito", "TITOResponseAttempt"),
    "TITORenderer": ("fireworks.training.sdk.tito", "TITORenderer"),
    "TITOSegmentResult": ("fireworks.training.sdk.tito", "TITOSegmentResult"),
    "TITOSidecar": ("fireworks.training.sdk.tito", "TITOSidecar"),
    "TITOTrajectoryEndpoint": ("fireworks.training.sdk.tito", "TITOTrajectoryEndpoint"),
    "TITOTrajectoryArtifact": ("fireworks.training.sdk.tito", "TITOTrajectoryArtifact"),
    "TITOTurn": ("fireworks.training.sdk.tito", "TITOTurn"),
    "TrajectoryDriftPolicy": ("fireworks.training.sdk.tito", "TrajectoryDriftPolicy"),
    "normalize_openai_tool_arguments": (
        "fireworks.training.sdk.tito",
        "normalize_openai_tool_arguments",
    ),
    "TITOLocalDebugConfig": ("fireworks.training.sdk.tito_debug", "TITOLocalDebugConfig"),
    "TITOLocalDebugSink": ("fireworks.training.sdk.tito_debug", "TITOLocalDebugSink"),
    # Shared training schemas.
    "WSDSchedule": ("fireworks.training.sdk.training_spec", "WSDSchedule"),
    "CosineSchedule": ("fireworks.training.sdk.training_spec", "CosineSchedule"),
    "LinearSchedule": ("fireworks.training.sdk.training_spec", "LinearSchedule"),
    "LRSchedulerSpec": ("fireworks.training.sdk.training_spec", "LRSchedulerSpec"),
    "ConstantSchedule": ("fireworks.training.sdk.training_spec", "ConstantSchedule"),
    "compute_lr": ("fireworks.training.sdk.training_spec", "compute_lr"),
    "has_v1_scheduler_fields": (
        "fireworks.training.sdk.training_spec",
        "has_v1_scheduler_fields",
    ),
    "parse_lr_scheduler_spec": (
        "fireworks.training.sdk.training_spec",
        "parse_lr_scheduler_spec",
    ),
    "default_constant_schedule": (
        "fireworks.training.sdk.training_spec",
        "default_constant_schedule",
    ),
    "normalize_lr_scheduler_spec": (
        "fireworks.training.sdk.training_spec",
        "normalize_lr_scheduler_spec",
    ),
    "WeightSyncer": ("fireworks.training.sdk.weight_syncer", "WeightSyncer"),
    "DEFAULT_MERGED_BASE_EXPORT_PRECISION": (
        "fireworks.training.sdk._snapshot_chain",
        "DEFAULT_MERGED_BASE_EXPORT_PRECISION",
    ),
    "ExportPrecision": ("fireworks.training.sdk._snapshot_chain", "ExportPrecision"),
    "FireworksClient": ("fireworks.training.sdk.fireworks_client", "FireworksClient"),
    "ModelDetailsUnavailableError": (
        "fireworks.training.sdk.fireworks_client",
        "ModelDetailsUnavailableError",
    ),
    "TrainingShapeProfile": (
        "fireworks.training.sdk.fireworks_client",
        "TrainingShapeProfile",
    ),
    "validate_output_model_id": (
        "fireworks.training.sdk.fireworks_client",
        "validate_output_model_id",
    ),
}

__all__ = sorted([*_EXPORTS, "types"])


def __getattr__(name: str) -> Any:
    if name == "types":
        value = import_module("fireworks.training.sdk.types")
        globals()[name] = value
        return value
    target = _EXPORTS.get(name)
    if target is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, attribute = target
    value = getattr(import_module(module_name), attribute)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted((*globals(), *__all__))
