# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .gateway_node_pool import GatewayNodePool

__all__ = ["NodePoolRetrieveNodePoolsResponse"]


class NodePoolRetrieveNodePoolsResponse(BaseModel):
    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)
    """
    A token, which can be sent as `page_token` to retrieve the next page. If this
    field is omitted, there are no subsequent pages.
    """

    node_pools: Optional[List[GatewayNodePool]] = FieldInfo(alias="nodePools", default=None)

    total_size: Optional[int] = FieldInfo(alias="totalSize", default=None)
    """The total number of node pools."""
