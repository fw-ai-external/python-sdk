# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .gateway_status import GatewayStatus

__all__ = ["GatewaySnapshot"]


class GatewaySnapshot(BaseModel):
    create_time: Optional[datetime] = FieldInfo(alias="createTime", default=None)
    """The creation time of the snapshot."""

    image_ref: Optional[str] = FieldInfo(alias="imageRef", default=None)
    """The URI of the container image for this snapshot."""

    name: Optional[str] = None

    state: Optional[Literal["STATE_UNSPECIFIED", "CREATING", "READY", "FAILED", "DELETING"]] = None
    """The state of the snapshot."""

    status: Optional[GatewayStatus] = None
    """The status code and message of the snapshot."""

    update_time: Optional[datetime] = FieldInfo(alias="updateTime", default=None)
    """The update time for the snapshot."""
