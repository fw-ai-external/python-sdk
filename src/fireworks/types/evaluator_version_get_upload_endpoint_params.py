# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["EvaluatorVersionGetUploadEndpointParams"]


class EvaluatorVersionGetUploadEndpointParams(TypedDict, total=False):
    account_id: str

    evaluator_id: Required[str]

    filename_to_size: Required[Annotated[Dict[str, str], PropertyInfo(alias="filenameToSize")]]
    """
    Map of filename to file size for generating upload signed URLs. Typically
    contains a single entry like {"evaluator.tar.gz": 12345}.
    """
