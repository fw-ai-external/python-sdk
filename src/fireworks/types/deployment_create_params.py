# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._types import SequenceNotStr
from .._utils import PropertyInfo
from .auto_tune_param import AutoTuneParam
from .placement_param import PlacementParam
from .autoscaling_policy_param import AutoscalingPolicyParam

__all__ = ["DeploymentCreateParams"]


class DeploymentCreateParams(TypedDict, total=False):
    account_id: str

    base_model: Required[Annotated[str, PropertyInfo(alias="baseModel")]]

    deployment_id: Annotated[str, PropertyInfo(alias="deploymentId")]
    """The ID of the deployment. If not specified, a random ID will be generated."""

    disable_auto_deploy: Annotated[bool, PropertyInfo(alias="disableAutoDeploy")]
    """
    By default, a deployment created with a currently undeployed base model will be
    deployed to this deployment. If true, this auto-deploy function is disabled.
    """

    disable_speculative_decoding: Annotated[bool, PropertyInfo(alias="disableSpeculativeDecoding")]
    """
    By default, a deployment will use the speculative decoding settings from the
    base model. If true, this will disable speculative decoding.
    """

    skip_image_tag_validation: Annotated[bool, PropertyInfo(alias="skipImageTagValidation")]
    """
    If true, skip the image tag policy validation that blocks certain image tags.
    This allows creating deployments with image tags that would otherwise be
    blocked.
    """

    skip_shape_validation: Annotated[bool, PropertyInfo(alias="skipShapeValidation")]
    """
    By default, a deployment will ensure the deployment shape provided is validated.
    If true, we will not require the deployment shape to be validated.
    """

    validate_only: Annotated[bool, PropertyInfo(alias="validateOnly")]
    """
    If true, this will not create the deployment, but will return the deployment
    that would be created.
    """

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
            "AMD_MI350X_288GB",
        ],
        PropertyInfo(alias="acceleratorType"),
    ]
    """The type of accelerator to use."""

    active_model_version: Annotated[str, PropertyInfo(alias="activeModelVersion")]
    """
    The model version that is currently active and applied to running replicas of a
    deployment.
    """

    autoscaling_policy: Annotated[AutoscalingPolicyParam, PropertyInfo(alias="autoscalingPolicy")]

    auto_tune: Annotated[AutoTuneParam, PropertyInfo(alias="autoTune")]
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

    enable_hot_load: Annotated[bool, PropertyInfo(alias="enableHotLoad")]
    """Whether to use hot load for this deployment."""

    enable_hot_reload_latest_addon: Annotated[bool, PropertyInfo(alias="enableHotReloadLatestAddon")]
    """
    Allows up to 1 addon at a time to be loaded, and will merge it into the base
    model.
    """

    enable_mtp: Annotated[bool, PropertyInfo(alias="enableMtp")]
    """If true, MTP is enabled for this deployment."""

    enable_session_affinity: Annotated[bool, PropertyInfo(alias="enableSessionAffinity")]
    """
    Whether to apply sticky routing based on `user` field. Serverless will be set to
    true when creating deployment.
    """

    expire_time: Annotated[Union[str, datetime], PropertyInfo(alias="expireTime", format="iso8601")]
    """
    Deprecated: This field is deprecated and no longer causes auto-deletion. The
    time at which this deployment will automatically be deleted.
    """

    hot_load_bucket_type: Annotated[
        Literal["BUCKET_TYPE_UNSPECIFIED", "MINIO", "S3", "NEBIUS", "FW_HOSTED"],
        PropertyInfo(alias="hotLoadBucketType"),
    ]

    hot_load_bucket_url: Annotated[str, PropertyInfo(alias="hotLoadBucketUrl")]

    max_context_length: Annotated[int, PropertyInfo(alias="maxContextLength")]
    """
    The maximum context length supported by the model (context window). If set to 0
    or not specified, the model's default maximum context length will be used.
    """

    max_replica_count: Annotated[int, PropertyInfo(alias="maxReplicaCount")]
    """
    The maximum number of replicas. If not specified, the default is
    max(min_replica_count, 1). May be set to 0 to downscale the deployment to 0.
    """

    max_with_revocable_replica_count: Annotated[int, PropertyInfo(alias="maxWithRevocableReplicaCount")]
    """
    max_with_revocable_replica_count is max replica count including revocable
    capacity. The max revocable capacity will be max_with_revocable_replica_count -
    max_replica_count.
    """

    min_replica_count: Annotated[int, PropertyInfo(alias="minReplicaCount")]
    """The minimum number of replicas. If not specified, the default is 0."""

    ngram_speculation_length: Annotated[int, PropertyInfo(alias="ngramSpeculationLength")]
    """The length of previous input sequence to be considered for N-gram speculation."""

    placement: PlacementParam
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

    pricing_plan_id: Annotated[str, PropertyInfo(alias="pricingPlanId")]
    """
    Optional pricing plan ID for custom billing configuration. If set, this
    deployment will use the pricing plan's billing rules instead of default billing
    behavior.
    """

    target_model_version: Annotated[str, PropertyInfo(alias="targetModelVersion")]
    """
    The target model version that is being rolled out to the deployment. In a ready
    steady state, the target model version is the same as the active model version.
    """
