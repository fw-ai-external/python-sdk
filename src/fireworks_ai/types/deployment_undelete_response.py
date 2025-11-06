# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["DeploymentUndeleteResponse", "AutoscalingPolicy", "AutoTune", "Placement", "Status"]


class AutoscalingPolicy(BaseModel):
    load_targets: Optional[Dict[str, float]] = FieldInfo(alias="loadTargets", default=None)

    scale_down_window: Optional[str] = FieldInfo(alias="scaleDownWindow", default=None)
    """
    The duration the autoscaler will wait before scaling down a deployment after
    observing decreased load. Default is 10m.
    """

    scale_to_zero_window: Optional[str] = FieldInfo(alias="scaleToZeroWindow", default=None)
    """
    The duration after which there are no requests that the deployment will be
    scaled down to zero replicas, if min_replica_count==0. Default is 1h. This must
    be at least 5 minutes.
    """

    scale_up_window: Optional[str] = FieldInfo(alias="scaleUpWindow", default=None)
    """
    The duration the autoscaler will wait before scaling up a deployment after
    observing increased load. Default is 30s.
    """


class AutoTune(BaseModel):
    long_prompt: Optional[bool] = FieldInfo(alias="longPrompt", default=None)
    """If true, this deployment is optimized for long prompt lengths."""


class Placement(BaseModel):
    multi_region: Optional[Literal["MULTI_REGION_UNSPECIFIED", "GLOBAL", "US"]] = FieldInfo(
        alias="multiRegion", default=None
    )
    """The multi-region where the deployment must be placed."""

    region: Optional[
        Literal[
            "REGION_UNSPECIFIED",
            "US_IOWA_1",
            "US_VIRGINIA_1",
            "US_ILLINOIS_1",
            "AP_TOKYO_1",
            "US_ARIZONA_1",
            "US_TEXAS_1",
            "US_ILLINOIS_2",
            "EU_FRANKFURT_1",
            "US_TEXAS_2",
            "EU_ICELAND_1",
            "EU_ICELAND_2",
            "US_WASHINGTON_1",
            "US_WASHINGTON_2",
            "US_WASHINGTON_3",
            "AP_TOKYO_2",
            "US_CALIFORNIA_1",
            "US_UTAH_1",
            "US_TEXAS_3",
            "US_GEORGIA_1",
            "US_GEORGIA_2",
            "US_WASHINGTON_4",
            "US_GEORGIA_3",
        ]
    ] = None
    """The region where the deployment must be placed."""

    regions: Optional[
        List[
            Literal[
                "REGION_UNSPECIFIED",
                "US_IOWA_1",
                "US_VIRGINIA_1",
                "US_ILLINOIS_1",
                "AP_TOKYO_1",
                "US_ARIZONA_1",
                "US_TEXAS_1",
                "US_ILLINOIS_2",
                "EU_FRANKFURT_1",
                "US_TEXAS_2",
                "EU_ICELAND_1",
                "EU_ICELAND_2",
                "US_WASHINGTON_1",
                "US_WASHINGTON_2",
                "US_WASHINGTON_3",
                "AP_TOKYO_2",
                "US_CALIFORNIA_1",
                "US_UTAH_1",
                "US_TEXAS_3",
                "US_GEORGIA_1",
                "US_GEORGIA_2",
                "US_WASHINGTON_4",
                "US_GEORGIA_3",
            ]
        ]
    ] = None


class Status(BaseModel):
    code: Optional[
        Literal[
            "OK",
            "CANCELLED",
            "UNKNOWN",
            "INVALID_ARGUMENT",
            "DEADLINE_EXCEEDED",
            "NOT_FOUND",
            "ALREADY_EXISTS",
            "PERMISSION_DENIED",
            "UNAUTHENTICATED",
            "RESOURCE_EXHAUSTED",
            "FAILED_PRECONDITION",
            "ABORTED",
            "OUT_OF_RANGE",
            "UNIMPLEMENTED",
            "INTERNAL",
            "UNAVAILABLE",
            "DATA_LOSS",
        ]
    ] = None
    """The status code."""

    message: Optional[str] = None
    """A developer-facing error message in English."""


class DeploymentUndeleteResponse(BaseModel):
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

    active_model_version: Optional[str] = FieldInfo(alias="activeModelVersion", default=None)
    """The active model version for this deployment.

    Used to enable a specific model version.
    """

    autoscaling_policy: Optional[AutoscalingPolicy] = FieldInfo(alias="autoscalingPolicy", default=None)

    auto_tune: Optional[AutoTune] = FieldInfo(alias="autoTune", default=None)
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

    direct_route_type: Optional[
        Literal["DIRECT_ROUTE_TYPE_UNSPECIFIED", "INTERNET", "GCP_PRIVATE_SERVICE_CONNECT", "AWS_PRIVATELINK"]
    ] = FieldInfo(alias="directRouteType", default=None)
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

    placement: Optional[Placement] = None
    """
    The desired geographic region where the deployment must be placed. If
    unspecified, the default is the GLOBAL multi-region.
    """

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

    purge_time: Optional[datetime] = FieldInfo(alias="purgeTime", default=None)
    """The time at which the resource will be hard deleted."""

    region: Optional[
        Literal[
            "REGION_UNSPECIFIED",
            "US_IOWA_1",
            "US_VIRGINIA_1",
            "US_ILLINOIS_1",
            "AP_TOKYO_1",
            "US_ARIZONA_1",
            "US_TEXAS_1",
            "US_ILLINOIS_2",
            "EU_FRANKFURT_1",
            "US_TEXAS_2",
            "EU_ICELAND_1",
            "EU_ICELAND_2",
            "US_WASHINGTON_1",
            "US_WASHINGTON_2",
            "US_WASHINGTON_3",
            "AP_TOKYO_2",
            "US_CALIFORNIA_1",
            "US_UTAH_1",
            "US_TEXAS_3",
            "US_GEORGIA_1",
            "US_GEORGIA_2",
            "US_WASHINGTON_4",
            "US_GEORGIA_3",
        ]
    ] = None
    """The geographic region where the deployment is presently located.

    This region may change over time, but within the `placement` constraint.
    """

    replica_count: Optional[int] = FieldInfo(alias="replicaCount", default=None)

    state: Optional[Literal["STATE_UNSPECIFIED", "CREATING", "READY", "DELETING", "FAILED", "UPDATING", "DELETED"]] = (
        None
    )
    """The state of the deployment."""

    status: Optional[Status] = None
    """Detailed status information regarding the most recent operation."""

    update_time: Optional[datetime] = FieldInfo(alias="updateTime", default=None)
    """The update time for the deployment."""
