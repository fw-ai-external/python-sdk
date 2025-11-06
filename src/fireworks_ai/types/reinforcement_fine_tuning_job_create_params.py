# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["ReinforcementFineTuningJobCreateParams", "InferenceParameters", "TrainingConfig", "WandbConfig"]


class ReinforcementFineTuningJobCreateParams(TypedDict, total=False):
    dataset: Required[str]
    """The name of the dataset used for training."""

    evaluator: Required[str]
    """The evaluator resource name to use for RLOR fine-tuning job."""

    reinforcement_fine_tuning_job_id: Annotated[str, PropertyInfo(alias="reinforcementFineTuningJobId")]
    """
    ID of the reinforcement fine-tuning job, a random UUID will be generated if not
    specified.
    """

    display_name: Annotated[str, PropertyInfo(alias="displayName")]

    eval_auto_carveout: Annotated[bool, PropertyInfo(alias="evalAutoCarveout")]
    """Whether to auto-carve the dataset for eval."""

    evaluation_dataset: Annotated[str, PropertyInfo(alias="evaluationDataset")]
    """The name of a separate dataset to use for evaluation."""

    inference_parameters: Annotated[InferenceParameters, PropertyInfo(alias="inferenceParameters")]
    """BIJ parameters."""

    mcp_server: Annotated[str, PropertyInfo(alias="mcpServer")]

    training_config: Annotated[TrainingConfig, PropertyInfo(alias="trainingConfig")]
    """Common training configurations."""

    wandb_config: Annotated[WandbConfig, PropertyInfo(alias="wandbConfig")]
    """The Weights & Biases team/user account for logging training progress."""


class InferenceParameters(TypedDict, total=False):
    extra_body: Annotated[str, PropertyInfo(alias="extraBody")]
    """
    Additional parameters for the inference request as a JSON string. For example:
    "{\"stop\": [\"\\n\"]}".
    """

    max_tokens: Annotated[int, PropertyInfo(alias="maxTokens")]
    """Maximum number of tokens to generate per response."""

    n: int
    """Number of response candidates to generate per input."""

    temperature: float
    """Sampling temperature, typically between 0 and 2."""

    top_k: Annotated[int, PropertyInfo(alias="topK")]
    """Top-k sampling parameter, limits the token selection to the top k tokens."""

    top_p: Annotated[float, PropertyInfo(alias="topP")]
    """Top-p sampling parameter, typically between 0 and 1."""


class TrainingConfig(TypedDict, total=False):
    accelerator_count: Annotated[int, PropertyInfo(alias="acceleratorCount")]
    """
    The number of accelerators used for the fine-tuning job. If not specified, the
    default is the estimated minimum required by the base model.
    """

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


class WandbConfig(TypedDict, total=False):
    api_key: Annotated[str, PropertyInfo(alias="apiKey")]
    """The API key for the wandb service."""

    enabled: bool
    """Whether to enable wandb logging."""

    entity: str
    """The entity name for the wandb service."""

    project: str
    """The project name for the wandb service."""

    run_id: Annotated[str, PropertyInfo(alias="runId")]
    """The run ID for the wandb service."""
