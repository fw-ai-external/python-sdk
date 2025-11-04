# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal, TypeAlias

__all__ = ["GatewayJobState"]

GatewayJobState: TypeAlias = Literal[
    "JOB_STATE_UNSPECIFIED",
    "JOB_STATE_CREATING",
    "JOB_STATE_RUNNING",
    "JOB_STATE_COMPLETED",
    "JOB_STATE_FAILED",
    "JOB_STATE_CANCELLED",
    "JOB_STATE_DELETING",
    "JOB_STATE_WRITING_RESULTS",
    "JOB_STATE_VALIDATING",
    "JOB_STATE_DELETING_CLEANING_UP",
    "JOB_STATE_PENDING",
    "JOB_STATE_EXPIRED",
    "JOB_STATE_RE_QUEUEING",
    "JOB_STATE_CREATING_INPUT_DATASET",
    "JOB_STATE_IDLE",
]
