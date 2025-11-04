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
from ...types.accounts import peft_merge_job_list_params, peft_merge_job_create_params, peft_merge_job_retrieve_params
from ...types.accounts.gateway_peft_merge_job import GatewayPeftMergeJob
from ...types.accounts.peft_merge_job_list_response import PeftMergeJobListResponse

__all__ = ["PeftMergeJobsResource", "AsyncPeftMergeJobsResource"]


class PeftMergeJobsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> PeftMergeJobsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stainless-sdks/fireworks-ai-python#accessing-raw-response-data-eg-headers
        """
        return PeftMergeJobsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PeftMergeJobsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stainless-sdks/fireworks-ai-python#with_streaming_response
        """
        return PeftMergeJobsResourceWithStreamingResponse(self)

    def create(
        self,
        account_id: str,
        *,
        merged_model: str,
        peft_model: str,
        display_name: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayPeftMergeJob:
        """
        Create Peft-Merge Job

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._post(
            f"/v1/accounts/{account_id}/PeftMergeJobs",
            body=maybe_transform(
                {
                    "merged_model": merged_model,
                    "peft_model": peft_model,
                    "display_name": display_name,
                },
                peft_merge_job_create_params.PeftMergeJobCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GatewayPeftMergeJob,
        )

    def retrieve(
        self,
        peft_merge_job_id: str,
        *,
        account_id: str,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayPeftMergeJob:
        """Get Peft-Merge Job

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
        if not peft_merge_job_id:
            raise ValueError(f"Expected a non-empty value for `peft_merge_job_id` but received {peft_merge_job_id!r}")
        return self._get(
            f"/v1/accounts/{account_id}/PeftMergeJobs/{peft_merge_job_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"read_mask": read_mask}, peft_merge_job_retrieve_params.PeftMergeJobRetrieveParams
                ),
            ),
            cast_to=GatewayPeftMergeJob,
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
    ) -> PeftMergeJobListResponse:
        """
        List Peft-Merge Jobs

        Args:
          filter: Only jobs satisfying the provided filter (if specified) will be returned. See
              https://google.aip.dev/160 for the filter grammar.

          order_by: A comma-separated list of fields to order by. e.g. "foo,bar" The default sort
              order is ascending. To specify a descending order for a field, append a " desc"
              suffix. e.g. "foo desc,bar" Subfields are specified with a "." character. e.g.
              "foo.bar" If not specified, the default order is by "created_time".

          page_size: The maximum number of peft merge jobs to return. The maximum page_size is 200,
              values above 200 will be coerced to 200. If unspecified, the default is 50.

          page_token: A page token, received from a previous ListPeftMergeJobs call. Provide this to
              retrieve the subsequent page. When paginating, all other parameters provided to
              ListPeftMergeJobs must match the call that provided the page token.

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
            f"/v1/accounts/{account_id}/PeftMergeJobs",
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
                    peft_merge_job_list_params.PeftMergeJobListParams,
                ),
            ),
            cast_to=PeftMergeJobListResponse,
        )

    def delete(
        self,
        peft_merge_job_id: str,
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
        Delete Peft-Merge Job

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not peft_merge_job_id:
            raise ValueError(f"Expected a non-empty value for `peft_merge_job_id` but received {peft_merge_job_id!r}")
        return self._delete(
            f"/v1/accounts/{account_id}/PeftMergeJobs/{peft_merge_job_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncPeftMergeJobsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncPeftMergeJobsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stainless-sdks/fireworks-ai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncPeftMergeJobsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPeftMergeJobsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stainless-sdks/fireworks-ai-python#with_streaming_response
        """
        return AsyncPeftMergeJobsResourceWithStreamingResponse(self)

    async def create(
        self,
        account_id: str,
        *,
        merged_model: str,
        peft_model: str,
        display_name: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayPeftMergeJob:
        """
        Create Peft-Merge Job

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._post(
            f"/v1/accounts/{account_id}/PeftMergeJobs",
            body=await async_maybe_transform(
                {
                    "merged_model": merged_model,
                    "peft_model": peft_model,
                    "display_name": display_name,
                },
                peft_merge_job_create_params.PeftMergeJobCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GatewayPeftMergeJob,
        )

    async def retrieve(
        self,
        peft_merge_job_id: str,
        *,
        account_id: str,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayPeftMergeJob:
        """Get Peft-Merge Job

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
        if not peft_merge_job_id:
            raise ValueError(f"Expected a non-empty value for `peft_merge_job_id` but received {peft_merge_job_id!r}")
        return await self._get(
            f"/v1/accounts/{account_id}/PeftMergeJobs/{peft_merge_job_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"read_mask": read_mask}, peft_merge_job_retrieve_params.PeftMergeJobRetrieveParams
                ),
            ),
            cast_to=GatewayPeftMergeJob,
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
    ) -> PeftMergeJobListResponse:
        """
        List Peft-Merge Jobs

        Args:
          filter: Only jobs satisfying the provided filter (if specified) will be returned. See
              https://google.aip.dev/160 for the filter grammar.

          order_by: A comma-separated list of fields to order by. e.g. "foo,bar" The default sort
              order is ascending. To specify a descending order for a field, append a " desc"
              suffix. e.g. "foo desc,bar" Subfields are specified with a "." character. e.g.
              "foo.bar" If not specified, the default order is by "created_time".

          page_size: The maximum number of peft merge jobs to return. The maximum page_size is 200,
              values above 200 will be coerced to 200. If unspecified, the default is 50.

          page_token: A page token, received from a previous ListPeftMergeJobs call. Provide this to
              retrieve the subsequent page. When paginating, all other parameters provided to
              ListPeftMergeJobs must match the call that provided the page token.

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
            f"/v1/accounts/{account_id}/PeftMergeJobs",
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
                    peft_merge_job_list_params.PeftMergeJobListParams,
                ),
            ),
            cast_to=PeftMergeJobListResponse,
        )

    async def delete(
        self,
        peft_merge_job_id: str,
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
        Delete Peft-Merge Job

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not peft_merge_job_id:
            raise ValueError(f"Expected a non-empty value for `peft_merge_job_id` but received {peft_merge_job_id!r}")
        return await self._delete(
            f"/v1/accounts/{account_id}/PeftMergeJobs/{peft_merge_job_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class PeftMergeJobsResourceWithRawResponse:
    def __init__(self, peft_merge_jobs: PeftMergeJobsResource) -> None:
        self._peft_merge_jobs = peft_merge_jobs

        self.create = to_raw_response_wrapper(
            peft_merge_jobs.create,
        )
        self.retrieve = to_raw_response_wrapper(
            peft_merge_jobs.retrieve,
        )
        self.list = to_raw_response_wrapper(
            peft_merge_jobs.list,
        )
        self.delete = to_raw_response_wrapper(
            peft_merge_jobs.delete,
        )


class AsyncPeftMergeJobsResourceWithRawResponse:
    def __init__(self, peft_merge_jobs: AsyncPeftMergeJobsResource) -> None:
        self._peft_merge_jobs = peft_merge_jobs

        self.create = async_to_raw_response_wrapper(
            peft_merge_jobs.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            peft_merge_jobs.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            peft_merge_jobs.list,
        )
        self.delete = async_to_raw_response_wrapper(
            peft_merge_jobs.delete,
        )


class PeftMergeJobsResourceWithStreamingResponse:
    def __init__(self, peft_merge_jobs: PeftMergeJobsResource) -> None:
        self._peft_merge_jobs = peft_merge_jobs

        self.create = to_streamed_response_wrapper(
            peft_merge_jobs.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            peft_merge_jobs.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            peft_merge_jobs.list,
        )
        self.delete = to_streamed_response_wrapper(
            peft_merge_jobs.delete,
        )


class AsyncPeftMergeJobsResourceWithStreamingResponse:
    def __init__(self, peft_merge_jobs: AsyncPeftMergeJobsResource) -> None:
        self._peft_merge_jobs = peft_merge_jobs

        self.create = async_to_streamed_response_wrapper(
            peft_merge_jobs.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            peft_merge_jobs.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            peft_merge_jobs.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            peft_merge_jobs.delete,
        )
