# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["PeftDetails"]


class PeftDetails(BaseModel):
    base_model: str = FieldInfo(alias="baseModel")

    r: int
    """The rank of the update matrices. Must be between 4 and 64, inclusive."""

    target_modules: List[str] = FieldInfo(alias="targetModules")

    base_model_type: Optional[str] = FieldInfo(alias="baseModelType", default=None)
    """The type of the model."""

    merge_addon_model_name: Optional[str] = FieldInfo(alias="mergeAddonModelName", default=None)
