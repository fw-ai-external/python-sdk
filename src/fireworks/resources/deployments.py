# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Literal

import httpx

from ..types import (
    deployment_get_params,
    deployment_list_params,
    deployment_scale_params,
    deployment_create_params,
    deployment_delete_params,
    deployment_update_params,
    deployment_undelete_params,
)
from .._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..pagination import SyncCursorDeployments, AsyncCursorDeployments
from .._base_client import AsyncPaginator, make_request_options
from ..types.deployment import Deployment
from ..types.auto_tune_param import AutoTuneParam
from ..types.placement_param import PlacementParam
from ..types.autoscaling_policy_param import AutoscalingPolicyParam

__all__ = ["DeploymentsResource", "AsyncDeploymentsResource"]


class DeploymentsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> DeploymentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#accessing-raw-response-data-eg-headers
        """
        return DeploymentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DeploymentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#with_streaming_response
        """
        return DeploymentsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        account_id: str | None = None,
        base_model: str,
        deployment_id: str | Omit = omit,
        disable_auto_deploy: bool | Omit = omit,
        disable_speculative_decoding: bool | Omit = omit,
        skip_image_tag_validation: bool | Omit = omit,
        skip_shape_validation: bool | Omit = omit,
        validate_only: bool | Omit = omit,
        accelerator_count: int | Omit = omit,
        accelerator_type: Literal[
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
        ]
        | Omit = omit,
        active_model_version: str | Omit = omit,
        autoscaling_policy: AutoscalingPolicyParam | Omit = omit,
        auto_tune: AutoTuneParam | Omit = omit,
        deployment_shape: str | Omit = omit,
        deployment_template: str | Omit = omit,
        description: str | Omit = omit,
        direct_route_api_keys: SequenceNotStr[str] | Omit = omit,
        direct_route_type: Literal[
            "DIRECT_ROUTE_TYPE_UNSPECIFIED", "INTERNET", "GCP_PRIVATE_SERVICE_CONNECT", "AWS_PRIVATELINK"
        ]
        | Omit = omit,
        disable_deployment_size_validation: bool | Omit = omit,
        display_name: str | Omit = omit,
        draft_model: str | Omit = omit,
        draft_token_count: int | Omit = omit,
        enable_addons: bool | Omit = omit,
        enable_hot_load: bool | Omit = omit,
        enable_hot_reload_latest_addon: bool | Omit = omit,
        enable_mtp: bool | Omit = omit,
        enable_session_affinity: bool | Omit = omit,
        expire_time: Union[str, datetime] | Omit = omit,
        hot_load_bucket_type: Literal["BUCKET_TYPE_UNSPECIFIED", "MINIO", "S3", "NEBIUS", "FW_HOSTED"] | Omit = omit,
        hot_load_bucket_url: str | Omit = omit,
        max_context_length: int | Omit = omit,
        max_replica_count: int | Omit = omit,
        max_with_revocable_replica_count: int | Omit = omit,
        min_replica_count: int | Omit = omit,
        ngram_speculation_length: int | Omit = omit,
        placement: PlacementParam | Omit = omit,
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
        | Omit = omit,
        pricing_plan_id: str | Omit = omit,
        target_model_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Deployment:
        """Create Deployment

        Args:
          deployment_id: The ID of the deployment.

        If not specified, a random ID will be generated.

          disable_auto_deploy: By default, a deployment created with a currently undeployed base model will be
              deployed to this deployment. If true, this auto-deploy function is disabled.

          disable_speculative_decoding: By default, a deployment will use the speculative decoding settings from the
              base model. If true, this will disable speculative decoding.

          skip_image_tag_validation: If true, skip the image tag policy validation that blocks certain image tags.
              This allows creating deployments with image tags that would otherwise be
              blocked.

          skip_shape_validation: By default, a deployment will ensure the deployment shape provided is validated.
              If true, we will not require the deployment shape to be validated.

          validate_only: If true, this will not create the deployment, but will return the deployment
              that would be created.

          accelerator_count: The number of accelerators used per replica. If not specified, the default is
              the estimated minimum required by the base model.

          accelerator_type: The type of accelerator to use.

          active_model_version: The model version that is currently active and applied to running replicas of a
              deployment.

          auto_tune: The performance profile to use for this deployment.

          deployment_shape: The name of the deployment shape that this deployment is using. On the server
              side, this will be replaced with the deployment shape version name.

          deployment_template: The name of the deployment template to use for this deployment. Only available
              to enterprise accounts.

          description: Description of the deployment.

          direct_route_api_keys: The set of API keys used to access the direct route deployment. If direct
              routing is not enabled, this field is unused.

          direct_route_type: If set, this deployment will expose an endpoint that bypasses the Fireworks API
              gateway.

          disable_deployment_size_validation: Whether the deployment size validation is disabled.

          display_name: Human-readable display name of the deployment. e.g. "My Deployment" Must be
              fewer than 64 characters long.

          draft_model: The draft model name for speculative decoding. e.g.
              accounts/fireworks/models/my-draft-model If empty, speculative decoding using a
              draft model is disabled. Default is the base model's default_draft_model. Set
              CreateDeploymentRequest.disable_speculative_decoding to false to disable this
              behavior.

          draft_token_count: The number of candidate tokens to generate per step for speculative decoding.
              Default is the base model's draft_token_count. Set
              CreateDeploymentRequest.disable_speculative_decoding to false to disable this
              behavior.

          enable_addons: If true, PEFT addons are enabled for this deployment.

          enable_hot_load: Whether to use hot load for this deployment.

          enable_hot_reload_latest_addon: Allows up to 1 addon at a time to be loaded, and will merge it into the base
              model.

          enable_mtp: If true, MTP is enabled for this deployment.

          enable_session_affinity: Whether to apply sticky routing based on `user` field. Serverless will be set to
              true when creating deployment.

          expire_time: Deprecated: This field is deprecated and no longer causes auto-deletion. The
              time at which this deployment will automatically be deleted.

          max_context_length: The maximum context length supported by the model (context window). If set to 0
              or not specified, the model's default maximum context length will be used.

          max_replica_count: The maximum number of replicas. If not specified, the default is
              max(min_replica_count, 1). May be set to 0 to downscale the deployment to 0.

          max_with_revocable_replica_count: max_with_revocable_replica_count is max replica count including revocable
              capacity. The max revocable capacity will be max_with_revocable_replica_count -
              max_replica_count.

          min_replica_count: The minimum number of replicas. If not specified, the default is 0.

          ngram_speculation_length: The length of previous input sequence to be considered for N-gram speculation.

          placement: The desired geographic region where the deployment must be placed. If
              unspecified, the default is the GLOBAL multi-region.

          precision: The precision with which the model should be served.

          pricing_plan_id: Optional pricing plan ID for custom billing configuration. If set, this
              deployment will use the pricing plan's billing rules instead of default billing
              behavior.

          target_model_version: The target model version that is being rolled out to the deployment. In a ready
              steady state, the target model version is the same as the active model version.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if account_id is None:
            account_id = self._client._get_account_id_path_param()
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._post(
            f"/v1/accounts/{account_id}/deployments"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/deployments",
            body=maybe_transform(
                {
                    "base_model": base_model,
                    "accelerator_count": accelerator_count,
                    "accelerator_type": accelerator_type,
                    "active_model_version": active_model_version,
                    "autoscaling_policy": autoscaling_policy,
                    "auto_tune": auto_tune,
                    "deployment_shape": deployment_shape,
                    "deployment_template": deployment_template,
                    "description": description,
                    "direct_route_api_keys": direct_route_api_keys,
                    "direct_route_type": direct_route_type,
                    "disable_deployment_size_validation": disable_deployment_size_validation,
                    "display_name": display_name,
                    "draft_model": draft_model,
                    "draft_token_count": draft_token_count,
                    "enable_addons": enable_addons,
                    "enable_hot_load": enable_hot_load,
                    "enable_hot_reload_latest_addon": enable_hot_reload_latest_addon,
                    "enable_mtp": enable_mtp,
                    "enable_session_affinity": enable_session_affinity,
                    "expire_time": expire_time,
                    "hot_load_bucket_type": hot_load_bucket_type,
                    "hot_load_bucket_url": hot_load_bucket_url,
                    "max_context_length": max_context_length,
                    "max_replica_count": max_replica_count,
                    "max_with_revocable_replica_count": max_with_revocable_replica_count,
                    "min_replica_count": min_replica_count,
                    "ngram_speculation_length": ngram_speculation_length,
                    "placement": placement,
                    "precision": precision,
                    "pricing_plan_id": pricing_plan_id,
                    "target_model_version": target_model_version,
                },
                deployment_create_params.DeploymentCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "deployment_id": deployment_id,
                        "disable_auto_deploy": disable_auto_deploy,
                        "disable_speculative_decoding": disable_speculative_decoding,
                        "skip_image_tag_validation": skip_image_tag_validation,
                        "skip_shape_validation": skip_shape_validation,
                        "validate_only": validate_only,
                    },
                    deployment_create_params.DeploymentCreateParams,
                ),
            ),
            cast_to=Deployment,
        )

    def update(
        self,
        deployment_id: str,
        *,
        account_id: str | None = None,
        base_model: str,
        skip_shape_validation: bool | Omit = omit,
        accelerator_count: int | Omit = omit,
        accelerator_type: Literal[
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
        ]
        | Omit = omit,
        active_model_version: str | Omit = omit,
        autoscaling_policy: AutoscalingPolicyParam | Omit = omit,
        auto_tune: AutoTuneParam | Omit = omit,
        deployment_shape: str | Omit = omit,
        deployment_template: str | Omit = omit,
        description: str | Omit = omit,
        direct_route_api_keys: SequenceNotStr[str] | Omit = omit,
        direct_route_type: Literal[
            "DIRECT_ROUTE_TYPE_UNSPECIFIED", "INTERNET", "GCP_PRIVATE_SERVICE_CONNECT", "AWS_PRIVATELINK"
        ]
        | Omit = omit,
        disable_deployment_size_validation: bool | Omit = omit,
        display_name: str | Omit = omit,
        draft_model: str | Omit = omit,
        draft_token_count: int | Omit = omit,
        enable_addons: bool | Omit = omit,
        enable_hot_load: bool | Omit = omit,
        enable_hot_reload_latest_addon: bool | Omit = omit,
        enable_mtp: bool | Omit = omit,
        enable_session_affinity: bool | Omit = omit,
        expire_time: Union[str, datetime] | Omit = omit,
        hot_load_bucket_type: Literal["BUCKET_TYPE_UNSPECIFIED", "MINIO", "S3", "NEBIUS", "FW_HOSTED"] | Omit = omit,
        hot_load_bucket_url: str | Omit = omit,
        max_context_length: int | Omit = omit,
        max_replica_count: int | Omit = omit,
        max_with_revocable_replica_count: int | Omit = omit,
        min_replica_count: int | Omit = omit,
        ngram_speculation_length: int | Omit = omit,
        placement: PlacementParam | Omit = omit,
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
        | Omit = omit,
        pricing_plan_id: str | Omit = omit,
        target_model_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Deployment:
        """
        Update Deployment

        Args:
          skip_shape_validation: By default, updating a deployment shape will ensure the new deployment shape
              provided is validated. If true, we will not require the deployment shape to be
              validated.

          accelerator_count: The number of accelerators used per replica. If not specified, the default is
              the estimated minimum required by the base model.

          accelerator_type: The type of accelerator to use.

          active_model_version: The model version that is currently active and applied to running replicas of a
              deployment.

          auto_tune: The performance profile to use for this deployment.

          deployment_shape: The name of the deployment shape that this deployment is using. On the server
              side, this will be replaced with the deployment shape version name.

          deployment_template: The name of the deployment template to use for this deployment. Only available
              to enterprise accounts.

          description: Description of the deployment.

          direct_route_api_keys: The set of API keys used to access the direct route deployment. If direct
              routing is not enabled, this field is unused.

          direct_route_type: If set, this deployment will expose an endpoint that bypasses the Fireworks API
              gateway.

          disable_deployment_size_validation: Whether the deployment size validation is disabled.

          display_name: Human-readable display name of the deployment. e.g. "My Deployment" Must be
              fewer than 64 characters long.

          draft_model: The draft model name for speculative decoding. e.g.
              accounts/fireworks/models/my-draft-model If empty, speculative decoding using a
              draft model is disabled. Default is the base model's default_draft_model. Set
              CreateDeploymentRequest.disable_speculative_decoding to false to disable this
              behavior.

          draft_token_count: The number of candidate tokens to generate per step for speculative decoding.
              Default is the base model's draft_token_count. Set
              CreateDeploymentRequest.disable_speculative_decoding to false to disable this
              behavior.

          enable_addons: If true, PEFT addons are enabled for this deployment.

          enable_hot_load: Whether to use hot load for this deployment.

          enable_hot_reload_latest_addon: Allows up to 1 addon at a time to be loaded, and will merge it into the base
              model.

          enable_mtp: If true, MTP is enabled for this deployment.

          enable_session_affinity: Whether to apply sticky routing based on `user` field. Serverless will be set to
              true when creating deployment.

          expire_time: Deprecated: This field is deprecated and no longer causes auto-deletion. The
              time at which this deployment will automatically be deleted.

          max_context_length: The maximum context length supported by the model (context window). If set to 0
              or not specified, the model's default maximum context length will be used.

          max_replica_count: The maximum number of replicas. If not specified, the default is
              max(min_replica_count, 1). May be set to 0 to downscale the deployment to 0.

          max_with_revocable_replica_count: max_with_revocable_replica_count is max replica count including revocable
              capacity. The max revocable capacity will be max_with_revocable_replica_count -
              max_replica_count.

          min_replica_count: The minimum number of replicas. If not specified, the default is 0.

          ngram_speculation_length: The length of previous input sequence to be considered for N-gram speculation.

          placement: The desired geographic region where the deployment must be placed. If
              unspecified, the default is the GLOBAL multi-region.

          precision: The precision with which the model should be served.

          pricing_plan_id: Optional pricing plan ID for custom billing configuration. If set, this
              deployment will use the pricing plan's billing rules instead of default billing
              behavior.

          target_model_version: The target model version that is being rolled out to the deployment. In a ready
              steady state, the target model version is the same as the active model version.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if account_id is None:
            account_id = self._client._get_account_id_path_param()
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not deployment_id:
            raise ValueError(f"Expected a non-empty value for `deployment_id` but received {deployment_id!r}")
        return self._patch(
            f"/v1/accounts/{account_id}/deployments/{deployment_id}"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/deployments/{deployment_id}",
            body=maybe_transform(
                {
                    "base_model": base_model,
                    "accelerator_count": accelerator_count,
                    "accelerator_type": accelerator_type,
                    "active_model_version": active_model_version,
                    "autoscaling_policy": autoscaling_policy,
                    "auto_tune": auto_tune,
                    "deployment_shape": deployment_shape,
                    "deployment_template": deployment_template,
                    "description": description,
                    "direct_route_api_keys": direct_route_api_keys,
                    "direct_route_type": direct_route_type,
                    "disable_deployment_size_validation": disable_deployment_size_validation,
                    "display_name": display_name,
                    "draft_model": draft_model,
                    "draft_token_count": draft_token_count,
                    "enable_addons": enable_addons,
                    "enable_hot_load": enable_hot_load,
                    "enable_hot_reload_latest_addon": enable_hot_reload_latest_addon,
                    "enable_mtp": enable_mtp,
                    "enable_session_affinity": enable_session_affinity,
                    "expire_time": expire_time,
                    "hot_load_bucket_type": hot_load_bucket_type,
                    "hot_load_bucket_url": hot_load_bucket_url,
                    "max_context_length": max_context_length,
                    "max_replica_count": max_replica_count,
                    "max_with_revocable_replica_count": max_with_revocable_replica_count,
                    "min_replica_count": min_replica_count,
                    "ngram_speculation_length": ngram_speculation_length,
                    "placement": placement,
                    "precision": precision,
                    "pricing_plan_id": pricing_plan_id,
                    "target_model_version": target_model_version,
                },
                deployment_update_params.DeploymentUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"skip_shape_validation": skip_shape_validation}, deployment_update_params.DeploymentUpdateParams
                ),
            ),
            cast_to=Deployment,
        )

    def list(
        self,
        *,
        account_id: str | None = None,
        filter: str | Omit = omit,
        order_by: str | Omit = omit,
        page_size: int | Omit = omit,
        page_token: str | Omit = omit,
        read_mask: str | Omit = omit,
        show_deleted: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SyncCursorDeployments[Deployment]:
        """
        List Deployments

        Args:
          filter: Only deployment satisfying the provided filter (if specified) will be returned.
              See https://google.aip.dev/160 for the filter grammar.

          order_by: A comma-separated list of fields to order by. e.g. "foo,bar" The default sort
              order is ascending. To specify a descending order for a field, append a " desc"
              suffix. e.g. "foo desc,bar" Subfields are specified with a "." character. e.g.
              "foo.bar" If not specified, the default order is by "create_time".

          page_size: The maximum number of deployments to return. The maximum page_size is 200,
              values above 200 will be coerced to 200. If unspecified, the default is 50.

          page_token: A page token, received from a previous ListDeployments call. Provide this to
              retrieve the subsequent page. When paginating, all other parameters provided to
              ListDeployments must match the call that provided the page token.

          read_mask: The fields to be returned in the response. If empty or "\\**", all fields will be
              returned.

          show_deleted: If set, DELETED deployments will be included.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if account_id is None:
            account_id = self._client._get_account_id_path_param()
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._get_api_list(
            f"/v1/accounts/{account_id}/deployments"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/deployments",
            page=SyncCursorDeployments[Deployment],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "filter": filter,
                        "order_by": order_by,
                        "page_size": page_size,
                        "page_token": page_token,
                        "read_mask": read_mask,
                        "show_deleted": show_deleted,
                    },
                    deployment_list_params.DeploymentListParams,
                ),
            ),
            model=Deployment,
        )

    def delete(
        self,
        deployment_id: str,
        *,
        account_id: str | None = None,
        hard: bool | Omit = omit,
        ignore_checks: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Delete Deployment

        Args:
          hard: If true, this will perform a hard deletion.

          ignore_checks: If true, this will ignore checks and force the deletion of a deployment that is
              currently deployed and is in use.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if account_id is None:
            account_id = self._client._get_account_id_path_param()
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not deployment_id:
            raise ValueError(f"Expected a non-empty value for `deployment_id` but received {deployment_id!r}")
        return self._delete(
            f"/v1/accounts/{account_id}/deployments/{deployment_id}"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/deployments/{deployment_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "hard": hard,
                        "ignore_checks": ignore_checks,
                    },
                    deployment_delete_params.DeploymentDeleteParams,
                ),
            ),
            cast_to=object,
        )

    def get(
        self,
        deployment_id: str,
        *,
        account_id: str | None = None,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Deployment:
        """Get Deployment

        Args:
          read_mask: The fields to be returned in the response.

        If empty or "\\**", all fields will be
              returned.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if account_id is None:
            account_id = self._client._get_account_id_path_param()
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not deployment_id:
            raise ValueError(f"Expected a non-empty value for `deployment_id` but received {deployment_id!r}")
        return self._get(
            f"/v1/accounts/{account_id}/deployments/{deployment_id}"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/deployments/{deployment_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"read_mask": read_mask}, deployment_get_params.DeploymentGetParams),
            ),
            cast_to=Deployment,
        )

    def scale(
        self,
        deployment_id: str,
        *,
        account_id: str | None = None,
        replica_count: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Scale Deployment to a specific number of replicas or to zero

        Args:
          replica_count: The desired number of replicas.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if account_id is None:
            account_id = self._client._get_account_id_path_param()
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not deployment_id:
            raise ValueError(f"Expected a non-empty value for `deployment_id` but received {deployment_id!r}")
        return self._patch(
            f"/v1/accounts/{account_id}/deployments/{deployment_id}:scale"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/deployments/{deployment_id}:scale",
            body=maybe_transform({"replica_count": replica_count}, deployment_scale_params.DeploymentScaleParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def undelete(
        self,
        deployment_id: str,
        *,
        account_id: str | None = None,
        body: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Deployment:
        """
        Undelete Deployment

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if account_id is None:
            account_id = self._client._get_account_id_path_param()
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not deployment_id:
            raise ValueError(f"Expected a non-empty value for `deployment_id` but received {deployment_id!r}")
        return self._post(
            f"/v1/accounts/{account_id}/deployments/{deployment_id}:undelete"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/deployments/{deployment_id}:undelete",
            body=maybe_transform(body, deployment_undelete_params.DeploymentUndeleteParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Deployment,
        )


class AsyncDeploymentsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncDeploymentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncDeploymentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDeploymentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#with_streaming_response
        """
        return AsyncDeploymentsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        account_id: str | None = None,
        base_model: str,
        deployment_id: str | Omit = omit,
        disable_auto_deploy: bool | Omit = omit,
        disable_speculative_decoding: bool | Omit = omit,
        skip_image_tag_validation: bool | Omit = omit,
        skip_shape_validation: bool | Omit = omit,
        validate_only: bool | Omit = omit,
        accelerator_count: int | Omit = omit,
        accelerator_type: Literal[
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
        ]
        | Omit = omit,
        active_model_version: str | Omit = omit,
        autoscaling_policy: AutoscalingPolicyParam | Omit = omit,
        auto_tune: AutoTuneParam | Omit = omit,
        deployment_shape: str | Omit = omit,
        deployment_template: str | Omit = omit,
        description: str | Omit = omit,
        direct_route_api_keys: SequenceNotStr[str] | Omit = omit,
        direct_route_type: Literal[
            "DIRECT_ROUTE_TYPE_UNSPECIFIED", "INTERNET", "GCP_PRIVATE_SERVICE_CONNECT", "AWS_PRIVATELINK"
        ]
        | Omit = omit,
        disable_deployment_size_validation: bool | Omit = omit,
        display_name: str | Omit = omit,
        draft_model: str | Omit = omit,
        draft_token_count: int | Omit = omit,
        enable_addons: bool | Omit = omit,
        enable_hot_load: bool | Omit = omit,
        enable_hot_reload_latest_addon: bool | Omit = omit,
        enable_mtp: bool | Omit = omit,
        enable_session_affinity: bool | Omit = omit,
        expire_time: Union[str, datetime] | Omit = omit,
        hot_load_bucket_type: Literal["BUCKET_TYPE_UNSPECIFIED", "MINIO", "S3", "NEBIUS", "FW_HOSTED"] | Omit = omit,
        hot_load_bucket_url: str | Omit = omit,
        max_context_length: int | Omit = omit,
        max_replica_count: int | Omit = omit,
        max_with_revocable_replica_count: int | Omit = omit,
        min_replica_count: int | Omit = omit,
        ngram_speculation_length: int | Omit = omit,
        placement: PlacementParam | Omit = omit,
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
        | Omit = omit,
        pricing_plan_id: str | Omit = omit,
        target_model_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Deployment:
        """Create Deployment

        Args:
          deployment_id: The ID of the deployment.

        If not specified, a random ID will be generated.

          disable_auto_deploy: By default, a deployment created with a currently undeployed base model will be
              deployed to this deployment. If true, this auto-deploy function is disabled.

          disable_speculative_decoding: By default, a deployment will use the speculative decoding settings from the
              base model. If true, this will disable speculative decoding.

          skip_image_tag_validation: If true, skip the image tag policy validation that blocks certain image tags.
              This allows creating deployments with image tags that would otherwise be
              blocked.

          skip_shape_validation: By default, a deployment will ensure the deployment shape provided is validated.
              If true, we will not require the deployment shape to be validated.

          validate_only: If true, this will not create the deployment, but will return the deployment
              that would be created.

          accelerator_count: The number of accelerators used per replica. If not specified, the default is
              the estimated minimum required by the base model.

          accelerator_type: The type of accelerator to use.

          active_model_version: The model version that is currently active and applied to running replicas of a
              deployment.

          auto_tune: The performance profile to use for this deployment.

          deployment_shape: The name of the deployment shape that this deployment is using. On the server
              side, this will be replaced with the deployment shape version name.

          deployment_template: The name of the deployment template to use for this deployment. Only available
              to enterprise accounts.

          description: Description of the deployment.

          direct_route_api_keys: The set of API keys used to access the direct route deployment. If direct
              routing is not enabled, this field is unused.

          direct_route_type: If set, this deployment will expose an endpoint that bypasses the Fireworks API
              gateway.

          disable_deployment_size_validation: Whether the deployment size validation is disabled.

          display_name: Human-readable display name of the deployment. e.g. "My Deployment" Must be
              fewer than 64 characters long.

          draft_model: The draft model name for speculative decoding. e.g.
              accounts/fireworks/models/my-draft-model If empty, speculative decoding using a
              draft model is disabled. Default is the base model's default_draft_model. Set
              CreateDeploymentRequest.disable_speculative_decoding to false to disable this
              behavior.

          draft_token_count: The number of candidate tokens to generate per step for speculative decoding.
              Default is the base model's draft_token_count. Set
              CreateDeploymentRequest.disable_speculative_decoding to false to disable this
              behavior.

          enable_addons: If true, PEFT addons are enabled for this deployment.

          enable_hot_load: Whether to use hot load for this deployment.

          enable_hot_reload_latest_addon: Allows up to 1 addon at a time to be loaded, and will merge it into the base
              model.

          enable_mtp: If true, MTP is enabled for this deployment.

          enable_session_affinity: Whether to apply sticky routing based on `user` field. Serverless will be set to
              true when creating deployment.

          expire_time: Deprecated: This field is deprecated and no longer causes auto-deletion. The
              time at which this deployment will automatically be deleted.

          max_context_length: The maximum context length supported by the model (context window). If set to 0
              or not specified, the model's default maximum context length will be used.

          max_replica_count: The maximum number of replicas. If not specified, the default is
              max(min_replica_count, 1). May be set to 0 to downscale the deployment to 0.

          max_with_revocable_replica_count: max_with_revocable_replica_count is max replica count including revocable
              capacity. The max revocable capacity will be max_with_revocable_replica_count -
              max_replica_count.

          min_replica_count: The minimum number of replicas. If not specified, the default is 0.

          ngram_speculation_length: The length of previous input sequence to be considered for N-gram speculation.

          placement: The desired geographic region where the deployment must be placed. If
              unspecified, the default is the GLOBAL multi-region.

          precision: The precision with which the model should be served.

          pricing_plan_id: Optional pricing plan ID for custom billing configuration. If set, this
              deployment will use the pricing plan's billing rules instead of default billing
              behavior.

          target_model_version: The target model version that is being rolled out to the deployment. In a ready
              steady state, the target model version is the same as the active model version.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if account_id is None:
            account_id = self._client._get_account_id_path_param()
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._post(
            f"/v1/accounts/{account_id}/deployments"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/deployments",
            body=await async_maybe_transform(
                {
                    "base_model": base_model,
                    "accelerator_count": accelerator_count,
                    "accelerator_type": accelerator_type,
                    "active_model_version": active_model_version,
                    "autoscaling_policy": autoscaling_policy,
                    "auto_tune": auto_tune,
                    "deployment_shape": deployment_shape,
                    "deployment_template": deployment_template,
                    "description": description,
                    "direct_route_api_keys": direct_route_api_keys,
                    "direct_route_type": direct_route_type,
                    "disable_deployment_size_validation": disable_deployment_size_validation,
                    "display_name": display_name,
                    "draft_model": draft_model,
                    "draft_token_count": draft_token_count,
                    "enable_addons": enable_addons,
                    "enable_hot_load": enable_hot_load,
                    "enable_hot_reload_latest_addon": enable_hot_reload_latest_addon,
                    "enable_mtp": enable_mtp,
                    "enable_session_affinity": enable_session_affinity,
                    "expire_time": expire_time,
                    "hot_load_bucket_type": hot_load_bucket_type,
                    "hot_load_bucket_url": hot_load_bucket_url,
                    "max_context_length": max_context_length,
                    "max_replica_count": max_replica_count,
                    "max_with_revocable_replica_count": max_with_revocable_replica_count,
                    "min_replica_count": min_replica_count,
                    "ngram_speculation_length": ngram_speculation_length,
                    "placement": placement,
                    "precision": precision,
                    "pricing_plan_id": pricing_plan_id,
                    "target_model_version": target_model_version,
                },
                deployment_create_params.DeploymentCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "deployment_id": deployment_id,
                        "disable_auto_deploy": disable_auto_deploy,
                        "disable_speculative_decoding": disable_speculative_decoding,
                        "skip_image_tag_validation": skip_image_tag_validation,
                        "skip_shape_validation": skip_shape_validation,
                        "validate_only": validate_only,
                    },
                    deployment_create_params.DeploymentCreateParams,
                ),
            ),
            cast_to=Deployment,
        )

    async def update(
        self,
        deployment_id: str,
        *,
        account_id: str | None = None,
        base_model: str,
        skip_shape_validation: bool | Omit = omit,
        accelerator_count: int | Omit = omit,
        accelerator_type: Literal[
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
        ]
        | Omit = omit,
        active_model_version: str | Omit = omit,
        autoscaling_policy: AutoscalingPolicyParam | Omit = omit,
        auto_tune: AutoTuneParam | Omit = omit,
        deployment_shape: str | Omit = omit,
        deployment_template: str | Omit = omit,
        description: str | Omit = omit,
        direct_route_api_keys: SequenceNotStr[str] | Omit = omit,
        direct_route_type: Literal[
            "DIRECT_ROUTE_TYPE_UNSPECIFIED", "INTERNET", "GCP_PRIVATE_SERVICE_CONNECT", "AWS_PRIVATELINK"
        ]
        | Omit = omit,
        disable_deployment_size_validation: bool | Omit = omit,
        display_name: str | Omit = omit,
        draft_model: str | Omit = omit,
        draft_token_count: int | Omit = omit,
        enable_addons: bool | Omit = omit,
        enable_hot_load: bool | Omit = omit,
        enable_hot_reload_latest_addon: bool | Omit = omit,
        enable_mtp: bool | Omit = omit,
        enable_session_affinity: bool | Omit = omit,
        expire_time: Union[str, datetime] | Omit = omit,
        hot_load_bucket_type: Literal["BUCKET_TYPE_UNSPECIFIED", "MINIO", "S3", "NEBIUS", "FW_HOSTED"] | Omit = omit,
        hot_load_bucket_url: str | Omit = omit,
        max_context_length: int | Omit = omit,
        max_replica_count: int | Omit = omit,
        max_with_revocable_replica_count: int | Omit = omit,
        min_replica_count: int | Omit = omit,
        ngram_speculation_length: int | Omit = omit,
        placement: PlacementParam | Omit = omit,
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
        | Omit = omit,
        pricing_plan_id: str | Omit = omit,
        target_model_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Deployment:
        """
        Update Deployment

        Args:
          skip_shape_validation: By default, updating a deployment shape will ensure the new deployment shape
              provided is validated. If true, we will not require the deployment shape to be
              validated.

          accelerator_count: The number of accelerators used per replica. If not specified, the default is
              the estimated minimum required by the base model.

          accelerator_type: The type of accelerator to use.

          active_model_version: The model version that is currently active and applied to running replicas of a
              deployment.

          auto_tune: The performance profile to use for this deployment.

          deployment_shape: The name of the deployment shape that this deployment is using. On the server
              side, this will be replaced with the deployment shape version name.

          deployment_template: The name of the deployment template to use for this deployment. Only available
              to enterprise accounts.

          description: Description of the deployment.

          direct_route_api_keys: The set of API keys used to access the direct route deployment. If direct
              routing is not enabled, this field is unused.

          direct_route_type: If set, this deployment will expose an endpoint that bypasses the Fireworks API
              gateway.

          disable_deployment_size_validation: Whether the deployment size validation is disabled.

          display_name: Human-readable display name of the deployment. e.g. "My Deployment" Must be
              fewer than 64 characters long.

          draft_model: The draft model name for speculative decoding. e.g.
              accounts/fireworks/models/my-draft-model If empty, speculative decoding using a
              draft model is disabled. Default is the base model's default_draft_model. Set
              CreateDeploymentRequest.disable_speculative_decoding to false to disable this
              behavior.

          draft_token_count: The number of candidate tokens to generate per step for speculative decoding.
              Default is the base model's draft_token_count. Set
              CreateDeploymentRequest.disable_speculative_decoding to false to disable this
              behavior.

          enable_addons: If true, PEFT addons are enabled for this deployment.

          enable_hot_load: Whether to use hot load for this deployment.

          enable_hot_reload_latest_addon: Allows up to 1 addon at a time to be loaded, and will merge it into the base
              model.

          enable_mtp: If true, MTP is enabled for this deployment.

          enable_session_affinity: Whether to apply sticky routing based on `user` field. Serverless will be set to
              true when creating deployment.

          expire_time: Deprecated: This field is deprecated and no longer causes auto-deletion. The
              time at which this deployment will automatically be deleted.

          max_context_length: The maximum context length supported by the model (context window). If set to 0
              or not specified, the model's default maximum context length will be used.

          max_replica_count: The maximum number of replicas. If not specified, the default is
              max(min_replica_count, 1). May be set to 0 to downscale the deployment to 0.

          max_with_revocable_replica_count: max_with_revocable_replica_count is max replica count including revocable
              capacity. The max revocable capacity will be max_with_revocable_replica_count -
              max_replica_count.

          min_replica_count: The minimum number of replicas. If not specified, the default is 0.

          ngram_speculation_length: The length of previous input sequence to be considered for N-gram speculation.

          placement: The desired geographic region where the deployment must be placed. If
              unspecified, the default is the GLOBAL multi-region.

          precision: The precision with which the model should be served.

          pricing_plan_id: Optional pricing plan ID for custom billing configuration. If set, this
              deployment will use the pricing plan's billing rules instead of default billing
              behavior.

          target_model_version: The target model version that is being rolled out to the deployment. In a ready
              steady state, the target model version is the same as the active model version.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if account_id is None:
            account_id = self._client._get_account_id_path_param()
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not deployment_id:
            raise ValueError(f"Expected a non-empty value for `deployment_id` but received {deployment_id!r}")
        return await self._patch(
            f"/v1/accounts/{account_id}/deployments/{deployment_id}"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/deployments/{deployment_id}",
            body=await async_maybe_transform(
                {
                    "base_model": base_model,
                    "accelerator_count": accelerator_count,
                    "accelerator_type": accelerator_type,
                    "active_model_version": active_model_version,
                    "autoscaling_policy": autoscaling_policy,
                    "auto_tune": auto_tune,
                    "deployment_shape": deployment_shape,
                    "deployment_template": deployment_template,
                    "description": description,
                    "direct_route_api_keys": direct_route_api_keys,
                    "direct_route_type": direct_route_type,
                    "disable_deployment_size_validation": disable_deployment_size_validation,
                    "display_name": display_name,
                    "draft_model": draft_model,
                    "draft_token_count": draft_token_count,
                    "enable_addons": enable_addons,
                    "enable_hot_load": enable_hot_load,
                    "enable_hot_reload_latest_addon": enable_hot_reload_latest_addon,
                    "enable_mtp": enable_mtp,
                    "enable_session_affinity": enable_session_affinity,
                    "expire_time": expire_time,
                    "hot_load_bucket_type": hot_load_bucket_type,
                    "hot_load_bucket_url": hot_load_bucket_url,
                    "max_context_length": max_context_length,
                    "max_replica_count": max_replica_count,
                    "max_with_revocable_replica_count": max_with_revocable_replica_count,
                    "min_replica_count": min_replica_count,
                    "ngram_speculation_length": ngram_speculation_length,
                    "placement": placement,
                    "precision": precision,
                    "pricing_plan_id": pricing_plan_id,
                    "target_model_version": target_model_version,
                },
                deployment_update_params.DeploymentUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"skip_shape_validation": skip_shape_validation}, deployment_update_params.DeploymentUpdateParams
                ),
            ),
            cast_to=Deployment,
        )

    def list(
        self,
        *,
        account_id: str | None = None,
        filter: str | Omit = omit,
        order_by: str | Omit = omit,
        page_size: int | Omit = omit,
        page_token: str | Omit = omit,
        read_mask: str | Omit = omit,
        show_deleted: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[Deployment, AsyncCursorDeployments[Deployment]]:
        """
        List Deployments

        Args:
          filter: Only deployment satisfying the provided filter (if specified) will be returned.
              See https://google.aip.dev/160 for the filter grammar.

          order_by: A comma-separated list of fields to order by. e.g. "foo,bar" The default sort
              order is ascending. To specify a descending order for a field, append a " desc"
              suffix. e.g. "foo desc,bar" Subfields are specified with a "." character. e.g.
              "foo.bar" If not specified, the default order is by "create_time".

          page_size: The maximum number of deployments to return. The maximum page_size is 200,
              values above 200 will be coerced to 200. If unspecified, the default is 50.

          page_token: A page token, received from a previous ListDeployments call. Provide this to
              retrieve the subsequent page. When paginating, all other parameters provided to
              ListDeployments must match the call that provided the page token.

          read_mask: The fields to be returned in the response. If empty or "\\**", all fields will be
              returned.

          show_deleted: If set, DELETED deployments will be included.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if account_id is None:
            account_id = self._client._get_account_id_path_param()
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._get_api_list(
            f"/v1/accounts/{account_id}/deployments"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/deployments",
            page=AsyncCursorDeployments[Deployment],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "filter": filter,
                        "order_by": order_by,
                        "page_size": page_size,
                        "page_token": page_token,
                        "read_mask": read_mask,
                        "show_deleted": show_deleted,
                    },
                    deployment_list_params.DeploymentListParams,
                ),
            ),
            model=Deployment,
        )

    async def delete(
        self,
        deployment_id: str,
        *,
        account_id: str | None = None,
        hard: bool | Omit = omit,
        ignore_checks: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Delete Deployment

        Args:
          hard: If true, this will perform a hard deletion.

          ignore_checks: If true, this will ignore checks and force the deletion of a deployment that is
              currently deployed and is in use.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if account_id is None:
            account_id = self._client._get_account_id_path_param()
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not deployment_id:
            raise ValueError(f"Expected a non-empty value for `deployment_id` but received {deployment_id!r}")
        return await self._delete(
            f"/v1/accounts/{account_id}/deployments/{deployment_id}"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/deployments/{deployment_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "hard": hard,
                        "ignore_checks": ignore_checks,
                    },
                    deployment_delete_params.DeploymentDeleteParams,
                ),
            ),
            cast_to=object,
        )

    async def get(
        self,
        deployment_id: str,
        *,
        account_id: str | None = None,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Deployment:
        """Get Deployment

        Args:
          read_mask: The fields to be returned in the response.

        If empty or "\\**", all fields will be
              returned.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if account_id is None:
            account_id = self._client._get_account_id_path_param()
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not deployment_id:
            raise ValueError(f"Expected a non-empty value for `deployment_id` but received {deployment_id!r}")
        return await self._get(
            f"/v1/accounts/{account_id}/deployments/{deployment_id}"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/deployments/{deployment_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"read_mask": read_mask}, deployment_get_params.DeploymentGetParams),
            ),
            cast_to=Deployment,
        )

    async def scale(
        self,
        deployment_id: str,
        *,
        account_id: str | None = None,
        replica_count: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Scale Deployment to a specific number of replicas or to zero

        Args:
          replica_count: The desired number of replicas.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if account_id is None:
            account_id = self._client._get_account_id_path_param()
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not deployment_id:
            raise ValueError(f"Expected a non-empty value for `deployment_id` but received {deployment_id!r}")
        return await self._patch(
            f"/v1/accounts/{account_id}/deployments/{deployment_id}:scale"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/deployments/{deployment_id}:scale",
            body=await async_maybe_transform(
                {"replica_count": replica_count}, deployment_scale_params.DeploymentScaleParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def undelete(
        self,
        deployment_id: str,
        *,
        account_id: str | None = None,
        body: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Deployment:
        """
        Undelete Deployment

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if account_id is None:
            account_id = self._client._get_account_id_path_param()
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not deployment_id:
            raise ValueError(f"Expected a non-empty value for `deployment_id` but received {deployment_id!r}")
        return await self._post(
            f"/v1/accounts/{account_id}/deployments/{deployment_id}:undelete"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/deployments/{deployment_id}:undelete",
            body=await async_maybe_transform(body, deployment_undelete_params.DeploymentUndeleteParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Deployment,
        )


class DeploymentsResourceWithRawResponse:
    def __init__(self, deployments: DeploymentsResource) -> None:
        self._deployments = deployments

        self.create = to_raw_response_wrapper(
            deployments.create,
        )
        self.update = to_raw_response_wrapper(
            deployments.update,
        )
        self.list = to_raw_response_wrapper(
            deployments.list,
        )
        self.delete = to_raw_response_wrapper(
            deployments.delete,
        )
        self.get = to_raw_response_wrapper(
            deployments.get,
        )
        self.scale = to_raw_response_wrapper(
            deployments.scale,
        )
        self.undelete = to_raw_response_wrapper(
            deployments.undelete,
        )


class AsyncDeploymentsResourceWithRawResponse:
    def __init__(self, deployments: AsyncDeploymentsResource) -> None:
        self._deployments = deployments

        self.create = async_to_raw_response_wrapper(
            deployments.create,
        )
        self.update = async_to_raw_response_wrapper(
            deployments.update,
        )
        self.list = async_to_raw_response_wrapper(
            deployments.list,
        )
        self.delete = async_to_raw_response_wrapper(
            deployments.delete,
        )
        self.get = async_to_raw_response_wrapper(
            deployments.get,
        )
        self.scale = async_to_raw_response_wrapper(
            deployments.scale,
        )
        self.undelete = async_to_raw_response_wrapper(
            deployments.undelete,
        )


class DeploymentsResourceWithStreamingResponse:
    def __init__(self, deployments: DeploymentsResource) -> None:
        self._deployments = deployments

        self.create = to_streamed_response_wrapper(
            deployments.create,
        )
        self.update = to_streamed_response_wrapper(
            deployments.update,
        )
        self.list = to_streamed_response_wrapper(
            deployments.list,
        )
        self.delete = to_streamed_response_wrapper(
            deployments.delete,
        )
        self.get = to_streamed_response_wrapper(
            deployments.get,
        )
        self.scale = to_streamed_response_wrapper(
            deployments.scale,
        )
        self.undelete = to_streamed_response_wrapper(
            deployments.undelete,
        )


class AsyncDeploymentsResourceWithStreamingResponse:
    def __init__(self, deployments: AsyncDeploymentsResource) -> None:
        self._deployments = deployments

        self.create = async_to_streamed_response_wrapper(
            deployments.create,
        )
        self.update = async_to_streamed_response_wrapper(
            deployments.update,
        )
        self.list = async_to_streamed_response_wrapper(
            deployments.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            deployments.delete,
        )
        self.get = async_to_streamed_response_wrapper(
            deployments.get,
        )
        self.scale = async_to_streamed_response_wrapper(
            deployments.scale,
        )
        self.undelete = async_to_streamed_response_wrapper(
            deployments.undelete,
        )
