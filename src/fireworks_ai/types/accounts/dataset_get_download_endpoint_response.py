# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["DatasetGetDownloadEndpointResponse"]


class DatasetGetDownloadEndpointResponse(BaseModel):
    filename_to_signed_urls: Optional[Dict[str, str]] = FieldInfo(alias="filenameToSignedUrls", default=None)
