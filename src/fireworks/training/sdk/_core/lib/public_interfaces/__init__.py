"""Owned interfaces; defer clients to avoid future/telemetry import cycles."""

from typing import Any
from importlib import import_module

from fireworks.training.sdk._core.lib.public_interfaces.api_future import APIFuture, AwaitableConcurrentFuture

_CLIENT_MODULES = {
    "ServiceClient": "service_client",
    "SamplingClient": "sampling_client",
    "TrainingClient": "training_client",
}

__all__ = [
    "ServiceClient",
    "TrainingClient",
    "SamplingClient",
    "APIFuture",
    "AwaitableConcurrentFuture",
]


def __getattr__(name: str) -> Any:
    module = _CLIENT_MODULES.get(name)
    if module is None:
        raise AttributeError(name)
    value = getattr(import_module(f"{__name__}.{module}"), name)
    globals()[name] = value
    return value
