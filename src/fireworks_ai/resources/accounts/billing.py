# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime

import httpx

from ..._types import Body, Query, Headers, NotGiven, not_given
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
from ...types.accounts import billing_get_summary_params
from ...types.accounts.billing_get_summary_response import BillingGetSummaryResponse

__all__ = ["BillingResource", "AsyncBillingResource"]


class BillingResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> BillingResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stainless-sdks/fireworks-ai-python#accessing-raw-response-data-eg-headers
        """
        return BillingResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> BillingResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stainless-sdks/fireworks-ai-python#with_streaming_response
        """
        return BillingResourceWithStreamingResponse(self)

    def get_summary(
        self,
        account_id: str,
        *,
        end_time: Union[str, datetime],
        start_time: Union[str, datetime],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BillingGetSummaryResponse:
        """
        Get billing summary information for an account

        Args:
          end_time: End time for the billing period (exclusive). Note: Costs are aggregated daily.
              Only the date portion (YYYY-MM-DD) is used; the time portion is ignored. Costs
              for the end date are NOT included. For example, to get costs for Oct 5 and Oct
              6, use: start_time: 2025-10-05T00:00:00Z end_time: 2025-10-07T00:00:00Z (Oct 7
              is excluded)

          start_time: Start time for the billing period. Note: Costs are aggregated daily. Only the
              date portion (YYYY-MM-DD) is used; the time portion is ignored. For example,
              2025-10-05T07:18:29Z and 2025-10-05T23:59:59Z are treated the same as
              2025-10-05T00:00:00Z.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._get(
            f"/v1/accounts/{account_id}/billing/summary",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "end_time": end_time,
                        "start_time": start_time,
                    },
                    billing_get_summary_params.BillingGetSummaryParams,
                ),
            ),
            cast_to=BillingGetSummaryResponse,
        )


class AsyncBillingResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncBillingResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stainless-sdks/fireworks-ai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncBillingResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncBillingResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stainless-sdks/fireworks-ai-python#with_streaming_response
        """
        return AsyncBillingResourceWithStreamingResponse(self)

    async def get_summary(
        self,
        account_id: str,
        *,
        end_time: Union[str, datetime],
        start_time: Union[str, datetime],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BillingGetSummaryResponse:
        """
        Get billing summary information for an account

        Args:
          end_time: End time for the billing period (exclusive). Note: Costs are aggregated daily.
              Only the date portion (YYYY-MM-DD) is used; the time portion is ignored. Costs
              for the end date are NOT included. For example, to get costs for Oct 5 and Oct
              6, use: start_time: 2025-10-05T00:00:00Z end_time: 2025-10-07T00:00:00Z (Oct 7
              is excluded)

          start_time: Start time for the billing period. Note: Costs are aggregated daily. Only the
              date portion (YYYY-MM-DD) is used; the time portion is ignored. For example,
              2025-10-05T07:18:29Z and 2025-10-05T23:59:59Z are treated the same as
              2025-10-05T00:00:00Z.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._get(
            f"/v1/accounts/{account_id}/billing/summary",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "end_time": end_time,
                        "start_time": start_time,
                    },
                    billing_get_summary_params.BillingGetSummaryParams,
                ),
            ),
            cast_to=BillingGetSummaryResponse,
        )


class BillingResourceWithRawResponse:
    def __init__(self, billing: BillingResource) -> None:
        self._billing = billing

        self.get_summary = to_raw_response_wrapper(
            billing.get_summary,
        )


class AsyncBillingResourceWithRawResponse:
    def __init__(self, billing: AsyncBillingResource) -> None:
        self._billing = billing

        self.get_summary = async_to_raw_response_wrapper(
            billing.get_summary,
        )


class BillingResourceWithStreamingResponse:
    def __init__(self, billing: BillingResource) -> None:
        self._billing = billing

        self.get_summary = to_streamed_response_wrapper(
            billing.get_summary,
        )


class AsyncBillingResourceWithStreamingResponse:
    def __init__(self, billing: AsyncBillingResource) -> None:
        self._billing = billing

        self.get_summary = async_to_streamed_response_wrapper(
            billing.get_summary,
        )
