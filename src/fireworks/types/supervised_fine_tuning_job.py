# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .shared.status import Status
from .shared.wandb_config import WandbConfig

__all__ = ["SupervisedFineTuningJob", "AwsS3Config", "AzureBlobStorageConfig", "EstimatedCost", "JobProgress"]


class AwsS3Config(BaseModel):
    """The AWS configuration for S3 dataset access."""

    credentials_secret: Optional[str] = FieldInfo(alias="credentialsSecret", default=None)

    iam_role_arn: Optional[str] = FieldInfo(alias="iamRoleArn", default=None)


class AzureBlobStorageConfig(BaseModel):
    """The Azure configuration for Azure Blob Storage dataset access."""

    credentials_secret: Optional[str] = FieldInfo(alias="credentialsSecret", default=None)
    """
    Reference to a Secret resource containing Azure credentials. Format:
    accounts/{account_id}/secrets/{secret_id} The secret value must be JSON:
    {"connection_string": "..."} or {"sas_token": "..."} or {"account_key": "..."}
    Mutually exclusive with managed_identity_client_id.
    """

    managed_identity_client_id: Optional[str] = FieldInfo(alias="managedIdentityClientId", default=None)
    """
    Managed Identity Client ID for GCP-to-Azure Workload Identity Federation.
    Format: uuid Mutually exclusive with credentials_secret.
    """

    tenant_id: Optional[str] = FieldInfo(alias="tenantId", default=None)


class EstimatedCost(BaseModel):
    """The estimated cost of the job."""

    currency_code: Optional[str] = FieldInfo(alias="currencyCode", default=None)
    """The three-letter currency code defined in ISO 4217."""

    nanos: Optional[int] = None
    """
    Number of nano (10^-9) units of the amount. The value must be between
    -999,999,999 and +999,999,999 inclusive. If `units` is positive, `nanos` must be
    positive or zero. If `units` is zero, `nanos` can be positive, zero, or
    negative. If `units` is negative, `nanos` must be negative or zero. For example
    $-1.75 is represented as `units`=-1 and `nanos`=-750,000,000.
    """

    units: Optional[str] = None
    """
    The whole units of the amount. For example if `currencyCode` is `"USD"`, then 1
    unit is one US dollar.
    """


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


class SupervisedFineTuningJob(BaseModel):
    dataset: str
    """The name of the dataset used for training."""

    aws_s3_config: Optional[AwsS3Config] = FieldInfo(alias="awsS3Config", default=None)
    """The AWS configuration for S3 dataset access."""

    azure_blob_storage_config: Optional[AzureBlobStorageConfig] = FieldInfo(
        alias="azureBlobStorageConfig", default=None
    )
    """The Azure configuration for Azure Blob Storage dataset access."""

    base_model: Optional[str] = FieldInfo(alias="baseModel", default=None)
    """
    The name of the base model to be fine-tuned Only one of 'base_model' or
    'warm_start_from' should be specified.
    """

    batch_size: Optional[int] = FieldInfo(alias="batchSize", default=None)

    batch_size_samples: Optional[int] = FieldInfo(alias="batchSizeSamples", default=None)
    """The number of samples per gradient batch."""

    completed_time: Optional[datetime] = FieldInfo(alias="completedTime", default=None)

    created_by: Optional[str] = FieldInfo(alias="createdBy", default=None)
    """The email address of the user who initiated this fine-tuning job."""

    create_time: Optional[datetime] = FieldInfo(alias="createTime", default=None)

    display_name: Optional[str] = FieldInfo(alias="displayName", default=None)

    early_stop: Optional[bool] = FieldInfo(alias="earlyStop", default=None)
    """Whether to stop training early if the validation loss does not improve."""

    epochs: Optional[int] = None
    """The number of epochs to train for."""

    estimated_cost: Optional[EstimatedCost] = FieldInfo(alias="estimatedCost", default=None)
    """The estimated cost of the job."""

    eval_auto_carveout: Optional[bool] = FieldInfo(alias="evalAutoCarveout", default=None)
    """Whether to auto-carve the dataset for eval."""

    evaluation_dataset: Optional[str] = FieldInfo(alias="evaluationDataset", default=None)
    """The name of a separate dataset to use for evaluation."""

    gradient_accumulation_steps: Optional[int] = FieldInfo(alias="gradientAccumulationSteps", default=None)

    is_turbo: Optional[bool] = FieldInfo(alias="isTurbo", default=None)
    """Whether to run the fine-tuning job in turbo mode."""

    jinja_template: Optional[str] = FieldInfo(alias="jinjaTemplate", default=None)

    job_progress: Optional[JobProgress] = FieldInfo(alias="jobProgress", default=None)
    """Job progress."""

    learning_rate: Optional[float] = FieldInfo(alias="learningRate", default=None)
    """The learning rate used for training."""

    learning_rate_warmup_steps: Optional[int] = FieldInfo(alias="learningRateWarmupSteps", default=None)

    lora_rank: Optional[int] = FieldInfo(alias="loraRank", default=None)
    """The rank of the LoRA layers."""

    max_context_length: Optional[int] = FieldInfo(alias="maxContextLength", default=None)
    """The maximum context length to use with the model."""

    metrics_file_signed_url: Optional[str] = FieldInfo(alias="metricsFileSignedUrl", default=None)

    mtp_enabled: Optional[bool] = FieldInfo(alias="mtpEnabled", default=None)

    mtp_freeze_base_model: Optional[bool] = FieldInfo(alias="mtpFreezeBaseModel", default=None)

    mtp_num_draft_tokens: Optional[int] = FieldInfo(alias="mtpNumDraftTokens", default=None)

    name: Optional[str] = None

    nodes: Optional[int] = None
    """The number of nodes to use for the fine-tuning job."""

    optimizer_weight_decay: Optional[float] = FieldInfo(alias="optimizerWeightDecay", default=None)
    """Weight decay (L2 regularization) for optimizer."""

    output_model: Optional[str] = FieldInfo(alias="outputModel", default=None)
    """The model ID to be assigned to the resulting fine-tuned model.

    If not specified, the job ID will be used.
    """

    region: Optional[
        Literal[
            "REGION_UNSPECIFIED",
            "US_IOWA_1",
            "US_VIRGINIA_1",
            "US_VIRGINIA_2",
            "US_ILLINOIS_1",
            "AP_TOKYO_1",
            "EU_LONDON_1",
            "US_ARIZONA_1",
            "US_TEXAS_1",
            "US_ILLINOIS_2",
            "EU_FRANKFURT_1",
            "US_TEXAS_2",
            "EU_PARIS_1",
            "EU_HELSINKI_1",
            "US_NEVADA_1",
            "EU_ICELAND_1",
            "EU_ICELAND_2",
            "US_WASHINGTON_1",
            "US_WASHINGTON_2",
            "EU_ICELAND_DEV_1",
            "US_WASHINGTON_3",
            "US_ARIZONA_2",
            "AP_TOKYO_2",
            "US_CALIFORNIA_1",
            "US_MISSOURI_1",
            "US_UTAH_1",
            "US_TEXAS_3",
            "US_ARIZONA_3",
            "US_GEORGIA_1",
            "US_GEORGIA_2",
            "US_WASHINGTON_4",
            "US_GEORGIA_3",
            "NA_BRITISHCOLUMBIA_1",
            "US_GEORGIA_4",
            "EU_ICELAND_3",
            "US_OHIO_1",
            "US_NEWYORK_1",
        ]
    ] = None
    """The region where the fine-tuning job is located."""

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
        ]
    ] = None
    """JobState represents the state an asynchronous job can be in.

    - JOB_STATE_PAUSED: Job is paused, typically due to account suspension or manual
      intervention.
    """

    status: Optional[Status] = None

    trainer_logs_signed_url: Optional[str] = FieldInfo(alias="trainerLogsSignedUrl", default=None)
    """
    The signed URL for the trainer logs file (stdout/stderr). Only populated if the
    account has trainer log reading enabled.
    """

    update_time: Optional[datetime] = FieldInfo(alias="updateTime", default=None)
    """The update time for the supervised fine-tuning job."""

    use_purpose: Optional[str] = FieldInfo(alias="usePurpose", default=None)
    """Use dedicated resources for the job.

    The only supported value currently is "pilot". Defaults to empty.
    """

    wandb_config: Optional[WandbConfig] = FieldInfo(alias="wandbConfig", default=None)
    """The Weights & Biases team/user account for logging training progress."""

    warm_start_from: Optional[str] = FieldInfo(alias="warmStartFrom", default=None)
    """
    The PEFT addon model in Fireworks format to be fine-tuned from Only one of
    'base_model' or 'warm_start_from' should be specified.
    """
