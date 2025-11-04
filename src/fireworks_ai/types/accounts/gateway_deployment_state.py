# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal, TypeAlias

__all__ = ["GatewayDeploymentState"]

GatewayDeploymentState: TypeAlias = Literal[
    "STATE_UNSPECIFIED", "CREATING", "READY", "DELETING", "FAILED", "UPDATING", "DELETED"
]
