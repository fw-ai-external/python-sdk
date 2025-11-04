# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .versions import (
    VersionsResource,
    AsyncVersionsResource,
    VersionsResourceWithRawResponse,
    AsyncVersionsResourceWithRawResponse,
    VersionsResourceWithStreamingResponse,
    AsyncVersionsResourceWithStreamingResponse,
)
from ...._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.accounts import (
    DeploymentPrecision,
    GatewayAcceleratorType,
    DeploymentShapePresetType,
    deployment_shape_list_params,
    deployment_shape_create_params,
    deployment_shape_update_params,
    deployment_shape_retrieve_params,
)
from ....types.accounts.deployment_precision import DeploymentPrecision
from ....types.accounts.gateway_accelerator_type import GatewayAcceleratorType
from ....types.accounts.gateway_deployment_shape import GatewayDeploymentShape
from ....types.accounts.deployment_shape_preset_type import DeploymentShapePresetType
from ....types.accounts.deployment_shape_list_response import DeploymentShapeListResponse

__all__ = ["DeploymentShapesResource", "AsyncDeploymentShapesResource"]


class DeploymentShapesResource(SyncAPIResource):
    @cached_property
    def versions(self) -> VersionsResource:
        return VersionsResource(self._client)

    @cached_property
    def with_raw_response(self) -> DeploymentShapesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stainless-sdks/fireworks-ai-python#accessing-raw-response-data-eg-headers
        """
        return DeploymentShapesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DeploymentShapesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stainless-sdks/fireworks-ai-python#with_streaming_response
        """
        return DeploymentShapesResourceWithStreamingResponse(self)

    def create(
        self,
        account_id: str,
        *,
        base_model: str,
        deployment_shape_id: str | Omit = omit,
        disable_size_validation: bool | Omit = omit,
        accelerator_count: int | Omit = omit,
        accelerator_type: GatewayAcceleratorType | Omit = omit,
        description: str | Omit = omit,
        display_name: str | Omit = omit,
        draft_model: str | Omit = omit,
        draft_token_count: int | Omit = omit,
        enable_addons: bool | Omit = omit,
        enable_session_affinity: bool | Omit = omit,
        ngram_speculation_length: int | Omit = omit,
        precision: DeploymentPrecision | Omit = omit,
        preset_type: DeploymentShapePresetType | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayDeploymentShape:
        """CRUD APIs for deployment shape.

        Create Deployment Shape

        Args:
          deployment_shape_id: The ID of the deployment shape. If not specified, a random ID will be generated.

          disable_size_validation: Whether to disable the size validation for the deployment shape.

          accelerator_count: The number of accelerators used per replica. If not specified, the default is
              the estimated minimum required by the base model.

          accelerator_type: The type of accelerator to use. If not specified, the default is
              NVIDIA_A100_80GB.

          description: The description of the deployment shape. Must be fewer than 1000 characters
              long.

          display_name: Human-readable display name of the deployment shape. e.g. "My Deployment Shape"
              Must be fewer than 64 characters long.

          draft_model: The draft model name for speculative decoding. e.g.
              accounts/fireworks/models/my-draft-model If empty, speculative decoding using a
              draft model is disabled. Default is the base model's default_draft_model. this
              behavior.

          draft_token_count: The number of candidate tokens to generate per step for speculative decoding.
              Default is the base model's draft_token_count.

          enable_addons: If true, LORA addons are enabled for deployments created from this shape.

          enable_session_affinity: Whether to apply sticky routing based on `user` field.

          ngram_speculation_length: The length of previous input sequence to be considered for N-gram speculation.

          precision: The precision with which the model should be served.

          preset_type: Type of deployment shape for different deployment configurations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._post(
            f"/v1/accounts/{account_id}/deploymentShapes",
            body=maybe_transform(
                {
                    "base_model": base_model,
                    "accelerator_count": accelerator_count,
                    "accelerator_type": accelerator_type,
                    "description": description,
                    "display_name": display_name,
                    "draft_model": draft_model,
                    "draft_token_count": draft_token_count,
                    "enable_addons": enable_addons,
                    "enable_session_affinity": enable_session_affinity,
                    "ngram_speculation_length": ngram_speculation_length,
                    "precision": precision,
                    "preset_type": preset_type,
                },
                deployment_shape_create_params.DeploymentShapeCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "deployment_shape_id": deployment_shape_id,
                        "disable_size_validation": disable_size_validation,
                    },
                    deployment_shape_create_params.DeploymentShapeCreateParams,
                ),
            ),
            cast_to=GatewayDeploymentShape,
        )

    def retrieve(
        self,
        deployment_shape_id: str,
        *,
        account_id: str,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayDeploymentShape:
        """
        Get Deployment Shape

        Args:
          read_mask: The fields to be returned in the response. If empty or "\\**", all fields will be
              returned.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not deployment_shape_id:
            raise ValueError(
                f"Expected a non-empty value for `deployment_shape_id` but received {deployment_shape_id!r}"
            )
        return self._get(
            f"/v1/accounts/{account_id}/deploymentShapes/{deployment_shape_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"read_mask": read_mask}, deployment_shape_retrieve_params.DeploymentShapeRetrieveParams
                ),
            ),
            cast_to=GatewayDeploymentShape,
        )

    def update(
        self,
        deployment_shape_id: str,
        *,
        account_id: str,
        base_model: str,
        disable_size_validation: bool | Omit = omit,
        from_latest_validated: bool | Omit = omit,
        accelerator_count: int | Omit = omit,
        accelerator_type: GatewayAcceleratorType | Omit = omit,
        description: str | Omit = omit,
        display_name: str | Omit = omit,
        draft_model: str | Omit = omit,
        draft_token_count: int | Omit = omit,
        enable_addons: bool | Omit = omit,
        enable_session_affinity: bool | Omit = omit,
        ngram_speculation_length: int | Omit = omit,
        precision: DeploymentPrecision | Omit = omit,
        preset_type: DeploymentShapePresetType | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayDeploymentShape:
        """
        Update Deployment Shape

        Args:
          disable_size_validation: Whether to disable the size validation for the deployment shape.

          from_latest_validated: When true, the update will use the latest validated version snapshot as the base
              for fields not present in the update mask; otherwise, the current shape is used.

          accelerator_count: The number of accelerators used per replica. If not specified, the default is
              the estimated minimum required by the base model.

          accelerator_type: The type of accelerator to use. If not specified, the default is
              NVIDIA_A100_80GB.

          description: The description of the deployment shape. Must be fewer than 1000 characters
              long.

          display_name: Human-readable display name of the deployment shape. e.g. "My Deployment Shape"
              Must be fewer than 64 characters long.

          draft_model: The draft model name for speculative decoding. e.g.
              accounts/fireworks/models/my-draft-model If empty, speculative decoding using a
              draft model is disabled. Default is the base model's default_draft_model. this
              behavior.

          draft_token_count: The number of candidate tokens to generate per step for speculative decoding.
              Default is the base model's draft_token_count.

          enable_addons: If true, LORA addons are enabled for deployments created from this shape.

          enable_session_affinity: Whether to apply sticky routing based on `user` field.

          ngram_speculation_length: The length of previous input sequence to be considered for N-gram speculation.

          precision: The precision with which the model should be served.

          preset_type: Type of deployment shape for different deployment configurations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not deployment_shape_id:
            raise ValueError(
                f"Expected a non-empty value for `deployment_shape_id` but received {deployment_shape_id!r}"
            )
        return self._patch(
            f"/v1/accounts/{account_id}/deploymentShapes/{deployment_shape_id}",
            body=maybe_transform(
                {
                    "base_model": base_model,
                    "accelerator_count": accelerator_count,
                    "accelerator_type": accelerator_type,
                    "description": description,
                    "display_name": display_name,
                    "draft_model": draft_model,
                    "draft_token_count": draft_token_count,
                    "enable_addons": enable_addons,
                    "enable_session_affinity": enable_session_affinity,
                    "ngram_speculation_length": ngram_speculation_length,
                    "precision": precision,
                    "preset_type": preset_type,
                },
                deployment_shape_update_params.DeploymentShapeUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "disable_size_validation": disable_size_validation,
                        "from_latest_validated": from_latest_validated,
                    },
                    deployment_shape_update_params.DeploymentShapeUpdateParams,
                ),
            ),
            cast_to=GatewayDeploymentShape,
        )

    def list(
        self,
        account_id: str,
        *,
        filter: str | Omit = omit,
        order_by: str | Omit = omit,
        page_size: int | Omit = omit,
        page_token: str | Omit = omit,
        read_mask: str | Omit = omit,
        target_model: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DeploymentShapeListResponse:
        """
        List Deployment Shapes

        Args:
          filter: Only deployment satisfying the provided filter (if specified) will be returned.
              See https://google.aip.dev/160 for the filter grammar.

          order_by: A comma-separated list of fields to order by. e.g. "foo,bar" The default sort
              order is ascending. To specify a descending order for a field, append a " desc"
              suffix. e.g. "foo desc,bar" Subfields are specified with a "." character. e.g.
              "foo.bar" If not specified, the default order is by "create_time".

          page_size: The maximum number of deployments to return. The maximum page_size is 200,
              values above 200 will be coerced to 200. If unspecified, the default is 50.

          page_token: A page token, received from a previous ListDeploymentShapes call. Provide this
              to retrieve the subsequent page. When paginating, all other parameters provided
              to ListDeploymentShapes must match the call that provided the page token.

          read_mask: The fields to be returned in the response. If empty or "\\**", all fields will be
              returned.

          target_model: Target model that the returned deployment shapes should be compatible with.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._get(
            f"/v1/accounts/{account_id}/deploymentShapes",
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
                        "target_model": target_model,
                    },
                    deployment_shape_list_params.DeploymentShapeListParams,
                ),
            ),
            cast_to=DeploymentShapeListResponse,
        )

    def delete(
        self,
        deployment_shape_id: str,
        *,
        account_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Delete Deployment Shape

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not deployment_shape_id:
            raise ValueError(
                f"Expected a non-empty value for `deployment_shape_id` but received {deployment_shape_id!r}"
            )
        return self._delete(
            f"/v1/accounts/{account_id}/deploymentShapes/{deployment_shape_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncDeploymentShapesResource(AsyncAPIResource):
    @cached_property
    def versions(self) -> AsyncVersionsResource:
        return AsyncVersionsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncDeploymentShapesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stainless-sdks/fireworks-ai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncDeploymentShapesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDeploymentShapesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stainless-sdks/fireworks-ai-python#with_streaming_response
        """
        return AsyncDeploymentShapesResourceWithStreamingResponse(self)

    async def create(
        self,
        account_id: str,
        *,
        base_model: str,
        deployment_shape_id: str | Omit = omit,
        disable_size_validation: bool | Omit = omit,
        accelerator_count: int | Omit = omit,
        accelerator_type: GatewayAcceleratorType | Omit = omit,
        description: str | Omit = omit,
        display_name: str | Omit = omit,
        draft_model: str | Omit = omit,
        draft_token_count: int | Omit = omit,
        enable_addons: bool | Omit = omit,
        enable_session_affinity: bool | Omit = omit,
        ngram_speculation_length: int | Omit = omit,
        precision: DeploymentPrecision | Omit = omit,
        preset_type: DeploymentShapePresetType | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayDeploymentShape:
        """CRUD APIs for deployment shape.

        Create Deployment Shape

        Args:
          deployment_shape_id: The ID of the deployment shape. If not specified, a random ID will be generated.

          disable_size_validation: Whether to disable the size validation for the deployment shape.

          accelerator_count: The number of accelerators used per replica. If not specified, the default is
              the estimated minimum required by the base model.

          accelerator_type: The type of accelerator to use. If not specified, the default is
              NVIDIA_A100_80GB.

          description: The description of the deployment shape. Must be fewer than 1000 characters
              long.

          display_name: Human-readable display name of the deployment shape. e.g. "My Deployment Shape"
              Must be fewer than 64 characters long.

          draft_model: The draft model name for speculative decoding. e.g.
              accounts/fireworks/models/my-draft-model If empty, speculative decoding using a
              draft model is disabled. Default is the base model's default_draft_model. this
              behavior.

          draft_token_count: The number of candidate tokens to generate per step for speculative decoding.
              Default is the base model's draft_token_count.

          enable_addons: If true, LORA addons are enabled for deployments created from this shape.

          enable_session_affinity: Whether to apply sticky routing based on `user` field.

          ngram_speculation_length: The length of previous input sequence to be considered for N-gram speculation.

          precision: The precision with which the model should be served.

          preset_type: Type of deployment shape for different deployment configurations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._post(
            f"/v1/accounts/{account_id}/deploymentShapes",
            body=await async_maybe_transform(
                {
                    "base_model": base_model,
                    "accelerator_count": accelerator_count,
                    "accelerator_type": accelerator_type,
                    "description": description,
                    "display_name": display_name,
                    "draft_model": draft_model,
                    "draft_token_count": draft_token_count,
                    "enable_addons": enable_addons,
                    "enable_session_affinity": enable_session_affinity,
                    "ngram_speculation_length": ngram_speculation_length,
                    "precision": precision,
                    "preset_type": preset_type,
                },
                deployment_shape_create_params.DeploymentShapeCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "deployment_shape_id": deployment_shape_id,
                        "disable_size_validation": disable_size_validation,
                    },
                    deployment_shape_create_params.DeploymentShapeCreateParams,
                ),
            ),
            cast_to=GatewayDeploymentShape,
        )

    async def retrieve(
        self,
        deployment_shape_id: str,
        *,
        account_id: str,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayDeploymentShape:
        """
        Get Deployment Shape

        Args:
          read_mask: The fields to be returned in the response. If empty or "\\**", all fields will be
              returned.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not deployment_shape_id:
            raise ValueError(
                f"Expected a non-empty value for `deployment_shape_id` but received {deployment_shape_id!r}"
            )
        return await self._get(
            f"/v1/accounts/{account_id}/deploymentShapes/{deployment_shape_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"read_mask": read_mask}, deployment_shape_retrieve_params.DeploymentShapeRetrieveParams
                ),
            ),
            cast_to=GatewayDeploymentShape,
        )

    async def update(
        self,
        deployment_shape_id: str,
        *,
        account_id: str,
        base_model: str,
        disable_size_validation: bool | Omit = omit,
        from_latest_validated: bool | Omit = omit,
        accelerator_count: int | Omit = omit,
        accelerator_type: GatewayAcceleratorType | Omit = omit,
        description: str | Omit = omit,
        display_name: str | Omit = omit,
        draft_model: str | Omit = omit,
        draft_token_count: int | Omit = omit,
        enable_addons: bool | Omit = omit,
        enable_session_affinity: bool | Omit = omit,
        ngram_speculation_length: int | Omit = omit,
        precision: DeploymentPrecision | Omit = omit,
        preset_type: DeploymentShapePresetType | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayDeploymentShape:
        """
        Update Deployment Shape

        Args:
          disable_size_validation: Whether to disable the size validation for the deployment shape.

          from_latest_validated: When true, the update will use the latest validated version snapshot as the base
              for fields not present in the update mask; otherwise, the current shape is used.

          accelerator_count: The number of accelerators used per replica. If not specified, the default is
              the estimated minimum required by the base model.

          accelerator_type: The type of accelerator to use. If not specified, the default is
              NVIDIA_A100_80GB.

          description: The description of the deployment shape. Must be fewer than 1000 characters
              long.

          display_name: Human-readable display name of the deployment shape. e.g. "My Deployment Shape"
              Must be fewer than 64 characters long.

          draft_model: The draft model name for speculative decoding. e.g.
              accounts/fireworks/models/my-draft-model If empty, speculative decoding using a
              draft model is disabled. Default is the base model's default_draft_model. this
              behavior.

          draft_token_count: The number of candidate tokens to generate per step for speculative decoding.
              Default is the base model's draft_token_count.

          enable_addons: If true, LORA addons are enabled for deployments created from this shape.

          enable_session_affinity: Whether to apply sticky routing based on `user` field.

          ngram_speculation_length: The length of previous input sequence to be considered for N-gram speculation.

          precision: The precision with which the model should be served.

          preset_type: Type of deployment shape for different deployment configurations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not deployment_shape_id:
            raise ValueError(
                f"Expected a non-empty value for `deployment_shape_id` but received {deployment_shape_id!r}"
            )
        return await self._patch(
            f"/v1/accounts/{account_id}/deploymentShapes/{deployment_shape_id}",
            body=await async_maybe_transform(
                {
                    "base_model": base_model,
                    "accelerator_count": accelerator_count,
                    "accelerator_type": accelerator_type,
                    "description": description,
                    "display_name": display_name,
                    "draft_model": draft_model,
                    "draft_token_count": draft_token_count,
                    "enable_addons": enable_addons,
                    "enable_session_affinity": enable_session_affinity,
                    "ngram_speculation_length": ngram_speculation_length,
                    "precision": precision,
                    "preset_type": preset_type,
                },
                deployment_shape_update_params.DeploymentShapeUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "disable_size_validation": disable_size_validation,
                        "from_latest_validated": from_latest_validated,
                    },
                    deployment_shape_update_params.DeploymentShapeUpdateParams,
                ),
            ),
            cast_to=GatewayDeploymentShape,
        )

    async def list(
        self,
        account_id: str,
        *,
        filter: str | Omit = omit,
        order_by: str | Omit = omit,
        page_size: int | Omit = omit,
        page_token: str | Omit = omit,
        read_mask: str | Omit = omit,
        target_model: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DeploymentShapeListResponse:
        """
        List Deployment Shapes

        Args:
          filter: Only deployment satisfying the provided filter (if specified) will be returned.
              See https://google.aip.dev/160 for the filter grammar.

          order_by: A comma-separated list of fields to order by. e.g. "foo,bar" The default sort
              order is ascending. To specify a descending order for a field, append a " desc"
              suffix. e.g. "foo desc,bar" Subfields are specified with a "." character. e.g.
              "foo.bar" If not specified, the default order is by "create_time".

          page_size: The maximum number of deployments to return. The maximum page_size is 200,
              values above 200 will be coerced to 200. If unspecified, the default is 50.

          page_token: A page token, received from a previous ListDeploymentShapes call. Provide this
              to retrieve the subsequent page. When paginating, all other parameters provided
              to ListDeploymentShapes must match the call that provided the page token.

          read_mask: The fields to be returned in the response. If empty or "\\**", all fields will be
              returned.

          target_model: Target model that the returned deployment shapes should be compatible with.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._get(
            f"/v1/accounts/{account_id}/deploymentShapes",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "filter": filter,
                        "order_by": order_by,
                        "page_size": page_size,
                        "page_token": page_token,
                        "read_mask": read_mask,
                        "target_model": target_model,
                    },
                    deployment_shape_list_params.DeploymentShapeListParams,
                ),
            ),
            cast_to=DeploymentShapeListResponse,
        )

    async def delete(
        self,
        deployment_shape_id: str,
        *,
        account_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Delete Deployment Shape

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not deployment_shape_id:
            raise ValueError(
                f"Expected a non-empty value for `deployment_shape_id` but received {deployment_shape_id!r}"
            )
        return await self._delete(
            f"/v1/accounts/{account_id}/deploymentShapes/{deployment_shape_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class DeploymentShapesResourceWithRawResponse:
    def __init__(self, deployment_shapes: DeploymentShapesResource) -> None:
        self._deployment_shapes = deployment_shapes

        self.create = to_raw_response_wrapper(
            deployment_shapes.create,
        )
        self.retrieve = to_raw_response_wrapper(
            deployment_shapes.retrieve,
        )
        self.update = to_raw_response_wrapper(
            deployment_shapes.update,
        )
        self.list = to_raw_response_wrapper(
            deployment_shapes.list,
        )
        self.delete = to_raw_response_wrapper(
            deployment_shapes.delete,
        )

    @cached_property
    def versions(self) -> VersionsResourceWithRawResponse:
        return VersionsResourceWithRawResponse(self._deployment_shapes.versions)


class AsyncDeploymentShapesResourceWithRawResponse:
    def __init__(self, deployment_shapes: AsyncDeploymentShapesResource) -> None:
        self._deployment_shapes = deployment_shapes

        self.create = async_to_raw_response_wrapper(
            deployment_shapes.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            deployment_shapes.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            deployment_shapes.update,
        )
        self.list = async_to_raw_response_wrapper(
            deployment_shapes.list,
        )
        self.delete = async_to_raw_response_wrapper(
            deployment_shapes.delete,
        )

    @cached_property
    def versions(self) -> AsyncVersionsResourceWithRawResponse:
        return AsyncVersionsResourceWithRawResponse(self._deployment_shapes.versions)


class DeploymentShapesResourceWithStreamingResponse:
    def __init__(self, deployment_shapes: DeploymentShapesResource) -> None:
        self._deployment_shapes = deployment_shapes

        self.create = to_streamed_response_wrapper(
            deployment_shapes.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            deployment_shapes.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            deployment_shapes.update,
        )
        self.list = to_streamed_response_wrapper(
            deployment_shapes.list,
        )
        self.delete = to_streamed_response_wrapper(
            deployment_shapes.delete,
        )

    @cached_property
    def versions(self) -> VersionsResourceWithStreamingResponse:
        return VersionsResourceWithStreamingResponse(self._deployment_shapes.versions)


class AsyncDeploymentShapesResourceWithStreamingResponse:
    def __init__(self, deployment_shapes: AsyncDeploymentShapesResource) -> None:
        self._deployment_shapes = deployment_shapes

        self.create = async_to_streamed_response_wrapper(
            deployment_shapes.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            deployment_shapes.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            deployment_shapes.update,
        )
        self.list = async_to_streamed_response_wrapper(
            deployment_shapes.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            deployment_shapes.delete,
        )

    @cached_property
    def versions(self) -> AsyncVersionsResourceWithStreamingResponse:
        return AsyncVersionsResourceWithStreamingResponse(self._deployment_shapes.versions)
