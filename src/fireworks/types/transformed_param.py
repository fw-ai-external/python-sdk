# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["TransformedParam"]


class TransformedParam(TypedDict, total=False):
    source_dataset_id: Required[Annotated[str, PropertyInfo(alias="sourceDatasetId")]]

    filter: str

    original_format: Annotated[
        Literal["FORMAT_UNSPECIFIED", "CHAT", "COMPLETION", "RL"], PropertyInfo(alias="originalFormat")
    ]
