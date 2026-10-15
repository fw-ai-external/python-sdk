from typing_extensions import Literal

from fireworks.training.sdk._core._models import BaseModel

__all__ = ["SessionHeartbeatResponse"]


class SessionHeartbeatResponse(BaseModel):
    type: Literal["session_heartbeat"] = "session_heartbeat"
