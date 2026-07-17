# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["APIKey"]


class APIKey(BaseModel):
    annotations: Optional[Dict[str, str]] = None
    """Optional key-value annotations for this API key."""

    create_time: Optional[datetime] = FieldInfo(alias="createTime", default=None)
    """Timestamp indicating when the API key was created."""

    display_name: Optional[str] = FieldInfo(alias="displayName", default=None)
    """Display name for the API key, defaults to "default" if not specified."""

    email: Optional[str] = None
    """Email of the user who owns this API key."""

    expire_time: Optional[datetime] = FieldInfo(alias="expireTime", default=None)
    """Timestamp indicating when the API key will expire.

    If not set, the key never expires.
    """

    is_firepass: Optional[bool] = FieldInfo(alias="isFirepass", default=None)
    """True when this key is a FirePass inference key."""

    key: Optional[str] = None
    """
    The actual API key value, only available upon creation and not stored
    thereafter.
    """

    key_id: Optional[str] = FieldInfo(alias="keyId", default=None)
    """Unique identifier (Key ID) for the API key, used primarily for deletion."""

    last_used: Optional[datetime] = FieldInfo(alias="lastUsed", default=None)
    """Timestamp indicating when the API key was last used.

    Not set if the key has never been used.
    """

    prefix: Optional[str] = None

    secure: Optional[bool] = None
    """
    Indicates whether the plaintext value of the API key is unknown to Fireworks. If
    true, Fireworks does not know this API key's plaintext value. If false,
    Fireworks does know the plaintext value.
    """
