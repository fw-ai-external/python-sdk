from typing import Optional

from fireworks.training.sdk._core._compat import ConfigDict
from fireworks.training.sdk._core._models import StrictBase
from fireworks.training.sdk.types.model_id import ModelID
from fireworks.training.sdk.types._pydantic_types.forward_backward_input import ForwardBackwardInput

__all__ = ["ForwardBackwardRequest"]


class ForwardBackwardRequest(StrictBase):
    forward_backward_input: ForwardBackwardInput

    model_id: ModelID

    seq_id: Optional[int] = None

    model_config = ConfigDict(protected_namespaces=tuple())
