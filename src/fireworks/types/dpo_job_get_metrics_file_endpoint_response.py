# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["DpoJobGetMetricsFileEndpointResponse"]


class DpoJobGetMetricsFileEndpointResponse(BaseModel):
    signed_url: Optional[str] = FieldInfo(alias="signedUrl", default=None)
