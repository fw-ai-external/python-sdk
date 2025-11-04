# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo
from .gateway_environment_param import GatewayEnvironmentParam

__all__ = ["EnvironmentCreateParams"]


class EnvironmentCreateParams(TypedDict, total=False):
    environment: Required[GatewayEnvironmentParam]
    """The properties of the Environment being created."""

    environment_id: Required[Annotated[str, PropertyInfo(alias="environmentId")]]
