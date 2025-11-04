# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["GatewayNodePoolBinding"]


class GatewayNodePoolBinding(BaseModel):
    principal: str
    """The principal that is allowed use the node pool.

    This must be the email address of the user.
    """

    account_id: Optional[str] = FieldInfo(alias="accountId", default=None)
    """The account ID that this binding is associated with."""

    cluster_id: Optional[str] = FieldInfo(alias="clusterId", default=None)
    """The cluster ID that this binding is associated with."""

    create_time: Optional[datetime] = FieldInfo(alias="createTime", default=None)
    """The creation time of the node pool binding."""

    node_pool_id: Optional[str] = FieldInfo(alias="nodePoolId", default=None)
    """The node pool ID that this binding is associated with."""
