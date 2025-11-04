# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["IdentityProviderListParams"]


class IdentityProviderListParams(TypedDict, total=False):
    filter: str
    """Filter expression"""

    order_by: Annotated[str, PropertyInfo(alias="orderBy")]
    """Order by"""

    page_size: Annotated[int, PropertyInfo(alias="pageSize")]
    """Page size"""

    page_token: Annotated[str, PropertyInfo(alias="pageToken")]
    """Page token"""

    read_mask: Annotated[str, PropertyInfo(alias="readMask")]
    """The fields to be returned in the response.

    If empty or "\\**", all fields will be returned.
    """
