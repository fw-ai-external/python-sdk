# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["EvaluatorListParams"]


class EvaluatorListParams(TypedDict, total=False):
    filter: str

    order_by: Annotated[str, PropertyInfo(alias="orderBy")]

    page_size: Annotated[int, PropertyInfo(alias="pageSize")]

    page_token: Annotated[str, PropertyInfo(alias="pageToken")]

    read_mask: Annotated[str, PropertyInfo(alias="readMask")]
    """The fields to be returned in the response.

    If empty or "\\**", all fields will be returned.
    """
