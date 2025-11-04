# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo
from .gateway_environment_connection_param import GatewayEnvironmentConnectionParam

__all__ = ["EnvironmentConnectParams"]


class EnvironmentConnectParams(TypedDict, total=False):
    account_id: Required[str]

    connection: Required[GatewayEnvironmentConnectionParam]

    vscode_version: Annotated[str, PropertyInfo(alias="vscodeVersion")]
