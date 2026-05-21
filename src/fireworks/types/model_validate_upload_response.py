from typing import List, Optional

from .._models import BaseModel

__all__ = ["ModelValidateUploadResponse"]


class ModelValidateUploadResponse(BaseModel):
    warnings: Optional[List[str]] = None
