# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from .._types import SequenceNotStr
from .._utils import PropertyInfo
from .shared_params.wandb_config import WandbConfig

__all__ = ["ReinforcementFineTuningStepCreateParams", "TrainingConfig"]


class ReinforcementFineTuningStepCreateParams(TypedDict, total=False):
    rlor_trainer_job_id: Annotated[str, PropertyInfo(alias="rlorTrainerJobId")]
    """ID of the RLOR trainer job, a random UUID will be generated if not specified."""

    dataset: str
    """The name of the dataset used for training."""

    display_name: Annotated[str, PropertyInfo(alias="displayName")]

    eval_auto_carveout: Annotated[bool, PropertyInfo(alias="evalAutoCarveout")]
    """Whether to auto-carve the dataset for eval."""

    evaluation_dataset: Annotated[str, PropertyInfo(alias="evaluationDataset")]
    """The name of a separate dataset to use for evaluation."""

    reward_weights: Annotated[SequenceNotStr[str], PropertyInfo(alias="rewardWeights")]
    """
    A list of reward metrics to use for training in format of
    "<reward_name>=<weight>".
    """

    training_config: Annotated[TrainingConfig, PropertyInfo(alias="trainingConfig")]
    """Common training configurations."""

    wandb_config: Annotated[WandbConfig, PropertyInfo(alias="wandbConfig")]
    """The Weights & Biases team/user account for logging training progress."""


class TrainingConfig(TypedDict, total=False):
    base_model: Annotated[str, PropertyInfo(alias="baseModel")]
    """
    The name of the base model to be fine-tuned Only one of 'base_model' or
    'warm_start_from' should be specified.
    """

    batch_size: Annotated[int, PropertyInfo(alias="batchSize")]
    """The maximum packed number of tokens per batch for training in sequence packing."""

    epochs: int
    """The number of epochs to train for."""

    gradient_accumulation_steps: Annotated[int, PropertyInfo(alias="gradientAccumulationSteps")]

    jinja_template: Annotated[str, PropertyInfo(alias="jinjaTemplate")]

    learning_rate: Annotated[float, PropertyInfo(alias="learningRate")]
    """The learning rate used for training."""

    learning_rate_warmup_steps: Annotated[int, PropertyInfo(alias="learningRateWarmupSteps")]

    lora_rank: Annotated[int, PropertyInfo(alias="loraRank")]
    """The rank of the LoRA layers."""

    max_context_length: Annotated[int, PropertyInfo(alias="maxContextLength")]
    """The maximum context length to use with the model."""

    output_model: Annotated[str, PropertyInfo(alias="outputModel")]
    """The model ID to be assigned to the resulting fine-tuned model.

    If not specified, the job ID will be used.
    """

    region: Literal[
        "REGION_UNSPECIFIED",
        "US_IOWA_1",
        "US_VIRGINIA_1",
        "US_ILLINOIS_1",
        "AP_TOKYO_1",
        "US_ARIZONA_1",
        "US_TEXAS_1",
        "US_ILLINOIS_2",
        "EU_FRANKFURT_1",
        "US_TEXAS_2",
        "EU_ICELAND_1",
        "EU_ICELAND_2",
        "US_WASHINGTON_1",
        "US_WASHINGTON_2",
        "US_WASHINGTON_3",
        "AP_TOKYO_2",
        "US_CALIFORNIA_1",
        "US_UTAH_1",
        "US_TEXAS_3",
        "US_GEORGIA_1",
        "US_GEORGIA_2",
        "US_WASHINGTON_4",
        "US_GEORGIA_3",
    ]
    """The region where the fine-tuning job is located."""

    warm_start_from: Annotated[str, PropertyInfo(alias="warmStartFrom")]
    """
    The PEFT addon model in Fireworks format to be fine-tuned from Only one of
    'base_model' or 'warm_start_from' should be specified.
    """
