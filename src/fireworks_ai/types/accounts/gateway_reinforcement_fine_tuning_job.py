# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .gateway_region import GatewayRegion
from .gateway_status import GatewayStatus
from .gateway_job_state import GatewayJobState
from .gateway_wandb_config import GatewayWandbConfig
from .gateway_inference_parameters import GatewayInferenceParameters

__all__ = ["GatewayReinforcementFineTuningJob", "TrainingConfig"]


class TrainingConfig(BaseModel):
    accelerator_count: Optional[int] = FieldInfo(alias="acceleratorCount", default=None)
    """
    The number of accelerators used for the fine-tuning job. If not specified, the
    default is the estimated minimum required by the base model.
    """

    base_model: Optional[str] = FieldInfo(alias="baseModel", default=None)
    """
    The name of the base model to be fine-tuned Only one of 'base_model' or
    'warm_start_from' should be specified.
    """

    batch_size: Optional[int] = FieldInfo(alias="batchSize", default=None)
    """The maximum packed number of tokens per batch for training in sequence packing."""

    epochs: Optional[int] = None
    """The number of epochs to train for."""

    gradient_accumulation_steps: Optional[int] = FieldInfo(alias="gradientAccumulationSteps", default=None)

    jinja_template: Optional[str] = FieldInfo(alias="jinjaTemplate", default=None)

    learning_rate: Optional[float] = FieldInfo(alias="learningRate", default=None)
    """The learning rate used for training."""

    learning_rate_warmup_steps: Optional[int] = FieldInfo(alias="learningRateWarmupSteps", default=None)

    lora_rank: Optional[int] = FieldInfo(alias="loraRank", default=None)
    """The rank of the LoRA layers."""

    max_context_length: Optional[int] = FieldInfo(alias="maxContextLength", default=None)
    """The maximum context length to use with the model."""

    output_model: Optional[str] = FieldInfo(alias="outputModel", default=None)
    """The model ID to be assigned to the resulting fine-tuned model.

    If not specified, the job ID will be used.
    """

    region: Optional[GatewayRegion] = None
    """The region where the fine-tuning job is located."""

    warm_start_from: Optional[str] = FieldInfo(alias="warmStartFrom", default=None)
    """
    The PEFT addon model in Fireworks format to be fine-tuned from Only one of
    'base_model' or 'warm_start_from' should be specified.
    """


class GatewayReinforcementFineTuningJob(BaseModel):
    dataset: str
    """The name of the dataset used for training."""

    evaluator: str
    """The evaluator resource name to use for RLOR fine-tuning job."""

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

    inference_parameters: Optional[GatewayInferenceParameters] = FieldInfo(alias="inferenceParameters", default=None)
    """BIJ parameters."""

    mcp_server: Optional[str] = FieldInfo(alias="mcpServer", default=None)

    name: Optional[str] = None

    output_metrics: Optional[str] = FieldInfo(alias="outputMetrics", default=None)

    output_stats: Optional[str] = FieldInfo(alias="outputStats", default=None)
    """The output dataset's aggregated stats for the evaluation job."""

    state: Optional[GatewayJobState] = None
    """JobState represents the state an asynchronous job can be in."""

    status: Optional[GatewayStatus] = None

    training_config: Optional[TrainingConfig] = FieldInfo(alias="trainingConfig", default=None)
    """Common training configurations."""

    wandb_config: Optional[GatewayWandbConfig] = FieldInfo(alias="wandbConfig", default=None)
    """The Weights & Biases team/user account for logging training progress."""
