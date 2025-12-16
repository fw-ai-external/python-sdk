# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["CodeSnippets"]


class CodeSnippets(BaseModel):
    entry_file: Optional[str] = FieldInfo(alias="entryFile", default=None)

    entry_func: Optional[str] = FieldInfo(alias="entryFunc", default=None)

    file_contents: Optional[Dict[str, str]] = FieldInfo(alias="fileContents", default=None)

    language: Optional[str] = None
