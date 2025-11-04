# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["LeaderboardListEvaluationJobsParams"]


class LeaderboardListEvaluationJobsParams(TypedDict, total=False):
    account_id: Required[str]

    filter: str

    order_by: Annotated[str, PropertyInfo(alias="orderBy")]

    page_size: Annotated[int, PropertyInfo(alias="pageSize")]

    page_token: Annotated[str, PropertyInfo(alias="pageToken")]
