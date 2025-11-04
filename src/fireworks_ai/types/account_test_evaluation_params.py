# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .accounts.evaluation_param import EvaluationParam

__all__ = ["AccountTestEvaluationParams"]


class AccountTestEvaluationParams(TypedDict, total=False):
    evaluation: Required[EvaluationParam]

    sample_data: Required[Annotated[str, PropertyInfo(alias="sampleData")]]
