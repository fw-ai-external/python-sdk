# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from .._utils import PropertyInfo
from .model_kind import ModelKind
from .type_date_param import TypeDateParam
from .peft_details_param import PeftDetailsParam
from .base_model_details_param import BaseModelDetailsParam
from .conversation_config_param import ConversationConfigParam

__all__ = ["ModelParam"]


class ModelParam(TypedDict, total=False):
    base_model_details: Annotated[BaseModelDetailsParam, PropertyInfo(alias="baseModelDetails")]
    """Base model details. Required if kind is HF_BASE_MODEL.

    Must not be set otherwise.
    """

    context_length: Annotated[int, PropertyInfo(alias="contextLength")]
    """The maximum context length supported by the model."""

    conversation_config: Annotated[ConversationConfigParam, PropertyInfo(alias="conversationConfig")]
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

    deprecation_date: Annotated[TypeDateParam, PropertyInfo(alias="deprecationDate")]
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

    kind: ModelKind
    """The kind of model. If not specified, the default is HF_PEFT_ADDON."""

    peft_details: Annotated[PeftDetailsParam, PropertyInfo(alias="peftDetails")]
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
