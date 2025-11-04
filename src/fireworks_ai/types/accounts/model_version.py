# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from .model import Model
from ..._models import BaseModel

__all__ = ["ModelVersion"]


class ModelVersion(BaseModel):
    create_time: Optional[datetime] = FieldInfo(alias="createTime", default=None)

    name: Optional[str] = None
    """The resource name of the deployment snapshot."""

    snapshot: Optional[Model] = None
