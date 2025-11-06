# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["SplittedParam"]


class SplittedParam(TypedDict, total=False):
    source_dataset_id: Required[Annotated[str, PropertyInfo(alias="sourceDatasetId")]]
