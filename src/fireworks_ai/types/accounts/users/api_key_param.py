# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["APIKeyParam"]


class APIKeyParam(TypedDict, total=False):
    display_name: Annotated[str, PropertyInfo(alias="displayName")]
    """Display name for the API key, defaults to "default" if not specified."""

    expire_time: Annotated[Union[str, datetime], PropertyInfo(alias="expireTime", format="iso8601")]
    """Timestamp indicating when the API key will expire.

    If not set, the key never expires.
    """
