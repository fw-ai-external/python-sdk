# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["PreviewEvaluationResponse", "Result"]


class Result(BaseModel):
    messages: Optional[List[object]] = None

    metrics: Optional[Dict[str, float]] = None

    reason: Optional[str] = None

    score: Optional[float] = None
    """Score (if applicable) Deprecated: Use metrics field instead."""

    success: Optional[bool] = None


class PreviewEvaluationResponse(BaseModel):
    results: Optional[List[Result]] = None

    total_runtime_ms: Optional[str] = FieldInfo(alias="totalRuntimeMs", default=None)

    total_samples: Optional[int] = FieldInfo(alias="totalSamples", default=None)
