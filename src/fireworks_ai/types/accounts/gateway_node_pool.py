# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .gateway_status import GatewayStatus
from .gateway_eks_node_pool import GatewayEksNodePool
from .gateway_fake_node_pool import GatewayFakeNodePool
from .gateway_node_pool_state import GatewayNodePoolState
from .gateway_node_pool_stats import GatewayNodePoolStats

__all__ = ["GatewayNodePool"]


class GatewayNodePool(BaseModel):
    annotations: Optional[Dict[str, str]] = None
    """
    Arbitrary, user-specified metadata. Keys and values must adhere to Kubernetes
    constraints:
    https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/#syntax-and-character-set
    Additionally, the "fireworks.ai/" prefix is reserved.
    """

    create_time: Optional[datetime] = FieldInfo(alias="createTime", default=None)
    """The creation time of the node pool."""

    display_name: Optional[str] = FieldInfo(alias="displayName", default=None)
    """Human-readable display name of the node pool.

    e.g. "My Node Pool" Must be fewer than 64 characters long.
    """

    eks_node_pool: Optional[GatewayEksNodePool] = FieldInfo(alias="eksNodePool", default=None)

    fake_node_pool: Optional[GatewayFakeNodePool] = FieldInfo(alias="fakeNodePool", default=None)
    """A fake node pool to be used with FakeCluster."""

    max_node_count: Optional[int] = FieldInfo(alias="maxNodeCount", default=None)
    """
    https://cloud.google.com/kubernetes-engine/quotas Maximum number of nodes in
    this node pool. Must be a positive integer greater than or equal to
    min_node_count. If not specified, the default is 1.
    """

    min_node_count: Optional[int] = FieldInfo(alias="minNodeCount", default=None)
    """
    https://cloud.google.com/kubernetes-engine/quotas Minimum number of nodes in
    this node pool. Must be a non-negative integer less than or equal to
    max_node_count. If not specified, the default is 0.
    """

    name: Optional[str] = None

    node_pool_stats: Optional[GatewayNodePoolStats] = FieldInfo(alias="nodePoolStats", default=None)
    """Live statistics of the node pool."""

    overprovision_node_count: Optional[int] = FieldInfo(alias="overprovisionNodeCount", default=None)
    """The number of nodes to overprovision by the autoscaler.

    Must be a non-negative integer and less than or equal to min_node_count and
    max_node_count-min_node_count. If not specified, the default is 0.
    """

    state: Optional[GatewayNodePoolState] = None
    """The current state of the node pool."""

    status: Optional[GatewayStatus] = None
    """
    Contains detailed message when the last node pool operation fails, e.g. when
    node pool is in FAILED state or when last node pool update fails.
    """

    update_time: Optional[datetime] = FieldInfo(alias="updateTime", default=None)
    """The update time for the node pool."""
