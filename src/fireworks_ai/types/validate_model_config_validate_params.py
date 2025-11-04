# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["ValidateModelConfigValidateParams"]


class ValidateModelConfigValidateParams(TypedDict, total=False):
    config_json: Required[Annotated[str, PropertyInfo(alias="configJson")]]
    """The config JSON of the model."""

    tokenizer_config_json: Annotated[str, PropertyInfo(alias="tokenizerConfigJson")]
    """The tokenizer config JSON of the model."""
