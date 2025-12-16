# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel

__all__ = ["NewLogProbsContentTopLogProbs"]


class NewLogProbsContentTopLogProbs(BaseModel):
    token: str

    logprob: float

    token_id: int

    bytes: Optional[List[int]] = None
