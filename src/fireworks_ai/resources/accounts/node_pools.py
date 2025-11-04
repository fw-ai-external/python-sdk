# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict

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
    GatewayNodePool,
    node_pool_update_params,
    node_pool_retrieve_params,
    node_pool_node_pools_params,
    node_pool_retrieve_node_pools_params,
    node_pool_retrieve_node_pool_id_get_stats_params,
)
from ...types.accounts.gateway_node_pool import GatewayNodePool
from ...types.accounts.gateway_node_pool_param import GatewayNodePoolParam
from ...types.accounts.gateway_node_pool_stats import GatewayNodePoolStats
from ...types.accounts.gateway_eks_node_pool_param import GatewayEksNodePoolParam
from ...types.accounts.gateway_fake_node_pool_param import GatewayFakeNodePoolParam
from ...types.accounts.node_pool_retrieve_node_pools_response import NodePoolRetrieveNodePoolsResponse

__all__ = ["NodePoolsResource", "AsyncNodePoolsResource"]


class NodePoolsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> NodePoolsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#accessing-raw-response-data-eg-headers
        """
        return NodePoolsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> NodePoolsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#with_streaming_response
        """
        return NodePoolsResourceWithStreamingResponse(self)

    def retrieve(
        self,
        node_pool_id: str,
        *,
        account_id: str,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayNodePool:
        """Get Node Pool

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
        if not node_pool_id:
            raise ValueError(f"Expected a non-empty value for `node_pool_id` but received {node_pool_id!r}")
        return self._get(
            f"/v1/accounts/{account_id}/nodePools/{node_pool_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"read_mask": read_mask}, node_pool_retrieve_params.NodePoolRetrieveParams),
            ),
            cast_to=GatewayNodePool,
        )

    def update(
        self,
        node_pool_id: str,
        *,
        account_id: str,
        annotations: Dict[str, str] | Omit = omit,
        display_name: str | Omit = omit,
        eks_node_pool: GatewayEksNodePoolParam | Omit = omit,
        fake_node_pool: GatewayFakeNodePoolParam | Omit = omit,
        max_node_count: int | Omit = omit,
        min_node_count: int | Omit = omit,
        overprovision_node_count: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayNodePool:
        """Update Node Pool

        Args:
          annotations: Arbitrary, user-specified metadata.

        Keys and values must adhere to Kubernetes
              constraints:
              https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/#syntax-and-character-set
              Additionally, the "fireworks.ai/" prefix is reserved.

          display_name: Human-readable display name of the node pool. e.g. "My Node Pool" Must be fewer
              than 64 characters long.

          fake_node_pool: A fake node pool to be used with FakeCluster.

          max_node_count: https://cloud.google.com/kubernetes-engine/quotas Maximum number of nodes in
              this node pool. Must be a positive integer greater than or equal to
              min_node_count. If not specified, the default is 1.

          min_node_count: https://cloud.google.com/kubernetes-engine/quotas Minimum number of nodes in
              this node pool. Must be a non-negative integer less than or equal to
              max_node_count. If not specified, the default is 0.

          overprovision_node_count: The number of nodes to overprovision by the autoscaler. Must be a non-negative
              integer and less than or equal to min_node_count and
              max_node_count-min_node_count. If not specified, the default is 0.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not node_pool_id:
            raise ValueError(f"Expected a non-empty value for `node_pool_id` but received {node_pool_id!r}")
        return self._patch(
            f"/v1/accounts/{account_id}/nodePools/{node_pool_id}",
            body=maybe_transform(
                {
                    "annotations": annotations,
                    "display_name": display_name,
                    "eks_node_pool": eks_node_pool,
                    "fake_node_pool": fake_node_pool,
                    "max_node_count": max_node_count,
                    "min_node_count": min_node_count,
                    "overprovision_node_count": overprovision_node_count,
                },
                node_pool_update_params.NodePoolUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GatewayNodePool,
        )

    def delete(
        self,
        node_pool_id: str,
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
        Delete Node Pool

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not node_pool_id:
            raise ValueError(f"Expected a non-empty value for `node_pool_id` but received {node_pool_id!r}")
        return self._delete(
            f"/v1/accounts/{account_id}/nodePools/{node_pool_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def node_pools(
        self,
        account_id: str,
        *,
        node_pool: GatewayNodePoolParam,
        node_pool_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayNodePool:
        """
        Create Node Pool

        Args:
          node_pool: The properties of the NodePool being created.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._post(
            f"/v1/accounts/{account_id}/nodePools",
            body=maybe_transform(
                {
                    "node_pool": node_pool,
                    "node_pool_id": node_pool_id,
                },
                node_pool_node_pools_params.NodePoolNodePoolsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GatewayNodePool,
        )

    def retrieve_node_pool_id_get_stats(
        self,
        node_pool_id: str,
        *,
        account_id: str,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayNodePoolStats:
        """
        Get Node Pool Stats

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
        if not node_pool_id:
            raise ValueError(f"Expected a non-empty value for `node_pool_id` but received {node_pool_id!r}")
        return self._get(
            f"/v1/accounts/{account_id}/nodePools/{node_pool_id}:getStats",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"read_mask": read_mask},
                    node_pool_retrieve_node_pool_id_get_stats_params.NodePoolRetrieveNodePoolIDGetStatsParams,
                ),
            ),
            cast_to=GatewayNodePoolStats,
        )

    def retrieve_node_pools(
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
    ) -> NodePoolRetrieveNodePoolsResponse:
        """
        List Node Pools

        Args:
          filter: Only node pools satisfying the provided filter (if specified) will be returned.
              See https://google.aip.dev/160 for the filter grammar.

          order_by: A comma-separated list of fields to order by. e.g. "foo,bar" The default sort
              order is ascending. To specify a descending order for a field, append a " desc"
              suffix. e.g. "foo desc,bar" Subfields are specified with a "." character. e.g.
              "foo.bar" If not specified, the default order is by "name".

          page_size: The maximum number of node pools to return. The maximum page_size is 200, values
              above 200 will be coerced to 200. If unspecified, the default is 50.

          page_token: A page token, received from a previous ListNodePools call. Provide this to
              retrieve the subsequent page. When paginating, all other parameters provided to
              ListNodePools must match the call that provided the page token.

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
            f"/v1/accounts/{account_id}/nodePools",
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
                    node_pool_retrieve_node_pools_params.NodePoolRetrieveNodePoolsParams,
                ),
            ),
            cast_to=NodePoolRetrieveNodePoolsResponse,
        )


class AsyncNodePoolsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncNodePoolsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncNodePoolsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncNodePoolsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#with_streaming_response
        """
        return AsyncNodePoolsResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        node_pool_id: str,
        *,
        account_id: str,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayNodePool:
        """Get Node Pool

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
        if not node_pool_id:
            raise ValueError(f"Expected a non-empty value for `node_pool_id` but received {node_pool_id!r}")
        return await self._get(
            f"/v1/accounts/{account_id}/nodePools/{node_pool_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"read_mask": read_mask}, node_pool_retrieve_params.NodePoolRetrieveParams
                ),
            ),
            cast_to=GatewayNodePool,
        )

    async def update(
        self,
        node_pool_id: str,
        *,
        account_id: str,
        annotations: Dict[str, str] | Omit = omit,
        display_name: str | Omit = omit,
        eks_node_pool: GatewayEksNodePoolParam | Omit = omit,
        fake_node_pool: GatewayFakeNodePoolParam | Omit = omit,
        max_node_count: int | Omit = omit,
        min_node_count: int | Omit = omit,
        overprovision_node_count: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayNodePool:
        """Update Node Pool

        Args:
          annotations: Arbitrary, user-specified metadata.

        Keys and values must adhere to Kubernetes
              constraints:
              https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/#syntax-and-character-set
              Additionally, the "fireworks.ai/" prefix is reserved.

          display_name: Human-readable display name of the node pool. e.g. "My Node Pool" Must be fewer
              than 64 characters long.

          fake_node_pool: A fake node pool to be used with FakeCluster.

          max_node_count: https://cloud.google.com/kubernetes-engine/quotas Maximum number of nodes in
              this node pool. Must be a positive integer greater than or equal to
              min_node_count. If not specified, the default is 1.

          min_node_count: https://cloud.google.com/kubernetes-engine/quotas Minimum number of nodes in
              this node pool. Must be a non-negative integer less than or equal to
              max_node_count. If not specified, the default is 0.

          overprovision_node_count: The number of nodes to overprovision by the autoscaler. Must be a non-negative
              integer and less than or equal to min_node_count and
              max_node_count-min_node_count. If not specified, the default is 0.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not node_pool_id:
            raise ValueError(f"Expected a non-empty value for `node_pool_id` but received {node_pool_id!r}")
        return await self._patch(
            f"/v1/accounts/{account_id}/nodePools/{node_pool_id}",
            body=await async_maybe_transform(
                {
                    "annotations": annotations,
                    "display_name": display_name,
                    "eks_node_pool": eks_node_pool,
                    "fake_node_pool": fake_node_pool,
                    "max_node_count": max_node_count,
                    "min_node_count": min_node_count,
                    "overprovision_node_count": overprovision_node_count,
                },
                node_pool_update_params.NodePoolUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GatewayNodePool,
        )

    async def delete(
        self,
        node_pool_id: str,
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
        Delete Node Pool

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not node_pool_id:
            raise ValueError(f"Expected a non-empty value for `node_pool_id` but received {node_pool_id!r}")
        return await self._delete(
            f"/v1/accounts/{account_id}/nodePools/{node_pool_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def node_pools(
        self,
        account_id: str,
        *,
        node_pool: GatewayNodePoolParam,
        node_pool_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayNodePool:
        """
        Create Node Pool

        Args:
          node_pool: The properties of the NodePool being created.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._post(
            f"/v1/accounts/{account_id}/nodePools",
            body=await async_maybe_transform(
                {
                    "node_pool": node_pool,
                    "node_pool_id": node_pool_id,
                },
                node_pool_node_pools_params.NodePoolNodePoolsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GatewayNodePool,
        )

    async def retrieve_node_pool_id_get_stats(
        self,
        node_pool_id: str,
        *,
        account_id: str,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayNodePoolStats:
        """
        Get Node Pool Stats

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
        if not node_pool_id:
            raise ValueError(f"Expected a non-empty value for `node_pool_id` but received {node_pool_id!r}")
        return await self._get(
            f"/v1/accounts/{account_id}/nodePools/{node_pool_id}:getStats",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"read_mask": read_mask},
                    node_pool_retrieve_node_pool_id_get_stats_params.NodePoolRetrieveNodePoolIDGetStatsParams,
                ),
            ),
            cast_to=GatewayNodePoolStats,
        )

    async def retrieve_node_pools(
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
    ) -> NodePoolRetrieveNodePoolsResponse:
        """
        List Node Pools

        Args:
          filter: Only node pools satisfying the provided filter (if specified) will be returned.
              See https://google.aip.dev/160 for the filter grammar.

          order_by: A comma-separated list of fields to order by. e.g. "foo,bar" The default sort
              order is ascending. To specify a descending order for a field, append a " desc"
              suffix. e.g. "foo desc,bar" Subfields are specified with a "." character. e.g.
              "foo.bar" If not specified, the default order is by "name".

          page_size: The maximum number of node pools to return. The maximum page_size is 200, values
              above 200 will be coerced to 200. If unspecified, the default is 50.

          page_token: A page token, received from a previous ListNodePools call. Provide this to
              retrieve the subsequent page. When paginating, all other parameters provided to
              ListNodePools must match the call that provided the page token.

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
            f"/v1/accounts/{account_id}/nodePools",
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
                    node_pool_retrieve_node_pools_params.NodePoolRetrieveNodePoolsParams,
                ),
            ),
            cast_to=NodePoolRetrieveNodePoolsResponse,
        )


class NodePoolsResourceWithRawResponse:
    def __init__(self, node_pools: NodePoolsResource) -> None:
        self._node_pools = node_pools

        self.retrieve = to_raw_response_wrapper(
            node_pools.retrieve,
        )
        self.update = to_raw_response_wrapper(
            node_pools.update,
        )
        self.delete = to_raw_response_wrapper(
            node_pools.delete,
        )
        self.node_pools = to_raw_response_wrapper(
            node_pools.node_pools,
        )
        self.retrieve_node_pool_id_get_stats = to_raw_response_wrapper(
            node_pools.retrieve_node_pool_id_get_stats,
        )
        self.retrieve_node_pools = to_raw_response_wrapper(
            node_pools.retrieve_node_pools,
        )


class AsyncNodePoolsResourceWithRawResponse:
    def __init__(self, node_pools: AsyncNodePoolsResource) -> None:
        self._node_pools = node_pools

        self.retrieve = async_to_raw_response_wrapper(
            node_pools.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            node_pools.update,
        )
        self.delete = async_to_raw_response_wrapper(
            node_pools.delete,
        )
        self.node_pools = async_to_raw_response_wrapper(
            node_pools.node_pools,
        )
        self.retrieve_node_pool_id_get_stats = async_to_raw_response_wrapper(
            node_pools.retrieve_node_pool_id_get_stats,
        )
        self.retrieve_node_pools = async_to_raw_response_wrapper(
            node_pools.retrieve_node_pools,
        )


class NodePoolsResourceWithStreamingResponse:
    def __init__(self, node_pools: NodePoolsResource) -> None:
        self._node_pools = node_pools

        self.retrieve = to_streamed_response_wrapper(
            node_pools.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            node_pools.update,
        )
        self.delete = to_streamed_response_wrapper(
            node_pools.delete,
        )
        self.node_pools = to_streamed_response_wrapper(
            node_pools.node_pools,
        )
        self.retrieve_node_pool_id_get_stats = to_streamed_response_wrapper(
            node_pools.retrieve_node_pool_id_get_stats,
        )
        self.retrieve_node_pools = to_streamed_response_wrapper(
            node_pools.retrieve_node_pools,
        )


class AsyncNodePoolsResourceWithStreamingResponse:
    def __init__(self, node_pools: AsyncNodePoolsResource) -> None:
        self._node_pools = node_pools

        self.retrieve = async_to_streamed_response_wrapper(
            node_pools.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            node_pools.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            node_pools.delete,
        )
        self.node_pools = async_to_streamed_response_wrapper(
            node_pools.node_pools,
        )
        self.retrieve_node_pool_id_get_stats = async_to_streamed_response_wrapper(
            node_pools.retrieve_node_pool_id_get_stats,
        )
        self.retrieve_node_pools = async_to_streamed_response_wrapper(
            node_pools.retrieve_node_pools,
        )
