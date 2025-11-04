# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, Annotated, TypedDict

from ..._utils import PropertyInfo
from .gateway_region import GatewayRegion

__all__ = ["GatewayPlacementParam"]


class GatewayPlacementParam(TypedDict, total=False):
    multi_region: Annotated[Literal["MULTI_REGION_UNSPECIFIED", "GLOBAL", "US"], PropertyInfo(alias="multiRegion")]
    """The multi-region where the deployment must be placed."""

    region: GatewayRegion
    """The region where the deployment must be placed."""

    regions: List[GatewayRegion]
