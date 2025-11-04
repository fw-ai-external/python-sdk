# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["ModelValidateUploadParams"]


class ModelValidateUploadParams(TypedDict, total=False):
    account_id: Required[str]

    config_only: Annotated[bool, PropertyInfo(alias="configOnly")]
    """If true, skip tokenizer and parameter name validation."""

    skip_hf_config_validation: Annotated[bool, PropertyInfo(alias="skipHfConfigValidation")]
    """If true, skip the Hugging Face config validation."""

    trust_remote_code: Annotated[bool, PropertyInfo(alias="trustRemoteCode")]
    """If true, trusts remote code when validating the Hugging Face config."""
