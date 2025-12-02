# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["LoraUpdateParams"]


class LoraUpdateParams(TypedDict, total=False):
    account_id: Required[str]

    default: bool
    """
    If true, this is the default target when querying this model without the
    `#<deployment>` suffix. The first deployment a model is deployed to will have
    this field set to true.
    """

    deployment: str
    """The resource name of the base deployment the model is deployed to."""

    description: str
    """Description of the resource."""

    display_name: Annotated[str, PropertyInfo(alias="displayName")]

    model: str

    public: bool
    """If true, the deployed model will be publicly reachable."""

    serverless: bool
