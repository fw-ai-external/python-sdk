from typing import Optional

from fireworks.training.sdk._core._models import BaseModel
from fireworks.training.sdk.types.model_id import ModelID
from fireworks.training.sdk.types.request_id import RequestID

__all__ = ["UntypedAPIFuture"]


class UntypedAPIFuture(BaseModel):
    request_id: RequestID

    model_id: Optional[ModelID] = None
