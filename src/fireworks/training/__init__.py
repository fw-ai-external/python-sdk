"""
Fireworks Training - owned GRPO/DPO/SFT clients

Subpackages:
    fireworks.training.sdk      — Native training clients + Fireworks orchestration

Recipe loops (GRPO, DPO, SFT, etc.) now live in the standalone cookbook repo.

Copyright (c) Fireworks AI, Inc. and affiliates.
"""

from __future__ import annotations

from types import ModuleType
from importlib import import_module

sdk: ModuleType
tinker: ModuleType
__all__ = ["sdk", "tinker"]


def __getattr__(name: str) -> ModuleType:
    if name in __all__:
        # lazy: training dependencies are optional for inference-only installs.
        return import_module(".sdk", __name__)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
