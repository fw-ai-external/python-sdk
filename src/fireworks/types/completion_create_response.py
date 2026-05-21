# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

import builtins
from typing import Dict, List, Optional

from .._models import BaseModel
from .shared.choice import Choice
from .shared.usage_info import UsageInfo

__all__ = ["CompletionCreateResponse"]


class CompletionCreateResponse(BaseModel):
    """The response message from a /v1/completions call."""

    id: str
    """A unique identifier of the response"""

    choices: List[Choice]
    """The list of generated completion choices"""

    created: int
    """The Unix time in seconds when the response was generated"""

    model: str
    """The model used for the completion"""

    usage: UsageInfo
    """Usage statistics for the completion"""

    object: Optional[str] = None
    """The object type, which is always "text_completion" """

    perf_metrics: Optional[Dict[str, builtins.object]] = None
    """See parameter [perf_metrics_in_response](#body-perf-metrics-in-response)"""
