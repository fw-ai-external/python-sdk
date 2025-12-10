# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._types import SequenceNotStr
from .._utils import PropertyInfo

__all__ = [
    "EvaluatorPreviewParams",
    "Evaluator",
    "EvaluatorCriterion",
    "EvaluatorCriterionCodeSnippets",
    "EvaluatorRollupSettings",
    "EvaluatorSource",
]


class EvaluatorPreviewParams(TypedDict, total=False):
    account_id: str

    evaluator: Required[Evaluator]

    sample_data: Required[Annotated[SequenceNotStr[str], PropertyInfo(alias="sampleData")]]

    max_samples: Annotated[int, PropertyInfo(alias="maxSamples")]


class EvaluatorCriterionCodeSnippets(TypedDict, total=False):
    entry_file: Annotated[str, PropertyInfo(alias="entryFile")]

    entry_func: Annotated[str, PropertyInfo(alias="entryFunc")]

    file_contents: Annotated[Dict[str, str], PropertyInfo(alias="fileContents")]

    language: str


class EvaluatorCriterion(TypedDict, total=False):
    code_snippets: Annotated[EvaluatorCriterionCodeSnippets, PropertyInfo(alias="codeSnippets")]

    description: str

    name: str

    type: Literal["TYPE_UNSPECIFIED", "CODE_SNIPPETS"]


class EvaluatorRollupSettings(TypedDict, total=False):
    """Strategy for metrics reports summary/rollup.
    e.g.

    {metric1: 1, metric2: 0.3}, rollup_settings could be criteria_weights: {metric1: 0.5, metric2: 0.5}, then final score will be 0.5 * 1 + 0.5 * 0.3 = 0.65
    If skip_rollup is true, the rollup step will be skipped since the criteria will also report the rollup score and metrics altogether.
    """

    criteria_weights: Annotated[Dict[str, float], PropertyInfo(alias="criteriaWeights")]

    python_code: Annotated[str, PropertyInfo(alias="pythonCode")]

    skip_rollup: Annotated[bool, PropertyInfo(alias="skipRollup")]

    success_threshold: Annotated[float, PropertyInfo(alias="successThreshold")]


class EvaluatorSource(TypedDict, total=False):
    """Source information for the evaluator codebase."""

    github_repository_name: Annotated[str, PropertyInfo(alias="githubRepositoryName")]
    """Normalized GitHub repository name (e.g.

    owner/repository) when the source is GitHub.
    """

    type: Literal["TYPE_UNSPECIFIED", "TYPE_UPLOAD", "TYPE_GITHUB", "TYPE_TEMPORARY"]
    """Identifies how the evaluator source code is provided."""


class Evaluator(TypedDict, total=False):
    commit_hash: Annotated[str, PropertyInfo(alias="commitHash")]

    criteria: Iterable[EvaluatorCriterion]

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

    rollup_settings: Annotated[EvaluatorRollupSettings, PropertyInfo(alias="rollupSettings")]
    """Strategy for metrics reports summary/rollup. e.g.

    {metric1: 1, metric2: 0.3}, rollup_settings could be criteria_weights: {metric1:
    0.5, metric2: 0.5}, then final score will be 0.5 _ 1 + 0.5 _ 0.3 = 0.65 If
    skip_rollup is true, the rollup step will be skipped since the criteria will
    also report the rollup score and metrics altogether.
    """

    source: EvaluatorSource
    """Source information for the evaluator codebase."""
