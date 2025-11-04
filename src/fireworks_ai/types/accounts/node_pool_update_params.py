# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo
from .gateway_eks_node_pool_param import GatewayEksNodePoolParam
from .gateway_fake_node_pool_param import GatewayFakeNodePoolParam

__all__ = ["NodePoolUpdateParams"]


class NodePoolUpdateParams(TypedDict, total=False):
    account_id: Required[str]

    annotations: Dict[str, str]
    """
    Arbitrary, user-specified metadata. Keys and values must adhere to Kubernetes
    constraints:
    https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/#syntax-and-character-set
    Additionally, the "fireworks.ai/" prefix is reserved.
    """

    display_name: Annotated[str, PropertyInfo(alias="displayName")]
    """Human-readable display name of the node pool.

    e.g. "My Node Pool" Must be fewer than 64 characters long.
    """

    eks_node_pool: Annotated[GatewayEksNodePoolParam, PropertyInfo(alias="eksNodePool")]

    fake_node_pool: Annotated[GatewayFakeNodePoolParam, PropertyInfo(alias="fakeNodePool")]
    """A fake node pool to be used with FakeCluster."""

    max_node_count: Annotated[int, PropertyInfo(alias="maxNodeCount")]
    """
    https://cloud.google.com/kubernetes-engine/quotas Maximum number of nodes in
    this node pool. Must be a positive integer greater than or equal to
    min_node_count. If not specified, the default is 1.
    """

    min_node_count: Annotated[int, PropertyInfo(alias="minNodeCount")]
    """
    https://cloud.google.com/kubernetes-engine/quotas Minimum number of nodes in
    this node pool. Must be a non-negative integer less than or equal to
    max_node_count. If not specified, the default is 0.
    """

    overprovision_node_count: Annotated[int, PropertyInfo(alias="overprovisionNodeCount")]
    """The number of nodes to overprovision by the autoscaler.

    Must be a non-negative integer and less than or equal to min_node_count and
    max_node_count-min_node_count. If not specified, the default is 0.
    """
