# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["ReinforcementFineTuningJobCreateResponse", "InferenceParameters", "Status", "TrainingConfig", "WandbConfig"]


class InferenceParameters(BaseModel):
    extra_body: Optional[str] = FieldInfo(alias="extraBody", default=None)
    """
    Additional parameters for the inference request as a JSON string. For example:
    "{\"stop\": [\"\\n\"]}".
    """

    max_tokens: Optional[int] = FieldInfo(alias="maxTokens", default=None)
    """Maximum number of tokens to generate per response."""

    n: Optional[int] = None
    """Number of response candidates to generate per input."""

    temperature: Optional[float] = None
    """Sampling temperature, typically between 0 and 2."""

    top_k: Optional[int] = FieldInfo(alias="topK", default=None)
    """Top-k sampling parameter, limits the token selection to the top k tokens."""

    top_p: Optional[float] = FieldInfo(alias="topP", default=None)
    """Top-p sampling parameter, typically between 0 and 1."""


class Status(BaseModel):
    code: Optional[
        Literal[
            "OK",
            "CANCELLED",
            "UNKNOWN",
            "INVALID_ARGUMENT",
            "DEADLINE_EXCEEDED",
            "NOT_FOUND",
            "ALREADY_EXISTS",
            "PERMISSION_DENIED",
            "UNAUTHENTICATED",
            "RESOURCE_EXHAUSTED",
            "FAILED_PRECONDITION",
            "ABORTED",
            "OUT_OF_RANGE",
            "UNIMPLEMENTED",
            "INTERNAL",
            "UNAVAILABLE",
            "DATA_LOSS",
        ]
    ] = None
    """The status code."""

    message: Optional[str] = None
    """A developer-facing error message in English."""


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

    region: Optional[
        Literal[
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
        ]
    ] = None
    """The region where the fine-tuning job is located."""

    warm_start_from: Optional[str] = FieldInfo(alias="warmStartFrom", default=None)
    """
    The PEFT addon model in Fireworks format to be fine-tuned from Only one of
    'base_model' or 'warm_start_from' should be specified.
    """


class WandbConfig(BaseModel):
    api_key: Optional[str] = FieldInfo(alias="apiKey", default=None)
    """The API key for the wandb service."""

    enabled: Optional[bool] = None
    """Whether to enable wandb logging."""

    entity: Optional[str] = None
    """The entity name for the wandb service."""

    project: Optional[str] = None
    """The project name for the wandb service."""

    run_id: Optional[str] = FieldInfo(alias="runId", default=None)
    """The run ID for the wandb service."""

    url: Optional[str] = None
    """The URL for the wandb service."""


class ReinforcementFineTuningJobCreateResponse(BaseModel):
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
        ]
    ] = None
    """JobState represents the state an asynchronous job can be in."""

    status: Optional[Status] = None

    training_config: Optional[TrainingConfig] = FieldInfo(alias="trainingConfig", default=None)
    """Common training configurations."""

    wandb_config: Optional[WandbConfig] = FieldInfo(alias="wandbConfig", default=None)
    """The Weights & Biases team/user account for logging training progress."""
