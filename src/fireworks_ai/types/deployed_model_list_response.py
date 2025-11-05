# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["DeployedModelListResponse", "DeployedModel", "DeployedModelStatus"]


class DeployedModelStatus(BaseModel):
    code: Optional[
        Literal[
            "OK",
            "CANCELLED",
            "UNKNOWN",
            "INVALID_ARGUMENT",
            "DEADLINE_EXCEEDED",
            "NOT_FOUND",
            "ALREADY_EXISTS",
            "PERMISSION_DENIED",
            "UNAUTHENTICATED",
            "RESOURCE_EXHAUSTED",
            "FAILED_PRECONDITION",
            "ABORTED",
            "OUT_OF_RANGE",
            "UNIMPLEMENTED",
            "INTERNAL",
            "UNAVAILABLE",
            "DATA_LOSS",
        ]
    ] = None
    """The status code."""

    message: Optional[str] = None
    """A developer-facing error message in English."""


class DeployedModel(BaseModel):
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

    state: Optional[Literal["STATE_UNSPECIFIED", "UNDEPLOYING", "DEPLOYING", "DEPLOYED", "UPDATING"]] = None
    """The state of the deployed model."""

    status: Optional[DeployedModelStatus] = None
    """Contains model deploy/undeploy details."""

    update_time: Optional[datetime] = FieldInfo(alias="updateTime", default=None)
    """The update time for the deployed model."""


class DeployedModelListResponse(BaseModel):
    deployed_models: Optional[List[DeployedModel]] = FieldInfo(alias="deployedModels", default=None)

    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)
    """
    A token, which can be sent as `page_token` to retrieve the next page. If this
    field is omitted, there are no subsequent pages.
    """

    total_size: Optional[int] = FieldInfo(alias="totalSize", default=None)
