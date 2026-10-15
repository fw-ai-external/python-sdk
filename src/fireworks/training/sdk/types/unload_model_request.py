from typing_extensions import Literal

from fireworks.training.sdk._core._compat import ConfigDict
from fireworks.training.sdk._core._models import StrictBase
from fireworks.training.sdk.types.model_id import ModelID

__all__ = ["UnloadModelRequest"]


class UnloadModelRequest(StrictBase):
    model_id: ModelID

    type: Literal["unload_model"] = "unload_model"

    model_config = ConfigDict(protected_namespaces=tuple())
