# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Literal, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["GatewayEvaluatorParam", "Criterion", "CriterionCodeSnippets", "RollupSettings"]


class CriterionCodeSnippets(TypedDict, total=False):
    entry_file: Annotated[str, PropertyInfo(alias="entryFile")]

    entry_func: Annotated[str, PropertyInfo(alias="entryFunc")]

    file_contents: Annotated[Dict[str, str], PropertyInfo(alias="fileContents")]

    language: str


class Criterion(TypedDict, total=False):
    code_snippets: Annotated[CriterionCodeSnippets, PropertyInfo(alias="codeSnippets")]

    description: str

    name: str

    type: Literal["TYPE_UNSPECIFIED", "CODE_SNIPPETS"]


class RollupSettings(TypedDict, total=False):
    criteria_weights: Annotated[Dict[str, float], PropertyInfo(alias="criteriaWeights")]

    python_code: Annotated[str, PropertyInfo(alias="pythonCode")]

    skip_rollup: Annotated[bool, PropertyInfo(alias="skipRollup")]

    success_threshold: Annotated[float, PropertyInfo(alias="successThreshold")]


class GatewayEvaluatorParam(TypedDict, total=False):
    commit_hash: Annotated[str, PropertyInfo(alias="commitHash")]

    criteria: Iterable[Criterion]

    description: str

    display_name: Annotated[str, PropertyInfo(alias="displayName")]

    entry_point: Annotated[str, PropertyInfo(alias="entryPoint")]

    multi_metrics: Annotated[bool, PropertyInfo(alias="multiMetrics")]
    """
    If true, the criteria will report multiple metric-score pairs Otherwise, each
    criteria will report the score assigned to the criteria name as metric.
    """

    requirements: str

    rollup_settings: Annotated[RollupSettings, PropertyInfo(alias="rollupSettings")]
    """Strategy for metrics reports summary/rollup. e.g.

    {metric1: 1, metric2: 0.3}, rollup_settings could be criteria_weights: {metric1:
    0.5, metric2: 0.5}, then final score will be 0.5 _ 1 + 0.5 _ 0.3 = 0.65 If
    skip_rollup is true, the rollup step will be skipped since the criteria will
    also report the rollup score and metrics altogether.
    """
