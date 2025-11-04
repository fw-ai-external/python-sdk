# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .gateway_status import GatewayStatus
from .gateway_job_state import GatewayJobState

__all__ = ["GatewayPeftMergeJob"]


class GatewayPeftMergeJob(BaseModel):
    merged_model: str = FieldInfo(alias="mergedModel")

    peft_model: str = FieldInfo(alias="peftModel")

    created_by: Optional[str] = FieldInfo(alias="createdBy", default=None)
    """The email address of the user who created this peft merge job."""

    create_time: Optional[datetime] = FieldInfo(alias="createTime", default=None)

    display_name: Optional[str] = FieldInfo(alias="displayName", default=None)

    name: Optional[str] = None

    state: Optional[GatewayJobState] = None
    """JobState represents the state an asynchronous job can be in."""

    status: Optional[GatewayStatus] = None

    update_time: Optional[datetime] = FieldInfo(alias="updateTime", default=None)
    """The update time for the peft merge job."""
