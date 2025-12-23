# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .shared.status import Status
from .evaluator_source import EvaluatorSource

__all__ = ["EvaluatorUpdateResponse"]


class EvaluatorUpdateResponse(BaseModel):
    commit_hash: Optional[str] = FieldInfo(alias="commitHash", default=None)

    created_by: Optional[str] = FieldInfo(alias="createdBy", default=None)

    create_time: Optional[datetime] = FieldInfo(alias="createTime", default=None)

    default_dataset: Optional[str] = FieldInfo(alias="defaultDataset", default=None)

    description: Optional[str] = None

    display_name: Optional[str] = FieldInfo(alias="displayName", default=None)

    entry_point: Optional[str] = FieldInfo(alias="entryPoint", default=None)

    name: Optional[str] = None

    requirements: Optional[str] = None

    source: Optional[EvaluatorSource] = None
    """Source information for the evaluator codebase."""

    state: Optional[Literal["STATE_UNSPECIFIED", "ACTIVE", "BUILDING", "BUILD_FAILED"]] = None

    status: Optional[Status] = None

    update_time: Optional[datetime] = FieldInfo(alias="updateTime", default=None)
