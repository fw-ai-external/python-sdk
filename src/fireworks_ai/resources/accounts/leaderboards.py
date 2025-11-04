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
    GatewayLeaderboard,
    leaderboard_list_params,
    leaderboard_create_params,
    leaderboard_retrieve_params,
    leaderboard_list_evaluation_jobs_params,
)
from ...types.accounts.gateway_leaderboard import GatewayLeaderboard
from ...types.accounts.gateway_leaderboard_param import GatewayLeaderboardParam
from ...types.accounts.leaderboard_list_response import LeaderboardListResponse
from ...types.accounts.leaderboard_retrieve_response import LeaderboardRetrieveResponse
from ...types.accounts.leaderboard_list_evaluation_jobs_response import LeaderboardListEvaluationJobsResponse

__all__ = ["LeaderboardsResource", "AsyncLeaderboardsResource"]


class LeaderboardsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> LeaderboardsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#accessing-raw-response-data-eg-headers
        """
        return LeaderboardsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> LeaderboardsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#with_streaming_response
        """
        return LeaderboardsResourceWithStreamingResponse(self)

    def create(
        self,
        account_id: str,
        *,
        leaderboard: GatewayLeaderboardParam,
        leaderboard_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayLeaderboard:
        """
        CRUD APIs for leaderboards.

        Args:
          leaderboard: Leaderboard to create.

          leaderboard_id: Optional explicit leaderboard ID (defaults to server-generated).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._post(
            f"/v1/accounts/{account_id}/leaderboards",
            body=maybe_transform(
                {
                    "leaderboard": leaderboard,
                    "leaderboard_id": leaderboard_id,
                },
                leaderboard_create_params.LeaderboardCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GatewayLeaderboard,
        )

    def retrieve(
        self,
        leaderboard_id: str,
        *,
        account_id: str,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> LeaderboardRetrieveResponse:
        """
        Args:
          read_mask: Optional read mask for leaderboard fields.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not leaderboard_id:
            raise ValueError(f"Expected a non-empty value for `leaderboard_id` but received {leaderboard_id!r}")
        return self._get(
            f"/v1/accounts/{account_id}/leaderboards/{leaderboard_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"read_mask": read_mask}, leaderboard_retrieve_params.LeaderboardRetrieveParams),
            ),
            cast_to=LeaderboardRetrieveResponse,
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
    ) -> LeaderboardListResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._get(
            f"/v1/accounts/{account_id}/leaderboards",
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
                    leaderboard_list_params.LeaderboardListParams,
                ),
            ),
            cast_to=LeaderboardListResponse,
        )

    def delete(
        self,
        leaderboard_id: str,
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
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not leaderboard_id:
            raise ValueError(f"Expected a non-empty value for `leaderboard_id` but received {leaderboard_id!r}")
        return self._delete(
            f"/v1/accounts/{account_id}/leaderboards/{leaderboard_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def list_evaluation_jobs(
        self,
        leaderboard_id: str,
        *,
        account_id: str,
        filter: str | Omit = omit,
        order_by: str | Omit = omit,
        page_size: int | Omit = omit,
        page_token: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> LeaderboardListEvaluationJobsResponse:
        """
        List evaluation jobs for a leaderboard (custom method)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not leaderboard_id:
            raise ValueError(f"Expected a non-empty value for `leaderboard_id` but received {leaderboard_id!r}")
        return self._get(
            f"/v1/accounts/{account_id}/leaderboards/{leaderboard_id}:listEvaluationJobs",
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
                    },
                    leaderboard_list_evaluation_jobs_params.LeaderboardListEvaluationJobsParams,
                ),
            ),
            cast_to=LeaderboardListEvaluationJobsResponse,
        )


class AsyncLeaderboardsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncLeaderboardsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncLeaderboardsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncLeaderboardsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#with_streaming_response
        """
        return AsyncLeaderboardsResourceWithStreamingResponse(self)

    async def create(
        self,
        account_id: str,
        *,
        leaderboard: GatewayLeaderboardParam,
        leaderboard_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayLeaderboard:
        """
        CRUD APIs for leaderboards.

        Args:
          leaderboard: Leaderboard to create.

          leaderboard_id: Optional explicit leaderboard ID (defaults to server-generated).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._post(
            f"/v1/accounts/{account_id}/leaderboards",
            body=await async_maybe_transform(
                {
                    "leaderboard": leaderboard,
                    "leaderboard_id": leaderboard_id,
                },
                leaderboard_create_params.LeaderboardCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GatewayLeaderboard,
        )

    async def retrieve(
        self,
        leaderboard_id: str,
        *,
        account_id: str,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> LeaderboardRetrieveResponse:
        """
        Args:
          read_mask: Optional read mask for leaderboard fields.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not leaderboard_id:
            raise ValueError(f"Expected a non-empty value for `leaderboard_id` but received {leaderboard_id!r}")
        return await self._get(
            f"/v1/accounts/{account_id}/leaderboards/{leaderboard_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"read_mask": read_mask}, leaderboard_retrieve_params.LeaderboardRetrieveParams
                ),
            ),
            cast_to=LeaderboardRetrieveResponse,
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
    ) -> LeaderboardListResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._get(
            f"/v1/accounts/{account_id}/leaderboards",
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
                    leaderboard_list_params.LeaderboardListParams,
                ),
            ),
            cast_to=LeaderboardListResponse,
        )

    async def delete(
        self,
        leaderboard_id: str,
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
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not leaderboard_id:
            raise ValueError(f"Expected a non-empty value for `leaderboard_id` but received {leaderboard_id!r}")
        return await self._delete(
            f"/v1/accounts/{account_id}/leaderboards/{leaderboard_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def list_evaluation_jobs(
        self,
        leaderboard_id: str,
        *,
        account_id: str,
        filter: str | Omit = omit,
        order_by: str | Omit = omit,
        page_size: int | Omit = omit,
        page_token: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> LeaderboardListEvaluationJobsResponse:
        """
        List evaluation jobs for a leaderboard (custom method)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not leaderboard_id:
            raise ValueError(f"Expected a non-empty value for `leaderboard_id` but received {leaderboard_id!r}")
        return await self._get(
            f"/v1/accounts/{account_id}/leaderboards/{leaderboard_id}:listEvaluationJobs",
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
                    },
                    leaderboard_list_evaluation_jobs_params.LeaderboardListEvaluationJobsParams,
                ),
            ),
            cast_to=LeaderboardListEvaluationJobsResponse,
        )


class LeaderboardsResourceWithRawResponse:
    def __init__(self, leaderboards: LeaderboardsResource) -> None:
        self._leaderboards = leaderboards

        self.create = to_raw_response_wrapper(
            leaderboards.create,
        )
        self.retrieve = to_raw_response_wrapper(
            leaderboards.retrieve,
        )
        self.list = to_raw_response_wrapper(
            leaderboards.list,
        )
        self.delete = to_raw_response_wrapper(
            leaderboards.delete,
        )
        self.list_evaluation_jobs = to_raw_response_wrapper(
            leaderboards.list_evaluation_jobs,
        )


class AsyncLeaderboardsResourceWithRawResponse:
    def __init__(self, leaderboards: AsyncLeaderboardsResource) -> None:
        self._leaderboards = leaderboards

        self.create = async_to_raw_response_wrapper(
            leaderboards.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            leaderboards.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            leaderboards.list,
        )
        self.delete = async_to_raw_response_wrapper(
            leaderboards.delete,
        )
        self.list_evaluation_jobs = async_to_raw_response_wrapper(
            leaderboards.list_evaluation_jobs,
        )


class LeaderboardsResourceWithStreamingResponse:
    def __init__(self, leaderboards: LeaderboardsResource) -> None:
        self._leaderboards = leaderboards

        self.create = to_streamed_response_wrapper(
            leaderboards.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            leaderboards.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            leaderboards.list,
        )
        self.delete = to_streamed_response_wrapper(
            leaderboards.delete,
        )
        self.list_evaluation_jobs = to_streamed_response_wrapper(
            leaderboards.list_evaluation_jobs,
        )


class AsyncLeaderboardsResourceWithStreamingResponse:
    def __init__(self, leaderboards: AsyncLeaderboardsResource) -> None:
        self._leaderboards = leaderboards

        self.create = async_to_streamed_response_wrapper(
            leaderboards.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            leaderboards.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            leaderboards.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            leaderboards.delete,
        )
        self.list_evaluation_jobs = async_to_streamed_response_wrapper(
            leaderboards.list_evaluation_jobs,
        )
