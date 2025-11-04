# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .gateway_deployment_shape import GatewayDeploymentShape

__all__ = ["DeploymentShapeListResponse"]


class DeploymentShapeListResponse(BaseModel):
    deployment_shapes: Optional[List[GatewayDeploymentShape]] = FieldInfo(alias="deploymentShapes", default=None)

    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)
    """
    A token, which can be sent as `page_token` to retrieve the next page. If this
    field is omitted, there are no subsequent pages.
    """

    total_size: Optional[int] = FieldInfo(alias="totalSize", default=None)
    """The total number of deployment shapes."""
