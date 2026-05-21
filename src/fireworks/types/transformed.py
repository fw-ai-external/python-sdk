# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["Transformed"]


class Transformed(BaseModel):
    source_dataset_id: str = FieldInfo(alias="sourceDatasetId")

    filter: Optional[str] = None

    original_format: Optional[Literal["FORMAT_UNSPECIFIED", "CHAT", "COMPLETION", "RL"]] = FieldInfo(
        alias="originalFormat", default=None
    )
