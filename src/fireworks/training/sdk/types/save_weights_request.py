from typing import Optional
from typing_extensions import Literal

from fireworks.training.sdk._core._compat import ConfigDict
from fireworks.training.sdk._core._models import StrictBase
from fireworks.training.sdk.types.model_id import ModelID

__all__ = ["SaveWeightsRequest"]


class SaveWeightsRequest(StrictBase):
    model_id: ModelID

    path: Optional[str] = None
    """A file/directory name for the weights"""

    seq_id: Optional[int] = None

    ttl_seconds: Optional[int] = None
    """TTL in seconds for this checkpoint (None = never expires)"""

    overwrite: bool = False
    """If True, overwrite any existing checkpoint with the same name"""

    type: Literal["save_weights"] = "save_weights"

    model_config = ConfigDict(protected_namespaces=tuple())
