from typing import List

from fireworks.training.sdk._core._models import StrictBase
from fireworks.training.sdk.types.telemetry_event import TelemetryEvent

__all__ = ["TelemetrySendRequest"]


class TelemetrySendRequest(StrictBase):
    events: List[TelemetryEvent]

    platform: str
    """Host platform name"""

    sdk_version: str
    """SDK version string"""

    session_id: str
