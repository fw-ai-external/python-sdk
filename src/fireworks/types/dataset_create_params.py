# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .dataset_param import DatasetParam

__all__ = ["DatasetCreateParams"]


class DatasetCreateParams(TypedDict, total=False):
    dataset: Required[DatasetParam]

    dataset_id: Required[Annotated[str, PropertyInfo(alias="datasetId")]]

    filter: str

    source_dataset_id: Annotated[str, PropertyInfo(alias="sourceDatasetId")]
