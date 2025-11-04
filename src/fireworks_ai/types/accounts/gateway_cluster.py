# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .gateway_status import GatewayStatus
from .gateway_eks_cluster import GatewayEksCluster
from .gateway_fake_cluster import GatewayFakeCluster
from .gateway_cluster_state import GatewayClusterState

__all__ = ["GatewayCluster"]


class GatewayCluster(BaseModel):
    create_time: Optional[datetime] = FieldInfo(alias="createTime", default=None)
    """The creation time of the cluster."""

    display_name: Optional[str] = FieldInfo(alias="displayName", default=None)
    """Human-readable display name of the cluster.

    e.g. "My Cluster" Must be fewer than 64 characters long.
    """

    eks_cluster: Optional[GatewayEksCluster] = FieldInfo(alias="eksCluster", default=None)

    fake_cluster: Optional[GatewayFakeCluster] = FieldInfo(alias="fakeCluster", default=None)

    name: Optional[str] = None

    state: Optional[GatewayClusterState] = None
    """The current state of the cluster."""

    status: Optional[GatewayStatus] = None
    """Detailed information about the current status of the cluster."""

    update_time: Optional[datetime] = FieldInfo(alias="updateTime", default=None)
    """The update time for the cluster."""
