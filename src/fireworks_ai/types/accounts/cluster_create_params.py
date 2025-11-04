# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo
from .gateway_cluster_param import GatewayClusterParam

__all__ = ["ClusterCreateParams"]


class ClusterCreateParams(TypedDict, total=False):
    cluster: Required[GatewayClusterParam]
    """The properties of the cluster being created."""

    cluster_id: Required[Annotated[str, PropertyInfo(alias="clusterId")]]
