# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .gateway_secret import GatewaySecret

__all__ = ["SecretListResponse"]


class SecretListResponse(BaseModel):
    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)

    secrets: Optional[List[GatewaySecret]] = None

    total_size: Optional[int] = FieldInfo(alias="totalSize", default=None)
    """The total number of secrets."""
