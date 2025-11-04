# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

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
from ....types.accounts.users import APIKey, api_key_api_keys_params, api_key_retrieve_api_keys_params
from ....types.accounts.users.api_key import APIKey
from ....types.accounts.users.api_key_param import APIKeyParam
from ....types.accounts.users.api_key_retrieve_api_keys_response import APIKeyRetrieveAPIKeysResponse

__all__ = ["APIKeysResource", "AsyncAPIKeysResource"]


class APIKeysResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> APIKeysResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#accessing-raw-response-data-eg-headers
        """
        return APIKeysResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> APIKeysResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#with_streaming_response
        """
        return APIKeysResourceWithStreamingResponse(self)

    def api_keys(
        self,
        user_id: str,
        *,
        account_id: str,
        api_key: APIKeyParam,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> APIKey:
        """
        Create API Key

        Args:
          api_key: The API key to be created.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not user_id:
            raise ValueError(f"Expected a non-empty value for `user_id` but received {user_id!r}")
        return self._post(
            f"/v1/accounts/{account_id}/users/{user_id}/apiKeys",
            body=maybe_transform({"api_key": api_key}, api_key_api_keys_params.APIKeyAPIKeysParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=APIKey,
        )

    def retrieve_api_keys(
        self,
        user_id: str,
        *,
        account_id: str,
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
    ) -> APIKeyRetrieveAPIKeysResponse:
        """
        List API Keys

        Args:
          filter: Field for filtering results.

          order_by: Field for ordering results.

          page_size: Number of API keys to return in the response. Pagination support to be added.

          page_token: Token for fetching the next page of results. Pagination support to be added.

          read_mask: The fields to be returned in the response. If empty or "\\**", all fields will be
              returned.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not user_id:
            raise ValueError(f"Expected a non-empty value for `user_id` but received {user_id!r}")
        return self._get(
            f"/v1/accounts/{account_id}/users/{user_id}/apiKeys",
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
                    api_key_retrieve_api_keys_params.APIKeyRetrieveAPIKeysParams,
                ),
            ),
            cast_to=APIKeyRetrieveAPIKeysResponse,
        )


class AsyncAPIKeysResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAPIKeysResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncAPIKeysResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAPIKeysResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#with_streaming_response
        """
        return AsyncAPIKeysResourceWithStreamingResponse(self)

    async def api_keys(
        self,
        user_id: str,
        *,
        account_id: str,
        api_key: APIKeyParam,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> APIKey:
        """
        Create API Key

        Args:
          api_key: The API key to be created.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not user_id:
            raise ValueError(f"Expected a non-empty value for `user_id` but received {user_id!r}")
        return await self._post(
            f"/v1/accounts/{account_id}/users/{user_id}/apiKeys",
            body=await async_maybe_transform({"api_key": api_key}, api_key_api_keys_params.APIKeyAPIKeysParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=APIKey,
        )

    async def retrieve_api_keys(
        self,
        user_id: str,
        *,
        account_id: str,
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
    ) -> APIKeyRetrieveAPIKeysResponse:
        """
        List API Keys

        Args:
          filter: Field for filtering results.

          order_by: Field for ordering results.

          page_size: Number of API keys to return in the response. Pagination support to be added.

          page_token: Token for fetching the next page of results. Pagination support to be added.

          read_mask: The fields to be returned in the response. If empty or "\\**", all fields will be
              returned.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not user_id:
            raise ValueError(f"Expected a non-empty value for `user_id` but received {user_id!r}")
        return await self._get(
            f"/v1/accounts/{account_id}/users/{user_id}/apiKeys",
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
                    api_key_retrieve_api_keys_params.APIKeyRetrieveAPIKeysParams,
                ),
            ),
            cast_to=APIKeyRetrieveAPIKeysResponse,
        )


class APIKeysResourceWithRawResponse:
    def __init__(self, api_keys: APIKeysResource) -> None:
        self._api_keys = api_keys

        self.api_keys = to_raw_response_wrapper(
            api_keys.api_keys,
        )
        self.retrieve_api_keys = to_raw_response_wrapper(
            api_keys.retrieve_api_keys,
        )


class AsyncAPIKeysResourceWithRawResponse:
    def __init__(self, api_keys: AsyncAPIKeysResource) -> None:
        self._api_keys = api_keys

        self.api_keys = async_to_raw_response_wrapper(
            api_keys.api_keys,
        )
        self.retrieve_api_keys = async_to_raw_response_wrapper(
            api_keys.retrieve_api_keys,
        )


class APIKeysResourceWithStreamingResponse:
    def __init__(self, api_keys: APIKeysResource) -> None:
        self._api_keys = api_keys

        self.api_keys = to_streamed_response_wrapper(
            api_keys.api_keys,
        )
        self.retrieve_api_keys = to_streamed_response_wrapper(
            api_keys.retrieve_api_keys,
        )


class AsyncAPIKeysResourceWithStreamingResponse:
    def __init__(self, api_keys: AsyncAPIKeysResource) -> None:
        self._api_keys = api_keys

        self.api_keys = async_to_streamed_response_wrapper(
            api_keys.api_keys,
        )
        self.retrieve_api_keys = async_to_streamed_response_wrapper(
            api_keys.retrieve_api_keys,
        )
