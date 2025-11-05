# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["DatasetGetResponse", "EvaluationResult", "Splitted", "Status", "Transformed"]


class EvaluationResult(BaseModel):
    evaluation_job_id: str = FieldInfo(alias="evaluationJobId")


class Splitted(BaseModel):
    source_dataset_id: str = FieldInfo(alias="sourceDatasetId")


class Status(BaseModel):
    code: Optional[
        Literal[
            "OK",
            "CANCELLED",
            "UNKNOWN",
            "INVALID_ARGUMENT",
            "DEADLINE_EXCEEDED",
            "NOT_FOUND",
            "ALREADY_EXISTS",
            "PERMISSION_DENIED",
            "UNAUTHENTICATED",
            "RESOURCE_EXHAUSTED",
            "FAILED_PRECONDITION",
            "ABORTED",
            "OUT_OF_RANGE",
            "UNIMPLEMENTED",
            "INTERNAL",
            "UNAVAILABLE",
            "DATA_LOSS",
        ]
    ] = None
    """The status code."""

    message: Optional[str] = None
    """A developer-facing error message in English."""


class Transformed(BaseModel):
    source_dataset_id: str = FieldInfo(alias="sourceDatasetId")

    filter: Optional[str] = None

    original_format: Optional[Literal["FORMAT_UNSPECIFIED", "CHAT", "COMPLETION", "RL"]] = FieldInfo(
        alias="originalFormat", default=None
    )


class DatasetGetResponse(BaseModel):
    created_by: Optional[str] = FieldInfo(alias="createdBy", default=None)
    """The email address of the user who initiated this fine-tuning job."""

    create_time: Optional[datetime] = FieldInfo(alias="createTime", default=None)

    display_name: Optional[str] = FieldInfo(alias="displayName", default=None)

    estimated_token_count: Optional[str] = FieldInfo(alias="estimatedTokenCount", default=None)
    """The estimated number of tokens in the dataset."""

    eval_protocol: Optional[object] = FieldInfo(alias="evalProtocol", default=None)

    evaluation_result: Optional[EvaluationResult] = FieldInfo(alias="evaluationResult", default=None)

    example_count: Optional[str] = FieldInfo(alias="exampleCount", default=None)

    external_url: Optional[str] = FieldInfo(alias="externalUrl", default=None)

    format: Optional[Literal["FORMAT_UNSPECIFIED", "CHAT", "COMPLETION", "RL"]] = None

    name: Optional[str] = None

    source_job_name: Optional[str] = FieldInfo(alias="sourceJobName", default=None)
    """
    The resource name of the job that created this dataset (e.g., batch inference
    job). Used for lineage tracking to understand dataset provenance.
    """

    splitted: Optional[Splitted] = None

    state: Optional[Literal["STATE_UNSPECIFIED", "UPLOADING", "READY"]] = None

    status: Optional[Status] = None

    transformed: Optional[Transformed] = None

    update_time: Optional[datetime] = FieldInfo(alias="updateTime", default=None)
    """The update time for the dataset."""

    user_uploaded: Optional[object] = FieldInfo(alias="userUploaded", default=None)
