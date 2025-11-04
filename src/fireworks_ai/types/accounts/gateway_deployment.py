# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .gateway_region import GatewayRegion
from .gateway_status import GatewayStatus
from .gateway_auto_tune import GatewayAutoTune
from .gateway_placement import GatewayPlacement
from .deployment_precision import DeploymentPrecision
from .gateway_accelerator_type import GatewayAcceleratorType
from .gateway_deployment_state import GatewayDeploymentState
from .gateway_direct_route_type import GatewayDirectRouteType
from .gateway_autoscaling_policy import GatewayAutoscalingPolicy

__all__ = ["GatewayDeployment"]


class GatewayDeployment(BaseModel):
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

    active_model_version: Optional[str] = FieldInfo(alias="activeModelVersion", default=None)
    """The active model version for this deployment.

    Used to enable a specific model version.
    """

    autoscaling_policy: Optional[GatewayAutoscalingPolicy] = FieldInfo(alias="autoscalingPolicy", default=None)

    auto_tune: Optional[GatewayAutoTune] = FieldInfo(alias="autoTune", default=None)
    """The performance profile to use for this deployment."""

    cluster: Optional[str] = None
    """If set, this deployment is deployed to a cloud-premise cluster."""

    create_time: Optional[datetime] = FieldInfo(alias="createTime", default=None)
    """The creation time of the deployment."""

    delete_time: Optional[datetime] = FieldInfo(alias="deleteTime", default=None)
    """The time at which the resource will be soft deleted."""

    deployment_shape: Optional[str] = FieldInfo(alias="deploymentShape", default=None)
    """
    The name of the deployment shape that this deployment is using. On the server
    side, this will be replaced with the deployment shape version name.
    """

    deployment_template: Optional[str] = FieldInfo(alias="deploymentTemplate", default=None)
    """The name of the deployment template to use for this deployment.

    Only available to enterprise accounts.
    """

    description: Optional[str] = None
    """Description of the deployment."""

    desired_replica_count: Optional[int] = FieldInfo(alias="desiredReplicaCount", default=None)
    """The desired number of replicas for this deployment.

    This represents the target replica count that the system is trying to achieve.
    """

    direct_route_api_keys: Optional[List[str]] = FieldInfo(alias="directRouteApiKeys", default=None)
    """The set of API keys used to access the direct route deployment.

    If direct routing is not enabled, this field is unused.
    """

    direct_route_handle: Optional[str] = FieldInfo(alias="directRouteHandle", default=None)
    """The handle for calling a direct route.

    The meaning of the handle depends on the direct route type of the deployment:
    INTERNET -> The host name for accessing the deployment
    GCP_PRIVATE_SERVICE_CONNECT -> The service attachment name used to create the
    PSC endpoint. AWS_PRIVATELINK -> The service name used to create the VPC
    endpoint.
    """

    direct_route_type: Optional[GatewayDirectRouteType] = FieldInfo(alias="directRouteType", default=None)
    """
    If set, this deployment will expose an endpoint that bypasses the Fireworks API
    gateway.
    """

    disable_deployment_size_validation: Optional[bool] = FieldInfo(
        alias="disableDeploymentSizeValidation", default=None
    )
    """Whether the deployment size validation is disabled."""

    display_name: Optional[str] = FieldInfo(alias="displayName", default=None)
    """Human-readable display name of the deployment.

    e.g. "My Deployment" Must be fewer than 64 characters long.
    """

    draft_model: Optional[str] = FieldInfo(alias="draftModel", default=None)
    """The draft model name for speculative decoding.

    e.g. accounts/fireworks/models/my-draft-model If empty, speculative decoding
    using a draft model is disabled. Default is the base model's
    default_draft_model. Set CreateDeploymentRequest.disable_speculative_decoding to
    false to disable this behavior.
    """

    draft_token_count: Optional[int] = FieldInfo(alias="draftTokenCount", default=None)
    """
    The number of candidate tokens to generate per step for speculative decoding.
    Default is the base model's draft_token_count. Set
    CreateDeploymentRequest.disable_speculative_decoding to false to disable this
    behavior.
    """

    enable_addons: Optional[bool] = FieldInfo(alias="enableAddons", default=None)
    """If true, PEFT addons are enabled for this deployment."""

    enable_hot_reload_latest_addon: Optional[bool] = FieldInfo(alias="enableHotReloadLatestAddon", default=None)
    """
    Allows up to 1 addon at a time to be loaded, and will merge it into the base
    model.
    """

    enable_mtp: Optional[bool] = FieldInfo(alias="enableMtp", default=None)
    """If true, MTP is enabled for this deployment."""

    enable_session_affinity: Optional[bool] = FieldInfo(alias="enableSessionAffinity", default=None)
    """Whether to apply sticky routing based on `user` field."""

    expire_time: Optional[datetime] = FieldInfo(alias="expireTime", default=None)
    """The time at which this deployment will automatically be deleted."""

    max_replica_count: Optional[int] = FieldInfo(alias="maxReplicaCount", default=None)
    """
    The maximum number of replicas. If not specified, the default is
    max(min_replica_count, 1). May be set to 0 to downscale the deployment to 0.
    """

    min_replica_count: Optional[int] = FieldInfo(alias="minReplicaCount", default=None)
    """The minimum number of replicas. If not specified, the default is 0."""

    name: Optional[str] = None

    ngram_speculation_length: Optional[int] = FieldInfo(alias="ngramSpeculationLength", default=None)
    """The length of previous input sequence to be considered for N-gram speculation."""

    num_peft_device_cached: Optional[int] = FieldInfo(alias="numPeftDeviceCached", default=None)

    placement: Optional[GatewayPlacement] = None
    """
    The desired geographic region where the deployment must be placed. If
    unspecified, the default is the GLOBAL multi-region.
    """

    precision: Optional[DeploymentPrecision] = None
    """The precision with which the model should be served."""

    purge_time: Optional[datetime] = FieldInfo(alias="purgeTime", default=None)
    """The time at which the resource will be hard deleted."""

    region: Optional[GatewayRegion] = None
    """The geographic region where the deployment is presently located.

    This region may change over time, but within the `placement` constraint.
    """

    replica_count: Optional[int] = FieldInfo(alias="replicaCount", default=None)

    state: Optional[GatewayDeploymentState] = None
    """The state of the deployment."""

    status: Optional[GatewayStatus] = None
    """Detailed status information regarding the most recent operation."""

    update_time: Optional[datetime] = FieldInfo(alias="updateTime", default=None)
    """The update time for the deployment."""
