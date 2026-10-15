from __future__ import annotations

from fireworks.training.sdk._core._models import BaseModel

__all__ = ["AuthTokenResponse"]


class AuthTokenResponse(BaseModel):
    jwt: str
