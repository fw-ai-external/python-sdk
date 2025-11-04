# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .gateway_evaluator import GatewayEvaluator

__all__ = ["EvaluatorListResponse"]


class EvaluatorListResponse(BaseModel):
    evaluators: Optional[List[GatewayEvaluator]] = None

    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)

    total_size: Optional[int] = FieldInfo(alias="totalSize", default=None)
