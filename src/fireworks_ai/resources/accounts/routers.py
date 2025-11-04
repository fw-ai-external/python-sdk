# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
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
from ...types.accounts import router_list_params, router_create_params, router_update_params, router_retrieve_params
from ...types.accounts.gateway_router import GatewayRouter
from ...types.accounts.router_list_response import RouterListResponse

__all__ = ["RoutersResource", "AsyncRoutersResource"]


class RoutersResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> RoutersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stainless-sdks/fireworks-ai-python#accessing-raw-response-data-eg-headers
        """
        return RoutersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RoutersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stainless-sdks/fireworks-ai-python#with_streaming_response
        """
        return RoutersResourceWithStreamingResponse(self)

    def create(
        self,
        account_id: str,
        *,
        router_id: str | Omit = omit,
        deployments: SequenceNotStr[str] | Omit = omit,
        display_name: str | Omit = omit,
        even_load: object | Omit = omit,
        model: str | Omit = omit,
        weighted_random: object | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayRouter:
        """
        Create Router

        Args:
          router_id: ID of the router.

          deployments: The deployment names to be covered by the router.

          even_load: Dynamically adjust traffic allocation to balance the load per replica across the
              deployments as much as possible.

          model: The model name to route requests to. model is only applicable to single-region
              deployments. For multi-region deployments, model must be empty.

          weighted_random: Use replica count as weight.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._post(
            f"/v1/accounts/{account_id}/routers",
            body=maybe_transform(
                {
                    "deployments": deployments,
                    "display_name": display_name,
                    "even_load": even_load,
                    "model": model,
                    "weighted_random": weighted_random,
                },
                router_create_params.RouterCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"router_id": router_id}, router_create_params.RouterCreateParams),
            ),
            cast_to=GatewayRouter,
        )

    def retrieve(
        self,
        router_id: str,
        *,
        account_id: str,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayRouter:
        """CRUD APIs for routers.

        Get Router

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
        if not router_id:
            raise ValueError(f"Expected a non-empty value for `router_id` but received {router_id!r}")
        return self._get(
            f"/v1/accounts/{account_id}/routers/{router_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"read_mask": read_mask}, router_retrieve_params.RouterRetrieveParams),
            ),
            cast_to=GatewayRouter,
        )

    def update(
        self,
        router_id: str,
        *,
        account_id: str,
        deployments: SequenceNotStr[str] | Omit = omit,
        display_name: str | Omit = omit,
        even_load: object | Omit = omit,
        model: str | Omit = omit,
        weighted_random: object | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayRouter:
        """
        Update Router

        Args:
          deployments: The deployment names to be covered by the router.

          even_load: Dynamically adjust traffic allocation to balance the load per replica across the
              deployments as much as possible.

          model: The model name to route requests to. model is only applicable to single-region
              deployments. For multi-region deployments, model must be empty.

          weighted_random: Use replica count as weight.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not router_id:
            raise ValueError(f"Expected a non-empty value for `router_id` but received {router_id!r}")
        return self._patch(
            f"/v1/accounts/{account_id}/routers/{router_id}",
            body=maybe_transform(
                {
                    "deployments": deployments,
                    "display_name": display_name,
                    "even_load": even_load,
                    "model": model,
                    "weighted_random": weighted_random,
                },
                router_update_params.RouterUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GatewayRouter,
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
    ) -> RouterListResponse:
        """List Routers

        Args:
          filter: Filter criteria for the returned routers.

        See https://google.aip.dev/160 for the
              filter syntax specification.

          order_by: A comma-separated list of fields to order by. e.g. "foo,bar" The default sort
              order is ascending. To specify a descending order for a field, append a " desc"
              suffix. e.g. "foo desc,bar" Subfields are specified with a "." character. e.g.
              "foo.bar" If not specified, the default order is by "name".

          page_size: The maximum number of routers to return. The maximum page_size is 200, values
              above 200 will be coerced to 200. If unspecified, the default is 50.

          page_token: A page token, received from a previous ListRouters call. Provide this to
              retrieve the subsequent page. When paginating, all other parameters provided to
              ListRouters must match the call that provided the page token.

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
            f"/v1/accounts/{account_id}/routers",
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
                    router_list_params.RouterListParams,
                ),
            ),
            cast_to=RouterListResponse,
        )

    def delete(
        self,
        router_id: str,
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
        Delete Router

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not router_id:
            raise ValueError(f"Expected a non-empty value for `router_id` but received {router_id!r}")
        return self._delete(
            f"/v1/accounts/{account_id}/routers/{router_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncRoutersResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncRoutersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stainless-sdks/fireworks-ai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncRoutersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRoutersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stainless-sdks/fireworks-ai-python#with_streaming_response
        """
        return AsyncRoutersResourceWithStreamingResponse(self)

    async def create(
        self,
        account_id: str,
        *,
        router_id: str | Omit = omit,
        deployments: SequenceNotStr[str] | Omit = omit,
        display_name: str | Omit = omit,
        even_load: object | Omit = omit,
        model: str | Omit = omit,
        weighted_random: object | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayRouter:
        """
        Create Router

        Args:
          router_id: ID of the router.

          deployments: The deployment names to be covered by the router.

          even_load: Dynamically adjust traffic allocation to balance the load per replica across the
              deployments as much as possible.

          model: The model name to route requests to. model is only applicable to single-region
              deployments. For multi-region deployments, model must be empty.

          weighted_random: Use replica count as weight.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._post(
            f"/v1/accounts/{account_id}/routers",
            body=await async_maybe_transform(
                {
                    "deployments": deployments,
                    "display_name": display_name,
                    "even_load": even_load,
                    "model": model,
                    "weighted_random": weighted_random,
                },
                router_create_params.RouterCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"router_id": router_id}, router_create_params.RouterCreateParams),
            ),
            cast_to=GatewayRouter,
        )

    async def retrieve(
        self,
        router_id: str,
        *,
        account_id: str,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayRouter:
        """CRUD APIs for routers.

        Get Router

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
        if not router_id:
            raise ValueError(f"Expected a non-empty value for `router_id` but received {router_id!r}")
        return await self._get(
            f"/v1/accounts/{account_id}/routers/{router_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"read_mask": read_mask}, router_retrieve_params.RouterRetrieveParams
                ),
            ),
            cast_to=GatewayRouter,
        )

    async def update(
        self,
        router_id: str,
        *,
        account_id: str,
        deployments: SequenceNotStr[str] | Omit = omit,
        display_name: str | Omit = omit,
        even_load: object | Omit = omit,
        model: str | Omit = omit,
        weighted_random: object | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayRouter:
        """
        Update Router

        Args:
          deployments: The deployment names to be covered by the router.

          even_load: Dynamically adjust traffic allocation to balance the load per replica across the
              deployments as much as possible.

          model: The model name to route requests to. model is only applicable to single-region
              deployments. For multi-region deployments, model must be empty.

          weighted_random: Use replica count as weight.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not router_id:
            raise ValueError(f"Expected a non-empty value for `router_id` but received {router_id!r}")
        return await self._patch(
            f"/v1/accounts/{account_id}/routers/{router_id}",
            body=await async_maybe_transform(
                {
                    "deployments": deployments,
                    "display_name": display_name,
                    "even_load": even_load,
                    "model": model,
                    "weighted_random": weighted_random,
                },
                router_update_params.RouterUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GatewayRouter,
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
    ) -> RouterListResponse:
        """List Routers

        Args:
          filter: Filter criteria for the returned routers.

        See https://google.aip.dev/160 for the
              filter syntax specification.

          order_by: A comma-separated list of fields to order by. e.g. "foo,bar" The default sort
              order is ascending. To specify a descending order for a field, append a " desc"
              suffix. e.g. "foo desc,bar" Subfields are specified with a "." character. e.g.
              "foo.bar" If not specified, the default order is by "name".

          page_size: The maximum number of routers to return. The maximum page_size is 200, values
              above 200 will be coerced to 200. If unspecified, the default is 50.

          page_token: A page token, received from a previous ListRouters call. Provide this to
              retrieve the subsequent page. When paginating, all other parameters provided to
              ListRouters must match the call that provided the page token.

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
            f"/v1/accounts/{account_id}/routers",
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
                    router_list_params.RouterListParams,
                ),
            ),
            cast_to=RouterListResponse,
        )

    async def delete(
        self,
        router_id: str,
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
        Delete Router

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not router_id:
            raise ValueError(f"Expected a non-empty value for `router_id` but received {router_id!r}")
        return await self._delete(
            f"/v1/accounts/{account_id}/routers/{router_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class RoutersResourceWithRawResponse:
    def __init__(self, routers: RoutersResource) -> None:
        self._routers = routers

        self.create = to_raw_response_wrapper(
            routers.create,
        )
        self.retrieve = to_raw_response_wrapper(
            routers.retrieve,
        )
        self.update = to_raw_response_wrapper(
            routers.update,
        )
        self.list = to_raw_response_wrapper(
            routers.list,
        )
        self.delete = to_raw_response_wrapper(
            routers.delete,
        )


class AsyncRoutersResourceWithRawResponse:
    def __init__(self, routers: AsyncRoutersResource) -> None:
        self._routers = routers

        self.create = async_to_raw_response_wrapper(
            routers.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            routers.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            routers.update,
        )
        self.list = async_to_raw_response_wrapper(
            routers.list,
        )
        self.delete = async_to_raw_response_wrapper(
            routers.delete,
        )


class RoutersResourceWithStreamingResponse:
    def __init__(self, routers: RoutersResource) -> None:
        self._routers = routers

        self.create = to_streamed_response_wrapper(
            routers.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            routers.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            routers.update,
        )
        self.list = to_streamed_response_wrapper(
            routers.list,
        )
        self.delete = to_streamed_response_wrapper(
            routers.delete,
        )


class AsyncRoutersResourceWithStreamingResponse:
    def __init__(self, routers: AsyncRoutersResource) -> None:
        self._routers = routers

        self.create = async_to_streamed_response_wrapper(
            routers.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            routers.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            routers.update,
        )
        self.list = async_to_streamed_response_wrapper(
            routers.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            routers.delete,
        )
