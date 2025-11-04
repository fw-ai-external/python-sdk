# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["EnvironmentUpdateParams"]


class EnvironmentUpdateParams(TypedDict, total=False):
    account_id: Required[str]

    annotations: Dict[str, str]
    """
    Arbitrary, user-specified metadata. Keys and values must adhere to Kubernetes
    constraints:
    https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/#syntax-and-character-set
    Additionally, the "fireworks.ai/" prefix is reserved.
    """

    base_image_ref: Annotated[str, PropertyInfo(alias="baseImageRef")]
    """The URI of the base container image used for this environment."""

    display_name: Annotated[str, PropertyInfo(alias="displayName")]

    shared: bool
    """
    Whether the environment is shared with all users in the account. This allows all
    users to connect, disconnect, update, delete, clone, and create batch jobs using
    the environment.
    """
