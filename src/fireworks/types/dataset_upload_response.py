# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["DatasetUploadResponse"]


class DatasetUploadResponse(BaseModel):
    id: Optional[str] = None
    """The dataset id."""

    bytes: Optional[int] = None
    """The size of the file, in bytes."""

    created_at: Optional[int] = None
    """The Unix timestamp (in seconds) for when the file was created."""

    filename: Optional[str] = None
    """The name of the file."""

    object: Optional[str] = None
    """The object type, which is always file."""

    purpose: Optional[str] = None
    """The intended purpose of the file."""
