# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["DatasetSplitParams"]


class DatasetSplitParams(TypedDict, total=False):
    account_id: Required[str]

    chunk_size: Annotated[int, PropertyInfo(alias="chunkSize")]

    parent: str
    """The parent account ID of the requester."""
