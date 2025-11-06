# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["InferenceParameters"]


class InferenceParameters(TypedDict, total=False):
    extra_body: Annotated[str, PropertyInfo(alias="extraBody")]
    """
    Additional parameters for the inference request as a JSON string. For example:
    "{\"stop\": [\"\\n\"]}".
    """

    max_tokens: Annotated[int, PropertyInfo(alias="maxTokens")]
    """Maximum number of tokens to generate per response."""

    n: int
    """Number of response candidates to generate per input."""

    temperature: float
    """Sampling temperature, typically between 0 and 2."""

    top_k: Annotated[int, PropertyInfo(alias="topK")]
    """Top-k sampling parameter, limits the token selection to the top k tokens."""

    top_p: Annotated[float, PropertyInfo(alias="topP")]
    """Top-p sampling parameter, typically between 0 and 1."""
