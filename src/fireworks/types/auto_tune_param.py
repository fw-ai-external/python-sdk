# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["AutoTuneParam"]


class AutoTuneParam(TypedDict, total=False):
    long_prompt: Annotated[bool, PropertyInfo(alias="longPrompt")]
    """If true, this deployment is optimized for long prompt lengths."""
