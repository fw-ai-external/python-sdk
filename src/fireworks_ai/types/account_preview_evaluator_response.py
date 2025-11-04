# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["AccountPreviewEvaluatorResponse", "Result"]


class Result(BaseModel):
    per_metric_evals: Optional[Dict[str, object]] = FieldInfo(alias="perMetricEvals", default=None)

    reason: Optional[str] = None

    score: Optional[float] = None

    success: Optional[str] = None


class AccountPreviewEvaluatorResponse(BaseModel):
    results: Optional[List[Result]] = None

    stderr: Optional[List[str]] = None

    stdout: Optional[List[str]] = None

    total_runtime_ms: Optional[str] = FieldInfo(alias="totalRuntimeMs", default=None)

    total_samples: Optional[int] = FieldInfo(alias="totalSamples", default=None)
