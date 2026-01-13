# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["EvaluatorVersionValidateUploadParams"]


class EvaluatorVersionValidateUploadParams(TypedDict, total=False):
    account_id: str

    evaluator_id: Required[str]

    auto_promote: Annotated[bool, PropertyInfo(alias="autoPromote")]
    """
    If true (default), this version will automatically be set as the evaluator's
    current_version_id upon successful build. Set to false if you want to manually
    promote the version later using UpdateEvaluator with current_version_id.
    """
