# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo
from .criterion_param import CriterionParam
from .rollup_settings_param import RollupSettingsParam
from .evaluator_source_param import EvaluatorSourceParam

__all__ = ["EvaluatorUpdateParams"]


class EvaluatorUpdateParams(TypedDict, total=False):
    account_id: str

    prepare_code_upload: Annotated[bool, PropertyInfo(alias="prepareCodeUpload")]
    """
    If true, prepare a new code upload/build attempt by transitioning the evaluator
    to BUILDING state. Can be used without update_mask.
    """

    commit_hash: Annotated[str, PropertyInfo(alias="commitHash")]

    criteria: Iterable[CriterionParam]

    default_dataset: Annotated[str, PropertyInfo(alias="defaultDataset")]

    description: str

    display_name: Annotated[str, PropertyInfo(alias="displayName")]

    entry_point: Annotated[str, PropertyInfo(alias="entryPoint")]

    multi_metrics: Annotated[bool, PropertyInfo(alias="multiMetrics")]
    """
    If true, the criteria will report multiple metric-score pairs Otherwise, each
    criteria will report the score assigned to the criteria name as metric.
    """

    requirements: str

    rollup_settings: Annotated[RollupSettingsParam, PropertyInfo(alias="rollupSettings")]
    """Strategy for metrics reports summary/rollup. e.g.

    {metric1: 1, metric2: 0.3}, rollup_settings could be criteria_weights: {metric1:
    0.5, metric2: 0.5}, then final score will be 0.5 _ 1 + 0.5 _ 0.3 = 0.65 If
    skip_rollup is true, the rollup step will be skipped since the criteria will
    also report the rollup score and metrics altogether.
    """

    source: EvaluatorSourceParam
    """Source information for the evaluator codebase."""
