# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .gateway_node_pool_binding import GatewayNodePoolBinding

__all__ = ["NodePoolBindingListResponse"]


class NodePoolBindingListResponse(BaseModel):
    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)
    """
    A token, which can be sent as `page_token` to retrieve the next page. If this
    field is omitted, there are no subsequent pages.
    """

    node_pool_bindings: Optional[List[GatewayNodePoolBinding]] = FieldInfo(alias="nodePoolBindings", default=None)

    total_size: Optional[int] = FieldInfo(alias="totalSize", default=None)
    """The total number of node pool bindings."""
