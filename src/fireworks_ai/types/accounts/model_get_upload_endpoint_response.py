# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["ModelGetUploadEndpointResponse"]


class ModelGetUploadEndpointResponse(BaseModel):
    filename_to_signed_urls: Optional[Dict[str, str]] = FieldInfo(alias="filenameToSignedUrls", default=None)

    filename_to_unsigned_uris: Optional[Dict[str, str]] = FieldInfo(alias="filenameToUnsignedUris", default=None)
    """Unsigned URIs (e.g.

    s3://bucket/key, gs://bucket/key) for uploading model files. Returned when the
    caller has permission to upload to the URIs.
    """
