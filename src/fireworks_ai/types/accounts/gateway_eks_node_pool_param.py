# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._types import SequenceNotStr
from ..._utils import PropertyInfo

__all__ = ["GatewayEksNodePoolParam"]


class GatewayEksNodePoolParam(TypedDict, total=False):
    instance_type: Required[Annotated[str, PropertyInfo(alias="instanceType")]]
    """The type of instance used in this node pool.

    See https://aws.amazon.com/ec2/instance-types/ for a list of valid instance
    types.
    """

    launch_template: Annotated[str, PropertyInfo(alias="launchTemplate")]
    """Launch template to create for this node group."""

    node_group_name: Annotated[str, PropertyInfo(alias="nodeGroupName")]
    """The name of the node group. If not specified, the default is the node pool ID."""

    node_role: Annotated[str, PropertyInfo(alias="nodeRole")]
    """If not specified, the parent cluster's system_node_group_role will be used."""

    placement_group: Annotated[str, PropertyInfo(alias="placementGroup")]
    """Cluster placement group to colocate hosts in this pool."""

    spot: bool

    subnet_ids: Annotated[SequenceNotStr[str], PropertyInfo(alias="subnetIds")]
    """
    A list of subnet IDs for nodes in this node pool. If not specified, the parent
    cluster's default subnet IDs that matches the zone will be used. Note that all
    the subnets will need to be in the same zone.
    """

    zone: str
    """
    Zone for the node pool. If not specified, a random zone in the cluster's region
    will be selected.
    """
