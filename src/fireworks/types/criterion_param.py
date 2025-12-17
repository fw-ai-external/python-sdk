# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from .._utils import PropertyInfo
from .code_snippets_param import CodeSnippetsParam

__all__ = ["CriterionParam"]


class CriterionParam(TypedDict, total=False):
    code_snippets: Annotated[CodeSnippetsParam, PropertyInfo(alias="codeSnippets")]

    description: str

    name: str

    type: Literal["TYPE_UNSPECIFIED", "CODE_SNIPPETS"]
