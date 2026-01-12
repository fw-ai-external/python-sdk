# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Literal, Annotated, TypedDict

from .._utils import PropertyInfo
from .evaluator_source_param import EvaluatorSourceParam

__all__ = ["EvaluatorUpdateParams", "Criterion", "CriterionCodeSnippets"]


class EvaluatorUpdateParams(TypedDict, total=False):
    account_id: str

    prepare_code_upload: Annotated[bool, PropertyInfo(alias="prepareCodeUpload")]
    """
    If true, prepare a new code upload/build attempt by transitioning the evaluator
    to BUILDING state. Can be used without update_mask.
    """

    commit_hash: Annotated[str, PropertyInfo(alias="commitHash")]

    criteria: Iterable[Criterion]

    default_dataset: Annotated[str, PropertyInfo(alias="defaultDataset")]

    description: str

    display_name: Annotated[str, PropertyInfo(alias="displayName")]

    entry_point: Annotated[str, PropertyInfo(alias="entryPoint")]

    requirements: str

    source: EvaluatorSourceParam
    """Source information for the evaluator codebase."""


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
