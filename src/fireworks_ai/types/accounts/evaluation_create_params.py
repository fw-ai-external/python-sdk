# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo
from .evaluation_param import EvaluationParam

__all__ = ["EvaluationCreateParams"]


class EvaluationCreateParams(TypedDict, total=False):
    evaluation: Required[EvaluationParam]

    evaluation_id: Annotated[str, PropertyInfo(alias="evaluationId")]
