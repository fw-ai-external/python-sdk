# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .evaluator_source_param import EvaluatorSourceParam

__all__ = ["EvaluatorCreateParams", "Evaluator", "EvaluatorCriterion", "EvaluatorCriterionCodeSnippets"]


class EvaluatorCreateParams(TypedDict, total=False):
    account_id: str

    evaluator: Required[Evaluator]

    evaluator_id: Annotated[str, PropertyInfo(alias="evaluatorId")]


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


class Evaluator(TypedDict, total=False):
    commit_hash: Annotated[str, PropertyInfo(alias="commitHash")]

    criteria: Iterable[EvaluatorCriterion]

    current_version_id: Annotated[str, PropertyInfo(alias="currentVersionId")]
    """
    The version ID of the currently active version of this evaluator. This
    references EvaluatorVersion.VersionId for this evaluator. When set, GetEvaluator
    merges version-specific data (state, requirements, etc.) into the response.
    Empty for legacy evaluators that don't use versioning.
    """

    default_dataset: Annotated[str, PropertyInfo(alias="defaultDataset")]

    description: str

    display_name: Annotated[str, PropertyInfo(alias="displayName")]

    entry_point: Annotated[str, PropertyInfo(alias="entryPoint")]

    requirements: str

    source: EvaluatorSourceParam
    """Source information for the evaluator codebase."""
