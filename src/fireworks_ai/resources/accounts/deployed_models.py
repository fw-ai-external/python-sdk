# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.accounts import (
    deployed_model_list_params,
    deployed_model_load_params,
    deployed_model_update_params,
    deployed_model_retrieve_params,
)
from ...types.accounts.gateway_deployed_model import GatewayDeployedModel
from ...types.accounts.deployed_model_list_response import DeployedModelListResponse

__all__ = ["DeployedModelsResource", "AsyncDeployedModelsResource"]


class DeployedModelsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> DeployedModelsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stainless-sdks/fireworks-ai-python#accessing-raw-response-data-eg-headers
        """
        return DeployedModelsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DeployedModelsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stainless-sdks/fireworks-ai-python#with_streaming_response
        """
        return DeployedModelsResourceWithStreamingResponse(self)

    def retrieve(
        self,
        deployed_model_id: str,
        *,
        account_id: str,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayDeployedModel:
        """Get LoRA

        Args:
          read_mask: The fields to be returned in the response.

        If empty or "\\**", all fields will be
              returned.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not deployed_model_id:
            raise ValueError(f"Expected a non-empty value for `deployed_model_id` but received {deployed_model_id!r}")
        return self._get(
            f"/v1/accounts/{account_id}/deployedModels/{deployed_model_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"read_mask": read_mask}, deployed_model_retrieve_params.DeployedModelRetrieveParams
                ),
            ),
            cast_to=GatewayDeployedModel,
        )

    def update(
        self,
        deployed_model_id: str,
        *,
        account_id: str,
        default: bool | Omit = omit,
        deployment: str | Omit = omit,
        description: str | Omit = omit,
        display_name: str | Omit = omit,
        model: str | Omit = omit,
        public: bool | Omit = omit,
        serverless: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayDeployedModel:
        """
        Update LoRA

        Args:
          default: If true, this is the default target when querying this model without the
              `#<deployment>` suffix. The first deployment a model is deployed to will have
              this field set to true.

          deployment: The resource name of the base deployment the model is deployed to.

          description: Description of the resource.

          public: If true, the deployed model will be publicly reachable.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not deployed_model_id:
            raise ValueError(f"Expected a non-empty value for `deployed_model_id` but received {deployed_model_id!r}")
        return self._patch(
            f"/v1/accounts/{account_id}/deployedModels/{deployed_model_id}",
            body=maybe_transform(
                {
                    "default": default,
                    "deployment": deployment,
                    "description": description,
                    "display_name": display_name,
                    "model": model,
                    "public": public,
                    "serverless": serverless,
                },
                deployed_model_update_params.DeployedModelUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GatewayDeployedModel,
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
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DeployedModelListResponse:
        """
        List LoRAs

        Args:
          filter: Only depoyed models satisfying the provided filter (if specified) will be
              returned. See https://google.aip.dev/160 for the filter grammar.

          order_by: A comma-separated list of fields to order by. e.g. "foo,bar" The default sort
              order is ascending. To specify a descending order for a field, append a " desc"
              suffix. e.g. "foo desc,bar" Subfields are specified with a "." character. e.g.
              "foo.bar" If not specified, the default order is by "name".

          page_size: The maximum number of deployed models to return. The maximum page_size is 200,
              values above 200 will be coerced to 200. If unspecified, the default is 50.

          page_token: A page token, received from a previous ListDeployedModels call. Provide this to
              retrieve the subsequent page. When paginating, all other parameters provided to
              ListDeployedModels must match the call that provided the page token.

          read_mask: The fields to be returned in the response. If empty or "\\**", all fields will be
              returned.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._get(
            f"/v1/accounts/{account_id}/deployedModels",
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
                    },
                    deployed_model_list_params.DeployedModelListParams,
                ),
            ),
            cast_to=DeployedModelListResponse,
        )

    def load(
        self,
        account_id: str,
        *,
        replace_merged_addon: bool | Omit = omit,
        default: bool | Omit = omit,
        deployment: str | Omit = omit,
        description: str | Omit = omit,
        display_name: str | Omit = omit,
        model: str | Omit = omit,
        public: bool | Omit = omit,
        serverless: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayDeployedModel:
        """
        Load LoRA

        Args:
          replace_merged_addon: Merges new addon to the base model, while unmerging/deleting any existing addon
              in the deployment. Must be specified for hot reload deployments

          default: If true, this is the default target when querying this model without the
              `#<deployment>` suffix. The first deployment a model is deployed to will have
              this field set to true.

          deployment: The resource name of the base deployment the model is deployed to.

          description: Description of the resource.

          public: If true, the deployed model will be publicly reachable.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._post(
            f"/v1/accounts/{account_id}/deployedModels",
            body=maybe_transform(
                {
                    "default": default,
                    "deployment": deployment,
                    "description": description,
                    "display_name": display_name,
                    "model": model,
                    "public": public,
                    "serverless": serverless,
                },
                deployed_model_load_params.DeployedModelLoadParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"replace_merged_addon": replace_merged_addon}, deployed_model_load_params.DeployedModelLoadParams
                ),
            ),
            cast_to=GatewayDeployedModel,
        )

    def unload(
        self,
        deployed_model_id: str,
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
        Unload LoRA

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not deployed_model_id:
            raise ValueError(f"Expected a non-empty value for `deployed_model_id` but received {deployed_model_id!r}")
        return self._delete(
            f"/v1/accounts/{account_id}/deployedModels/{deployed_model_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncDeployedModelsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncDeployedModelsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stainless-sdks/fireworks-ai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncDeployedModelsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDeployedModelsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stainless-sdks/fireworks-ai-python#with_streaming_response
        """
        return AsyncDeployedModelsResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        deployed_model_id: str,
        *,
        account_id: str,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayDeployedModel:
        """Get LoRA

        Args:
          read_mask: The fields to be returned in the response.

        If empty or "\\**", all fields will be
              returned.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not deployed_model_id:
            raise ValueError(f"Expected a non-empty value for `deployed_model_id` but received {deployed_model_id!r}")
        return await self._get(
            f"/v1/accounts/{account_id}/deployedModels/{deployed_model_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"read_mask": read_mask}, deployed_model_retrieve_params.DeployedModelRetrieveParams
                ),
            ),
            cast_to=GatewayDeployedModel,
        )

    async def update(
        self,
        deployed_model_id: str,
        *,
        account_id: str,
        default: bool | Omit = omit,
        deployment: str | Omit = omit,
        description: str | Omit = omit,
        display_name: str | Omit = omit,
        model: str | Omit = omit,
        public: bool | Omit = omit,
        serverless: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayDeployedModel:
        """
        Update LoRA

        Args:
          default: If true, this is the default target when querying this model without the
              `#<deployment>` suffix. The first deployment a model is deployed to will have
              this field set to true.

          deployment: The resource name of the base deployment the model is deployed to.

          description: Description of the resource.

          public: If true, the deployed model will be publicly reachable.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not deployed_model_id:
            raise ValueError(f"Expected a non-empty value for `deployed_model_id` but received {deployed_model_id!r}")
        return await self._patch(
            f"/v1/accounts/{account_id}/deployedModels/{deployed_model_id}",
            body=await async_maybe_transform(
                {
                    "default": default,
                    "deployment": deployment,
                    "description": description,
                    "display_name": display_name,
                    "model": model,
                    "public": public,
                    "serverless": serverless,
                },
                deployed_model_update_params.DeployedModelUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GatewayDeployedModel,
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
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DeployedModelListResponse:
        """
        List LoRAs

        Args:
          filter: Only depoyed models satisfying the provided filter (if specified) will be
              returned. See https://google.aip.dev/160 for the filter grammar.

          order_by: A comma-separated list of fields to order by. e.g. "foo,bar" The default sort
              order is ascending. To specify a descending order for a field, append a " desc"
              suffix. e.g. "foo desc,bar" Subfields are specified with a "." character. e.g.
              "foo.bar" If not specified, the default order is by "name".

          page_size: The maximum number of deployed models to return. The maximum page_size is 200,
              values above 200 will be coerced to 200. If unspecified, the default is 50.

          page_token: A page token, received from a previous ListDeployedModels call. Provide this to
              retrieve the subsequent page. When paginating, all other parameters provided to
              ListDeployedModels must match the call that provided the page token.

          read_mask: The fields to be returned in the response. If empty or "\\**", all fields will be
              returned.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._get(
            f"/v1/accounts/{account_id}/deployedModels",
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
                    },
                    deployed_model_list_params.DeployedModelListParams,
                ),
            ),
            cast_to=DeployedModelListResponse,
        )

    async def load(
        self,
        account_id: str,
        *,
        replace_merged_addon: bool | Omit = omit,
        default: bool | Omit = omit,
        deployment: str | Omit = omit,
        description: str | Omit = omit,
        display_name: str | Omit = omit,
        model: str | Omit = omit,
        public: bool | Omit = omit,
        serverless: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayDeployedModel:
        """
        Load LoRA

        Args:
          replace_merged_addon: Merges new addon to the base model, while unmerging/deleting any existing addon
              in the deployment. Must be specified for hot reload deployments

          default: If true, this is the default target when querying this model without the
              `#<deployment>` suffix. The first deployment a model is deployed to will have
              this field set to true.

          deployment: The resource name of the base deployment the model is deployed to.

          description: Description of the resource.

          public: If true, the deployed model will be publicly reachable.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._post(
            f"/v1/accounts/{account_id}/deployedModels",
            body=await async_maybe_transform(
                {
                    "default": default,
                    "deployment": deployment,
                    "description": description,
                    "display_name": display_name,
                    "model": model,
                    "public": public,
                    "serverless": serverless,
                },
                deployed_model_load_params.DeployedModelLoadParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"replace_merged_addon": replace_merged_addon}, deployed_model_load_params.DeployedModelLoadParams
                ),
            ),
            cast_to=GatewayDeployedModel,
        )

    async def unload(
        self,
        deployed_model_id: str,
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
        Unload LoRA

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not deployed_model_id:
            raise ValueError(f"Expected a non-empty value for `deployed_model_id` but received {deployed_model_id!r}")
        return await self._delete(
            f"/v1/accounts/{account_id}/deployedModels/{deployed_model_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class DeployedModelsResourceWithRawResponse:
    def __init__(self, deployed_models: DeployedModelsResource) -> None:
        self._deployed_models = deployed_models

        self.retrieve = to_raw_response_wrapper(
            deployed_models.retrieve,
        )
        self.update = to_raw_response_wrapper(
            deployed_models.update,
        )
        self.list = to_raw_response_wrapper(
            deployed_models.list,
        )
        self.load = to_raw_response_wrapper(
            deployed_models.load,
        )
        self.unload = to_raw_response_wrapper(
            deployed_models.unload,
        )


class AsyncDeployedModelsResourceWithRawResponse:
    def __init__(self, deployed_models: AsyncDeployedModelsResource) -> None:
        self._deployed_models = deployed_models

        self.retrieve = async_to_raw_response_wrapper(
            deployed_models.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            deployed_models.update,
        )
        self.list = async_to_raw_response_wrapper(
            deployed_models.list,
        )
        self.load = async_to_raw_response_wrapper(
            deployed_models.load,
        )
        self.unload = async_to_raw_response_wrapper(
            deployed_models.unload,
        )


class DeployedModelsResourceWithStreamingResponse:
    def __init__(self, deployed_models: DeployedModelsResource) -> None:
        self._deployed_models = deployed_models

        self.retrieve = to_streamed_response_wrapper(
            deployed_models.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            deployed_models.update,
        )
        self.list = to_streamed_response_wrapper(
            deployed_models.list,
        )
        self.load = to_streamed_response_wrapper(
            deployed_models.load,
        )
        self.unload = to_streamed_response_wrapper(
            deployed_models.unload,
        )


class AsyncDeployedModelsResourceWithStreamingResponse:
    def __init__(self, deployed_models: AsyncDeployedModelsResource) -> None:
        self._deployed_models = deployed_models

        self.retrieve = async_to_streamed_response_wrapper(
            deployed_models.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            deployed_models.update,
        )
        self.list = async_to_streamed_response_wrapper(
            deployed_models.list,
        )
        self.load = async_to_streamed_response_wrapper(
            deployed_models.load,
        )
        self.unload = async_to_streamed_response_wrapper(
            deployed_models.unload,
        )
