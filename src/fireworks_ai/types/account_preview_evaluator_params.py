# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._types import SequenceNotStr
from .._utils import PropertyInfo
from .accounts.gateway_evaluator_param import GatewayEvaluatorParam

__all__ = ["AccountPreviewEvaluatorParams"]


class AccountPreviewEvaluatorParams(TypedDict, total=False):
    evaluator: Required[GatewayEvaluatorParam]

    sample_data: Required[Annotated[SequenceNotStr[str], PropertyInfo(alias="sampleData")]]

    max_samples: Annotated[int, PropertyInfo(alias="maxSamples")]
