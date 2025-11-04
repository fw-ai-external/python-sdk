# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .gateway_status import GatewayStatus

__all__ = ["GatewayEvaluator", "Criterion", "CriterionCodeSnippets", "RollupSettings"]


class CriterionCodeSnippets(BaseModel):
    entry_file: Optional[str] = FieldInfo(alias="entryFile", default=None)

    entry_func: Optional[str] = FieldInfo(alias="entryFunc", default=None)

    file_contents: Optional[Dict[str, str]] = FieldInfo(alias="fileContents", default=None)

    language: Optional[str] = None


class Criterion(BaseModel):
    code_snippets: Optional[CriterionCodeSnippets] = FieldInfo(alias="codeSnippets", default=None)

    description: Optional[str] = None

    name: Optional[str] = None

    type: Optional[Literal["TYPE_UNSPECIFIED", "CODE_SNIPPETS"]] = None


class RollupSettings(BaseModel):
    criteria_weights: Optional[Dict[str, float]] = FieldInfo(alias="criteriaWeights", default=None)

    python_code: Optional[str] = FieldInfo(alias="pythonCode", default=None)

    skip_rollup: Optional[bool] = FieldInfo(alias="skipRollup", default=None)

    success_threshold: Optional[float] = FieldInfo(alias="successThreshold", default=None)


class GatewayEvaluator(BaseModel):
    commit_hash: Optional[str] = FieldInfo(alias="commitHash", default=None)

    created_by: Optional[str] = FieldInfo(alias="createdBy", default=None)

    create_time: Optional[datetime] = FieldInfo(alias="createTime", default=None)

    criteria: Optional[List[Criterion]] = None

    description: Optional[str] = None

    display_name: Optional[str] = FieldInfo(alias="displayName", default=None)

    entry_point: Optional[str] = FieldInfo(alias="entryPoint", default=None)

    multi_metrics: Optional[bool] = FieldInfo(alias="multiMetrics", default=None)
    """
    If true, the criteria will report multiple metric-score pairs Otherwise, each
    criteria will report the score assigned to the criteria name as metric.
    """

    name: Optional[str] = None

    requirements: Optional[str] = None

    rollup_settings: Optional[RollupSettings] = FieldInfo(alias="rollupSettings", default=None)
    """Strategy for metrics reports summary/rollup. e.g.

    {metric1: 1, metric2: 0.3}, rollup_settings could be criteria_weights: {metric1:
    0.5, metric2: 0.5}, then final score will be 0.5 _ 1 + 0.5 _ 0.3 = 0.65 If
    skip_rollup is true, the rollup step will be skipped since the criteria will
    also report the rollup score and metrics altogether.
    """

    state: Optional[Literal["STATE_UNSPECIFIED", "ACTIVE", "BUILDING", "BUILD_FAILED"]] = None

    status: Optional[GatewayStatus] = None

    update_time: Optional[datetime] = FieldInfo(alias="updateTime", default=None)
