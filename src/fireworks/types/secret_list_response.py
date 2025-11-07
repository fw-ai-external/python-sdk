# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .secret import Secret
from .._models import BaseModel

__all__ = ["SecretListResponse"]


class SecretListResponse(BaseModel):
    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)

    secrets: Optional[List[Secret]] = None

    total_size: Optional[int] = FieldInfo(alias="totalSize", default=None)
    """The total number of secrets."""
