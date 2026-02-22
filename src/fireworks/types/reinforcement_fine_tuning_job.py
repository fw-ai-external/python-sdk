# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .shared.status import Status
from .shared.wandb_config import WandbConfig
from .shared.training_config import TrainingConfig
from .shared.reinforcement_learning_loss_config import ReinforcementLearningLossConfig

__all__ = ["ReinforcementFineTuningJob", "AwsS3Config", "AzureBlobStorageConfig", "InferenceParameters", "JobProgress"]


class AwsS3Config(BaseModel):
    """The AWS configuration for S3 dataset access."""

    credentials_secret: Optional[str] = FieldInfo(alias="credentialsSecret", default=None)

    iam_role_arn: Optional[str] = FieldInfo(alias="iamRoleArn", default=None)


class AzureBlobStorageConfig(BaseModel):
    """The Azure configuration for Blob Storage dataset access."""

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


class InferenceParameters(BaseModel):
    """RFT inference parameters."""

    extra_body: Optional[str] = FieldInfo(alias="extraBody", default=None)
    """
    Additional parameters for the inference request as a JSON string. For example:
    "{\"stop\": [\"\\n\"]}".
    """

    max_output_tokens: Optional[int] = FieldInfo(alias="maxOutputTokens", default=None)
    """Maximum number of tokens to generate per response."""

    response_candidates_count: Optional[int] = FieldInfo(alias="responseCandidatesCount", default=None)

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


class ReinforcementFineTuningJob(BaseModel):
    dataset: str
    """The name of the dataset used for training."""

    evaluator: str
    """The evaluator resource name to use for RLOR fine-tuning job."""

    accelerator_seconds: Optional[Dict[str, str]] = FieldInfo(alias="acceleratorSeconds", default=None)
    """
    Accelerator seconds used by the job, keyed by accelerator type (e.g.,
    "NVIDIA_H100_80GB"). Updated when job completes or is cancelled.
    """

    aws_s3_config: Optional[AwsS3Config] = FieldInfo(alias="awsS3Config", default=None)
    """The AWS configuration for S3 dataset access."""

    azure_blob_storage_config: Optional[AzureBlobStorageConfig] = FieldInfo(
        alias="azureBlobStorageConfig", default=None
    )
    """The Azure configuration for Blob Storage dataset access."""

    chunk_size: Optional[int] = FieldInfo(alias="chunkSize", default=None)
    """Data chunking for rollout, default size 200, enabled when dataset > 300.

    Valid range is 1-10,000.
    """

    completed_time: Optional[datetime] = FieldInfo(alias="completedTime", default=None)
    """The completed time for the reinforcement fine-tuning job."""

    created_by: Optional[str] = FieldInfo(alias="createdBy", default=None)
    """The email address of the user who initiated this fine-tuning job."""

    create_time: Optional[datetime] = FieldInfo(alias="createTime", default=None)

    display_name: Optional[str] = FieldInfo(alias="displayName", default=None)

    eval_auto_carveout: Optional[bool] = FieldInfo(alias="evalAutoCarveout", default=None)
    """Whether to auto-carve the dataset for eval."""

    evaluation_dataset: Optional[str] = FieldInfo(alias="evaluationDataset", default=None)
    """The name of a separate dataset to use for evaluation."""

    inference_parameters: Optional[InferenceParameters] = FieldInfo(alias="inferenceParameters", default=None)
    """RFT inference parameters."""

    job_progress: Optional[JobProgress] = FieldInfo(alias="jobProgress", default=None)
    """Job progress."""

    loss_config: Optional[ReinforcementLearningLossConfig] = FieldInfo(alias="lossConfig", default=None)
    """
    Reinforcement learning loss method + hyperparameters for the underlying
    trainers.
    """

    max_concurrent_evaluations: Optional[int] = FieldInfo(alias="maxConcurrentEvaluations", default=None)
    """Maximum number of concurrent evaluations during the RFT job."""

    max_concurrent_rollouts: Optional[int] = FieldInfo(alias="maxConcurrentRollouts", default=None)
    """Maximum number of concurrent rollouts during the RFT job."""

    max_inference_replica_count: Optional[int] = FieldInfo(alias="maxInferenceReplicaCount", default=None)

    mcp_server: Optional[str] = FieldInfo(alias="mcpServer", default=None)

    name: Optional[str] = None

    node_count: Optional[int] = FieldInfo(alias="nodeCount", default=None)
    """
    The number of nodes to use for the fine-tuning job. If not specified, the
    default is 1.
    """

    output_metrics: Optional[str] = FieldInfo(alias="outputMetrics", default=None)

    output_stats: Optional[str] = FieldInfo(alias="outputStats", default=None)
    """The output dataset's aggregated stats for the evaluation job."""

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

    training_config: Optional[TrainingConfig] = FieldInfo(alias="trainingConfig", default=None)
    """Common training configurations."""

    wandb_config: Optional[WandbConfig] = FieldInfo(alias="wandbConfig", default=None)
    """The Weights & Biases team/user account for logging training progress."""
