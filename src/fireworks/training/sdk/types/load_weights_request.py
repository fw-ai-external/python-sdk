from typing import Optional
from typing_extensions import Literal

from fireworks.training.sdk._core._compat import ConfigDict
from fireworks.training.sdk._core._models import StrictBase
from fireworks.training.sdk.types.model_id import ModelID

__all__ = ["LoadWeightsRequest"]


class LoadWeightsRequest(StrictBase):
    model_id: ModelID

    path: str
    """A tinker URI for model weights at a specific step"""

    optimizer: bool
    """Whether to load optimizer state along with model weights"""

    seq_id: Optional[int] = None

    weights_access_token: Optional[str] = None
    """Optional access token for loading checkpoints under a different account."""

    type: Literal["load_weights"] = "load_weights"

    model_config = ConfigDict(protected_namespaces=tuple())
