# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo
from .gateway_dataset_param import GatewayDatasetParam

__all__ = ["DatasetCreateParams"]


class DatasetCreateParams(TypedDict, total=False):
    dataset: Required[GatewayDatasetParam]

    dataset_id: Required[Annotated[str, PropertyInfo(alias="datasetId")]]

    filter: str

    source_dataset_id: Annotated[str, PropertyInfo(alias="sourceDatasetId")]
