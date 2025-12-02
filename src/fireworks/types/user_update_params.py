# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["UserUpdateParams"]


class UserUpdateParams(TypedDict, total=False):
    account_id: str

    role: Required[str]
    """The user's role, e.g. admin or user."""

    display_name: Annotated[str, PropertyInfo(alias="displayName")]
    """Human-readable display name of the user.

    e.g. "Alice" Must be fewer than 64 characters long.
    """

    email: str
    """The user's email address."""

    service_account: Annotated[bool, PropertyInfo(alias="serviceAccount")]
