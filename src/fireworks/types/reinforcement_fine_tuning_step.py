# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .shared.status import Status
from .shared.wandb_config import WandbConfig
from .shared.training_config import TrainingConfig
from .shared.reinforcement_learning_loss_config import ReinforcementLearningLossConfig

__all__ = ["ReinforcementFineTuningStep"]


class ReinforcementFineTuningStep(BaseModel):
    completed_time: Optional[datetime] = FieldInfo(alias="completedTime", default=None)

    created_by: Optional[str] = FieldInfo(alias="createdBy", default=None)
    """The email address of the user who initiated this fine-tuning job."""

    create_time: Optional[datetime] = FieldInfo(alias="createTime", default=None)

    dataset: Optional[str] = None
    """The name of the dataset used for training."""

    display_name: Optional[str] = FieldInfo(alias="displayName", default=None)

    eval_auto_carveout: Optional[bool] = FieldInfo(alias="evalAutoCarveout", default=None)
    """Whether to auto-carve the dataset for eval."""

    evaluation_dataset: Optional[str] = FieldInfo(alias="evaluationDataset", default=None)
    """The name of a separate dataset to use for evaluation."""

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

    wandb_config: Optional[WandbConfig] = FieldInfo(alias="wandbConfig", default=None)
    """The Weights & Biases team/user account for logging training progress."""
