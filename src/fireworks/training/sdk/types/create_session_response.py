from __future__ import annotations

from typing_extensions import Literal

from fireworks.training.sdk._core._models import BaseModel

__all__ = ["CreateSessionResponse"]


class CreateSessionResponse(BaseModel):
    type: Literal["create_session"] = "create_session"

    info_message: str | None = None
    warning_message: str | None = None
    error_message: str | None = None

    session_id: str
