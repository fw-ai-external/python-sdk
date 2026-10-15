from typing_extensions import Literal

from fireworks.training.sdk._core._compat import ConfigDict
from fireworks.training.sdk._core._models import StrictBase
from fireworks.training.sdk.types.model_id import ModelID

__all__ = ["GetInfoRequest"]


class GetInfoRequest(StrictBase):
    model_id: ModelID

    type: Literal["get_info"] = "get_info"

    model_config = ConfigDict(protected_namespaces=tuple())
