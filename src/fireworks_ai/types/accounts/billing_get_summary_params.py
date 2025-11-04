# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["BillingGetSummaryParams"]


class BillingGetSummaryParams(TypedDict, total=False):
    end_time: Required[Annotated[Union[str, datetime], PropertyInfo(alias="endTime", format="iso8601")]]
    """End time for the billing period (exclusive). Note: Costs are aggregated daily.

    Only the date portion (YYYY-MM-DD) is used; the time portion is ignored. Costs
    for the end date are NOT included. For example, to get costs for Oct 5 and Oct
    6, use: start_time: 2025-10-05T00:00:00Z end_time: 2025-10-07T00:00:00Z (Oct 7
    is excluded)
    """

    start_time: Required[Annotated[Union[str, datetime], PropertyInfo(alias="startTime", format="iso8601")]]
    """Start time for the billing period. Note: Costs are aggregated daily.

    Only the date portion (YYYY-MM-DD) is used; the time portion is ignored. For
    example, 2025-10-05T07:18:29Z and 2025-10-05T23:59:59Z are treated the same as
    2025-10-05T00:00:00Z.
    """
