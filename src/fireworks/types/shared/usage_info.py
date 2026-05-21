# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel
from .prompt_tokens_details import PromptTokensDetails

__all__ = ["UsageInfo"]


class UsageInfo(BaseModel):
    """Usage statistics."""

    prompt_tokens: int
    """The number of tokens in the prompt"""

    total_tokens: int
    """The total number of tokens used in the request (prompt + completion)"""

    completion_tokens: Optional[int] = None
    """The number of tokens in the generated completion"""

    prompt_tokens_details: Optional[PromptTokensDetails] = None
    """Details about prompt tokens, including cached tokens"""
