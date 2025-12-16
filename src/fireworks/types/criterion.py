# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .code_snippets import CodeSnippets

__all__ = ["Criterion"]


class Criterion(BaseModel):
    code_snippets: Optional[CodeSnippets] = FieldInfo(alias="codeSnippets", default=None)

    description: Optional[str] = None

    name: Optional[str] = None

    type: Optional[Literal["TYPE_UNSPECIFIED", "CODE_SNIPPETS"]] = None
