from typing import Any, Dict, List, Optional

from fireworks.training.sdk._core._models import StrictBase
from fireworks.training.sdk.types.loss_fn_type import LossFnType
from fireworks.training.sdk.types._pydantic_types.datum import Datum

__all__ = ["ForwardBackwardInput"]


class ForwardBackwardInput(StrictBase):
    data: List[Datum]
    """Array of input data for the forward/backward pass"""

    loss_fn: LossFnType
    """Fully qualified function path for the loss function"""

    loss_fn_config: Optional[Dict[str, Any]] = None
    """Optional configuration parameters for the loss function (e.g., PPO clip thresholds, DPO beta)"""
