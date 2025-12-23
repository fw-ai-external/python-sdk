# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo
from .evaluator_source_param import EvaluatorSourceParam

__all__ = ["EvaluatorUpdateParams"]


class EvaluatorUpdateParams(TypedDict, total=False):
    account_id: str

    prepare_code_upload: Annotated[bool, PropertyInfo(alias="prepareCodeUpload")]
    """
    If true, prepare a new code upload/build attempt by transitioning the evaluator
    to BUILDING state. Can be used without update_mask.
    """

    commit_hash: Annotated[str, PropertyInfo(alias="commitHash")]

    default_dataset: Annotated[str, PropertyInfo(alias="defaultDataset")]

    description: str

    display_name: Annotated[str, PropertyInfo(alias="displayName")]

    entry_point: Annotated[str, PropertyInfo(alias="entryPoint")]

    requirements: str

    source: EvaluatorSourceParam
    """Source information for the evaluator codebase."""
