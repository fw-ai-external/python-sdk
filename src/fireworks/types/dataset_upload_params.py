from __future__ import annotations

from typing_extensions import TypedDict

from .._types import FileTypes

__all__ = ["DatasetUploadParams"]


class DatasetUploadParams(TypedDict, total=False):
    account_id: str

    file: FileTypes
