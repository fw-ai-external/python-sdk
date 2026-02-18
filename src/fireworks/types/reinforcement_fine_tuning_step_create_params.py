# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from .._types import SequenceNotStr
from .._utils import PropertyInfo
from .shared_params.wandb_config import WandbConfig
from .shared_params.training_config import TrainingConfig
from .shared_params.reinforcement_learning_loss_config import ReinforcementLearningLossConfig

__all__ = ["ReinforcementFineTuningStepCreateParams", "AwsS3Config", "AzureBlobStorageConfig"]


class ReinforcementFineTuningStepCreateParams(TypedDict, total=False):
    account_id: str

    rlor_trainer_job_id: Annotated[str, PropertyInfo(alias="rlorTrainerJobId")]
    """ID of the RLOR trainer job, a random UUID will be generated if not specified."""

    aws_s3_config: Annotated[AwsS3Config, PropertyInfo(alias="awsS3Config")]
    """The AWS configuration for S3 dataset access."""

    azure_blob_storage_config: Annotated[AzureBlobStorageConfig, PropertyInfo(alias="azureBlobStorageConfig")]
    """The Azure configuration for Azure Blob Storage dataset access."""

    dataset: str
    """The name of the dataset used for training."""

    display_name: Annotated[str, PropertyInfo(alias="displayName")]

    eval_auto_carveout: Annotated[bool, PropertyInfo(alias="evalAutoCarveout")]
    """Whether to auto-carve the dataset for eval."""

    evaluation_dataset: Annotated[str, PropertyInfo(alias="evaluationDataset")]
    """The name of a separate dataset to use for evaluation."""

    forward_only: Annotated[bool, PropertyInfo(alias="forwardOnly")]
    """
    When true, run the trainer in forward-only mode (no backward/optimizer). Used
    for reference models in GRPO that only need forward passes.
    """

    hot_load_deployment_id: Annotated[str, PropertyInfo(alias="hotLoadDeploymentId")]
    """The deployment ID used for hot loading.

    When set, checkpoints are saved to this deployment's hot load bucket, enabling
    weight swaps on inference. Only valid for service-mode or keep-alive jobs.
    """

    keep_alive: Annotated[bool, PropertyInfo(alias="keepAlive")]

    loss_config: Annotated[ReinforcementLearningLossConfig, PropertyInfo(alias="lossConfig")]
    """
    Reinforcement learning loss method + hyperparameters for the underlying trainer.
    """

    node_count: Annotated[int, PropertyInfo(alias="nodeCount")]
    """
    The number of nodes to use for the fine-tuning job. If not specified, the
    default is 1.
    """

    reward_weights: Annotated[SequenceNotStr[str], PropertyInfo(alias="rewardWeights")]
    """
    A list of reward metrics to use for training in format of
    "<reward_name>=<weight>".
    """

    rollout_deployment_name: Annotated[str, PropertyInfo(alias="rolloutDeploymentName")]
    """Rollout deployment name associated with this RLOR trainer job. This is optional.

    If not set, trainer will not trigger weight sync to rollout engine.
    """

    service_mode: Annotated[bool, PropertyInfo(alias="serviceMode")]
    """Service-mode RLOR trainers currently support full-parameter tuning only.

    When enabled, `trainingConfig.loraRank` must be 0 (`loraRank>0` is rejected).
    """

    training_config: Annotated[TrainingConfig, PropertyInfo(alias="trainingConfig")]
    """Common training configurations."""

    use_purpose: Annotated[str, PropertyInfo(alias="usePurpose")]
    """Use dedicated resources for the job.

    The only supported value currently is "pilot". Defaults to empty.
    """

    wandb_config: Annotated[WandbConfig, PropertyInfo(alias="wandbConfig")]
    """The Weights & Biases team/user account for logging training progress."""


class AwsS3Config(TypedDict, total=False):
    """The AWS configuration for S3 dataset access."""

    credentials_secret: Annotated[str, PropertyInfo(alias="credentialsSecret")]

    iam_role_arn: Annotated[str, PropertyInfo(alias="iamRoleArn")]


class AzureBlobStorageConfig(TypedDict, total=False):
    """The Azure configuration for Azure Blob Storage dataset access."""

    credentials_secret: Annotated[str, PropertyInfo(alias="credentialsSecret")]
    """
    Reference to a Secret resource containing Azure credentials. Format:
    accounts/{account_id}/secrets/{secret_id} The secret value must be JSON:
    {"connection_string": "..."} or {"sas_token": "..."} or {"account_key": "..."}
    Mutually exclusive with managed_identity_client_id.
    """

    managed_identity_client_id: Annotated[str, PropertyInfo(alias="managedIdentityClientId")]
    """
    Managed Identity Client ID for GCP-to-Azure Workload Identity Federation.
    Format: uuid Mutually exclusive with credentials_secret.
    """

    tenant_id: Annotated[str, PropertyInfo(alias="tenantId")]
