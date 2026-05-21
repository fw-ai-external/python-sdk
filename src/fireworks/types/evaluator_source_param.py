# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["EvaluatorSourceParam"]


class EvaluatorSourceParam(TypedDict, total=False):
    github_repository_name: Annotated[str, PropertyInfo(alias="githubRepositoryName")]
    """Normalized GitHub repository name (e.g.

    owner/repository) when the source is GitHub.
    """

    type: Literal["TYPE_UNSPECIFIED", "TYPE_UPLOAD", "TYPE_GITHUB", "TYPE_TEMPORARY"]
    """Identifies how the evaluator source code is provided."""
