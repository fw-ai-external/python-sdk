# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["GatewayLeaderboard", "Source", "SourceDataset", "SourceTimeInterval"]


class SourceDataset(BaseModel):
    dataset: Optional[str] = None


class SourceTimeInterval(BaseModel):
    end_time: Optional[datetime] = FieldInfo(alias="endTime", default=None)
    """Exclusive end time."""

    start_time: Optional[datetime] = FieldInfo(alias="startTime", default=None)
    """Inclusive start time."""


class Source(BaseModel):
    datasets: Optional[List[SourceDataset]] = None
    """Restrict to datasets (optional)."""

    evaluator: Optional[str] = None
    """Restrict to a single evaluator (optional)."""

    last_duration: Optional[str] = FieldInfo(alias="lastDuration", default=None)
    """Preferred: relative duration window (e.g., last 7d, 24h)."""

    time_interval: Optional[SourceTimeInterval] = FieldInfo(alias="timeInterval", default=None)
    """Preferred: absolute time interval window."""

    time_window: Optional[str] = FieldInfo(alias="timeWindow", default=None)
    """Deprecated: prefer last_duration or time_interval.

    e.g., "last_7d" or RFC3339 interval (optional)
    """


class GatewayLeaderboard(BaseModel):
    create_time: Optional[datetime] = FieldInfo(alias="createTime", default=None)
    """Create time (server populated)."""

    description: Optional[str] = None
    """Optional description."""

    display_name: Optional[str] = FieldInfo(alias="displayName", default=None)
    """Human-friendly display name."""

    job_count: Optional[int] = FieldInfo(alias="jobCount", default=None)
    """Computed count of jobs attached to this leaderboard."""

    name: Optional[str] = None

    source: Optional[Source] = None
    """Optional source-based selection for jobs."""

    update_time: Optional[datetime] = FieldInfo(alias="updateTime", default=None)
    """Update time (server populated)."""
