# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .shared.status import Status
from .shared.wandb_config import WandbConfig
from .shared.training_config import TrainingConfig
from .shared.reinforcement_learning_loss_config import ReinforcementLearningLossConfig

__all__ = ["ReinforcementFineTuningStep", "AwsS3Config", "JobProgress"]


class AwsS3Config(BaseModel):
    """The AWS configuration for S3 dataset access."""

    credentials_secret: Optional[str] = FieldInfo(alias="credentialsSecret", default=None)

    iam_role_arn: Optional[str] = FieldInfo(alias="iamRoleArn", default=None)


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


class ReinforcementFineTuningStep(BaseModel):
    accelerator_seconds: Optional[Dict[str, str]] = FieldInfo(alias="acceleratorSeconds", default=None)
    """
    Accelerator seconds used by the job, keyed by accelerator type (e.g.,
    "NVIDIA_H100_80GB"). Updated periodically.
    """

    aws_s3_config: Optional[AwsS3Config] = FieldInfo(alias="awsS3Config", default=None)
    """The AWS configuration for S3 dataset access."""

    completed_time: Optional[datetime] = FieldInfo(alias="completedTime", default=None)

    created_by: Optional[str] = FieldInfo(alias="createdBy", default=None)
    """The email address of the user who initiated this fine-tuning job."""

    create_time: Optional[datetime] = FieldInfo(alias="createTime", default=None)

    dataset: Optional[str] = None
    """The name of the dataset used for training."""

    direct_route_handle: Optional[str] = FieldInfo(alias="directRouteHandle", default=None)

    display_name: Optional[str] = FieldInfo(alias="displayName", default=None)

    eval_auto_carveout: Optional[bool] = FieldInfo(alias="evalAutoCarveout", default=None)
    """Whether to auto-carve the dataset for eval."""

    evaluation_dataset: Optional[str] = FieldInfo(alias="evaluationDataset", default=None)
    """The name of a separate dataset to use for evaluation."""

    hot_load_deployment_id: Optional[str] = FieldInfo(alias="hotLoadDeploymentId", default=None)
    """The deployment ID used for hot loading.

    When set, checkpoints are saved to this deployment's hot load bucket, enabling
    weight swaps on inference. Only valid for service-mode or keep-alive jobs.
    """

    job_progress: Optional[JobProgress] = FieldInfo(alias="jobProgress", default=None)
    """Job progress."""

    keep_alive: Optional[bool] = FieldInfo(alias="keepAlive", default=None)

    loss_config: Optional[ReinforcementLearningLossConfig] = FieldInfo(alias="lossConfig", default=None)
    """
    Reinforcement learning loss method + hyperparameters for the underlying trainer.
    """

    name: Optional[str] = None

    node_count: Optional[int] = FieldInfo(alias="nodeCount", default=None)
    """
    The number of nodes to use for the fine-tuning job. If not specified, the
    default is 1.
    """

    reward_weights: Optional[List[str]] = FieldInfo(alias="rewardWeights", default=None)
    """
    A list of reward metrics to use for training in format of
    "<reward_name>=<weight>".
    """

    rollout_deployment_name: Optional[str] = FieldInfo(alias="rolloutDeploymentName", default=None)
    """Rollout deployment name associated with this RLOR trainer job. This is optional.

    If not set, trainer will not trigger weight sync to rollout engine.
    """

    service_mode: Optional[bool] = FieldInfo(alias="serviceMode", default=None)

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

    training_config: Optional[TrainingConfig] = FieldInfo(alias="trainingConfig", default=None)
    """Common training configurations."""

    use_purpose: Optional[str] = FieldInfo(alias="usePurpose", default=None)
    """Use dedicated resources for the job.

    The only supported value currently is "pilot". Defaults to empty.
    """

    wandb_config: Optional[WandbConfig] = FieldInfo(alias="wandbConfig", default=None)
    """The Weights & Biases team/user account for logging training progress."""
