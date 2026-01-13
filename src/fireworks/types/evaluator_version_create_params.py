# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .evaluator_version_param import EvaluatorVersionParam

__all__ = ["EvaluatorVersionCreateParams"]


class EvaluatorVersionCreateParams(TypedDict, total=False):
    account_id: str

    evaluator_version: Required[Annotated[EvaluatorVersionParam, PropertyInfo(alias="evaluatorVersion")]]

    evaluator_version_id: Annotated[str, PropertyInfo(alias="evaluatorVersionId")]
