# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["APIKeyDeleteParams"]


class APIKeyDeleteParams(TypedDict, total=False):
    account_id: str

    key_id: Required[Annotated[str, PropertyInfo(alias="keyId")]]
    """The key ID for the API key."""
