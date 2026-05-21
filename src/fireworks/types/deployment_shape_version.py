# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .deployment_shape import DeploymentShape

__all__ = ["DeploymentShapeVersion"]


class DeploymentShapeVersion(BaseModel):
    create_time: Optional[datetime] = FieldInfo(alias="createTime", default=None)
    """The creation time of the deployment shape version.

    Lists will be ordered by this field.
    """

    latest_validated: Optional[bool] = FieldInfo(alias="latestValidated", default=None)
    """
    If true, this version is the latest validated version. Only one version of the
    shape can be the latest validated version.
    """

    name: Optional[str] = None

    public: Optional[bool] = None
    """If true, this version will be publicly readable."""

    snapshot: Optional[DeploymentShape] = None
    """Full snapshot of the Deployment Shape at this version."""

    validated: Optional[bool] = None
    """If true, this version has been validated."""
