# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .shared.status import Status

__all__ = ["User"]


class User(BaseModel):
    role: str
    """The user's role: admin, user, contributor, or inference-user."""

    create_time: Optional[datetime] = FieldInfo(alias="createTime", default=None)
    """The creation time of the user."""

    display_name: Optional[str] = FieldInfo(alias="displayName", default=None)
    """Human-readable display name of the user.

    e.g. "Alice" Must be fewer than 64 characters long.
    """

    email: Optional[str] = None
    """The user's email address."""

    name: Optional[str] = None

    service_account: Optional[bool] = FieldInfo(alias="serviceAccount", default=None)

    state: Optional[Literal["STATE_UNSPECIFIED", "CREATING", "READY", "UPDATING", "DELETING"]] = None
    """The state of the user."""

    status: Optional[Status] = None
    """Contains information about the user status."""

    update_time: Optional[datetime] = FieldInfo(alias="updateTime", default=None)
    """The update time for the user."""
