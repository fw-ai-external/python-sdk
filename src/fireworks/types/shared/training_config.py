# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["TrainingConfig"]


class TrainingConfig(BaseModel):
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
            "US_WASHINGTON_4",
            "US_GEORGIA_3",
        ]
    ] = None
    """The region where the fine-tuning job is located."""

    warm_start_from: Optional[str] = FieldInfo(alias="warmStartFrom", default=None)
    """
    The PEFT addon model in Fireworks format to be fine-tuned from Only one of
    'base_model' or 'warm_start_from' should be specified.
    """
