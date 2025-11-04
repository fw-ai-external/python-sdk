# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .gateway_status import GatewayStatus
from .gateway_deployed_model_state import GatewayDeployedModelState

__all__ = ["GatewayDeployedModel"]


class GatewayDeployedModel(BaseModel):
    create_time: Optional[datetime] = FieldInfo(alias="createTime", default=None)
    """The creation time of the resource."""

    default: Optional[bool] = None
    """
    If true, this is the default target when querying this model without the
    `#<deployment>` suffix. The first deployment a model is deployed to will have
    this field set to true.
    """

    deployment: Optional[str] = None
    """The resource name of the base deployment the model is deployed to."""

    description: Optional[str] = None
    """Description of the resource."""

    display_name: Optional[str] = FieldInfo(alias="displayName", default=None)

    model: Optional[str] = None

    name: Optional[str] = None

    public: Optional[bool] = None
    """If true, the deployed model will be publicly reachable."""

    serverless: Optional[bool] = None

    state: Optional[GatewayDeployedModelState] = None
    """The state of the deployed model."""

    status: Optional[GatewayStatus] = None
    """Contains model deploy/undeploy details."""

    update_time: Optional[datetime] = FieldInfo(alias="updateTime", default=None)
    """The update time for the deployed model."""
