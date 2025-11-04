# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .deployment_precision import DeploymentPrecision
from .gateway_accelerator_type import GatewayAcceleratorType
from .deployment_shape_preset_type import DeploymentShapePresetType

__all__ = ["GatewayDeploymentShape"]


class GatewayDeploymentShape(BaseModel):
    base_model: str = FieldInfo(alias="baseModel")

    accelerator_count: Optional[int] = FieldInfo(alias="acceleratorCount", default=None)
    """
    The number of accelerators used per replica. If not specified, the default is
    the estimated minimum required by the base model.
    """

    accelerator_type: Optional[GatewayAcceleratorType] = FieldInfo(alias="acceleratorType", default=None)
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

    precision: Optional[DeploymentPrecision] = None
    """The precision with which the model should be served."""

    preset_type: Optional[DeploymentShapePresetType] = FieldInfo(alias="presetType", default=None)
    """Type of deployment shape for different deployment configurations."""

    update_time: Optional[datetime] = FieldInfo(alias="updateTime", default=None)
    """The update time for the deployment shape."""
