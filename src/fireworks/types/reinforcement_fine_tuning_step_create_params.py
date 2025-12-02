# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from .._types import SequenceNotStr
from .._utils import PropertyInfo
from .shared_params.wandb_config import WandbConfig
from .shared_params.training_config import TrainingConfig

__all__ = ["ReinforcementFineTuningStepCreateParams"]


class ReinforcementFineTuningStepCreateParams(TypedDict, total=False):
    account_id: str

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
