# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["Splitted"]


class Splitted(BaseModel):
    source_dataset_id: str = FieldInfo(alias="sourceDatasetId")
