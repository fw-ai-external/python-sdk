from datetime import datetime

from fireworks.training.sdk._core._models import BaseModel
from fireworks.training.sdk.types.severity import Severity
from fireworks.training.sdk.types.event_type import EventType

__all__ = ["SessionStartEvent"]


class SessionStartEvent(BaseModel):
    event: EventType
    """Telemetry event type"""

    event_id: str

    event_session_index: int

    severity: Severity
    """Log severity level"""

    timestamp: datetime
