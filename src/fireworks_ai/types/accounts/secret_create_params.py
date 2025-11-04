# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["SecretCreateParams"]


class SecretCreateParams(TypedDict, total=False):
    key_name: Required[Annotated[str, PropertyInfo(alias="keyName")]]

    name: Required[str]

    value: str
