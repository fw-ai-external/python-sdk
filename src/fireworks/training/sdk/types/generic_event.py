from typing import Dict
from datetime import datetime

from fireworks.training.sdk._core._models import BaseModel
from fireworks.training.sdk.types.severity import Severity
from fireworks.training.sdk.types.event_type import EventType

__all__ = ["GenericEvent"]


class GenericEvent(BaseModel):
    event: EventType
    """Telemetry event type"""

    event_id: str

    event_name: str
    """Low-cardinality event name"""

    event_session_index: int

    severity: Severity
    """Log severity level"""

    timestamp: datetime

    event_data: Dict[str, object] = {}
    """Arbitrary structured JSON payload"""
