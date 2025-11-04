# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["GatewaySecret"]


class GatewaySecret(BaseModel):
    key_name: str = FieldInfo(alias="keyName")

    name: str

    value: Optional[str] = None
