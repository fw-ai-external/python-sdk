# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo
from .deployment_precision import DeploymentPrecision
from .gateway_accelerator_type import GatewayAcceleratorType
from .deployment_shape_preset_type import DeploymentShapePresetType

__all__ = ["DeploymentShapeCreateParams"]


class DeploymentShapeCreateParams(TypedDict, total=False):
    base_model: Required[Annotated[str, PropertyInfo(alias="baseModel")]]

    deployment_shape_id: Annotated[str, PropertyInfo(alias="deploymentShapeId")]
    """The ID of the deployment shape.

    If not specified, a random ID will be generated.
    """

    disable_size_validation: Annotated[bool, PropertyInfo(alias="disableSizeValidation")]
    """Whether to disable the size validation for the deployment shape."""

    accelerator_count: Annotated[int, PropertyInfo(alias="acceleratorCount")]
    """
    The number of accelerators used per replica. If not specified, the default is
    the estimated minimum required by the base model.
    """

    accelerator_type: Annotated[GatewayAcceleratorType, PropertyInfo(alias="acceleratorType")]
    """
    The type of accelerator to use. If not specified, the default is
    NVIDIA_A100_80GB.
    """

    description: str
    """The description of the deployment shape.

    Must be fewer than 1000 characters long.
    """

    display_name: Annotated[str, PropertyInfo(alias="displayName")]
    """Human-readable display name of the deployment shape.

    e.g. "My Deployment Shape" Must be fewer than 64 characters long.
    """

    draft_model: Annotated[str, PropertyInfo(alias="draftModel")]
    """The draft model name for speculative decoding.

    e.g. accounts/fireworks/models/my-draft-model If empty, speculative decoding
    using a draft model is disabled. Default is the base model's
    default_draft_model. this behavior.
    """

    draft_token_count: Annotated[int, PropertyInfo(alias="draftTokenCount")]
    """
    The number of candidate tokens to generate per step for speculative decoding.
    Default is the base model's draft_token_count.
    """

    enable_addons: Annotated[bool, PropertyInfo(alias="enableAddons")]
    """If true, LORA addons are enabled for deployments created from this shape."""

    enable_session_affinity: Annotated[bool, PropertyInfo(alias="enableSessionAffinity")]
    """Whether to apply sticky routing based on `user` field."""

    ngram_speculation_length: Annotated[int, PropertyInfo(alias="ngramSpeculationLength")]
    """The length of previous input sequence to be considered for N-gram speculation."""

    precision: DeploymentPrecision
    """The precision with which the model should be served."""

    preset_type: Annotated[DeploymentShapePresetType, PropertyInfo(alias="presetType")]
    """Type of deployment shape for different deployment configurations."""
