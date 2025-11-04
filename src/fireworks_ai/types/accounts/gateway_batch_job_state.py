# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal, TypeAlias

__all__ = ["GatewayBatchJobState"]

GatewayBatchJobState: TypeAlias = Literal[
    "STATE_UNSPECIFIED",
    "CREATING",
    "QUEUED",
    "PENDING",
    "RUNNING",
    "COMPLETED",
    "FAILED",
    "CANCELLING",
    "CANCELLED",
    "DELETING",
]
