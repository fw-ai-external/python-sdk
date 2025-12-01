# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .shared.status import Status
from .shared.wandb_config import WandbConfig
from .shared.training_config import TrainingConfig
from .shared.inference_parameters import InferenceParameters

__all__ = ["ReinforcementFineTuningJob"]


class ReinforcementFineTuningJob(BaseModel):
    dataset: str
    """The name of the dataset used for training."""

    evaluator: str
    """The evaluator resource name to use for RLOR fine-tuning job."""

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
    """BIJ parameters."""

    mcp_server: Optional[str] = FieldInfo(alias="mcpServer", default=None)

    name: Optional[str] = None

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

    training_config: Optional[TrainingConfig] = FieldInfo(alias="trainingConfig", default=None)
    """Common training configurations."""

    wandb_config: Optional[WandbConfig] = FieldInfo(alias="wandbConfig", default=None)
    """The Weights & Biases team/user account for logging training progress."""
