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
from ...types.accounts import (
    GatewayEvaluationJob,
    evaluation_job_list_params,
    evaluation_job_create_params,
    evaluation_job_retrieve_params,
)
from ...types.accounts.gateway_evaluation_job import GatewayEvaluationJob
from ...types.accounts.evaluation_job_list_response import EvaluationJobListResponse
from ...types.accounts.gateway_evaluation_job_param import GatewayEvaluationJobParam

__all__ = ["EvaluationJobsResource", "AsyncEvaluationJobsResource"]


class EvaluationJobsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> EvaluationJobsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#accessing-raw-response-data-eg-headers
        """
        return EvaluationJobsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> EvaluationJobsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#with_streaming_response
        """
        return EvaluationJobsResourceWithStreamingResponse(self)

    def create(
        self,
        account_id: str,
        *,
        evaluation_job: GatewayEvaluationJobParam,
        evaluation_job_id: str | Omit = omit,
        leaderboard_ids: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayEvaluationJob:
        """
        Create Evaluation Job

        Args:
          leaderboard_ids: Optional leaderboards to attach this job to upon creation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._post(
            f"/v1/accounts/{account_id}/evaluationJobs",
            body=maybe_transform(
                {
                    "evaluation_job": evaluation_job,
                    "evaluation_job_id": evaluation_job_id,
                    "leaderboard_ids": leaderboard_ids,
                },
                evaluation_job_create_params.EvaluationJobCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GatewayEvaluationJob,
        )

    def retrieve(
        self,
        evaluation_job_id: str,
        *,
        account_id: str,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayEvaluationJob:
        """Get Evaluation Job

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
        if not evaluation_job_id:
            raise ValueError(f"Expected a non-empty value for `evaluation_job_id` but received {evaluation_job_id!r}")
        return self._get(
            f"/v1/accounts/{account_id}/evaluationJobs/{evaluation_job_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"read_mask": read_mask}, evaluation_job_retrieve_params.EvaluationJobRetrieveParams
                ),
            ),
            cast_to=GatewayEvaluationJob,
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
    ) -> EvaluationJobListResponse:
        """
        List Evaluation Jobs

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
        return self._get(
            f"/v1/accounts/{account_id}/evaluationJobs",
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
                    evaluation_job_list_params.EvaluationJobListParams,
                ),
            ),
            cast_to=EvaluationJobListResponse,
        )

    def delete(
        self,
        evaluation_job_id: str,
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
        Delete Evaluation Job

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not evaluation_job_id:
            raise ValueError(f"Expected a non-empty value for `evaluation_job_id` but received {evaluation_job_id!r}")
        return self._delete(
            f"/v1/accounts/{account_id}/evaluationJobs/{evaluation_job_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncEvaluationJobsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncEvaluationJobsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncEvaluationJobsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncEvaluationJobsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#with_streaming_response
        """
        return AsyncEvaluationJobsResourceWithStreamingResponse(self)

    async def create(
        self,
        account_id: str,
        *,
        evaluation_job: GatewayEvaluationJobParam,
        evaluation_job_id: str | Omit = omit,
        leaderboard_ids: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayEvaluationJob:
        """
        Create Evaluation Job

        Args:
          leaderboard_ids: Optional leaderboards to attach this job to upon creation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._post(
            f"/v1/accounts/{account_id}/evaluationJobs",
            body=await async_maybe_transform(
                {
                    "evaluation_job": evaluation_job,
                    "evaluation_job_id": evaluation_job_id,
                    "leaderboard_ids": leaderboard_ids,
                },
                evaluation_job_create_params.EvaluationJobCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GatewayEvaluationJob,
        )

    async def retrieve(
        self,
        evaluation_job_id: str,
        *,
        account_id: str,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayEvaluationJob:
        """Get Evaluation Job

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
        if not evaluation_job_id:
            raise ValueError(f"Expected a non-empty value for `evaluation_job_id` but received {evaluation_job_id!r}")
        return await self._get(
            f"/v1/accounts/{account_id}/evaluationJobs/{evaluation_job_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"read_mask": read_mask}, evaluation_job_retrieve_params.EvaluationJobRetrieveParams
                ),
            ),
            cast_to=GatewayEvaluationJob,
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
    ) -> EvaluationJobListResponse:
        """
        List Evaluation Jobs

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
        return await self._get(
            f"/v1/accounts/{account_id}/evaluationJobs",
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
                    evaluation_job_list_params.EvaluationJobListParams,
                ),
            ),
            cast_to=EvaluationJobListResponse,
        )

    async def delete(
        self,
        evaluation_job_id: str,
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
        Delete Evaluation Job

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not evaluation_job_id:
            raise ValueError(f"Expected a non-empty value for `evaluation_job_id` but received {evaluation_job_id!r}")
        return await self._delete(
            f"/v1/accounts/{account_id}/evaluationJobs/{evaluation_job_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class EvaluationJobsResourceWithRawResponse:
    def __init__(self, evaluation_jobs: EvaluationJobsResource) -> None:
        self._evaluation_jobs = evaluation_jobs

        self.create = to_raw_response_wrapper(
            evaluation_jobs.create,
        )
        self.retrieve = to_raw_response_wrapper(
            evaluation_jobs.retrieve,
        )
        self.list = to_raw_response_wrapper(
            evaluation_jobs.list,
        )
        self.delete = to_raw_response_wrapper(
            evaluation_jobs.delete,
        )


class AsyncEvaluationJobsResourceWithRawResponse:
    def __init__(self, evaluation_jobs: AsyncEvaluationJobsResource) -> None:
        self._evaluation_jobs = evaluation_jobs

        self.create = async_to_raw_response_wrapper(
            evaluation_jobs.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            evaluation_jobs.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            evaluation_jobs.list,
        )
        self.delete = async_to_raw_response_wrapper(
            evaluation_jobs.delete,
        )


class EvaluationJobsResourceWithStreamingResponse:
    def __init__(self, evaluation_jobs: EvaluationJobsResource) -> None:
        self._evaluation_jobs = evaluation_jobs

        self.create = to_streamed_response_wrapper(
            evaluation_jobs.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            evaluation_jobs.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            evaluation_jobs.list,
        )
        self.delete = to_streamed_response_wrapper(
            evaluation_jobs.delete,
        )


class AsyncEvaluationJobsResourceWithStreamingResponse:
    def __init__(self, evaluation_jobs: AsyncEvaluationJobsResource) -> None:
        self._evaluation_jobs = evaluation_jobs

        self.create = async_to_streamed_response_wrapper(
            evaluation_jobs.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            evaluation_jobs.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            evaluation_jobs.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            evaluation_jobs.delete,
        )
