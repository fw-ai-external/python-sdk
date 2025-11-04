# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["GatewayEksNodePool"]


class GatewayEksNodePool(BaseModel):
    instance_type: str = FieldInfo(alias="instanceType")
    """The type of instance used in this node pool.

    See https://aws.amazon.com/ec2/instance-types/ for a list of valid instance
    types.
    """

    launch_template: Optional[str] = FieldInfo(alias="launchTemplate", default=None)
    """Launch template to create for this node group."""

    node_group_name: Optional[str] = FieldInfo(alias="nodeGroupName", default=None)
    """The name of the node group. If not specified, the default is the node pool ID."""

    node_role: Optional[str] = FieldInfo(alias="nodeRole", default=None)
    """If not specified, the parent cluster's system_node_group_role will be used."""

    placement_group: Optional[str] = FieldInfo(alias="placementGroup", default=None)
    """Cluster placement group to colocate hosts in this pool."""

    spot: Optional[bool] = None

    subnet_ids: Optional[List[str]] = FieldInfo(alias="subnetIds", default=None)
    """
    A list of subnet IDs for nodes in this node pool. If not specified, the parent
    cluster's default subnet IDs that matches the zone will be used. Note that all
    the subnets will need to be in the same zone.
    """

    zone: Optional[str] = None
    """
    Zone for the node pool. If not specified, a random zone in the cluster's region
    will be selected.
    """
