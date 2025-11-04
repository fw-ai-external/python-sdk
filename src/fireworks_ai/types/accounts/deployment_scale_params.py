# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["DeploymentScaleParams"]


class DeploymentScaleParams(TypedDict, total=False):
    account_id: Required[str]

    replica_count: Annotated[int, PropertyInfo(alias="replicaCount")]
    """The desired number of replicas."""
