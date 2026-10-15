from __future__ import annotations

from typing import Optional
from dataclasses import dataclass

from fireworks.training.sdk.types.model_id import ModelID
from fireworks.training.sdk.types.forward_backward_input import ForwardBackwardInput

__all__ = ["ForwardRequest"]


@dataclass(frozen=True)
class ForwardRequest:
    forward_input: ForwardBackwardInput

    model_id: ModelID

    seq_id: Optional[int] = None
