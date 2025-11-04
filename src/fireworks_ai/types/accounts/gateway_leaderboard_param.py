# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from datetime import datetime
from typing_extensions import Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["GatewayLeaderboardParam", "Source", "SourceDataset", "SourceTimeInterval"]


class SourceDataset(TypedDict, total=False):
    dataset: str


class SourceTimeInterval(TypedDict, total=False):
    end_time: Annotated[Union[str, datetime], PropertyInfo(alias="endTime", format="iso8601")]
    """Exclusive end time."""

    start_time: Annotated[Union[str, datetime], PropertyInfo(alias="startTime", format="iso8601")]
    """Inclusive start time."""


class Source(TypedDict, total=False):
    datasets: Iterable[SourceDataset]
    """Restrict to datasets (optional)."""

    evaluator: str
    """Restrict to a single evaluator (optional)."""

    last_duration: Annotated[str, PropertyInfo(alias="lastDuration")]
    """Preferred: relative duration window (e.g., last 7d, 24h)."""

    time_interval: Annotated[SourceTimeInterval, PropertyInfo(alias="timeInterval")]
    """Preferred: absolute time interval window."""

    time_window: Annotated[str, PropertyInfo(alias="timeWindow")]
    """Deprecated: prefer last_duration or time_interval.

    e.g., "last_7d" or RFC3339 interval (optional)
    """


class GatewayLeaderboardParam(TypedDict, total=False):
    description: str
    """Optional description."""

    display_name: Annotated[str, PropertyInfo(alias="displayName")]
    """Human-friendly display name."""

    source: Source
    """Optional source-based selection for jobs."""
