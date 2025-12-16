# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .criterion import Criterion
from .shared.status import Status
from .rollup_settings import RollupSettings
from .evaluator_source import EvaluatorSource

__all__ = ["EvaluatorUpdateResponse"]


class EvaluatorUpdateResponse(BaseModel):
    commit_hash: Optional[str] = FieldInfo(alias="commitHash", default=None)

    created_by: Optional[str] = FieldInfo(alias="createdBy", default=None)

    create_time: Optional[datetime] = FieldInfo(alias="createTime", default=None)

    criteria: Optional[List[Criterion]] = None

    default_dataset: Optional[str] = FieldInfo(alias="defaultDataset", default=None)

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

    source: Optional[EvaluatorSource] = None
    """Source information for the evaluator codebase."""

    state: Optional[Literal["STATE_UNSPECIFIED", "ACTIVE", "BUILDING", "BUILD_FAILED"]] = None

    status: Optional[Status] = None

    update_time: Optional[datetime] = FieldInfo(alias="updateTime", default=None)
