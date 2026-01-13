# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["EvaluatorVersionParam"]


class EvaluatorVersionParam(TypedDict, total=False):
    commit_hash: Annotated[str, PropertyInfo(alias="commitHash")]
    """Commit hash of this version from the user's original codebase."""

    entry_point: Annotated[str, PropertyInfo(alias="entryPoint")]
    """Entry point of the evaluator inside the codebase."""

    requirements: str
    """Content for the requirements.txt for package installation."""
