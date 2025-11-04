# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo
from .dataset_format import DatasetFormat

__all__ = ["GatewayTransformedParam"]


class GatewayTransformedParam(TypedDict, total=False):
    source_dataset_id: Required[Annotated[str, PropertyInfo(alias="sourceDatasetId")]]

    filter: str

    original_format: Annotated[DatasetFormat, PropertyInfo(alias="originalFormat")]
