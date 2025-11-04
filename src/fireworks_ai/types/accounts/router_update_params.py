# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._types import SequenceNotStr
from ..._utils import PropertyInfo

__all__ = ["RouterUpdateParams"]


class RouterUpdateParams(TypedDict, total=False):
    account_id: Required[str]

    deployments: SequenceNotStr[str]
    """The deployment names to be covered by the router."""

    display_name: Annotated[str, PropertyInfo(alias="displayName")]

    even_load: Annotated[object, PropertyInfo(alias="evenLoad")]
    """
    Dynamically adjust traffic allocation to balance the load per replica across the
    deployments as much as possible.
    """

    model: str
    """
    The model name to route requests to. model is only applicable to single-region
    deployments. For multi-region deployments, model must be empty.
    """

    weighted_random: Annotated[object, PropertyInfo(alias="weightedRandom")]
    """Use replica count as weight."""
