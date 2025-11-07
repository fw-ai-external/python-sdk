# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .shared.status import Status
from .shared.inference_parameters import InferenceParameters

__all__ = ["BatchInferenceJob", "JobProgress"]


class JobProgress(BaseModel):
    cached_input_token_count: Optional[int] = FieldInfo(alias="cachedInputTokenCount", default=None)
    """The number of input tokens that hit the prompt cache."""

    epoch: Optional[int] = None
    """
    The epoch for which the progress percent is reported, usually starting from 0.
    This is optional for jobs that don't run in an epoch fasion, e.g. BIJ, EVJ.
    """

    failed_requests: Optional[int] = FieldInfo(alias="failedRequests", default=None)
    """Number of requests that failed to process."""

    input_tokens: Optional[int] = FieldInfo(alias="inputTokens", default=None)
    """Total number of input tokens processed."""

    output_rows: Optional[int] = FieldInfo(alias="outputRows", default=None)
    """Number of output rows generated."""

    output_tokens: Optional[int] = FieldInfo(alias="outputTokens", default=None)
    """Total number of output tokens generated."""

    percent: Optional[int] = None
    """Progress percent, within the range from 0 to 100."""

    successfully_processed_requests: Optional[int] = FieldInfo(alias="successfullyProcessedRequests", default=None)
    """Number of requests that were processed successfully."""

    total_input_requests: Optional[int] = FieldInfo(alias="totalInputRequests", default=None)
    """Total number of input requests/rows in the job."""

    total_processed_requests: Optional[int] = FieldInfo(alias="totalProcessedRequests", default=None)
    """Total number of requests that have been processed (successfully or failed)."""


class BatchInferenceJob(BaseModel):
    continued_from_job_name: Optional[str] = FieldInfo(alias="continuedFromJobName", default=None)
    """
    The resource name of the batch inference job that this job continues from. Used
    for lineage tracking to understand job continuation chains.
    """

    created_by: Optional[str] = FieldInfo(alias="createdBy", default=None)
    """The email address of the user who initiated this batch inference job."""

    create_time: Optional[datetime] = FieldInfo(alias="createTime", default=None)
    """The creation time of the batch inference job."""

    display_name: Optional[str] = FieldInfo(alias="displayName", default=None)

    inference_parameters: Optional[InferenceParameters] = FieldInfo(alias="inferenceParameters", default=None)
    """Parameters controlling the inference process."""

    input_dataset_id: Optional[str] = FieldInfo(alias="inputDatasetId", default=None)
    """The name of the dataset used for inference.

    This is required, except when continued_from_job_name is specified.
    """

    job_progress: Optional[JobProgress] = FieldInfo(alias="jobProgress", default=None)
    """Job progress."""

    model: Optional[str] = None
    """The name of the model to use for inference.

    This is required, except when continued_from_job_name is specified.
    """

    name: Optional[str] = None

    output_dataset_id: Optional[str] = FieldInfo(alias="outputDatasetId", default=None)
    """The name of the dataset used for storing the results.

    This will also contain the error file.
    """

    precision: Optional[
        Literal[
            "PRECISION_UNSPECIFIED",
            "FP16",
            "FP8",
            "FP8_MM",
            "FP8_AR",
            "FP8_MM_KV_ATTN",
            "FP8_KV",
            "FP8_MM_V2",
            "FP8_V2",
            "FP8_MM_KV_ATTN_V2",
            "NF4",
            "FP4",
            "BF16",
            "FP4_BLOCKSCALED_MM",
            "FP4_MX_MOE",
        ]
    ] = None
    """
    The precision with which the model should be served. If PRECISION_UNSPECIFIED, a
    default will be chosen based on the model.
    """

    state: Optional[
        Literal[
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
            "JOB_STATE_CANCELLING",
            "JOB_STATE_EARLY_STOPPED",
        ]
    ] = None
    """JobState represents the state an asynchronous job can be in."""

    status: Optional[Status] = None

    update_time: Optional[datetime] = FieldInfo(alias="updateTime", default=None)
    """The update time for the batch inference job."""
