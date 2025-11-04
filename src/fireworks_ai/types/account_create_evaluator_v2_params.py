# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .accounts.gateway_evaluator_param import GatewayEvaluatorParam

__all__ = ["AccountCreateEvaluatorV2Params"]


class AccountCreateEvaluatorV2Params(TypedDict, total=False):
    evaluator: Required[GatewayEvaluatorParam]

    evaluator_id: Annotated[str, PropertyInfo(alias="evaluatorId")]
