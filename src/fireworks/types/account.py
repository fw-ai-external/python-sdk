# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .shared.status import Status

__all__ = ["Account"]


class Account(BaseModel):
    email: str
    """For developer accounts, this is the email of the developer user and is
    immutable.

    For ENTERPRISE and BUSINESS accounts, this is mutable and it is the email that
    will recieve the invoice for the account if automated billing is used.
    """

    create_time: Optional[datetime] = FieldInfo(alias="createTime", default=None)
    """The creation time of the account."""

    display_name: Optional[str] = FieldInfo(alias="displayName", default=None)
    """Human-readable display name of the account.

    e.g. "My Account" Must be fewer than 64 characters long.
    """

    name: Optional[str] = None

    state: Optional[Literal["STATE_UNSPECIFIED", "CREATING", "READY", "UPDATING", "DELETING"]] = None
    """The state of the account."""

    status: Optional[Status] = None
    """Contains information about the account status."""

    suspend_state: Optional[
        Literal[
            "UNSUSPENDED", "FAILED_PAYMENTS", "CREDIT_DEPLETED", "MONTHLY_SPEND_LIMIT_EXCEEDED", "BLOCKED_BY_ABUSE_RULE"
        ]
    ] = FieldInfo(alias="suspendState", default=None)

    update_time: Optional[datetime] = FieldInfo(alias="updateTime", default=None)
    """The update time for the account."""
