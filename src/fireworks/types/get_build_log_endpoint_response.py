# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["GetBuildLogEndpointResponse"]


class GetBuildLogEndpointResponse(BaseModel):
    build_log_signed_uri: Optional[str] = FieldInfo(alias="buildLogSignedUri", default=None)
