# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["TrainingConfig"]


class TrainingConfig(TypedDict, total=False):
    base_model: Annotated[str, PropertyInfo(alias="baseModel")]
    """
    The name of the base model to be fine-tuned Only one of 'base_model' or
    'warm_start_from' should be specified.
    """

    batch_size: Annotated[int, PropertyInfo(alias="batchSize")]
    """The maximum packed number of tokens per batch for training in sequence packing."""

    batch_size_samples: Annotated[int, PropertyInfo(alias="batchSizeSamples")]
    """The number of samples per gradient batch."""

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

    optimizer_weight_decay: Annotated[float, PropertyInfo(alias="optimizerWeightDecay")]
    """Weight decay (L2 regularization) for optimizer."""

    output_model: Annotated[str, PropertyInfo(alias="outputModel")]
    """The model ID to be assigned to the resulting fine-tuned model.

    If not specified, the job ID will be used.
    """

    region: Literal[
        "REGION_UNSPECIFIED",
        "US_IOWA_1",
        "US_VIRGINIA_1",
        "US_VIRGINIA_2",
        "US_ILLINOIS_1",
        "AP_TOKYO_1",
        "EU_LONDON_1",
        "US_ARIZONA_1",
        "US_TEXAS_1",
        "US_ILLINOIS_2",
        "EU_FRANKFURT_1",
        "US_TEXAS_2",
        "EU_PARIS_1",
        "EU_HELSINKI_1",
        "US_NEVADA_1",
        "EU_ICELAND_1",
        "EU_ICELAND_2",
        "US_WASHINGTON_1",
        "US_WASHINGTON_2",
        "EU_ICELAND_DEV_1",
        "US_WASHINGTON_3",
        "US_ARIZONA_2",
        "AP_TOKYO_2",
        "US_CALIFORNIA_1",
        "US_MISSOURI_1",
        "US_UTAH_1",
        "US_TEXAS_3",
        "US_ARIZONA_3",
        "US_GEORGIA_1",
        "US_GEORGIA_2",
        "US_WASHINGTON_4",
        "US_GEORGIA_3",
        "NA_BRITISHCOLUMBIA_1",
        "US_GEORGIA_4",
        "EU_ICELAND_3",
        "US_OHIO_1",
    ]
    """The region where the fine-tuning job is located."""

    warm_start_from: Annotated[str, PropertyInfo(alias="warmStartFrom")]
    """
    The PEFT addon model in Fireworks format to be fine-tuned from Only one of
    'base_model' or 'warm_start_from' should be specified.
    """
