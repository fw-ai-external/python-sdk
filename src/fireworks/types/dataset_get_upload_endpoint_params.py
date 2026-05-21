# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["DatasetGetUploadEndpointParams"]


class DatasetGetUploadEndpointParams(TypedDict, total=False):
    account_id: str

    filename_to_size: Required[Annotated[Dict[str, str], PropertyInfo(alias="filenameToSize")]]
    """A mapping from the file name to its size in bytes."""

    read_mask: Annotated[str, PropertyInfo(alias="readMask")]
    """The fields to be returned in the response.

    If empty or "\\**", all fields will be returned.
    """
