# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["AccountListParams"]


class AccountListParams(TypedDict, total=False):
    filter: str
    """Only accounts satisfying the provided filter (if specified) will be returned.

    See https://google.aip.dev/160 for the filter grammar.
    """

    order_by: Annotated[str, PropertyInfo(alias="orderBy")]
    """Not supported. Accounts will be returned ordered by `name`."""

    page_size: Annotated[int, PropertyInfo(alias="pageSize")]
    """The maximum number of accounts to return.

    The maximum page_size is 200, values above 200 will be coerced to 200. If
    unspecified, the default is 50.
    """

    page_token: Annotated[str, PropertyInfo(alias="pageToken")]
    """A page token, received from a previous ListAccounts call.

    Provide this to retrieve the subsequent page. When paginating, all other
    parameters provided to ListAccounts must match the call that provided the page
    token.
    """

    read_mask: Annotated[str, PropertyInfo(alias="readMask")]
    """The fields to be returned in the response.

    If empty or "\\**", all fields will be returned.
    """
