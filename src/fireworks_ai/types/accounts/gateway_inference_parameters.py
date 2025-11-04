# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["GatewayInferenceParameters"]


class GatewayInferenceParameters(BaseModel):
    extra_body: Optional[str] = FieldInfo(alias="extraBody", default=None)
    """
    Additional parameters for the inference request as a JSON string. For example:
    "{\"stop\": [\"\\n\"]}".
    """

    max_tokens: Optional[int] = FieldInfo(alias="maxTokens", default=None)
    """Maximum number of tokens to generate per response."""

    n: Optional[int] = None
    """Number of response candidates to generate per input."""

    temperature: Optional[float] = None
    """Sampling temperature, typically between 0 and 2."""

    top_k: Optional[int] = FieldInfo(alias="topK", default=None)
    """Top-k sampling parameter, limits the token selection to the top k tokens."""

    top_p: Optional[float] = FieldInfo(alias="topP", default=None)
    """Top-p sampling parameter, typically between 0 and 1."""
