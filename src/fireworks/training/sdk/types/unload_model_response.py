from typing import Optional
from typing_extensions import Literal

from fireworks.training.sdk._core._models import BaseModel
from fireworks.training.sdk.types.model_id import ModelID

__all__ = ["UnloadModelResponse"]


class UnloadModelResponse(BaseModel):
    model_id: ModelID

    type: Optional[Literal["unload_model"]] = None
