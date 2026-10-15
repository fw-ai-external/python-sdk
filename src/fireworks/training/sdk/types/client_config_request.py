from __future__ import annotations

from fireworks.training.sdk._core._models import StrictBase

__all__ = ["ClientConfigRequest"]


class ClientConfigRequest(StrictBase):
    sdk_version: str
    """The SDK version string for flag resolution."""
