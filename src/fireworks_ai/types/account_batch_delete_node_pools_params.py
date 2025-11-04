# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .._types import SequenceNotStr

__all__ = ["AccountBatchDeleteNodePoolsParams"]


class AccountBatchDeleteNodePoolsParams(TypedDict, total=False):
    names: Required[SequenceNotStr[str]]
    """The resource names of the node pools to delete."""
