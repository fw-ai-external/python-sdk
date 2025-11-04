# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo
from .gateway_node_pool_param import GatewayNodePoolParam

__all__ = ["NodePoolNodePoolsParams"]


class NodePoolNodePoolsParams(TypedDict, total=False):
    node_pool: Required[Annotated[GatewayNodePoolParam, PropertyInfo(alias="nodePool")]]
    """The properties of the NodePool being created."""

    node_pool_id: Required[Annotated[str, PropertyInfo(alias="nodePoolId")]]
