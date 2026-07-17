# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .placement import Placement
from .shared.status import Status

__all__ = ["BatchInferenceJob", "InferenceParameters", "JobProgress", "Lifecycle"]


class InferenceParameters(BaseModel):
    """Parameters controlling the inference process."""

    extra_body: Optional[str] = FieldInfo(alias="extraBody", default=None)
    """
    Additional parameters for the inference request as a JSON string. For example:
    "{\"stop\": [\"\\n\"]}".
    """

    max_tokens: Optional[int] = FieldInfo(alias="maxTokens", default=None)
    """Maximum number of tokens to generate per response."""

    n: Optional[int] = None
    """Number of response candidates to generate per input."""

    temperature: Optional[float] = None
    """Sampling temperature, typically between 0 and 2."""

    top_k: Optional[int] = FieldInfo(alias="topK", default=None)
    """Top-k sampling parameter, limits the token selection to the top k tokens."""

    top_p: Optional[float] = FieldInfo(alias="topP", default=None)
    """Top-p sampling parameter, typically between 0 and 1."""


class JobProgress(BaseModel):
    """Job progress."""

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


class Lifecycle(BaseModel):
    """Lifecycle milestone timestamps (validated / run-start / end) for the job."""

    end_time: Optional[datetime] = FieldInfo(alias="endTime", default=None)
    """
    The terminal time of the job (when it reached COMPLETED, FAILED, EXPIRED, or
    CANCELLED).
    """

    run_start_time: Optional[datetime] = FieldInfo(alias="runStartTime", default=None)
    """When the runner first started processing (the job first became RUNNING)."""

    validated_time: Optional[datetime] = FieldInfo(alias="validatedTime", default=None)
    """When dataset validation completed and the job left VALIDATING.

    Unset for jobs that skip validation or that fail before validating.
    """


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

    expire_time: Optional[datetime] = FieldInfo(alias="expireTime", default=None)
    """
    The time when the batch inference job will expire (stop running); any completed
    requests will have been written to the output dataset by then.

    This is the job's effective execution deadline, derived by the server as
    create_time + the bounded run window (see max_job_duration). It is exposed so
    customers can read back the concrete deadline without recomputing it
    client-side. OUTPUT_ONLY: it is always computed server-side and any
    client-supplied value is ignored (previously this was a SUPERUSER_ONLY input
    that overlapped with max_job_duration; the two are now unified as one public
    input (duration) + one public derived deadline (this timestamp)).
    """

    inference_parameters: Optional[InferenceParameters] = FieldInfo(alias="inferenceParameters", default=None)
    """Parameters controlling the inference process."""

    input_dataset_id: Optional[str] = FieldInfo(alias="inputDatasetId", default=None)
    """The name of the dataset used for inference.

    This is required, except when continued_from_job_name is specified.
    """

    job_progress: Optional[JobProgress] = FieldInfo(alias="jobProgress", default=None)
    """Job progress."""

    lifecycle: Optional[Lifecycle] = None
    """Lifecycle milestone timestamps (validated / run-start / end) for the job."""

    max_job_duration: Optional[str] = FieldInfo(alias="maxJobDuration", default=None)
    """
    The customer-requested wall-clock run window for the job: how long it may run
    before it is expired. This is the single public input that controls the job's
    lifetime. The server bounds it to [12h, 72h]; if unset it defaults to 24h. The
    resulting concrete deadline is surfaced as expire_time (= create_time + the
    bounded window) and the job is expired once that deadline passes. A duration
    (relative) is used rather than an absolute timestamp because the client does not
    know create_time at submit time. Customer-visible input.
    """

    model: Optional[str] = None
    """The name of the model to use for inference.

    This is required, except when continued_from_job_name is specified.
    """

    name: Optional[str] = None

    output_dataset_id: Optional[str] = FieldInfo(alias="outputDatasetId", default=None)
    """The name of the dataset used for storing the results.

    This will also contain the error file.
    """

    placement: Optional[Placement] = None
    """
    The desired geographic region where the batch inference job runs. Set
    `multi_region` to limit the job to a region group (US, EUROPE, APAC, or GLOBAL).
    If unspecified, the job runs in any supported region.
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
            "JOB_STATE_PAUSED",
            "JOB_STATE_DELETED",
            "JOB_STATE_ARCHIVED",
        ]
    ] = None
    """JobState represents the state an asynchronous job can be in."""

    status: Optional[Status] = None

    system_prompt: Optional[str] = FieldInfo(alias="systemPrompt", default=None)
    """Optional job-level system prompt.

    When set, it is injected as a leading system message into every input row that
    does NOT already begin with a system message (a row's own leading system message
    takes precedence). This lets callers avoid repeating a large, static system
    prompt on every row of the input dataset, shrinking the upload. Because the
    injected prefix is byte-identical across rows, prompt caching still applies.
    """

    update_time: Optional[datetime] = FieldInfo(alias="updateTime", default=None)
    """The update time for the batch inference job."""

    waiting_on_capacity: Optional[bool] = FieldInfo(alias="waitingOnCapacity", default=None)
    """
    True only while a job that has ALREADY started running is briefly re-acquiring
    capacity after a mid-run preemption/stockout (i.e. it regressed from RUNNING
    back to an internal PENDING/CREATING phase and is waiting to resume). This is
    intentionally a transient sub-status annotation on a job whose customer-facing
    `state` stays RUNNING — NOT a distinct `state` value: the job is still running
    (progress is saved, it auto-resumes) so introducing a new terminal-or-not enum
    value would force every state consumer (SDK/CLI/internal maps/billing) to
    special-case "still running." It drives the customer-facing "Briefly paused —
    waiting on capacity" card. It must NOT be set during first-time provisioning
    before the job has ever run, and is cleared once the job returns to RUNNING or
    reaches a terminal state. So "state=RUNNING, waiting_on_capacity=true" means:
    running, momentarily paused while it re-acquires capacity.
    """
