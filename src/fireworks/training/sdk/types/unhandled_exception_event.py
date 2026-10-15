from typing import Optional
from datetime import datetime

from fireworks.training.sdk._core._models import BaseModel
from fireworks.training.sdk.types.severity import Severity
from fireworks.training.sdk.types.event_type import EventType

__all__ = ["UnhandledExceptionEvent"]


class UnhandledExceptionEvent(BaseModel):
    error_message: str

    error_type: str

    event: EventType
    """Telemetry event type"""

    event_id: str

    event_session_index: int

    severity: Severity
    """Log severity level"""

    timestamp: datetime

    traceback: Optional[str] = None
    """Optional Python traceback string"""
