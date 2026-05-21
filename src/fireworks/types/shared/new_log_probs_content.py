# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel
from .new_log_probs_content_top_log_probs import NewLogProbsContentTopLogProbs

__all__ = ["NewLogProbsContent"]


class NewLogProbsContent(BaseModel):
    token: str

    bytes: List[int]

    logprob: float

    sampling_logprob: Optional[float] = None

    text_offset: int

    token_id: int

    last_activation: Optional[str] = None

    routing_matrix: Optional[str] = None

    top_logprobs: Optional[List[NewLogProbsContentTopLogProbs]] = None
