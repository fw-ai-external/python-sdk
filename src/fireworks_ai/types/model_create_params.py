# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from .._types import SequenceNotStr
from .._utils import PropertyInfo

__all__ = [
    "ModelCreateParams",
    "Model",
    "ModelBaseModelDetails",
    "ModelConversationConfig",
    "ModelDeprecationDate",
    "ModelPeftDetails",
]


class ModelCreateParams(TypedDict, total=False):
    model_id: Required[Annotated[str, PropertyInfo(alias="modelId")]]
    """ID of the model."""

    cluster: str
    """The resource name of the BYOC cluster to which this model belongs. e.g.

    accounts/my-account/clusters/my-cluster. Empty if it belongs to a Fireworks
    cluster.
    """

    model: Model
    """The properties of the Model being created."""


class ModelBaseModelDetails(TypedDict, total=False):
    checkpoint_format: Annotated[
        Literal["CHECKPOINT_FORMAT_UNSPECIFIED", "NATIVE", "HUGGINGFACE"], PropertyInfo(alias="checkpointFormat")
    ]

    model_type: Annotated[str, PropertyInfo(alias="modelType")]
    """The type of the model."""

    moe: bool
    """If true, this is a Mixture of Experts (MoE) model.

    For serverless models, this affects the price per token.
    """

    parameter_count: Annotated[str, PropertyInfo(alias="parameterCount")]
    """The number of model parameters.

    For serverless models, this determines the price per token.
    """

    supports_fireattention: Annotated[bool, PropertyInfo(alias="supportsFireattention")]
    """Whether this model supports fireattention."""

    supports_mtp: Annotated[bool, PropertyInfo(alias="supportsMtp")]
    """If true, this model supports MTP."""

    tunable: bool
    """If true, this model is available for fine-tuning."""

    world_size: Annotated[int, PropertyInfo(alias="worldSize")]
    """
    The default number of GPUs the model is served with. If not specified, the
    default is 1.
    """


class ModelConversationConfig(TypedDict, total=False):
    style: Required[str]
    """The chat template to use."""

    system: str
    """The system prompt (if the chat style supports it)."""

    template: str
    """The Jinja template (if style is "jinja")."""


class ModelDeprecationDate(TypedDict, total=False):
    day: int
    """Day of a month.

    Must be from 1 to 31 and valid for the year and month, or 0 to specify a year by
    itself or a year and month where the day isn't significant.
    """

    month: int
    """Month of a year.

    Must be from 1 to 12, or 0 to specify a year without a month and day.
    """

    year: int
    """Year of the date.

    Must be from 1 to 9999, or 0 to specify a date without a year.
    """


class ModelPeftDetails(TypedDict, total=False):
    base_model: Required[Annotated[str, PropertyInfo(alias="baseModel")]]

    r: Required[int]
    """The rank of the update matrices. Must be between 4 and 64, inclusive."""

    target_modules: Required[Annotated[SequenceNotStr[str], PropertyInfo(alias="targetModules")]]

    merge_addon_model_name: Annotated[str, PropertyInfo(alias="mergeAddonModelName")]


class Model(TypedDict, total=False):
    base_model_details: Annotated[ModelBaseModelDetails, PropertyInfo(alias="baseModelDetails")]
    """Base model details. Required if kind is HF_BASE_MODEL.

    Must not be set otherwise.
    """

    context_length: Annotated[int, PropertyInfo(alias="contextLength")]
    """The maximum context length supported by the model."""

    conversation_config: Annotated[ModelConversationConfig, PropertyInfo(alias="conversationConfig")]
    """If set, the Chat Completions API will be enabled for this model."""

    default_draft_model: Annotated[str, PropertyInfo(alias="defaultDraftModel")]
    """The default draft model to use when creating a deployment.

    If empty, speculative decoding is disabled by default.
    """

    default_draft_token_count: Annotated[int, PropertyInfo(alias="defaultDraftTokenCount")]
    """
    The default draft token count to use when creating a deployment. Must be
    specified if default_draft_model is specified.
    """

    deprecation_date: Annotated[ModelDeprecationDate, PropertyInfo(alias="deprecationDate")]
    """
    If specified, this is the date when the serverless deployment of the model will
    be taken down.
    """

    description: str
    """The description of the model. Must be fewer than 1000 characters long."""

    display_name: Annotated[str, PropertyInfo(alias="displayName")]
    """Human-readable display name of the model.

    e.g. "My Model" Must be fewer than 64 characters long.
    """

    github_url: Annotated[str, PropertyInfo(alias="githubUrl")]
    """The URL to GitHub repository of the model."""

    hugging_face_url: Annotated[str, PropertyInfo(alias="huggingFaceUrl")]
    """The URL to the Hugging Face model."""

    kind: Literal[
        "KIND_UNSPECIFIED",
        "HF_BASE_MODEL",
        "HF_PEFT_ADDON",
        "HF_TEFT_ADDON",
        "FLUMINA_BASE_MODEL",
        "FLUMINA_ADDON",
        "DRAFT_ADDON",
        "FIRE_AGENT",
        "LIVE_MERGE",
        "CUSTOM_MODEL",
        "EMBEDDING_MODEL",
        "SNAPSHOT_MODEL",
    ]
    """The kind of model. If not specified, the default is HF_PEFT_ADDON."""

    peft_details: Annotated[ModelPeftDetails, PropertyInfo(alias="peftDetails")]
    """PEFT addon details. Required if kind is HF_PEFT_ADDON or HF_TEFT_ADDON."""

    public: bool
    """If true, the model will be publicly readable."""

    snapshot_type: Annotated[Literal["FULL_SNAPSHOT", "INCREMENTAL_SNAPSHOT"], PropertyInfo(alias="snapshotType")]

    supports_image_input: Annotated[bool, PropertyInfo(alias="supportsImageInput")]
    """If set, images can be provided as input to the model."""

    supports_lora: Annotated[bool, PropertyInfo(alias="supportsLora")]
    """Whether this model supports LoRA."""

    supports_tools: Annotated[bool, PropertyInfo(alias="supportsTools")]
    """If set, tools (i.e.

    functions) can be provided as input to the model, and the model may respond with
    one or more tool calls.
    """

    teft_details: Annotated[object, PropertyInfo(alias="teftDetails")]
    """TEFT addon details. Required if kind is HF_TEFT_ADDON.

    Must not be set otherwise.
    """

    training_context_length: Annotated[int, PropertyInfo(alias="trainingContextLength")]
    """The maximum context length supported by the model."""

    use_hf_apply_chat_template: Annotated[bool, PropertyInfo(alias="useHfApplyChatTemplate")]
    """
    If true, the model will use the Hugging Face apply_chat_template API to apply
    the chat template.
    """
