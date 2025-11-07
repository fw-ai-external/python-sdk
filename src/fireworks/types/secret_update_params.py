# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["SecretUpdateParams"]


class SecretUpdateParams(TypedDict, total=False):
    account_id: Required[str]

    key_name: Required[Annotated[str, PropertyInfo(alias="keyName")]]

    value: str
