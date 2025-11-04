# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["VersionUpdateParams"]


class VersionUpdateParams(TypedDict, total=False):
    account_id: Required[str]

    deployment_shape_id: Required[str]

    public: bool
    """If true, this version will be publicly readable."""

    validated: bool
    """If true, this version has been validated."""
