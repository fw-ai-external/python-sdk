# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["GatewayFakeCluster"]


class GatewayFakeCluster(BaseModel):
    cluster_name: Optional[str] = FieldInfo(alias="clusterName", default=None)

    location: Optional[str] = None

    project_id: Optional[str] = FieldInfo(alias="projectId", default=None)
