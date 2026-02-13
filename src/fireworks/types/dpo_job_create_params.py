# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .shared_params.wandb_config import WandbConfig
from .shared_params.training_config import TrainingConfig
from .shared_params.reinforcement_learning_loss_config import ReinforcementLearningLossConfig

__all__ = ["DpoJobCreateParams", "AwsS3Config"]


class DpoJobCreateParams(TypedDict, total=False):
    account_id: str

    dataset: Required[str]
    """The name of the dataset used for training."""

    dpo_job_id: Annotated[str, PropertyInfo(alias="dpoJobId")]
    """ID of the DPO job, a random ID will be generated if not specified."""

    aws_s3_config: Annotated[AwsS3Config, PropertyInfo(alias="awsS3Config")]
    """The AWS configuration for S3 dataset access."""

    display_name: Annotated[str, PropertyInfo(alias="displayName")]

    loss_config: Annotated[ReinforcementLearningLossConfig, PropertyInfo(alias="lossConfig")]
    """
    Loss configuration for the training job. If not specified, defaults to DPO loss.
    Set method to ORPO for ORPO training.
    """

    training_config: Annotated[TrainingConfig, PropertyInfo(alias="trainingConfig")]
    """Common training configurations."""

    wandb_config: Annotated[WandbConfig, PropertyInfo(alias="wandbConfig")]
    """The Weights & Biases team/user account for logging job progress."""


class AwsS3Config(TypedDict, total=False):
    """The AWS configuration for S3 dataset access."""

    credentials_secret: Annotated[str, PropertyInfo(alias="credentialsSecret")]

    iam_role_arn: Annotated[str, PropertyInfo(alias="iamRoleArn")]
