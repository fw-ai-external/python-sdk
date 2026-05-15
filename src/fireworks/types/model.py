# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .type_date import TypeDate
from .peft_details import PeftDetails
from .shared.status import Status
from .base_model_details import BaseModelDetails
from .conversation_config import ConversationConfig
from .shared.deployed_model_ref import DeployedModelRef

__all__ = ["Model"]


class Model(BaseModel):
    base_model_details: Optional[BaseModelDetails] = FieldInfo(alias="baseModelDetails", default=None)
    """Base model details. Required if kind is HF_BASE_MODEL.

    Must not be set otherwise.
    """

    calibrated: Optional[bool] = None
    """If true, the model is calibrated and can be deployed to non-FP16 precisions."""

    cluster: Optional[str] = None
    """The resource name of the BYOC cluster to which this model belongs. e.g.

    accounts/my-account/clusters/my-cluster. Empty if it belongs to a Fireworks
    cluster.
    """

    context_length: Optional[int] = FieldInfo(alias="contextLength", default=None)
    """The maximum context length supported by the model."""

    conversation_config: Optional[ConversationConfig] = FieldInfo(alias="conversationConfig", default=None)
    """If set, the Chat Completions API will be enabled for this model."""

    create_time: Optional[datetime] = FieldInfo(alias="createTime", default=None)
    """The creation time of the model."""

    default_draft_model: Optional[str] = FieldInfo(alias="defaultDraftModel", default=None)
    """The default draft model to use when creating a deployment.

    If empty, speculative decoding is disabled by default.
    """

    default_draft_token_count: Optional[int] = FieldInfo(alias="defaultDraftTokenCount", default=None)
    """
    The default draft token count to use when creating a deployment. Must be
    specified if default_draft_model is specified.
    """

    default_sampling_params: Optional[Dict[str, float]] = FieldInfo(alias="defaultSamplingParams", default=None)
    """A json object that contains the default sampling parameters for the model."""

    deployed_model_refs: Optional[List[DeployedModelRef]] = FieldInfo(alias="deployedModelRefs", default=None)
    """Populated from GetModel API call only."""

    deprecation_date: Optional[TypeDate] = FieldInfo(alias="deprecationDate", default=None)
    """
    If specified, this is the date when the serverless deployment of the model will
    be taken down.
    """

    description: Optional[str] = None
    """The description of the model. Must be fewer than 1000 characters long."""

    display_name: Optional[str] = FieldInfo(alias="displayName", default=None)
    """Human-readable display name of the model.

    e.g. "My Model" Must be fewer than 64 characters long.
    """

    fine_tuning_job: Optional[str] = FieldInfo(alias="fineTuningJob", default=None)
    """
    If the model was created from a fine-tuning job, this is the fine-tuning job
    name.
    """

    github_url: Optional[str] = FieldInfo(alias="githubUrl", default=None)
    """The URL to GitHub repository of the model."""

    hugging_face_url: Optional[str] = FieldInfo(alias="huggingFaceUrl", default=None)
    """The URL to the Hugging Face model."""

    imported_from: Optional[str] = FieldInfo(alias="importedFrom", default=None)
    """The name of the the model from which this was imported.

    This field is empty if the model was not imported.
    """

    kind: Optional[
        Literal[
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
    ] = None
    """The kind of model. If not specified, the default is HF_PEFT_ADDON."""

    name: Optional[str] = None

    peft_details: Optional[PeftDetails] = FieldInfo(alias="peftDetails", default=None)
    """PEFT addon details. Required if kind is HF_PEFT_ADDON or HF_TEFT_ADDON."""

    public: Optional[bool] = None
    """If true, the model will be publicly readable."""

    rl_full_parameter_tunable: Optional[bool] = FieldInfo(alias="rlFullParameterTunable", default=None)
    """V2 only.

    Whether the model supports full-parameter reinforcement learning (lora_rank =
    0). True when validated POLICY_TRAINER + FORWARD_ONLY training shapes exist plus
    a deployment shape.
    """

    rl_lora_tunable: Optional[bool] = FieldInfo(alias="rlLoraTunable", default=None)
    """V2 only.

    Whether the model supports LoRA reinforcement learning (lora_rank > 0). True
    when a validated LORA_TRAINER training shape exists plus a deployment shape.
    """

    rl_tunable: Optional[bool] = FieldInfo(alias="rlTunable", default=None)
    """
    Deprecated: V1 training stack only — LoRA only, limited architecture support. If
    the model has use_training_v2=true and your account has AllowTrainingV2, use
    rl_lora_tunable and rl_full_parameter_tunable instead.
    """

    snapshot_type: Optional[Literal["FULL_SNAPSHOT", "INCREMENTAL_SNAPSHOT"]] = FieldInfo(
        alias="snapshotType", default=None
    )

    state: Optional[Literal["STATE_UNSPECIFIED", "UPLOADING", "READY"]] = None
    """The state of the model."""

    status: Optional[Status] = None
    """Contains detailed message when the last model operation fails."""

    supervised_full_parameter_tunable: Optional[bool] = FieldInfo(alias="supervisedFullParameterTunable", default=None)
    """V2 only.

    Whether the model supports full-parameter supervised fine-tuning and DPO
    (lora_rank = 0). True when a validated POLICY_TRAINER training shape exists.
    """

    supervised_lora_tunable: Optional[bool] = FieldInfo(alias="supervisedLoraTunable", default=None)
    """V2 only.

    Whether the model supports LoRA supervised fine-tuning and DPO (lora_rank > 0).
    True when a validated LORA_TRAINER training shape exists.
    """

    supports_image_input: Optional[bool] = FieldInfo(alias="supportsImageInput", default=None)
    """If set, images can be provided as input to the model."""

    supports_lora: Optional[bool] = FieldInfo(alias="supportsLora", default=None)
    """Whether this model supports LoRA."""

    supports_serverless: Optional[bool] = FieldInfo(alias="supportsServerless", default=None)
    """If true, the model has a serverless deployment."""

    supports_tools: Optional[bool] = FieldInfo(alias="supportsTools", default=None)
    """If set, tools (i.e.

    functions) can be provided as input to the model, and the model may respond with
    one or more tool calls.
    """

    teft_details: Optional[object] = FieldInfo(alias="teftDetails", default=None)
    """TEFT addon details. Required if kind is HF_TEFT_ADDON.

    Must not be set otherwise.
    """

    training_context_length: Optional[int] = FieldInfo(alias="trainingContextLength", default=None)
    """The maximum context length supported by the model."""

    tunable: Optional[bool] = None
    """
    Deprecated: V1 training stack only — LoRA only, limited architecture support. If
    the model has use_training_v2=true and your account has AllowTrainingV2, use
    supervised_lora_tunable and supervised_full_parameter_tunable instead.
    """

    update_time: Optional[datetime] = FieldInfo(alias="updateTime", default=None)
    """The update time for the model."""

    use_hf_apply_chat_template: Optional[bool] = FieldInfo(alias="useHfApplyChatTemplate", default=None)
    """
    If true, the model will use the Hugging Face apply_chat_template API to apply
    the chat template.
    """
