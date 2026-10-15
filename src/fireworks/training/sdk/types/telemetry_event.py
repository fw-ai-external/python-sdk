from typing import Union
from typing_extensions import TypeAlias

from fireworks.training.sdk.types.generic_event import GenericEvent
from fireworks.training.sdk.types.session_end_event import SessionEndEvent
from fireworks.training.sdk.types.session_start_event import SessionStartEvent
from fireworks.training.sdk.types.unhandled_exception_event import UnhandledExceptionEvent

__all__ = ["TelemetryEvent"]

TelemetryEvent: TypeAlias = Union[SessionStartEvent, SessionEndEvent, UnhandledExceptionEvent, GenericEvent]
