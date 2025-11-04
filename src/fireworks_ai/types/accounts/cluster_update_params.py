# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo
from .gateway_eks_cluster_param import GatewayEksClusterParam
from .gateway_fake_cluster_param import GatewayFakeClusterParam

__all__ = ["ClusterUpdateParams"]


class ClusterUpdateParams(TypedDict, total=False):
    account_id: Required[str]

    display_name: Annotated[str, PropertyInfo(alias="displayName")]
    """Human-readable display name of the cluster.

    e.g. "My Cluster" Must be fewer than 64 characters long.
    """

    eks_cluster: Annotated[GatewayEksClusterParam, PropertyInfo(alias="eksCluster")]

    fake_cluster: Annotated[GatewayFakeClusterParam, PropertyInfo(alias="fakeCluster")]
