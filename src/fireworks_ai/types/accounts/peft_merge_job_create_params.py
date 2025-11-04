# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["PeftMergeJobCreateParams"]


class PeftMergeJobCreateParams(TypedDict, total=False):
    merged_model: Required[Annotated[str, PropertyInfo(alias="mergedModel")]]

    peft_model: Required[Annotated[str, PropertyInfo(alias="peftModel")]]

    display_name: Annotated[str, PropertyInfo(alias="displayName")]
