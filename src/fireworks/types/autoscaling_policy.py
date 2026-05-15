# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["AutoscalingPolicy", "ScalingSchedules"]


class ScalingSchedules(BaseModel):
    duration: str
    """
    Duration that the schedule remains active after the cron trigger. Must be
    between 300 seconds (5 minutes) and 604,800 seconds (7 days), and use
    whole-second precision. Schedules needing longer windows should raise the
    deployment's base min_replica_count instead. Example: "36000s" = 10 hours (e.g.,
    8am to 6pm).
    """

    min_replica_count: int = FieldInfo(alias="minReplicaCount")
    """
    Minimum number of replicas guaranteed when this schedule is active. When
    multiple schedules overlap, the effective minimum is the highest
    min_replica_count across all active schedules ("max wins"). Must be >= 0 and <=
    the deployment's max_replica_count.
    """

    schedule: str
    """
    Cron expression defining when this schedule's window starts. Standard 5-field
    cron format: minute hour day-of-month month day-of-week. Examples: "0 8 \\** _
    Mon-Fri" (8am weekdays), "0 0 1 _ \\**" (midnight on 1st of month).
    """

    timezone: str
    """IANA timezone for the cron expression.

    e.g., "America/New_York", "Europe/London", "UTC". Required because cron
    expressions without a timezone are ambiguous. DST transitions are handled
    automatically.
    """

    description: Optional[str] = None
    """
    Human-readable description of the schedule. e.g., "Weekday business hours",
    "Wednesday peak load".
    """

    disabled: Optional[bool] = None
    """
    If true, this schedule is temporarily disabled without being deleted. Useful for
    holidays or temporary schedule changes.
    """


class AutoscalingPolicy(BaseModel):
    load_targets: Optional[Dict[str, float]] = FieldInfo(alias="loadTargets", default=None)

    scale_down_window: Optional[str] = FieldInfo(alias="scaleDownWindow", default=None)
    """
    The duration the autoscaler will wait before scaling down a deployment after
    observing decreased load. Default is 10m. Must be less than or equal to 1 hour.
    """

    scale_to_zero_window: Optional[str] = FieldInfo(alias="scaleToZeroWindow", default=None)
    """
    The duration after which there are no requests that the deployment will be
    scaled down to zero replicas, if min_replica_count==0. Default is 1h. This must
    be at least 5 minutes.
    """

    scale_up_window: Optional[str] = FieldInfo(alias="scaleUpWindow", default=None)
    """
    The duration the autoscaler will wait before scaling up a deployment after
    observing increased load. Default is 30s. Must be less than or equal to 1 hour.
    """

    scaling_schedules: Optional[Dict[str, ScalingSchedules]] = FieldInfo(alias="scalingSchedules", default=None)
    """
    Named scaling schedules that override min_replica_count on a time-based cron
    schedule. When multiple schedules are active simultaneously, the highest
    min_replica_count across all active schedules is used ("max wins"). When no
    schedule is active, the deployment's base min_replica_count applies. Maximum 5
    schedules per deployment.
    """
