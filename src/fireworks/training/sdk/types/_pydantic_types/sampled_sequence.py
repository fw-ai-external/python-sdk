from typing import List, Optional

from fireworks.training.sdk._core._models import BaseModel
from fireworks.training.sdk.types._pydantic_types.stop_reason import StopReason


class SampledSequence(BaseModel):
    stop_reason: StopReason
    """Reason why sampling stopped"""

    tokens: List[int]
    """List of generated token IDs"""

    logprobs: Optional[List[float]] = None
    """Log probabilities for each token (optional)"""
