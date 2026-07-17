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

__all__ = ["Model", "ServerlessMode", "ServerlessModeSKUInfo", "ServerlessModeSKUInfoAmount"]


class ServerlessModeSKUInfoAmount(BaseModel):
    """Represents an amount of money with its currency type."""

    currency_code: Optional[str] = FieldInfo(alias="currencyCode", default=None)
    """The three-letter currency code defined in ISO 4217."""

    nanos: Optional[int] = None
    """
    Number of nano (10^-9) units of the amount. The value must be between
    -999,999,999 and +999,999,999 inclusive. If `units` is positive, `nanos` must be
    positive or zero. If `units` is zero, `nanos` can be positive, zero, or
    negative. If `units` is negative, `nanos` must be negative or zero. For example
    $-1.75 is represented as `units`=-1 and `nanos`=-750,000,000.
    """

    units: Optional[str] = None
    """
    The whole units of the amount. For example if `currencyCode` is `"USD"`, then 1
    unit is one US dollar.
    """


class ServerlessModeSKUInfo(BaseModel):
    amount: Optional[ServerlessModeSKUInfoAmount] = None
    """Represents an amount of money with its currency type."""

    sku: Optional[str] = None

    unit: Optional[str] = None


class ServerlessMode(BaseModel):
    """
    ServerlessMode is one way a serverless base model can be invoked — standard
    serverless (default), Priority, Fast, or Spot — together with the invocation
    recipe customers must use for it.

    It is a child resource of the base Model: the {ServerlessModeId} segment of
    the resource name IS the mode name (default | priority | fast | spot). The
    base model is the linking key for all of its serving modes, even when a mode
    is served through a different resource (a Fast router, a Spot deployment).

    Modes split into two classes:
      - Alternate-resource modes (usage_identifier set) — e.g. fast resolves to a
        router, spot to the spot deployment's own model id.
      - Flag modes (service_tier set) — e.g. priority uses the base model id plus
        a request-body service_tier flag.

    Pricing is sourced live from Orb (keyed by the resolved model name / tier),
    so no price is stored on the mode.
    """

    create_time: Optional[datetime] = FieldInfo(alias="createTime", default=None)

    name: Optional[str] = None
    """
    The resource name, e.g.
    accounts/fireworks/models/kimi-k2p6/serverlessModes/fast. {AccountId} must be a
    serverless account (fireworks, ...); {ModelId} is the base model's id;
    {ServerlessModeId} is the mode name (default | priority | fast | spot).
    """

    service_tier: Optional[str] = FieldInfo(alias="serviceTier", default=None)
    """
    Invocation recipe: the service_tier request-body flag layered on top of the
    model id (e.g. "priority"). Only the priority mode sets this today.
    """

    sku_infos: Optional[List[ServerlessModeSKUInfo]] = FieldInfo(alias="skuInfos", default=None)
    """Per-path token pricing, sourced live from Orb on the read path.

    Reuses the same SKUInfo type as Model.sku_infos (e.g. "LLM input tokens
    (uncached)", "LLM input tokens (cached)", "LLM output tokens"; google.type.Money
    at unit="1M tokens"). Resolved per tier (DEFAULT/PRIORITY/FAST/...). Empty on
    the stored config; only populated by ListServerlessModels.

    (api_only) keeps this derived field out of the database entirely (like
    Model.sku_infos): it is never persisted by the admin write path and never read
    back from storage, only computed live at read time.
    """

    updated_by: Optional[str] = FieldInfo(alias="updatedBy", default=None)
    """The user who last mutated this mode (audit)."""

    update_time: Optional[datetime] = FieldInfo(alias="updateTime", default=None)

    usage_identifier: Optional[str] = FieldInfo(alias="usageIdentifier", default=None)
    """
    Invocation recipe: the value to pass as "model" in inference requests. Empty
    means use the base model id. May reference a DIFFERENT resource than the base
    model — a model OR a router, e.g. accounts/fireworks/routers/kimi-k2p6-fast for
    fast.
    """

    use_cases: Optional[List[str]] = FieldInfo(alias="useCases", default=None)
    """Curated use-case tags driving discovery filters (e.g. "coding")."""


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

    encryption_state: Optional[
        Literal["ENCRYPTION_STATE_UNSPECIFIED", "ENCRYPTION_STATE_PLAINTEXT", "ENCRYPTION_STATE_CMEK"]
    ] = FieldInfo(alias="encryptionState", default=None)
    """CMEK encryption state (authoritative, stamped at creation)."""

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
    0). True when validated POLICY_TRAINER + LORA_TRAINER training shapes exist plus
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
    the model has use_training_v2=true, use rl_lora_tunable and
    rl_full_parameter_tunable instead.
    """

    serverless_modes: Optional[List[ServerlessMode]] = FieldInfo(alias="serverlessModes", default=None)
    """The serverless modes this base model is available on — the serverless read
    shape.

    Populated on read (e.g. the serverless catalog read path); one entry per serving
    mode. Empty for non-serverless models.
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
    the model has use_training_v2=true, use supervised_lora_tunable and
    supervised_full_parameter_tunable instead.
    """

    update_time: Optional[datetime] = FieldInfo(alias="updateTime", default=None)
    """The update time for the model."""

    use_hf_apply_chat_template: Optional[bool] = FieldInfo(alias="useHfApplyChatTemplate", default=None)
    """
    If true, the model will use the Hugging Face apply_chat_template API to apply
    the chat template.
    """

    use_training_v2: Optional[bool] = FieldInfo(alias="useTrainingV2", default=None)
    """
    If true, SFT jobs for this base model use service-mode (StatefulSet +
    orchestration sidecar) instead of the legacy batch Job path.
    """
