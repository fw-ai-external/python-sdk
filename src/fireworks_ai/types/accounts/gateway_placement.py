# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .gateway_region import GatewayRegion

__all__ = ["GatewayPlacement"]


class GatewayPlacement(BaseModel):
    multi_region: Optional[Literal["MULTI_REGION_UNSPECIFIED", "GLOBAL", "US"]] = FieldInfo(
        alias="multiRegion", default=None
    )
    """The multi-region where the deployment must be placed."""

    region: Optional[GatewayRegion] = None
    """The region where the deployment must be placed."""

    regions: Optional[List[GatewayRegion]] = None
