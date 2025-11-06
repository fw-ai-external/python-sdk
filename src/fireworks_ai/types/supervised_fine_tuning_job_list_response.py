# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = [
    "SupervisedFineTuningJobListResponse",
    "SupervisedFineTuningJob",
    "SupervisedFineTuningJobHiddenStatesGenConfig",
    "SupervisedFineTuningJobStatus",
    "SupervisedFineTuningJobWandbConfig",
]


class SupervisedFineTuningJobHiddenStatesGenConfig(BaseModel):
    api_key: Optional[str] = FieldInfo(alias="apiKey", default=None)

    deployed_model: Optional[str] = FieldInfo(alias="deployedModel", default=None)

    input_limit: Optional[int] = FieldInfo(alias="inputLimit", default=None)

    input_offset: Optional[int] = FieldInfo(alias="inputOffset", default=None)

    max_context_len: Optional[int] = FieldInfo(alias="maxContextLen", default=None)

    max_tokens: Optional[int] = FieldInfo(alias="maxTokens", default=None)

    max_workers: Optional[int] = FieldInfo(alias="maxWorkers", default=None)

    output_activations: Optional[bool] = FieldInfo(alias="outputActivations", default=None)

    regenerate_assistant: Optional[bool] = FieldInfo(alias="regenerateAssistant", default=None)


class SupervisedFineTuningJobStatus(BaseModel):
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


class SupervisedFineTuningJobWandbConfig(BaseModel):
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


class SupervisedFineTuningJob(BaseModel):
    dataset: str
    """The name of the dataset used for training."""

    base_model: Optional[str] = FieldInfo(alias="baseModel", default=None)
    """
    The name of the base model to be fine-tuned Only one of 'base_model' or
    'warm_start_from' should be specified.
    """

    batch_size: Optional[int] = FieldInfo(alias="batchSize", default=None)

    completed_time: Optional[datetime] = FieldInfo(alias="completedTime", default=None)

    created_by: Optional[str] = FieldInfo(alias="createdBy", default=None)
    """The email address of the user who initiated this fine-tuning job."""

    create_time: Optional[datetime] = FieldInfo(alias="createTime", default=None)

    display_name: Optional[str] = FieldInfo(alias="displayName", default=None)

    early_stop: Optional[bool] = FieldInfo(alias="earlyStop", default=None)
    """Whether to stop training early if the validation loss does not improve."""

    epochs: Optional[int] = None
    """The number of epochs to train for."""

    eval_auto_carveout: Optional[bool] = FieldInfo(alias="evalAutoCarveout", default=None)
    """Whether to auto-carve the dataset for eval."""

    evaluation_dataset: Optional[str] = FieldInfo(alias="evaluationDataset", default=None)
    """The name of a separate dataset to use for evaluation."""

    gradient_accumulation_steps: Optional[int] = FieldInfo(alias="gradientAccumulationSteps", default=None)

    hidden_states_gen_config: Optional[SupervisedFineTuningJobHiddenStatesGenConfig] = FieldInfo(
        alias="hiddenStatesGenConfig", default=None
    )
    """Config for generating dataset with hidden states for training."""

    is_turbo: Optional[bool] = FieldInfo(alias="isTurbo", default=None)
    """Whether to run the fine-tuning job in turbo mode."""

    jinja_template: Optional[str] = FieldInfo(alias="jinjaTemplate", default=None)

    learning_rate: Optional[float] = FieldInfo(alias="learningRate", default=None)
    """The learning rate used for training."""

    learning_rate_warmup_steps: Optional[int] = FieldInfo(alias="learningRateWarmupSteps", default=None)

    lora_rank: Optional[int] = FieldInfo(alias="loraRank", default=None)
    """The rank of the LoRA layers."""

    max_context_length: Optional[int] = FieldInfo(alias="maxContextLength", default=None)
    """The maximum context length to use with the model."""

    metrics_file_signed_url: Optional[str] = FieldInfo(alias="metricsFileSignedUrl", default=None)

    mtp_enabled: Optional[bool] = FieldInfo(alias="mtpEnabled", default=None)

    mtp_freeze_base_model: Optional[bool] = FieldInfo(alias="mtpFreezeBaseModel", default=None)

    mtp_num_draft_tokens: Optional[int] = FieldInfo(alias="mtpNumDraftTokens", default=None)

    name: Optional[str] = None

    nodes: Optional[int] = None
    """The number of nodes to use for the fine-tuning job."""

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
            "US_WASHINGTON_4",
            "US_GEORGIA_3",
        ]
    ] = None
    """The region where the fine-tuning job is located."""

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
        ]
    ] = None
    """JobState represents the state an asynchronous job can be in."""

    status: Optional[SupervisedFineTuningJobStatus] = None

    update_time: Optional[datetime] = FieldInfo(alias="updateTime", default=None)
    """The update time for the supervised fine-tuning job."""

    wandb_config: Optional[SupervisedFineTuningJobWandbConfig] = FieldInfo(alias="wandbConfig", default=None)
    """The Weights & Biases team/user account for logging training progress."""

    warm_start_from: Optional[str] = FieldInfo(alias="warmStartFrom", default=None)
    """
    The PEFT addon model in Fireworks format to be fine-tuned from Only one of
    'base_model' or 'warm_start_from' should be specified.
    """


class SupervisedFineTuningJobListResponse(BaseModel):
    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)
    """
    A token, which can be sent as `page_token` to retrieve the next page. If this
    field is omitted, there are no subsequent pages.
    """

    supervised_fine_tuning_jobs: Optional[List[SupervisedFineTuningJob]] = FieldInfo(
        alias="supervisedFineTuningJobs", default=None
    )

    total_size: Optional[int] = FieldInfo(alias="totalSize", default=None)
