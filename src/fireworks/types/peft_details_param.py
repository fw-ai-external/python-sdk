# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._types import SequenceNotStr
from .._utils import PropertyInfo

__all__ = ["PeftDetailsParam"]


class PeftDetailsParam(TypedDict, total=False):
    base_model: Required[Annotated[str, PropertyInfo(alias="baseModel")]]

    r: Required[int]
    """The rank of the update matrices. Must be between 4 and 64, inclusive."""

    target_modules: Required[Annotated[SequenceNotStr[str], PropertyInfo(alias="targetModules")]]

    merge_addon_model_name: Annotated[str, PropertyInfo(alias="mergeAddonModelName")]
