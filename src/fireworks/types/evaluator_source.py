# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["EvaluatorSource"]


class EvaluatorSource(BaseModel):
    github_repository_name: Optional[str] = FieldInfo(alias="githubRepositoryName", default=None)
    """Normalized GitHub repository name (e.g.

    owner/repository) when the source is GitHub.
    """

    type: Optional[Literal["TYPE_UNSPECIFIED", "TYPE_UPLOAD", "TYPE_GITHUB", "TYPE_TEMPORARY"]] = None
    """Identifies how the evaluator source code is provided."""
