# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["AutoscalingPolicy"]


class AutoscalingPolicy(BaseModel):
    load_targets: Optional[Dict[str, float]] = FieldInfo(alias="loadTargets", default=None)

    scale_down_window: Optional[str] = FieldInfo(alias="scaleDownWindow", default=None)
    """
    The duration the autoscaler will wait before scaling down a deployment after
    observing decreased load. Default is 10m.
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
    observing increased load. Default is 30s.
    """
