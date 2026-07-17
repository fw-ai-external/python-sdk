# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["TrainingConfig", "TrainerShardingScheme"]


class TrainerShardingScheme(BaseModel):
    """Structured trainer sharding/parallelism configuration."""

    context_parallelism: Optional[int] = FieldInfo(alias="contextParallelism", default=None)
    """Context-parallel degree. 0 means unspecified (server defaults to 1)."""

    expert_parallelism: Optional[int] = FieldInfo(alias="expertParallelism", default=None)
    """Expert-parallel degree. 0 means unspecified (server defaults to 1)."""

    pipeline_parallelism: Optional[int] = FieldInfo(alias="pipelineParallelism", default=None)
    """Pipeline-parallel degree. 0 means unspecified (server defaults to 1)."""

    sequence_parallelism: Optional[bool] = FieldInfo(alias="sequenceParallelism", default=None)
    """Whether sequence parallelism should be enabled."""

    tensor_parallelism: Optional[int] = FieldInfo(alias="tensorParallelism", default=None)
    """Tensor-parallel degree. 0 means unspecified (server defaults to 1)."""


class TrainingConfig(BaseModel):
    base_model: Optional[str] = FieldInfo(alias="baseModel", default=None)
    """
    The name of the base model to be fine-tuned Only one of 'base_model' or
    'warm_start_from' should be specified.
    """

    batch_size: Optional[int] = FieldInfo(alias="batchSize", default=None)
    """Deprecated: legacy V1 token budget.

    Training V2 batches by samples via batch_size_samples.
    """

    batch_size_samples: Optional[int] = FieldInfo(alias="batchSizeSamples", default=None)
    """The number of samples per gradient batch."""

    epochs: Optional[int] = None
    """The number of epochs to train for."""

    gradient_accumulation_steps: Optional[int] = FieldInfo(alias="gradientAccumulationSteps", default=None)
    """Deprecated: legacy V1 gradient accumulation.

    Training V2 batches by samples via batch_size_samples and rejects this field
    when set.
    """

    jinja_template: Optional[str] = FieldInfo(alias="jinjaTemplate", default=None)
    """Deprecated: literal Jinja templates are not supported by Training V2.

    Conversation rendering is selected from the base model's registered renderer
    configuration instead.
    """

    learning_rate: Optional[float] = FieldInfo(alias="learningRate", default=None)
    """The learning rate used for training."""

    learning_rate_warmup_steps: Optional[int] = FieldInfo(alias="learningRateWarmupSteps", default=None)

    lora_alpha: Optional[int] = FieldInfo(alias="loraAlpha", default=None)
    """LoRA alpha scaling factor. If not specified (or 0), trainer defaults are used."""

    lora_dropout: Optional[float] = FieldInfo(alias="loraDropout", default=None)
    """LoRA dropout probability."""

    lora_rank: Optional[int] = FieldInfo(alias="loraRank", default=None)
    """The rank of the LoRA layers."""

    lora_target_modules: Optional[List[str]] = FieldInfo(alias="loraTargetModules", default=None)
    """Optional LoRA target module names (e.g. q_proj, k_proj, v_proj)."""

    max_context_length: Optional[int] = FieldInfo(alias="maxContextLength", default=None)
    """The maximum context length to use with the model."""

    optimizer_weight_decay: Optional[float] = FieldInfo(alias="optimizerWeightDecay", default=None)
    """Weight decay (L2 regularization) for optimizer."""

    output_model: Optional[str] = FieldInfo(alias="outputModel", default=None)
    """The model ID to be assigned to the resulting fine-tuned model.

    If not specified, the job ID will be used.
    """

    trainer_sharding_scheme: Optional[TrainerShardingScheme] = FieldInfo(alias="trainerShardingScheme", default=None)
    """Structured trainer sharding/parallelism configuration."""

    warm_start_from: Optional[str] = FieldInfo(alias="warmStartFrom", default=None)
    """
    The PEFT addon model in Fireworks format to be fine-tuned from Only one of
    'base_model' or 'warm_start_from' should be specified.
    """
