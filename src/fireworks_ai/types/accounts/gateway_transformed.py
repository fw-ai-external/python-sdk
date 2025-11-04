# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .dataset_format import DatasetFormat

__all__ = ["GatewayTransformed"]


class GatewayTransformed(BaseModel):
    source_dataset_id: str = FieldInfo(alias="sourceDatasetId")

    filter: Optional[str] = None

    original_format: Optional[DatasetFormat] = FieldInfo(alias="originalFormat", default=None)
