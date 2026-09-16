# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.
# NOTE: hand-written in generated style (Stainless codegen is currently
# unwired, PR #26426) against the stainless/openapi.yml entry from PR #47681.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .deployment_shape_version import DeploymentShapeVersion

__all__ = ["DeploymentShapeVersionMatchResponse"]


class DeploymentShapeVersionMatchResponse(BaseModel):
    deployment_shape_versions: Optional[List[DeploymentShapeVersion]] = FieldInfo(
        alias="deploymentShapeVersions", default=None
    )
    """The deployment shape versions compatible with the deployment create request."""

    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)
    """A token, which can be sent as `page_token` to retrieve the next page."""

    total_size: Optional[int] = FieldInfo(alias="totalSize", default=None)
    """The total number of deployment shape versions."""
