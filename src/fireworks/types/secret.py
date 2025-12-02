# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["Secret"]


class Secret(BaseModel):
    key_name: str = FieldInfo(alias="keyName")

    name: str

    value: Optional[str] = None
    """The secret value.

    This field is INPUT_ONLY and will not be returned in GET or LIST responses for
    security reasons. The value is only accepted when creating or updating secrets.
    """
