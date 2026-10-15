from typing_extensions import Literal

from fireworks.training.sdk._core._models import BaseModel
from fireworks.training.sdk.types.model_id import ModelID

__all__ = ["CreateModelResponse"]


class CreateModelResponse(BaseModel):
    model_id: ModelID

    type: Literal["create_model"] = "create_model"
