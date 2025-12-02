# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .api_key import APIKey
from .._models import BaseModel

__all__ = ["APIKeyListResponse"]


class APIKeyListResponse(BaseModel):
    api_keys: Optional[List[APIKey]] = FieldInfo(alias="apiKeys", default=None)
    """List of API keys retrieved."""

    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)

    total_size: Optional[int] = FieldInfo(alias="totalSize", default=None)
    """The total number of API keys."""
