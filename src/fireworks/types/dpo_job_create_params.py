# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .shared_params.wandb_config import WandbConfig
from .shared_params.training_config import TrainingConfig

__all__ = ["DpoJobCreateParams"]


class DpoJobCreateParams(TypedDict, total=False):
    account_id: str

    dataset: Required[str]
    """The name of the dataset used for training."""

    dpo_job_id: Annotated[str, PropertyInfo(alias="dpoJobId")]
    """ID of the DPO job, a random ID will be generated if not specified."""

    display_name: Annotated[str, PropertyInfo(alias="displayName")]

    training_config: Annotated[TrainingConfig, PropertyInfo(alias="trainingConfig")]
    """Common training configurations."""

    wandb_config: Annotated[WandbConfig, PropertyInfo(alias="wandbConfig")]
    """The Weights & Biases team/user account for logging job progress."""
