# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["LeaderboardRetrieveParams"]


class LeaderboardRetrieveParams(TypedDict, total=False):
    account_id: Required[str]

    read_mask: Annotated[str, PropertyInfo(alias="readMask")]
    """Optional read mask for leaderboard fields."""
