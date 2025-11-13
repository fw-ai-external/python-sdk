# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["DeploymentShapeVersionGetResponse", "Snapshot"]


class Snapshot(BaseModel):
    base_model: str = FieldInfo(alias="baseModel")

    accelerator_count: Optional[int] = FieldInfo(alias="acceleratorCount", default=None)
    """
    The number of accelerators used per replica. If not specified, the default is
    the estimated minimum required by the base model.
    """

    accelerator_type: Optional[
        Literal[
            "ACCELERATOR_TYPE_UNSPECIFIED",
            "NVIDIA_A100_80GB",
            "NVIDIA_H100_80GB",
            "AMD_MI300X_192GB",
            "NVIDIA_A10G_24GB",
            "NVIDIA_A100_40GB",
            "NVIDIA_L4_24GB",
            "NVIDIA_H200_141GB",
            "NVIDIA_B200_180GB",
            "AMD_MI325X_256GB",
        ]
    ] = FieldInfo(alias="acceleratorType", default=None)
    """
    The type of accelerator to use. If not specified, the default is
    NVIDIA_A100_80GB.
    """

    create_time: Optional[datetime] = FieldInfo(alias="createTime", default=None)
    """The creation time of the deployment shape."""

    description: Optional[str] = None
    """The description of the deployment shape.

    Must be fewer than 1000 characters long.
    """

    display_name: Optional[str] = FieldInfo(alias="displayName", default=None)
    """Human-readable display name of the deployment shape.

    e.g. "My Deployment Shape" Must be fewer than 64 characters long.
    """

    draft_model: Optional[str] = FieldInfo(alias="draftModel", default=None)
    """The draft model name for speculative decoding.

    e.g. accounts/fireworks/models/my-draft-model If empty, speculative decoding
    using a draft model is disabled. Default is the base model's
    default_draft_model. this behavior.
    """

    draft_token_count: Optional[int] = FieldInfo(alias="draftTokenCount", default=None)
    """
    The number of candidate tokens to generate per step for speculative decoding.
    Default is the base model's draft_token_count.
    """

    enable_addons: Optional[bool] = FieldInfo(alias="enableAddons", default=None)
    """If true, LORA addons are enabled for deployments created from this shape."""

    enable_session_affinity: Optional[bool] = FieldInfo(alias="enableSessionAffinity", default=None)
    """Whether to apply sticky routing based on `user` field."""

    api_model_type: Optional[str] = FieldInfo(alias="modelType", default=None)
    """The model type of the base model."""

    name: Optional[str] = None

    ngram_speculation_length: Optional[int] = FieldInfo(alias="ngramSpeculationLength", default=None)
    """The length of previous input sequence to be considered for N-gram speculation."""

    num_lora_device_cached: Optional[int] = FieldInfo(alias="numLoraDeviceCached", default=None)

    parameter_count: Optional[str] = FieldInfo(alias="parameterCount", default=None)
    """The parameter count of the base model ."""

    precision: Optional[
        Literal[
            "PRECISION_UNSPECIFIED",
            "FP16",
            "FP8",
            "FP8_MM",
            "FP8_AR",
            "FP8_MM_KV_ATTN",
            "FP8_KV",
            "FP8_MM_V2",
            "FP8_V2",
            "FP8_MM_KV_ATTN_V2",
            "NF4",
            "FP4",
            "BF16",
            "FP4_BLOCKSCALED_MM",
            "FP4_MX_MOE",
        ]
    ] = None
    """The precision with which the model should be served."""

    preset_type: Optional[
        Literal["PRESET_TYPE_UNSPECIFIED", "MINIMAL", "FAST", "THROUGHPUT", "REINFORCEMENT_FINE_TUNING"]
    ] = FieldInfo(alias="presetType", default=None)
    """Type of deployment shape for different deployment configurations."""

    update_time: Optional[datetime] = FieldInfo(alias="updateTime", default=None)
    """The update time for the deployment shape."""


class DeploymentShapeVersionGetResponse(BaseModel):
    create_time: Optional[datetime] = FieldInfo(alias="createTime", default=None)
    """The creation time of the deployment shape version.

    Lists will be ordered by this field.
    """

    latest_validated: Optional[bool] = FieldInfo(alias="latestValidated", default=None)
    """
    If true, this version is the latest validated version. Only one version of the
    shape can be the latest validated version.
    """

    name: Optional[str] = None

    public: Optional[bool] = None
    """If true, this version will be publicly readable."""

    snapshot: Optional[Snapshot] = None
    """Full snapshot of the Deployment Shape at this version."""

    validated: Optional[bool] = None
    """If true, this version has been validated."""
