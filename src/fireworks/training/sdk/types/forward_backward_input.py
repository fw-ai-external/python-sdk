from __future__ import annotations

from typing import Any, Dict, List, Optional
from dataclasses import field, dataclass

from fireworks.training.sdk.types.datum import Datum
from fireworks.training.sdk.types.loss_fn_type import LossFnType

__all__ = ["ForwardBackwardInput"]


@dataclass(frozen=True)
class ForwardBackwardInput:
    data: List[Datum]
    """Array of input data for the forward/backward pass"""

    loss_fn: LossFnType
    """Fully qualified function path for the loss function"""

    loss_fn_config: Optional[Dict[str, Any]] = field(default=None)
    """Optional configuration parameters for the loss function (e.g., PPO clip thresholds, DPO beta)"""
