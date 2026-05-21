# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["APIKeyListParams"]


class APIKeyListParams(TypedDict, total=False):
    account_id: str

    filter: str
    """Field for filtering results."""

    order_by: Annotated[str, PropertyInfo(alias="orderBy")]
    """Field for ordering results."""

    page_size: Annotated[int, PropertyInfo(alias="pageSize")]
    """Number of API keys to return in the response. Pagination support to be added."""

    page_token: Annotated[str, PropertyInfo(alias="pageToken")]
    """Token for fetching the next page of results. Pagination support to be added."""

    read_mask: Annotated[str, PropertyInfo(alias="readMask")]
    """The fields to be returned in the response.

    If empty or "\\**", all fields will be returned.
    """
