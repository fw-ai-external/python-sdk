# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["SecretCreateParams"]


class SecretCreateParams(TypedDict, total=False):
    account_id: str

    key_name: Required[Annotated[str, PropertyInfo(alias="keyName")]]

    name: Required[str]

    value: str
    """The secret value.

    This field is INPUT_ONLY and will not be returned in GET or LIST responses for
    security reasons. The value is only accepted when creating or updating secrets.
    """
