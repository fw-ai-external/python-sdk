# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["DatasetGetDownloadEndpointParams"]


class DatasetGetDownloadEndpointParams(TypedDict, total=False):
    account_id: Required[str]

    download_lineage: Annotated[bool, PropertyInfo(alias="downloadLineage")]
    """
    If true, downloads entire lineage chain (all related datasets). Filenames will
    be prefixed with dataset IDs to avoid collisions.
    """

    read_mask: Annotated[str, PropertyInfo(alias="readMask")]
    """The fields to be returned in the response.

    If empty or "\\**", all fields will be returned.
    """
