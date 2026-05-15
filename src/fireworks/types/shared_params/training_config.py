# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ..._types import SequenceNotStr
from ..._utils import PropertyInfo

__all__ = ["TrainingConfig", "TrainerShardingScheme"]


class TrainerShardingScheme(TypedDict, total=False):
    """Structured trainer sharding/parallelism configuration."""

    context_parallelism: Annotated[int, PropertyInfo(alias="contextParallelism")]
    """Context-parallel degree. 0 means unspecified (server defaults to 1)."""

    expert_parallelism: Annotated[int, PropertyInfo(alias="expertParallelism")]
    """Expert-parallel degree. 0 means unspecified (server defaults to 1)."""

    pipeline_parallelism: Annotated[int, PropertyInfo(alias="pipelineParallelism")]
    """Pipeline-parallel degree. 0 means unspecified (server defaults to 1)."""

    sequence_parallelism: Annotated[bool, PropertyInfo(alias="sequenceParallelism")]
    """Whether sequence parallelism should be enabled."""

    tensor_parallelism: Annotated[int, PropertyInfo(alias="tensorParallelism")]
    """Tensor-parallel degree. 0 means unspecified (server defaults to 1)."""


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

    lora_alpha: Annotated[int, PropertyInfo(alias="loraAlpha")]
    """LoRA alpha scaling factor. If not specified (or 0), trainer defaults are used."""

    lora_dropout: Annotated[float, PropertyInfo(alias="loraDropout")]
    """LoRA dropout probability."""

    lora_rank: Annotated[int, PropertyInfo(alias="loraRank")]
    """The rank of the LoRA layers."""

    lora_target_modules: Annotated[SequenceNotStr[str], PropertyInfo(alias="loraTargetModules")]
    """Optional LoRA target module names (e.g. q_proj, k_proj, v_proj)."""

    max_context_length: Annotated[int, PropertyInfo(alias="maxContextLength")]
    """The maximum context length to use with the model."""

    optimizer_weight_decay: Annotated[float, PropertyInfo(alias="optimizerWeightDecay")]
    """Weight decay (L2 regularization) for optimizer."""

    output_model: Annotated[str, PropertyInfo(alias="outputModel")]
    """The model ID to be assigned to the resulting fine-tuned model.

    If not specified, the job ID will be used.
    """

    trainer_sharding_scheme: Annotated[TrainerShardingScheme, PropertyInfo(alias="trainerShardingScheme")]
    """Structured trainer sharding/parallelism configuration."""

    warm_start_from: Annotated[str, PropertyInfo(alias="warmStartFrom")]
    """
    The PEFT addon model in Fireworks format to be fine-tuned from Only one of
    'base_model' or 'warm_start_from' should be specified.
    """
