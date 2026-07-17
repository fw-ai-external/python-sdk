# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .shared.status import Status

__all__ = ["Account", "NotificationSettings", "NotificationSettingsMonthlySpendThreshold"]


class NotificationSettingsMonthlySpendThreshold(BaseModel):
    """Represents an amount of money with its currency type."""

    currency_code: Optional[str] = FieldInfo(alias="currencyCode", default=None)
    """The three-letter currency code defined in ISO 4217."""

    nanos: Optional[int] = None
    """
    Number of nano (10^-9) units of the amount. The value must be between
    -999,999,999 and +999,999,999 inclusive. If `units` is positive, `nanos` must be
    positive or zero. If `units` is zero, `nanos` can be positive, zero, or
    negative. If `units` is negative, `nanos` must be negative or zero. For example
    $-1.75 is represented as `units`=-1 and `nanos`=-750,000,000.
    """

    units: Optional[str] = None
    """
    The whole units of the amount. For example if `currencyCode` is `"USD"`, then 1
    unit is one US dollar.
    """


class NotificationSettings(BaseModel):
    """Notification settings for this account."""

    monthly_spend_thresholds: Optional[List[NotificationSettingsMonthlySpendThreshold]] = FieldInfo(
        alias="monthlySpendThresholds", default=None
    )
    """
    Spend thresholds at which to send monthly usage warning emails. These should be
    below the account's monthly spend quota. Example: [{currency_code: "USD", units:
    500}, {currency_code: "USD", units: 800}] would alert at $500 and $800. Note: An
    alert at 80% of the monthly spend limit is always added in addition to the
    thresholds specified in this list.
    """


class Account(BaseModel):
    email: str
    """The primary email for the account.

    This is used for billing invoices and account notifications.
    """

    account_type: Optional[Literal["ACCOUNT_TYPE_UNSPECIFIED", "ENTERPRISE"]] = FieldInfo(
        alias="accountType", default=None
    )
    """The type of the account."""

    create_time: Optional[datetime] = FieldInfo(alias="createTime", default=None)
    """The creation time of the account."""

    display_name: Optional[str] = FieldInfo(alias="displayName", default=None)
    """Human-readable display name of the account.

    e.g. "My Account" Must be fewer than 64 characters long.
    """

    name: Optional[str] = None

    notification_settings: Optional[NotificationSettings] = FieldInfo(alias="notificationSettings", default=None)
    """Notification settings for this account."""

    productivity_only: Optional[bool] = FieldInfo(alias="productivityOnly", default=None)
    """Marks this account as productivity/coding-only. Set once at account creation."""

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
