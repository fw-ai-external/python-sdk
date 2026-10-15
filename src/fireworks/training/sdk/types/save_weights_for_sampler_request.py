from typing import Optional
from typing_extensions import Literal

from fireworks.training.sdk._core._compat import ConfigDict
from fireworks.training.sdk._core._models import StrictBase
from fireworks.training.sdk.types.model_id import ModelID

__all__ = ["SaveWeightsForSamplerRequest"]


class SaveWeightsForSamplerRequest(StrictBase):
    model_id: ModelID

    path: Optional[str] = None
    """A file/directory name for the weights"""

    sampling_session_seq_id: Optional[int] = None

    seq_id: Optional[int] = None

    ttl_seconds: Optional[int] = None
    """TTL in seconds for this checkpoint (None = never expires)"""

    type: Literal["save_weights_for_sampler"] = "save_weights_for_sampler"

    model_config = ConfigDict(protected_namespaces=tuple())
