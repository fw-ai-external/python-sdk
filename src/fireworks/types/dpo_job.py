# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .shared.status import Status
from .shared.wandb_config import WandbConfig
from .shared.training_config import TrainingConfig
from .shared.reinforcement_learning_loss_config import ReinforcementLearningLossConfig

__all__ = ["DpoJob", "AwsS3Config", "AzureBlobStorageConfig"]


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


class DpoJob(BaseModel):
    dataset: str
    """The name of the dataset used for training."""

    aws_s3_config: Optional[AwsS3Config] = FieldInfo(alias="awsS3Config", default=None)
    """The AWS configuration for S3 dataset access."""

    azure_blob_storage_config: Optional[AzureBlobStorageConfig] = FieldInfo(
        alias="azureBlobStorageConfig", default=None
    )
    """The Azure configuration for Azure Blob Storage dataset access."""

    completed_time: Optional[datetime] = FieldInfo(alias="completedTime", default=None)

    created_by: Optional[str] = FieldInfo(alias="createdBy", default=None)
    """The email address of the user who initiated this dpo job."""

    create_time: Optional[datetime] = FieldInfo(alias="createTime", default=None)

    display_name: Optional[str] = FieldInfo(alias="displayName", default=None)

    loss_config: Optional[ReinforcementLearningLossConfig] = FieldInfo(alias="lossConfig", default=None)
    """
    Loss configuration for the training job. If not specified, defaults to DPO loss.
    Set method to ORPO for ORPO training.
    """

    name: Optional[str] = None

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
    """The Weights & Biases team/user account for logging job progress."""
