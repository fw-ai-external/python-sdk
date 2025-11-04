# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["EvaluatorGetUploadEndpointParams"]


class EvaluatorGetUploadEndpointParams(TypedDict, total=False):
    account_id: Required[str]

    filename_to_size: Required[Annotated[Dict[str, str], PropertyInfo(alias="filenameToSize")]]

    read_mask: Annotated[str, PropertyInfo(alias="readMask")]
