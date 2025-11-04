# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from .provider import Provider
from ..._models import BaseModel
from .assertion import Assertion
from .gateway_status import GatewayStatus

__all__ = ["Evaluation"]


class Evaluation(BaseModel):
    assertions: List[Assertion]

    evaluation_type: str = FieldInfo(alias="evaluationType")

    providers: List[Provider]

    created_by: Optional[str] = FieldInfo(alias="createdBy", default=None)

    create_time: Optional[datetime] = FieldInfo(alias="createTime", default=None)

    description: Optional[str] = None

    name: Optional[str] = None

    status: Optional[GatewayStatus] = None

    update_time: Optional[datetime] = FieldInfo(alias="updateTime", default=None)
    """The update time for the evaluation."""
