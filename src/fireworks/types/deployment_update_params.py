# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Union
from datetime import datetime
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._types import SequenceNotStr
from .._utils import PropertyInfo

__all__ = ["DeploymentUpdateParams", "AutoscalingPolicy", "AutoTune", "Placement"]


class DeploymentUpdateParams(TypedDict, total=False):
    account_id: Required[str]

    base_model: Required[Annotated[str, PropertyInfo(alias="baseModel")]]

    accelerator_count: Annotated[int, PropertyInfo(alias="acceleratorCount")]
    """
    The number of accelerators used per replica. If not specified, the default is
    the estimated minimum required by the base model.
    """

    accelerator_type: Annotated[
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
        ],
        PropertyInfo(alias="acceleratorType"),
    ]
    """
    The type of accelerator to use. If not specified, the default is
    NVIDIA_A100_80GB.
    """

    active_model_version: Annotated[str, PropertyInfo(alias="activeModelVersion")]
    """The active model version for this deployment.

    Used to enable a specific model version.
    """

    autoscaling_policy: Annotated[AutoscalingPolicy, PropertyInfo(alias="autoscalingPolicy")]

    auto_tune: Annotated[AutoTune, PropertyInfo(alias="autoTune")]
    """The performance profile to use for this deployment."""

    deployment_shape: Annotated[str, PropertyInfo(alias="deploymentShape")]
    """
    The name of the deployment shape that this deployment is using. On the server
    side, this will be replaced with the deployment shape version name.
    """

    deployment_template: Annotated[str, PropertyInfo(alias="deploymentTemplate")]
    """The name of the deployment template to use for this deployment.

    Only available to enterprise accounts.
    """

    description: str
    """Description of the deployment."""

    direct_route_api_keys: Annotated[SequenceNotStr[str], PropertyInfo(alias="directRouteApiKeys")]
    """The set of API keys used to access the direct route deployment.

    If direct routing is not enabled, this field is unused.
    """

    direct_route_type: Annotated[
        Literal["DIRECT_ROUTE_TYPE_UNSPECIFIED", "INTERNET", "GCP_PRIVATE_SERVICE_CONNECT", "AWS_PRIVATELINK"],
        PropertyInfo(alias="directRouteType"),
    ]
    """
    If set, this deployment will expose an endpoint that bypasses the Fireworks API
    gateway.
    """

    disable_deployment_size_validation: Annotated[bool, PropertyInfo(alias="disableDeploymentSizeValidation")]
    """Whether the deployment size validation is disabled."""

    display_name: Annotated[str, PropertyInfo(alias="displayName")]
    """Human-readable display name of the deployment.

    e.g. "My Deployment" Must be fewer than 64 characters long.
    """

    draft_model: Annotated[str, PropertyInfo(alias="draftModel")]
    """The draft model name for speculative decoding.

    e.g. accounts/fireworks/models/my-draft-model If empty, speculative decoding
    using a draft model is disabled. Default is the base model's
    default_draft_model. Set CreateDeploymentRequest.disable_speculative_decoding to
    false to disable this behavior.
    """

    draft_token_count: Annotated[int, PropertyInfo(alias="draftTokenCount")]
    """
    The number of candidate tokens to generate per step for speculative decoding.
    Default is the base model's draft_token_count. Set
    CreateDeploymentRequest.disable_speculative_decoding to false to disable this
    behavior.
    """

    enable_addons: Annotated[bool, PropertyInfo(alias="enableAddons")]
    """If true, PEFT addons are enabled for this deployment."""

    enable_hot_reload_latest_addon: Annotated[bool, PropertyInfo(alias="enableHotReloadLatestAddon")]
    """
    Allows up to 1 addon at a time to be loaded, and will merge it into the base
    model.
    """

    enable_mtp: Annotated[bool, PropertyInfo(alias="enableMtp")]
    """If true, MTP is enabled for this deployment."""

    enable_session_affinity: Annotated[bool, PropertyInfo(alias="enableSessionAffinity")]
    """Whether to apply sticky routing based on `user` field."""

    expire_time: Annotated[Union[str, datetime], PropertyInfo(alias="expireTime", format="iso8601")]
    """The time at which this deployment will automatically be deleted."""

    max_replica_count: Annotated[int, PropertyInfo(alias="maxReplicaCount")]
    """
    The maximum number of replicas. If not specified, the default is
    max(min_replica_count, 1). May be set to 0 to downscale the deployment to 0.
    """

    min_replica_count: Annotated[int, PropertyInfo(alias="minReplicaCount")]
    """The minimum number of replicas. If not specified, the default is 0."""

    ngram_speculation_length: Annotated[int, PropertyInfo(alias="ngramSpeculationLength")]
    """The length of previous input sequence to be considered for N-gram speculation."""

    placement: Placement
    """
    The desired geographic region where the deployment must be placed. If
    unspecified, the default is the GLOBAL multi-region.
    """

    precision: Literal[
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
    """The precision with which the model should be served."""


class AutoscalingPolicy(TypedDict, total=False):
    load_targets: Annotated[Dict[str, float], PropertyInfo(alias="loadTargets")]

    scale_down_window: Annotated[str, PropertyInfo(alias="scaleDownWindow")]
    """
    The duration the autoscaler will wait before scaling down a deployment after
    observing decreased load. Default is 10m.
    """

    scale_to_zero_window: Annotated[str, PropertyInfo(alias="scaleToZeroWindow")]
    """
    The duration after which there are no requests that the deployment will be
    scaled down to zero replicas, if min_replica_count==0. Default is 1h. This must
    be at least 5 minutes.
    """

    scale_up_window: Annotated[str, PropertyInfo(alias="scaleUpWindow")]
    """
    The duration the autoscaler will wait before scaling up a deployment after
    observing increased load. Default is 30s.
    """


class AutoTune(TypedDict, total=False):
    long_prompt: Annotated[bool, PropertyInfo(alias="longPrompt")]
    """If true, this deployment is optimized for long prompt lengths."""


class Placement(TypedDict, total=False):
    multi_region: Annotated[Literal["MULTI_REGION_UNSPECIFIED", "GLOBAL", "US"], PropertyInfo(alias="multiRegion")]
    """The multi-region where the deployment must be placed."""

    region: Literal[
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
    """The region where the deployment must be placed."""

    regions: List[
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
