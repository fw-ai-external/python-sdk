# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .shared_params.wandb_config import WandbConfig
from .shared_params.training_config import TrainingConfig
from .shared_params.reinforcement_learning_loss_config import ReinforcementLearningLossConfig

__all__ = ["ReinforcementFineTuningJobCreateParams", "AwsS3Config", "InferenceParameters"]


class ReinforcementFineTuningJobCreateParams(TypedDict, total=False):
    account_id: str

    dataset: Required[str]
    """The name of the dataset used for training."""

    evaluator: Required[str]
    """The evaluator resource name to use for RLOR fine-tuning job."""

    reinforcement_fine_tuning_job_id: Annotated[str, PropertyInfo(alias="reinforcementFineTuningJobId")]
    """
    ID of the reinforcement fine-tuning job, a random UUID will be generated if not
    specified.
    """

    aws_s3_config: Annotated[AwsS3Config, PropertyInfo(alias="awsS3Config")]
    """The AWS configuration for S3 dataset access."""

    chunk_size: Annotated[int, PropertyInfo(alias="chunkSize")]
    """Data chunking for rollout, default size 200, enabled when dataset > 300.

    Valid range is 1-10,000.
    """

    display_name: Annotated[str, PropertyInfo(alias="displayName")]

    eval_auto_carveout: Annotated[bool, PropertyInfo(alias="evalAutoCarveout")]
    """Whether to auto-carve the dataset for eval."""

    evaluation_dataset: Annotated[str, PropertyInfo(alias="evaluationDataset")]
    """The name of a separate dataset to use for evaluation."""

    inference_parameters: Annotated[InferenceParameters, PropertyInfo(alias="inferenceParameters")]
    """RFT inference parameters."""

    loss_config: Annotated[ReinforcementLearningLossConfig, PropertyInfo(alias="lossConfig")]
    """
    Reinforcement learning loss method + hyperparameters for the underlying
    trainers.
    """

    max_concurrent_evaluations: Annotated[int, PropertyInfo(alias="maxConcurrentEvaluations")]
    """Maximum number of concurrent evaluations during the RFT job."""

    max_concurrent_rollouts: Annotated[int, PropertyInfo(alias="maxConcurrentRollouts")]
    """Maximum number of concurrent rollouts during the RFT job."""

    mcp_server: Annotated[str, PropertyInfo(alias="mcpServer")]

    node_count: Annotated[int, PropertyInfo(alias="nodeCount")]
    """
    The number of nodes to use for the fine-tuning job. If not specified, the
    default is 1.
    """

    training_config: Annotated[TrainingConfig, PropertyInfo(alias="trainingConfig")]
    """Common training configurations."""

    wandb_config: Annotated[WandbConfig, PropertyInfo(alias="wandbConfig")]
    """The Weights & Biases team/user account for logging training progress."""


class AwsS3Config(TypedDict, total=False):
    """The AWS configuration for S3 dataset access."""

    credentials_secret: Annotated[str, PropertyInfo(alias="credentialsSecret")]

    iam_role_arn: Annotated[str, PropertyInfo(alias="iamRoleArn")]


class InferenceParameters(TypedDict, total=False):
    """RFT inference parameters."""

    extra_body: Annotated[str, PropertyInfo(alias="extraBody")]
    """
    Additional parameters for the inference request as a JSON string. For example:
    "{\"stop\": [\"\\n\"]}".
    """

    max_output_tokens: Annotated[int, PropertyInfo(alias="maxOutputTokens")]
    """Maximum number of tokens to generate per response."""

    response_candidates_count: Annotated[int, PropertyInfo(alias="responseCandidatesCount")]

    temperature: float
    """Sampling temperature, typically between 0 and 2."""

    top_k: Annotated[int, PropertyInfo(alias="topK")]
    """Top-k sampling parameter, limits the token selection to the top k tokens."""

    top_p: Annotated[float, PropertyInfo(alias="topP")]
    """Top-p sampling parameter, typically between 0 and 1."""
