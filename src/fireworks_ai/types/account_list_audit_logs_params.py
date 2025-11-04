# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["AccountListAuditLogsParams"]


class AccountListAuditLogsParams(TypedDict, total=False):
    email: str
    """Optional. Filter audit logs for user email associated with the account."""

    end_time: Annotated[Union[str, datetime], PropertyInfo(alias="endTime", format="iso8601")]
    """
    End time of the audit logs to retrieve. If unspecified, the default is the
    current time.
    """

    filter: str
    """Unused but required to use existing ListRequest functionality."""

    order_by: Annotated[str, PropertyInfo(alias="orderBy")]
    """Unused but required to use existing ListRequest functionality."""

    page_size: Annotated[int, PropertyInfo(alias="pageSize")]
    """The maximum number of audit logs to return.

    The maximum page_size is 200, values above 200 will be coerced to 200. If
    unspecified, the default is 10.
    """

    page_token: Annotated[str, PropertyInfo(alias="pageToken")]
    """A page token, received from a previous ListAuditLogs call.

    Provide this to retrieve the subsequent page. When paginating, all other
    parameters provided to ListAuditLogs must match the call that provided the page
    token.
    """

    read_mask: Annotated[str, PropertyInfo(alias="readMask")]
    """The fields to be returned in the response.

    If empty or "\\**", all fields will be returned.
    """

    start_time: Annotated[Union[str, datetime], PropertyInfo(alias="startTime", format="iso8601")]
    """
    Start time of the audit logs to retrieve. If unspecified, the default is 30 days
    before now.
    """
