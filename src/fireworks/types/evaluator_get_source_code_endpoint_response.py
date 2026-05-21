from typing import Dict, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["EvaluatorGetSourceCodeEndpointResponse"]


class EvaluatorGetSourceCodeEndpointResponse(BaseModel):
    filename_to_signed_urls: Optional[Dict[str, str]] = FieldInfo(alias="filenameToSignedUrls", default=None)
