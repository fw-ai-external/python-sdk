# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo
from .gateway_leaderboard_param import GatewayLeaderboardParam

__all__ = ["LeaderboardCreateParams"]


class LeaderboardCreateParams(TypedDict, total=False):
    leaderboard: Required[GatewayLeaderboardParam]
    """Leaderboard to create."""

    leaderboard_id: Annotated[str, PropertyInfo(alias="leaderboardId")]
    """Optional explicit leaderboard ID (defaults to server-generated)."""
