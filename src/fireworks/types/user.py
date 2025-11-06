# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["User", "Status"]


class Status(BaseModel):
    code: Optional[
        Literal[
            "OK",
            "CANCELLED",
            "UNKNOWN",
            "INVALID_ARGUMENT",
            "DEADLINE_EXCEEDED",
            "NOT_FOUND",
            "ALREADY_EXISTS",
            "PERMISSION_DENIED",
            "UNAUTHENTICATED",
            "RESOURCE_EXHAUSTED",
            "FAILED_PRECONDITION",
            "ABORTED",
            "OUT_OF_RANGE",
            "UNIMPLEMENTED",
            "INTERNAL",
            "UNAVAILABLE",
            "DATA_LOSS",
        ]
    ] = None
    """The status code."""

    message: Optional[str] = None
    """A developer-facing error message in English."""


class User(BaseModel):
    role: str
    """The user's role, e.g. admin or user."""

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
