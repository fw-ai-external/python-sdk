from __future__ import annotations

from fireworks.training.sdk._core._models import BaseModel
from fireworks.training.sdk.types.request_error_category import RequestErrorCategory

__all__ = ["RequestFailedResponse"]


class RequestFailedResponse(BaseModel):
    error: str
    category: RequestErrorCategory
