# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .model_param import ModelParam

__all__ = ["ModelCreateParams"]


class ModelCreateParams(TypedDict, total=False):
    account_id: str

    model_id: Required[Annotated[str, PropertyInfo(alias="modelId")]]
    """ID of the model."""

    cluster: str
    """The resource name of the BYOC cluster to which this model belongs. e.g.

    accounts/my-account/clusters/my-cluster. Empty if it belongs to a Fireworks
    cluster.
    """

    model: ModelParam
    """The properties of the Model being created."""
