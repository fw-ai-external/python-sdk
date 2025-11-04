# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["ClusterGetConnectionInfoResponse"]


class ClusterGetConnectionInfoResponse(BaseModel):
    ca_data: Optional[str] = FieldInfo(alias="caData", default=None)
    """Base64-encoded cluster's CA certificate."""

    endpoint: Optional[str] = None
    """The cluster's Kubernetes API server endpoint."""
