# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["UserUpdateParams"]


class UserUpdateParams(TypedDict, total=False):
    account_id: str

    role: Required[str]
    """
    The user's role: admin, user, contributor, inference-user, or custom. When set
    to "custom", the user's permissions are governed by permission_preset.
    """

    display_name: Annotated[str, PropertyInfo(alias="displayName")]
    """Human-readable display name of the user.

    e.g. "Alice" Must be fewer than 64 characters long.
    """

    email: str
    """The user's email address."""

    permission_preset: Annotated[str, PropertyInfo(alias="permissionPreset")]
    """The permission preset for this user. Only valid when role is "custom"."""

    service_account: Annotated[bool, PropertyInfo(alias="serviceAccount")]
