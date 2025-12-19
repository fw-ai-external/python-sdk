# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ..types import batch_inference_job_get_params, batch_inference_job_list_params, batch_inference_job_create_params
from .._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..pagination import SyncCursorBatchInferenceJobs, AsyncCursorBatchInferenceJobs
from .._base_client import AsyncPaginator, make_request_options
from ..types.batch_inference_job import BatchInferenceJob

__all__ = ["BatchInferenceJobsResource", "AsyncBatchInferenceJobsResource"]


class BatchInferenceJobsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> BatchInferenceJobsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#accessing-raw-response-data-eg-headers
        """
        return BatchInferenceJobsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> BatchInferenceJobsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#with_streaming_response
        """
        return BatchInferenceJobsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        account_id: str | None = None,
        batch_inference_job_id: str | Omit = omit,
        continued_from_job_name: str | Omit = omit,
        display_name: str | Omit = omit,
        inference_parameters: batch_inference_job_create_params.InferenceParameters | Omit = omit,
        input_dataset_id: str | Omit = omit,
        model: str | Omit = omit,
        output_dataset_id: str | Omit = omit,
        precision: Literal[
            "PRECISION_UNSPECIFIED",
            "FP16",
            "FP8",
            "FP8_MM",
            "FP8_AR",
            "FP8_MM_KV_ATTN",
            "FP8_KV",
            "FP8_MM_V2",
            "FP8_V2",
            "FP8_MM_KV_ATTN_V2",
            "NF4",
            "FP4",
            "BF16",
            "FP4_BLOCKSCALED_MM",
            "FP4_MX_MOE",
        ]
        | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BatchInferenceJob:
        """
        Create Batch Inference Job

        Args:
          batch_inference_job_id: ID of the batch inference job.

          continued_from_job_name: The resource name of the batch inference job that this job continues from. Used
              for lineage tracking to understand job continuation chains.

          inference_parameters: Parameters controlling the inference process.

          input_dataset_id: The name of the dataset used for inference. This is required, except when
              continued_from_job_name is specified.

          model: The name of the model to use for inference. This is required, except when
              continued_from_job_name is specified.

          output_dataset_id: The name of the dataset used for storing the results. This will also contain the
              error file.

          precision: The precision with which the model should be served. If PRECISION_UNSPECIFIED, a
              default will be chosen based on the model.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if account_id is None:
            account_id = self._client._get_account_id_path_param()
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._post(
            f"/v1/accounts/{account_id}/batchInferenceJobs"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/batchInferenceJobs",
            body=maybe_transform(
                {
                    "continued_from_job_name": continued_from_job_name,
                    "display_name": display_name,
                    "inference_parameters": inference_parameters,
                    "input_dataset_id": input_dataset_id,
                    "model": model,
                    "output_dataset_id": output_dataset_id,
                    "precision": precision,
                },
                batch_inference_job_create_params.BatchInferenceJobCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"batch_inference_job_id": batch_inference_job_id},
                    batch_inference_job_create_params.BatchInferenceJobCreateParams,
                ),
            ),
            cast_to=BatchInferenceJob,
        )

    def list(
        self,
        *,
        account_id: str | None = None,
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
    ) -> SyncCursorBatchInferenceJobs[BatchInferenceJob]:
        """
        List Batch Inference Jobs

        Args:
          filter: Only jobs satisfying the provided filter (if specified) will be returned. See
              https://google.aip.dev/160 for the filter grammar.

          order_by: A comma-separated list of fields to order by. e.g. "foo,bar" The default sort
              order is ascending. To specify a descending order for a field, append a " desc"
              suffix. e.g. "foo desc,bar" Subfields are specified with a "." character. e.g.
              "foo.bar" If not specified, the default order is by "created_time".

          page_size: The maximum number of batch inference jobs to return. The maximum page_size is
              200, values above 200 will be coerced to 200. If unspecified, the default is 50.

          page_token: A page token, received from a previous ListBatchInferenceJobs call. Provide this
              to retrieve the subsequent page. When paginating, all other parameters provided
              to ListBatchInferenceJobs must match the call that provided the page token.

          read_mask: The fields to be returned in the response. If empty or "\\**", all fields will be
              returned.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if account_id is None:
            account_id = self._client._get_account_id_path_param()
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._get_api_list(
            f"/v1/accounts/{account_id}/batchInferenceJobs"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/batchInferenceJobs",
            page=SyncCursorBatchInferenceJobs[BatchInferenceJob],
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
                    batch_inference_job_list_params.BatchInferenceJobListParams,
                ),
            ),
            model=BatchInferenceJob,
        )

    def delete(
        self,
        batch_inference_job_id: str,
        *,
        account_id: str | None = None,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Delete Batch Inference Job

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if account_id is None:
            account_id = self._client._get_account_id_path_param()
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not batch_inference_job_id:
            raise ValueError(
                f"Expected a non-empty value for `batch_inference_job_id` but received {batch_inference_job_id!r}"
            )
        return self._delete(
            f"/v1/accounts/{account_id}/batchInferenceJobs/{batch_inference_job_id}"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/batchInferenceJobs/{batch_inference_job_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def get(
        self,
        batch_inference_job_id: str,
        *,
        account_id: str | None = None,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BatchInferenceJob:
        """
        Get Batch Inference Job

        Args:
          read_mask: The fields to be returned in the response. If empty or "\\**", all fields will be
              returned.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if account_id is None:
            account_id = self._client._get_account_id_path_param()
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not batch_inference_job_id:
            raise ValueError(
                f"Expected a non-empty value for `batch_inference_job_id` but received {batch_inference_job_id!r}"
            )
        return self._get(
            f"/v1/accounts/{account_id}/batchInferenceJobs/{batch_inference_job_id}"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/batchInferenceJobs/{batch_inference_job_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"read_mask": read_mask}, batch_inference_job_get_params.BatchInferenceJobGetParams
                ),
            ),
            cast_to=BatchInferenceJob,
        )


class AsyncBatchInferenceJobsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncBatchInferenceJobsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncBatchInferenceJobsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncBatchInferenceJobsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#with_streaming_response
        """
        return AsyncBatchInferenceJobsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        account_id: str | None = None,
        batch_inference_job_id: str | Omit = omit,
        continued_from_job_name: str | Omit = omit,
        display_name: str | Omit = omit,
        inference_parameters: batch_inference_job_create_params.InferenceParameters | Omit = omit,
        input_dataset_id: str | Omit = omit,
        model: str | Omit = omit,
        output_dataset_id: str | Omit = omit,
        precision: Literal[
            "PRECISION_UNSPECIFIED",
            "FP16",
            "FP8",
            "FP8_MM",
            "FP8_AR",
            "FP8_MM_KV_ATTN",
            "FP8_KV",
            "FP8_MM_V2",
            "FP8_V2",
            "FP8_MM_KV_ATTN_V2",
            "NF4",
            "FP4",
            "BF16",
            "FP4_BLOCKSCALED_MM",
            "FP4_MX_MOE",
        ]
        | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BatchInferenceJob:
        """
        Create Batch Inference Job

        Args:
          batch_inference_job_id: ID of the batch inference job.

          continued_from_job_name: The resource name of the batch inference job that this job continues from. Used
              for lineage tracking to understand job continuation chains.

          inference_parameters: Parameters controlling the inference process.

          input_dataset_id: The name of the dataset used for inference. This is required, except when
              continued_from_job_name is specified.

          model: The name of the model to use for inference. This is required, except when
              continued_from_job_name is specified.

          output_dataset_id: The name of the dataset used for storing the results. This will also contain the
              error file.

          precision: The precision with which the model should be served. If PRECISION_UNSPECIFIED, a
              default will be chosen based on the model.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if account_id is None:
            account_id = self._client._get_account_id_path_param()
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._post(
            f"/v1/accounts/{account_id}/batchInferenceJobs"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/batchInferenceJobs",
            body=await async_maybe_transform(
                {
                    "continued_from_job_name": continued_from_job_name,
                    "display_name": display_name,
                    "inference_parameters": inference_parameters,
                    "input_dataset_id": input_dataset_id,
                    "model": model,
                    "output_dataset_id": output_dataset_id,
                    "precision": precision,
                },
                batch_inference_job_create_params.BatchInferenceJobCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"batch_inference_job_id": batch_inference_job_id},
                    batch_inference_job_create_params.BatchInferenceJobCreateParams,
                ),
            ),
            cast_to=BatchInferenceJob,
        )

    def list(
        self,
        *,
        account_id: str | None = None,
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
    ) -> AsyncPaginator[BatchInferenceJob, AsyncCursorBatchInferenceJobs[BatchInferenceJob]]:
        """
        List Batch Inference Jobs

        Args:
          filter: Only jobs satisfying the provided filter (if specified) will be returned. See
              https://google.aip.dev/160 for the filter grammar.

          order_by: A comma-separated list of fields to order by. e.g. "foo,bar" The default sort
              order is ascending. To specify a descending order for a field, append a " desc"
              suffix. e.g. "foo desc,bar" Subfields are specified with a "." character. e.g.
              "foo.bar" If not specified, the default order is by "created_time".

          page_size: The maximum number of batch inference jobs to return. The maximum page_size is
              200, values above 200 will be coerced to 200. If unspecified, the default is 50.

          page_token: A page token, received from a previous ListBatchInferenceJobs call. Provide this
              to retrieve the subsequent page. When paginating, all other parameters provided
              to ListBatchInferenceJobs must match the call that provided the page token.

          read_mask: The fields to be returned in the response. If empty or "\\**", all fields will be
              returned.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if account_id is None:
            account_id = self._client._get_account_id_path_param()
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._get_api_list(
            f"/v1/accounts/{account_id}/batchInferenceJobs"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/batchInferenceJobs",
            page=AsyncCursorBatchInferenceJobs[BatchInferenceJob],
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
                    batch_inference_job_list_params.BatchInferenceJobListParams,
                ),
            ),
            model=BatchInferenceJob,
        )

    async def delete(
        self,
        batch_inference_job_id: str,
        *,
        account_id: str | None = None,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Delete Batch Inference Job

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if account_id is None:
            account_id = self._client._get_account_id_path_param()
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not batch_inference_job_id:
            raise ValueError(
                f"Expected a non-empty value for `batch_inference_job_id` but received {batch_inference_job_id!r}"
            )
        return await self._delete(
            f"/v1/accounts/{account_id}/batchInferenceJobs/{batch_inference_job_id}"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/batchInferenceJobs/{batch_inference_job_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def get(
        self,
        batch_inference_job_id: str,
        *,
        account_id: str | None = None,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BatchInferenceJob:
        """
        Get Batch Inference Job

        Args:
          read_mask: The fields to be returned in the response. If empty or "\\**", all fields will be
              returned.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if account_id is None:
            account_id = self._client._get_account_id_path_param()
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not batch_inference_job_id:
            raise ValueError(
                f"Expected a non-empty value for `batch_inference_job_id` but received {batch_inference_job_id!r}"
            )
        return await self._get(
            f"/v1/accounts/{account_id}/batchInferenceJobs/{batch_inference_job_id}"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/batchInferenceJobs/{batch_inference_job_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"read_mask": read_mask}, batch_inference_job_get_params.BatchInferenceJobGetParams
                ),
            ),
            cast_to=BatchInferenceJob,
        )


class BatchInferenceJobsResourceWithRawResponse:
    def __init__(self, batch_inference_jobs: BatchInferenceJobsResource) -> None:
        self._batch_inference_jobs = batch_inference_jobs

        self.create = to_raw_response_wrapper(
            batch_inference_jobs.create,
        )
        self.list = to_raw_response_wrapper(
            batch_inference_jobs.list,
        )
        self.delete = to_raw_response_wrapper(
            batch_inference_jobs.delete,
        )
        self.get = to_raw_response_wrapper(
            batch_inference_jobs.get,
        )


class AsyncBatchInferenceJobsResourceWithRawResponse:
    def __init__(self, batch_inference_jobs: AsyncBatchInferenceJobsResource) -> None:
        self._batch_inference_jobs = batch_inference_jobs

        self.create = async_to_raw_response_wrapper(
            batch_inference_jobs.create,
        )
        self.list = async_to_raw_response_wrapper(
            batch_inference_jobs.list,
        )
        self.delete = async_to_raw_response_wrapper(
            batch_inference_jobs.delete,
        )
        self.get = async_to_raw_response_wrapper(
            batch_inference_jobs.get,
        )


class BatchInferenceJobsResourceWithStreamingResponse:
    def __init__(self, batch_inference_jobs: BatchInferenceJobsResource) -> None:
        self._batch_inference_jobs = batch_inference_jobs

        self.create = to_streamed_response_wrapper(
            batch_inference_jobs.create,
        )
        self.list = to_streamed_response_wrapper(
            batch_inference_jobs.list,
        )
        self.delete = to_streamed_response_wrapper(
            batch_inference_jobs.delete,
        )
        self.get = to_streamed_response_wrapper(
            batch_inference_jobs.get,
        )


class AsyncBatchInferenceJobsResourceWithStreamingResponse:
    def __init__(self, batch_inference_jobs: AsyncBatchInferenceJobsResource) -> None:
        self._batch_inference_jobs = batch_inference_jobs

        self.create = async_to_streamed_response_wrapper(
            batch_inference_jobs.create,
        )
        self.list = async_to_streamed_response_wrapper(
            batch_inference_jobs.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            batch_inference_jobs.delete,
        )
        self.get = async_to_streamed_response_wrapper(
            batch_inference_jobs.get,
        )
