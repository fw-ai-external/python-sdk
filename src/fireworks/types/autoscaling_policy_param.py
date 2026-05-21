# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["AutoscalingPolicyParam"]


class AutoscalingPolicyParam(TypedDict, total=False):
    load_targets: Annotated[Dict[str, float], PropertyInfo(alias="loadTargets")]

    scale_down_window: Annotated[str, PropertyInfo(alias="scaleDownWindow")]
    """
    The duration the autoscaler will wait before scaling down a deployment after
    observing decreased load. Default is 10m. Must be less than or equal to 1 hour.
    """

    scale_to_zero_window: Annotated[str, PropertyInfo(alias="scaleToZeroWindow")]
    """
    The duration after which there are no requests that the deployment will be
    scaled down to zero replicas, if min_replica_count==0. Default is 1h. This must
    be at least 5 minutes.
    """

    scale_up_window: Annotated[str, PropertyInfo(alias="scaleUpWindow")]
    """
    The duration the autoscaler will wait before scaling up a deployment after
    observing increased load. Default is 30s. Must be less than or equal to 1 hour.
    """
