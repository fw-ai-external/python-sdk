# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["DeploymentDeleteParams"]


class DeploymentDeleteParams(TypedDict, total=False):
    account_id: str

    hard: bool
    """If true, this will perform a hard deletion."""

    ignore_checks: Annotated[bool, PropertyInfo(alias="ignoreChecks")]
    """
    If true, this will ignore checks and force the deletion of a deployment that is
    currently deployed and is in use.
    """
