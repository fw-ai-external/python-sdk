# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .shared_params.wandb_config import WandbConfig

__all__ = ["SupervisedFineTuningJobCreateParams", "AwsS3Config", "AzureBlobStorageConfig"]


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

    batch_size_samples: Annotated[int, PropertyInfo(alias="batchSizeSamples")]
    """The number of samples per gradient batch."""

    display_name: Annotated[str, PropertyInfo(alias="displayName")]

    early_stop: Annotated[bool, PropertyInfo(alias="earlyStop")]
    """Whether to stop training early if the validation loss does not improve."""

    epochs: int
    """The number of epochs to train for."""

    eval_auto_carveout: Annotated[bool, PropertyInfo(alias="evalAutoCarveout")]
    """Whether to auto-carve the dataset for eval."""

    evaluation_dataset: Annotated[str, PropertyInfo(alias="evaluationDataset")]
    """The name of a separate dataset to use for evaluation."""

    gradient_accumulation_steps: Annotated[int, PropertyInfo(alias="gradientAccumulationSteps")]

    is_turbo: Annotated[bool, PropertyInfo(alias="isTurbo")]
    """Whether to run the fine-tuning job in turbo mode."""

    jinja_template: Annotated[str, PropertyInfo(alias="jinjaTemplate")]

    learning_rate: Annotated[float, PropertyInfo(alias="learningRate")]
    """The learning rate used for training."""

    learning_rate_warmup_steps: Annotated[int, PropertyInfo(alias="learningRateWarmupSteps")]

    lora_rank: Annotated[int, PropertyInfo(alias="loraRank")]
    """The rank of the LoRA layers."""

    max_context_length: Annotated[int, PropertyInfo(alias="maxContextLength")]
    """The maximum context length to use with the model."""

    metrics_file_signed_url: Annotated[str, PropertyInfo(alias="metricsFileSignedUrl")]

    mtp_enabled: Annotated[bool, PropertyInfo(alias="mtpEnabled")]

    mtp_freeze_base_model: Annotated[bool, PropertyInfo(alias="mtpFreezeBaseModel")]

    mtp_num_draft_tokens: Annotated[int, PropertyInfo(alias="mtpNumDraftTokens")]

    nodes: int
    """The number of nodes to use for the fine-tuning job."""

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
        "US_NEWYORK_1",
    ]
    """The region where the fine-tuning job is located."""

    use_purpose: Annotated[str, PropertyInfo(alias="usePurpose")]
    """Use dedicated resources for the job.

    The only supported value currently is "pilot". Defaults to empty.
    """

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
