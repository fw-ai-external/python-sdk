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
    McpServerAuthenticationType,
    mcp_server_list_params,
    mcp_server_create_params,
    mcp_server_update_params,
    mcp_server_retrieve_params,
)
from ...types.accounts.gateway_mcp_server import GatewayMcpServer
from ...types.accounts.mcp_server_list_response import McpServerListResponse
from ...types.accounts.mcp_server_authentication_type import McpServerAuthenticationType

__all__ = ["McpServersResource", "AsyncMcpServersResource"]


class McpServersResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> McpServersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stainless-sdks/fireworks-ai-python#accessing-raw-response-data-eg-headers
        """
        return McpServersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> McpServersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stainless-sdks/fireworks-ai-python#with_streaming_response
        """
        return McpServersResourceWithStreamingResponse(self)

    def create(
        self,
        account_id: str,
        *,
        mcp_server_id: str,
        annotations: Dict[str, str] | Omit = omit,
        api_key_secret: str | Omit = omit,
        authentication_type: McpServerAuthenticationType | Omit = omit,
        description: str | Omit = omit,
        display_name: str | Omit = omit,
        endpoint_url: str | Omit = omit,
        max_qps: float | Omit = omit,
        public: bool | Omit = omit,
        remote_hosted: bool | Omit = omit,
        simulated: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayMcpServer:
        """
        Create MCP Server

        Args:
          mcp_server_id: ID of the mcp server.

          annotations: Annotations to identify MCP properties. Key/value pairs may be used by external
              tools or other services.

          api_key_secret: The resource name of the secret to use for authenticating with the MCP server.
              e.g. accounts/my-account/secrets/my-secret If provided for a remote-hosted MCP,
              the endpoint will be validated for connectivity during creation.

          authentication_type: The authentication method required by this MCP server.

          description: The description of the mcp. Must be fewer than 4000 characters long.

          display_name: Human-readable display name of the mcp. e.g. "My Mcp" Must be fewer than 64
              characters long.

          endpoint_url: The URL of the MCP server. Required if self_hosted is true. For managed MCPs,
              this will be populated after deployment.

          max_qps: Max QPS of this MCP server. 0 means no ratelimit.

          public: Whether this MCP is publicly available to all Fireworks users. If false, only
              accessible to the account that created it.

          remote_hosted: Whether this MCP is remote-hosted (true) or managed by Fireworks (false).

          simulated: Whether this is a simulated MCP server.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._post(
            f"/v1/accounts/{account_id}/mcpServers",
            body=maybe_transform(
                {
                    "annotations": annotations,
                    "api_key_secret": api_key_secret,
                    "authentication_type": authentication_type,
                    "description": description,
                    "display_name": display_name,
                    "endpoint_url": endpoint_url,
                    "max_qps": max_qps,
                    "public": public,
                    "remote_hosted": remote_hosted,
                    "simulated": simulated,
                },
                mcp_server_create_params.McpServerCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"mcp_server_id": mcp_server_id}, mcp_server_create_params.McpServerCreateParams),
            ),
            cast_to=GatewayMcpServer,
        )

    def retrieve(
        self,
        mcp_server_id: str,
        *,
        account_id: str,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayMcpServer:
        """Get MCP Server

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
        if not mcp_server_id:
            raise ValueError(f"Expected a non-empty value for `mcp_server_id` but received {mcp_server_id!r}")
        return self._get(
            f"/v1/accounts/{account_id}/mcpServers/{mcp_server_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"read_mask": read_mask}, mcp_server_retrieve_params.McpServerRetrieveParams),
            ),
            cast_to=GatewayMcpServer,
        )

    def update(
        self,
        mcp_server_id: str,
        *,
        account_id: str,
        annotations: Dict[str, str] | Omit = omit,
        api_key_secret: str | Omit = omit,
        authentication_type: McpServerAuthenticationType | Omit = omit,
        description: str | Omit = omit,
        display_name: str | Omit = omit,
        endpoint_url: str | Omit = omit,
        max_qps: float | Omit = omit,
        public: bool | Omit = omit,
        remote_hosted: bool | Omit = omit,
        simulated: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayMcpServer:
        """Update MCP Server

        Args:
          annotations: Annotations to identify MCP properties.

        Key/value pairs may be used by external
              tools or other services.

          api_key_secret: The resource name of the secret to use for authenticating with the MCP server.
              e.g. accounts/my-account/secrets/my-secret If provided for a remote-hosted MCP,
              the endpoint will be validated for connectivity during creation.

          authentication_type: The authentication method required by this MCP server.

          description: The description of the mcp. Must be fewer than 4000 characters long.

          display_name: Human-readable display name of the mcp. e.g. "My Mcp" Must be fewer than 64
              characters long.

          endpoint_url: The URL of the MCP server. Required if self_hosted is true. For managed MCPs,
              this will be populated after deployment.

          max_qps: Max QPS of this MCP server. 0 means no ratelimit.

          public: Whether this MCP is publicly available to all Fireworks users. If false, only
              accessible to the account that created it.

          remote_hosted: Whether this MCP is remote-hosted (true) or managed by Fireworks (false).

          simulated: Whether this is a simulated MCP server.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not mcp_server_id:
            raise ValueError(f"Expected a non-empty value for `mcp_server_id` but received {mcp_server_id!r}")
        return self._patch(
            f"/v1/accounts/{account_id}/mcpServers/{mcp_server_id}",
            body=maybe_transform(
                {
                    "annotations": annotations,
                    "api_key_secret": api_key_secret,
                    "authentication_type": authentication_type,
                    "description": description,
                    "display_name": display_name,
                    "endpoint_url": endpoint_url,
                    "max_qps": max_qps,
                    "public": public,
                    "remote_hosted": remote_hosted,
                    "simulated": simulated,
                },
                mcp_server_update_params.McpServerUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GatewayMcpServer,
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
    ) -> McpServerListResponse:
        """
        List MCP Servers

        Args:
          filter: Only mcp server satisfying the provided filter (if specified) will be returned.
              See https://google.aip.dev/160 for the filter grammar.

          order_by: A comma-separated list of fields to order by. e.g. "foo,bar" The default sort
              order is ascending. To specify a descending order for a field, append a " desc"
              suffix. e.g. "foo desc,bar" Subfields are specified with a "." character. e.g.
              "foo.bar" If not specified, the default order is by "name".

          page_size: The maximum number of mcp servers to return. The maximum page_size is 200,
              values above 200 will be coerced to 200. If unspecified, the default is 50.

          page_token: A page token, received from a previous ListMcpServers call. Provide this to
              retrieve the subsequent page. When paginating, all other parameters provided to
              ListMcpServers must match the call that provided the page token.

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
            f"/v1/accounts/{account_id}/mcpServers",
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
                    mcp_server_list_params.McpServerListParams,
                ),
            ),
            cast_to=McpServerListResponse,
        )

    def delete(
        self,
        mcp_server_id: str,
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
        Delete MCP Server

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not mcp_server_id:
            raise ValueError(f"Expected a non-empty value for `mcp_server_id` but received {mcp_server_id!r}")
        return self._delete(
            f"/v1/accounts/{account_id}/mcpServers/{mcp_server_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncMcpServersResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncMcpServersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stainless-sdks/fireworks-ai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncMcpServersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncMcpServersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stainless-sdks/fireworks-ai-python#with_streaming_response
        """
        return AsyncMcpServersResourceWithStreamingResponse(self)

    async def create(
        self,
        account_id: str,
        *,
        mcp_server_id: str,
        annotations: Dict[str, str] | Omit = omit,
        api_key_secret: str | Omit = omit,
        authentication_type: McpServerAuthenticationType | Omit = omit,
        description: str | Omit = omit,
        display_name: str | Omit = omit,
        endpoint_url: str | Omit = omit,
        max_qps: float | Omit = omit,
        public: bool | Omit = omit,
        remote_hosted: bool | Omit = omit,
        simulated: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayMcpServer:
        """
        Create MCP Server

        Args:
          mcp_server_id: ID of the mcp server.

          annotations: Annotations to identify MCP properties. Key/value pairs may be used by external
              tools or other services.

          api_key_secret: The resource name of the secret to use for authenticating with the MCP server.
              e.g. accounts/my-account/secrets/my-secret If provided for a remote-hosted MCP,
              the endpoint will be validated for connectivity during creation.

          authentication_type: The authentication method required by this MCP server.

          description: The description of the mcp. Must be fewer than 4000 characters long.

          display_name: Human-readable display name of the mcp. e.g. "My Mcp" Must be fewer than 64
              characters long.

          endpoint_url: The URL of the MCP server. Required if self_hosted is true. For managed MCPs,
              this will be populated after deployment.

          max_qps: Max QPS of this MCP server. 0 means no ratelimit.

          public: Whether this MCP is publicly available to all Fireworks users. If false, only
              accessible to the account that created it.

          remote_hosted: Whether this MCP is remote-hosted (true) or managed by Fireworks (false).

          simulated: Whether this is a simulated MCP server.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._post(
            f"/v1/accounts/{account_id}/mcpServers",
            body=await async_maybe_transform(
                {
                    "annotations": annotations,
                    "api_key_secret": api_key_secret,
                    "authentication_type": authentication_type,
                    "description": description,
                    "display_name": display_name,
                    "endpoint_url": endpoint_url,
                    "max_qps": max_qps,
                    "public": public,
                    "remote_hosted": remote_hosted,
                    "simulated": simulated,
                },
                mcp_server_create_params.McpServerCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"mcp_server_id": mcp_server_id}, mcp_server_create_params.McpServerCreateParams
                ),
            ),
            cast_to=GatewayMcpServer,
        )

    async def retrieve(
        self,
        mcp_server_id: str,
        *,
        account_id: str,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayMcpServer:
        """Get MCP Server

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
        if not mcp_server_id:
            raise ValueError(f"Expected a non-empty value for `mcp_server_id` but received {mcp_server_id!r}")
        return await self._get(
            f"/v1/accounts/{account_id}/mcpServers/{mcp_server_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"read_mask": read_mask}, mcp_server_retrieve_params.McpServerRetrieveParams
                ),
            ),
            cast_to=GatewayMcpServer,
        )

    async def update(
        self,
        mcp_server_id: str,
        *,
        account_id: str,
        annotations: Dict[str, str] | Omit = omit,
        api_key_secret: str | Omit = omit,
        authentication_type: McpServerAuthenticationType | Omit = omit,
        description: str | Omit = omit,
        display_name: str | Omit = omit,
        endpoint_url: str | Omit = omit,
        max_qps: float | Omit = omit,
        public: bool | Omit = omit,
        remote_hosted: bool | Omit = omit,
        simulated: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayMcpServer:
        """Update MCP Server

        Args:
          annotations: Annotations to identify MCP properties.

        Key/value pairs may be used by external
              tools or other services.

          api_key_secret: The resource name of the secret to use for authenticating with the MCP server.
              e.g. accounts/my-account/secrets/my-secret If provided for a remote-hosted MCP,
              the endpoint will be validated for connectivity during creation.

          authentication_type: The authentication method required by this MCP server.

          description: The description of the mcp. Must be fewer than 4000 characters long.

          display_name: Human-readable display name of the mcp. e.g. "My Mcp" Must be fewer than 64
              characters long.

          endpoint_url: The URL of the MCP server. Required if self_hosted is true. For managed MCPs,
              this will be populated after deployment.

          max_qps: Max QPS of this MCP server. 0 means no ratelimit.

          public: Whether this MCP is publicly available to all Fireworks users. If false, only
              accessible to the account that created it.

          remote_hosted: Whether this MCP is remote-hosted (true) or managed by Fireworks (false).

          simulated: Whether this is a simulated MCP server.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not mcp_server_id:
            raise ValueError(f"Expected a non-empty value for `mcp_server_id` but received {mcp_server_id!r}")
        return await self._patch(
            f"/v1/accounts/{account_id}/mcpServers/{mcp_server_id}",
            body=await async_maybe_transform(
                {
                    "annotations": annotations,
                    "api_key_secret": api_key_secret,
                    "authentication_type": authentication_type,
                    "description": description,
                    "display_name": display_name,
                    "endpoint_url": endpoint_url,
                    "max_qps": max_qps,
                    "public": public,
                    "remote_hosted": remote_hosted,
                    "simulated": simulated,
                },
                mcp_server_update_params.McpServerUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GatewayMcpServer,
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
    ) -> McpServerListResponse:
        """
        List MCP Servers

        Args:
          filter: Only mcp server satisfying the provided filter (if specified) will be returned.
              See https://google.aip.dev/160 for the filter grammar.

          order_by: A comma-separated list of fields to order by. e.g. "foo,bar" The default sort
              order is ascending. To specify a descending order for a field, append a " desc"
              suffix. e.g. "foo desc,bar" Subfields are specified with a "." character. e.g.
              "foo.bar" If not specified, the default order is by "name".

          page_size: The maximum number of mcp servers to return. The maximum page_size is 200,
              values above 200 will be coerced to 200. If unspecified, the default is 50.

          page_token: A page token, received from a previous ListMcpServers call. Provide this to
              retrieve the subsequent page. When paginating, all other parameters provided to
              ListMcpServers must match the call that provided the page token.

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
            f"/v1/accounts/{account_id}/mcpServers",
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
                    mcp_server_list_params.McpServerListParams,
                ),
            ),
            cast_to=McpServerListResponse,
        )

    async def delete(
        self,
        mcp_server_id: str,
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
        Delete MCP Server

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not mcp_server_id:
            raise ValueError(f"Expected a non-empty value for `mcp_server_id` but received {mcp_server_id!r}")
        return await self._delete(
            f"/v1/accounts/{account_id}/mcpServers/{mcp_server_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class McpServersResourceWithRawResponse:
    def __init__(self, mcp_servers: McpServersResource) -> None:
        self._mcp_servers = mcp_servers

        self.create = to_raw_response_wrapper(
            mcp_servers.create,
        )
        self.retrieve = to_raw_response_wrapper(
            mcp_servers.retrieve,
        )
        self.update = to_raw_response_wrapper(
            mcp_servers.update,
        )
        self.list = to_raw_response_wrapper(
            mcp_servers.list,
        )
        self.delete = to_raw_response_wrapper(
            mcp_servers.delete,
        )


class AsyncMcpServersResourceWithRawResponse:
    def __init__(self, mcp_servers: AsyncMcpServersResource) -> None:
        self._mcp_servers = mcp_servers

        self.create = async_to_raw_response_wrapper(
            mcp_servers.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            mcp_servers.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            mcp_servers.update,
        )
        self.list = async_to_raw_response_wrapper(
            mcp_servers.list,
        )
        self.delete = async_to_raw_response_wrapper(
            mcp_servers.delete,
        )


class McpServersResourceWithStreamingResponse:
    def __init__(self, mcp_servers: McpServersResource) -> None:
        self._mcp_servers = mcp_servers

        self.create = to_streamed_response_wrapper(
            mcp_servers.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            mcp_servers.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            mcp_servers.update,
        )
        self.list = to_streamed_response_wrapper(
            mcp_servers.list,
        )
        self.delete = to_streamed_response_wrapper(
            mcp_servers.delete,
        )


class AsyncMcpServersResourceWithStreamingResponse:
    def __init__(self, mcp_servers: AsyncMcpServersResource) -> None:
        self._mcp_servers = mcp_servers

        self.create = async_to_streamed_response_wrapper(
            mcp_servers.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            mcp_servers.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            mcp_servers.update,
        )
        self.list = async_to_streamed_response_wrapper(
            mcp_servers.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            mcp_servers.delete,
        )
