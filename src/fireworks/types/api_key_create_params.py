# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .api_key_param import APIKeyParam

__all__ = ["APIKeyCreateParams"]


class APIKeyCreateParams(TypedDict, total=False):
    account_id: str

    api_key: Required[Annotated[APIKeyParam, PropertyInfo(alias="apiKey")]]
    """The API key to be created."""
