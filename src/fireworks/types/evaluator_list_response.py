# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .shared.status import Status
from .evaluator_source import EvaluatorSource

__all__ = ["EvaluatorListResponse", "Criterion", "CriterionCodeSnippets"]


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


class EvaluatorListResponse(BaseModel):
    commit_hash: Optional[str] = FieldInfo(alias="commitHash", default=None)

    created_by: Optional[str] = FieldInfo(alias="createdBy", default=None)

    create_time: Optional[datetime] = FieldInfo(alias="createTime", default=None)

    criteria: Optional[List[Criterion]] = None

    current_version_id: Optional[str] = FieldInfo(alias="currentVersionId", default=None)
    """
    The version ID of the currently active version of this evaluator. This
    references EvaluatorVersion.VersionId for this evaluator. When set, GetEvaluator
    merges version-specific data (state, requirements, etc.) into the response.
    Empty for legacy evaluators that don't use versioning.
    """

    default_dataset: Optional[str] = FieldInfo(alias="defaultDataset", default=None)

    description: Optional[str] = None

    display_name: Optional[str] = FieldInfo(alias="displayName", default=None)

    entry_point: Optional[str] = FieldInfo(alias="entryPoint", default=None)

    name: Optional[str] = None

    requirements: Optional[str] = None

    source: Optional[EvaluatorSource] = None
    """Source information for the evaluator codebase."""

    state: Optional[Literal["STATE_UNSPECIFIED", "ACTIVE", "BUILDING", "BUILD_FAILED"]] = None

    status: Optional[Status] = None

    update_time: Optional[datetime] = FieldInfo(alias="updateTime", default=None)
