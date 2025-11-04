# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["DeploymentGetMetricsParams"]


class DeploymentGetMetricsParams(TypedDict, total=False):
    account_id: Required[str]

    read_mask: Annotated[str, PropertyInfo(alias="readMask")]
    """The fields to be returned in the response.

    If empty or "\\**", all fields will be returned.
    """

    time_range: Annotated[str, PropertyInfo(alias="timeRange")]
    """The time range to fetch metrics for (e.g. "1m", "10m", "2h"). Defaults to 10m."""
