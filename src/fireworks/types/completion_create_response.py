# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

import builtins
from typing import Dict, List, Optional

from .._models import BaseModel
from .shared.choice import Choice

__all__ = ["CompletionCreateResponse", "Usage", "UsagePromptTokensDetails"]


class UsagePromptTokensDetails(BaseModel):
    cached_tokens: Optional[int] = None


class Usage(BaseModel):
    prompt_tokens: int
    """The number of tokens in the prompt"""

    total_tokens: int
    """The total number of tokens used in the request (prompt + completion)"""

    completion_tokens: Optional[int] = None
    """The number of tokens in the generated completion"""

    prompt_tokens_details: Optional[UsagePromptTokensDetails] = None
    """Details about prompt tokens, including cached tokens"""


class CompletionCreateResponse(BaseModel):
    id: str
    """A unique identifier of the response"""

    choices: List[Choice]
    """The list of generated completion choices"""

    created: int
    """The Unix time in seconds when the response was generated"""

    model: str
    """The model used for the completion"""

    usage: Usage
    """Usage statistics for the completion"""

    object: Optional[str] = None
    """The object type, which is always "text_completion" """

    perf_metrics: Optional[Dict[str, builtins.object]] = None
    """See parameter [perf_metrics_in_response](#body-perf-metrics-in-response)"""
