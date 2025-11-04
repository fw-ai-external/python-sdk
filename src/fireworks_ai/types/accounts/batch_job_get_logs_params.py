# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from datetime import datetime
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["BatchJobGetLogsParams"]


class BatchJobGetLogsParams(TypedDict, total=False):
    account_id: Required[str]

    filter: str
    """
    Only entries matching this filter will be returned. Currently only basic
    substring match is performed.
    """

    page_size: Annotated[int, PropertyInfo(alias="pageSize")]
    """The maximum number of log entries to return.

    The maximum page_size is 10,000, values above 10,000 will be coerced to 10,000.
    If unspecified, the default is 100.
    """

    page_token: Annotated[str, PropertyInfo(alias="pageToken")]
    """A page token, received from a previous GetBatchJobLogsRequest call.

    Provide this to retrieve the subsequent page. When paginating, all other
    parameters provided to GetBatchJobLogsRequest must match the call that provided
    the page token.
    """

    ranks: Iterable[int]
    """Ranks, for which to fetch logs."""

    read_mask: Annotated[str, PropertyInfo(alias="readMask")]
    """The fields to be returned in the response.

    If empty or "\\**", all fields will be returned.
    """

    start_from_head: Annotated[bool, PropertyInfo(alias="startFromHead")]
    """Pagination direction, time-wise reverse direction by default (false)."""

    start_time: Annotated[Union[str, datetime], PropertyInfo(alias="startTime", format="iso8601")]
    """
    Entries before this timestamp won't be returned. If not specified, up to
    page_size last records will be returned.
    """
