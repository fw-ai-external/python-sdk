# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .shared_params.wandb_config import WandbConfig

__all__ = [
    "SupervisedFineTuningJobCreateParams",
    "AwsS3Config",
    "AzureBlobStorageConfig",
    "LrScheduler",
    "LrSchedulerCosine",
    "LrSchedulerLinear",
]


class SupervisedFineTuningJobCreateParams(TypedDict, total=False):
    account_id: str

    dataset: Required[str]
    """The name of the dataset used for training."""

    supervised_fine_tuning_job_id: Annotated[str, PropertyInfo(alias="supervisedFineTuningJobId")]
    """
    ID of the supervised fine-tuning job, a random UUID will be generated if not
    specified.
    """

    aws_s3_config: Annotated[AwsS3Config, PropertyInfo(alias="awsS3Config")]
    """The AWS configuration for S3 dataset access."""

    azure_blob_storage_config: Annotated[AzureBlobStorageConfig, PropertyInfo(alias="azureBlobStorageConfig")]
    """The Azure configuration for Azure Blob Storage dataset access."""

    base_model: Annotated[str, PropertyInfo(alias="baseModel")]
    """
    The name of the base model to be fine-tuned Only one of 'base_model' or
    'warm_start_from' should be specified.
    """

    batch_size: Annotated[int, PropertyInfo(alias="batchSize")]
    """Deprecated: legacy V1 token budget.

    Training V2 batches by samples via batch_size_samples.
    """

    batch_size_samples: Annotated[int, PropertyInfo(alias="batchSizeSamples")]
    """The number of samples per gradient batch."""

    display_name: Annotated[str, PropertyInfo(alias="displayName")]

    early_stop: Annotated[bool, PropertyInfo(alias="earlyStop")]
    """Deprecated: early stopping is not supported by managed training."""

    epochs: int
    """The number of epochs to train for."""

    eval_auto_carveout: Annotated[bool, PropertyInfo(alias="evalAutoCarveout")]
    """Whether to auto-carve the dataset for eval."""

    evaluation_dataset: Annotated[str, PropertyInfo(alias="evaluationDataset")]
    """The name of a separate dataset to use for evaluation."""

    gradient_accumulation_steps: Annotated[int, PropertyInfo(alias="gradientAccumulationSteps")]
    """Deprecated: legacy V1 gradient accumulation.

    Training V2 batches by samples via batch_size_samples and rejects this field
    when set.
    """

    is_turbo: Annotated[bool, PropertyInfo(alias="isTurbo")]
    """Whether to run the fine-tuning job in turbo mode."""

    jinja_template: Annotated[str, PropertyInfo(alias="jinjaTemplate")]
    """
    Deprecated: literal Jinja templates are not supported by Training V2.
    Conversation rendering is selected from the base model's registered renderer
    configuration instead.
    """

    learning_rate: Annotated[float, PropertyInfo(alias="learningRate")]
    """The learning rate used for training."""

    learning_rate_warmup_steps: Annotated[int, PropertyInfo(alias="learningRateWarmupSteps")]

    lora_rank: Annotated[int, PropertyInfo(alias="loraRank")]
    """The rank of the LoRA layers."""

    lr_scheduler: Annotated[LrScheduler, PropertyInfo(alias="lrScheduler")]
    """
    The learning-rate schedule (constant/linear/cosine + per-type knobs). When
    unset, the trainer uses the legacy constant schedule.
    """

    max_context_length: Annotated[int, PropertyInfo(alias="maxContextLength")]
    """The maximum context length to use with the model."""

    metrics_file_signed_url: Annotated[str, PropertyInfo(alias="metricsFileSignedUrl")]

    mtp_enabled: Annotated[bool, PropertyInfo(alias="mtpEnabled")]
    """Deprecated: MTP is no longer supported by managed training.

    This field is retained for API wire compatibility only.
    """

    mtp_freeze_base_model: Annotated[bool, PropertyInfo(alias="mtpFreezeBaseModel")]
    """Deprecated: see mtp_enabled."""

    mtp_num_draft_tokens: Annotated[int, PropertyInfo(alias="mtpNumDraftTokens")]
    """Deprecated: see mtp_enabled."""

    nodes: int
    """
    Deprecated: multi-node scheduling is now handled by the cookbook orchestrator in
    V2 workflows. This field is ignored for V2 jobs and will be removed in a future
    release.
    """

    optimizer_weight_decay: Annotated[float, PropertyInfo(alias="optimizerWeightDecay")]
    """Weight decay (L2 regularization) for optimizer."""

    output_model: Annotated[str, PropertyInfo(alias="outputModel")]
    """The model ID to be assigned to the resulting fine-tuned model.

    If not specified, the job ID will be used.
    """

    purpose: Literal["PURPOSE_UNSPECIFIED", "PURPOSE_PILOT"]
    """Scheduling purpose for this job."""

    wandb_config: Annotated[WandbConfig, PropertyInfo(alias="wandbConfig")]
    """The Weights & Biases team/user account for logging training progress."""

    warm_start_from: Annotated[str, PropertyInfo(alias="warmStartFrom")]
    """
    The PEFT addon model in Fireworks format to be fine-tuned from Only one of
    'base_model' or 'warm_start_from' should be specified.
    """


class AwsS3Config(TypedDict, total=False):
    """The AWS configuration for S3 dataset access."""

    credentials_secret: Annotated[str, PropertyInfo(alias="credentialsSecret")]

    iam_role_arn: Annotated[str, PropertyInfo(alias="iamRoleArn")]


class AzureBlobStorageConfig(TypedDict, total=False):
    """The Azure configuration for Azure Blob Storage dataset access."""

    credentials_secret: Annotated[str, PropertyInfo(alias="credentialsSecret")]
    """
    Reference to a Secret resource containing Azure credentials. Format:
    accounts/{account_id}/secrets/{secret_id} The secret value must be JSON:
    {"connection_string": "..."} or {"sas_token": "..."} or {"account_key": "..."}
    Mutually exclusive with managed_identity_client_id.
    """

    managed_identity_client_id: Annotated[str, PropertyInfo(alias="managedIdentityClientId")]
    """
    Managed Identity Client ID for GCP-to-Azure Workload Identity Federation.
    Format: uuid Mutually exclusive with credentials_secret.
    """

    tenant_id: Annotated[str, PropertyInfo(alias="tenantId")]


class LrSchedulerCosine(TypedDict, total=False):
    """Cosine annealing from the peak learning rate toward min_lr_ratio after warmup."""

    decay_ratio: Annotated[float, PropertyInfo(alias="decayRatio")]
    """Fraction of total training steps over which to decay.

    0 (unset) decays over the full run.
    """

    min_lr_ratio: Annotated[float, PropertyInfo(alias="minLrRatio")]
    """
    Floor learning rate as a fraction of the peak learning rate (0.0 = decay to
    zero, 0.1 = decay to 10% of the peak learning rate).
    """


class LrSchedulerLinear(TypedDict, total=False):
    """Linear decay from the peak learning rate toward min_lr_ratio after warmup."""

    decay_ratio: Annotated[float, PropertyInfo(alias="decayRatio")]
    """Fraction of total training steps over which to decay.

    0 (unset) decays over the full run.
    """

    min_lr_ratio: Annotated[float, PropertyInfo(alias="minLrRatio")]
    """
    Floor learning rate as a fraction of the peak learning rate (0.0 = decay to
    zero, 0.1 = decay to 10% of the peak learning rate).
    """


class LrScheduler(TypedDict, total=False):
    """
    The learning-rate schedule (constant/linear/cosine + per-type knobs).
    When unset, the trainer uses the legacy constant schedule.
    """

    constant: object
    """Constant learning rate held flat after warmup (legacy default). No decay knobs."""

    cosine: LrSchedulerCosine
    """Cosine annealing from the peak learning rate toward min_lr_ratio after warmup."""

    linear: LrSchedulerLinear
    """Linear decay from the peak learning rate toward min_lr_ratio after warmup."""
