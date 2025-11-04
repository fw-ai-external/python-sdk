# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal, TypeAlias

__all__ = ["GatewayEnvironmentState"]

GatewayEnvironmentState: TypeAlias = Literal[
    "STATE_UNSPECIFIED",
    "CREATING",
    "DISCONNECTED",
    "CONNECTING",
    "CONNECTED",
    "DISCONNECTING",
    "RECONNECTING",
    "DELETING",
]
