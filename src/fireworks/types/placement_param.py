# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["PlacementParam"]


class PlacementParam(TypedDict, total=False):
    """The desired geographic region where the deployment must be placed.

    Exactly one field will be
    specified.
    """

    multi_region: Annotated[
        Literal["MULTI_REGION_UNSPECIFIED", "GLOBAL", "US", "EUROPE", "APAC"], PropertyInfo(alias="multiRegion")
    ]
    """The multi-region where the deployment must be placed."""

    region: Literal[
        "REGION_UNSPECIFIED",
        "US_IOWA_1",
        "US_VIRGINIA_1",
        "US_VIRGINIA_2",
        "US_ILLINOIS_1",
        "AP_TOKYO_1",
        "EU_LONDON_1",
        "US_ARIZONA_1",
        "US_TEXAS_1",
        "US_ILLINOIS_2",
        "EU_FRANKFURT_1",
        "US_TEXAS_2",
        "EU_PARIS_1",
        "EU_HELSINKI_1",
        "US_NEVADA_1",
        "EU_ICELAND_1",
        "EU_ICELAND_2",
        "US_WASHINGTON_1",
        "US_WASHINGTON_2",
        "EU_ICELAND_DEV_1",
        "US_WASHINGTON_3",
        "US_ARIZONA_2",
        "AP_TOKYO_2",
        "US_CALIFORNIA_1",
        "US_MISSOURI_1",
        "US_UTAH_1",
        "US_TEXAS_3",
        "US_ARIZONA_3",
        "US_GEORGIA_1",
        "US_GEORGIA_2",
        "US_WASHINGTON_4",
        "US_GEORGIA_3",
        "NA_BRITISHCOLUMBIA_1",
        "US_GEORGIA_4",
        "EU_ICELAND_3",
    ]
    """The region where the deployment must be placed."""

    regions: List[
        Literal[
            "REGION_UNSPECIFIED",
            "US_IOWA_1",
            "US_VIRGINIA_1",
            "US_VIRGINIA_2",
            "US_ILLINOIS_1",
            "AP_TOKYO_1",
            "EU_LONDON_1",
            "US_ARIZONA_1",
            "US_TEXAS_1",
            "US_ILLINOIS_2",
            "EU_FRANKFURT_1",
            "US_TEXAS_2",
            "EU_PARIS_1",
            "EU_HELSINKI_1",
            "US_NEVADA_1",
            "EU_ICELAND_1",
            "EU_ICELAND_2",
            "US_WASHINGTON_1",
            "US_WASHINGTON_2",
            "EU_ICELAND_DEV_1",
            "US_WASHINGTON_3",
            "US_ARIZONA_2",
            "AP_TOKYO_2",
            "US_CALIFORNIA_1",
            "US_MISSOURI_1",
            "US_UTAH_1",
            "US_TEXAS_3",
            "US_ARIZONA_3",
            "US_GEORGIA_1",
            "US_GEORGIA_2",
            "US_WASHINGTON_4",
            "US_GEORGIA_3",
            "NA_BRITISHCOLUMBIA_1",
            "US_GEORGIA_4",
            "EU_ICELAND_3",
        ]
    ]
