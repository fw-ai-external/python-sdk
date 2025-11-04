# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo
from .deployment_precision import DeploymentPrecision

__all__ = ["ModelPrepareParams"]


class ModelPrepareParams(TypedDict, total=False):
    account_id: Required[str]

    precision: DeploymentPrecision

    read_mask: Annotated[str, PropertyInfo(alias="readMask")]
