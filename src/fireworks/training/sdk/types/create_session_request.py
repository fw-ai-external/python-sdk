from __future__ import annotations

from typing import Any
from typing_extensions import Literal

from fireworks.training.sdk._core._compat import ConfigDict
from fireworks.training.sdk._core._models import StrictBase

__all__ = ["CreateSessionRequest"]


class CreateSessionRequest(StrictBase):
    tags: list[str]
    user_metadata: dict[str, Any] | None
    sdk_version: str
    project_id: str | None = None

    type: Literal["create_session"] = "create_session"

    model_config = ConfigDict(protected_namespaces=tuple())
