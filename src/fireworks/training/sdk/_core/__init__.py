"""Fireworks-owned training runtime; no external SDK imports."""

from typing import Any
from importlib import import_module

_EXPORTS = {
    "types": ("fireworks.training.sdk", "types"),
    "RequestOptions": ("fireworks.training.sdk._core._client", "RequestOptions"),
    "Timeout": ("fireworks.training.sdk._core._client", "Timeout"),
    "APIConnectionError": ("fireworks.training.sdk._core._exceptions", "APIConnectionError"),
    "APIError": ("fireworks.training.sdk._core._exceptions", "APIError"),
    "APIResponseValidationError": ("fireworks.training.sdk._core._exceptions", "APIResponseValidationError"),
    "APIStatusError": ("fireworks.training.sdk._core._exceptions", "APIStatusError"),
    "APITimeoutError": ("fireworks.training.sdk._core._exceptions", "APITimeoutError"),
    "AuthenticationError": ("fireworks.training.sdk._core._exceptions", "AuthenticationError"),
    "BadRequestError": ("fireworks.training.sdk._core._exceptions", "BadRequestError"),
    "ConflictError": ("fireworks.training.sdk._core._exceptions", "ConflictError"),
    "InternalServerError": ("fireworks.training.sdk._core._exceptions", "InternalServerError"),
    "NotFoundError": ("fireworks.training.sdk._core._exceptions", "NotFoundError"),
    "PermissionDeniedError": ("fireworks.training.sdk._core._exceptions", "PermissionDeniedError"),
    "RateLimitError": ("fireworks.training.sdk._core._exceptions", "RateLimitError"),
    "RequestFailedError": ("fireworks.training.sdk._core._exceptions", "RequestFailedError"),
    "SidecarDiedError": ("fireworks.training.sdk._core._exceptions", "SidecarDiedError"),
    "SidecarError": ("fireworks.training.sdk._core._exceptions", "SidecarError"),
    "SidecarIPCError": ("fireworks.training.sdk._core._exceptions", "SidecarIPCError"),
    "SidecarStartupError": ("fireworks.training.sdk._core._exceptions", "SidecarStartupError"),
    "TrainingError": ("fireworks.training.sdk._core._exceptions", "TrainingError"),
    "UnprocessableEntityError": ("fireworks.training.sdk._core._exceptions", "UnprocessableEntityError"),
    "APIResponse": ("fireworks.training.sdk._core._response", "APIResponse"),
    "AsyncAPIResponse": ("fireworks.training.sdk._core._response", "AsyncAPIResponse"),
    "APIFuture": ("fireworks.training.sdk._core.lib.public_interfaces", "APIFuture"),
    "SamplingClient": ("fireworks.training.sdk._core.lib.public_interfaces", "SamplingClient"),
    "ServiceClient": ("fireworks.training.sdk._core.lib.public_interfaces", "ServiceClient"),
    "TrainingClient": ("fireworks.training.sdk._core.lib.public_interfaces", "TrainingClient"),
    "AdamParams": ("fireworks.training.sdk.types", "AdamParams"),
    "Checkpoint": ("fireworks.training.sdk.types", "Checkpoint"),
    "CheckpointType": ("fireworks.training.sdk.types", "CheckpointType"),
    "Datum": ("fireworks.training.sdk.types", "Datum"),
    "DmelChunk": ("fireworks.training.sdk.types", "DmelChunk"),
    "EncodedTextChunk": ("fireworks.training.sdk.types", "EncodedTextChunk"),
    "ForwardBackwardOutput": ("fireworks.training.sdk.types", "ForwardBackwardOutput"),
    "LoraConfig": ("fireworks.training.sdk.types", "LoraConfig"),
    "ModelID": ("fireworks.training.sdk.types", "ModelID"),
    "ModelInput": ("fireworks.training.sdk.types", "ModelInput"),
    "ModelInputChunk": ("fireworks.training.sdk.types", "ModelInputChunk"),
    "OptimStepRequest": ("fireworks.training.sdk.types", "OptimStepRequest"),
    "OptimStepResponse": ("fireworks.training.sdk.types", "OptimStepResponse"),
    "ParsedCheckpointTinkerPath": ("fireworks.training.sdk.types", "ParsedCheckpointTinkerPath"),
    "SampledSequence": ("fireworks.training.sdk.types", "SampledSequence"),
    "SampleRequest": ("fireworks.training.sdk.types", "SampleRequest"),
    "SampleResponse": ("fireworks.training.sdk.types", "SampleResponse"),
    "SamplingParams": ("fireworks.training.sdk.types", "SamplingParams"),
    "StopReason": ("fireworks.training.sdk.types", "StopReason"),
    "TensorData": ("fireworks.training.sdk.types", "TensorData"),
    "TensorDtype": ("fireworks.training.sdk.types", "TensorDtype"),
}


def __getattr__(name: str) -> Any:
    if name == "types":
        value = import_module("fireworks.training.sdk.types")
    else:
        target = _EXPORTS.get(name)
        if target is None:
            raise AttributeError(name)
        value = getattr(import_module(target[0]), target[1])
    globals()[name] = value
    return value
