# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import dpo_job_get_params, dpo_job_list_params, dpo_job_create_params
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
from .._base_client import make_request_options
from ..types.dpo_job import DpoJob
from ..types.dpo_job_list_response import DpoJobListResponse
from ..types.shared_params.wandb_config import WandbConfig
from ..types.shared_params.training_config import TrainingConfig
from ..types.dpo_job_get_metrics_file_endpoint_response import DpoJobGetMetricsFileEndpointResponse

__all__ = ["DpoJobsResource", "AsyncDpoJobsResource"]


class DpoJobsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> DpoJobsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#accessing-raw-response-data-eg-headers
        """
        return DpoJobsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DpoJobsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#with_streaming_response
        """
        return DpoJobsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        account_id: str | None = None,
        dataset: str,
        dpo_job_id: str | Omit = omit,
        display_name: str | Omit = omit,
        training_config: TrainingConfig | Omit = omit,
        wandb_config: WandbConfig | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DpoJob:
        """
        Args:
          dataset: The name of the dataset used for training.

          dpo_job_id: ID of the DPO job, a random ID will be generated if not specified.

          training_config: Common training configurations.

          wandb_config: The Weights & Biases team/user account for logging job progress.

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
            f"/v1/accounts/{account_id}/dpoJobs"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/dpoJobs",
            body=maybe_transform(
                {
                    "dataset": dataset,
                    "display_name": display_name,
                    "training_config": training_config,
                    "wandb_config": wandb_config,
                },
                dpo_job_create_params.DpoJobCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"dpo_job_id": dpo_job_id}, dpo_job_create_params.DpoJobCreateParams),
            ),
            cast_to=DpoJob,
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
    ) -> DpoJobListResponse:
        """Args:
          filter: Filter criteria for the returned jobs.

        See https://google.aip.dev/160 for the
              filter syntax specification.

          order_by: A comma-separated list of fields to order by. e.g. "foo,bar" The default sort
              order is ascending. To specify a descending order for a field, append a " desc"
              suffix. e.g. "foo desc,bar" Subfields are specified with a "." character. e.g.
              "foo.bar" If not specified, the default order is by "name".

          page_size: The maximum number of dpo jobs to return. The maximum page_size is 200, values
              above 200 will be coerced to 200. If unspecified, the default is 50.

          page_token: A page token, received from a previous ListDpoJobs call. Provide this to
              retrieve the subsequent page. When paginating, all other parameters provided to
              ListDpoJobs must match the call that provided the page token.

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
        return self._get(
            f"/v1/accounts/{account_id}/dpoJobs"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/dpoJobs",
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
                    dpo_job_list_params.DpoJobListParams,
                ),
            ),
            cast_to=DpoJobListResponse,
        )

    def delete(
        self,
        dpo_job_id: str,
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
        if not dpo_job_id:
            raise ValueError(f"Expected a non-empty value for `dpo_job_id` but received {dpo_job_id!r}")
        return self._delete(
            f"/v1/accounts/{account_id}/dpoJobs/{dpo_job_id}"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/dpoJobs/{dpo_job_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def get(
        self,
        dpo_job_id: str,
        *,
        account_id: str | None = None,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DpoJob:
        """Args:
          read_mask: The fields to be returned in the response.

        If empty or "\\**", all fields will be
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
        if not dpo_job_id:
            raise ValueError(f"Expected a non-empty value for `dpo_job_id` but received {dpo_job_id!r}")
        return self._get(
            f"/v1/accounts/{account_id}/dpoJobs/{dpo_job_id}"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/dpoJobs/{dpo_job_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"read_mask": read_mask}, dpo_job_get_params.DpoJobGetParams),
            ),
            cast_to=DpoJob,
        )

    def get_metrics_file_endpoint(
        self,
        dpo_job_id: str,
        *,
        account_id: str | None = None,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DpoJobGetMetricsFileEndpointResponse:
        """
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
        if not dpo_job_id:
            raise ValueError(f"Expected a non-empty value for `dpo_job_id` but received {dpo_job_id!r}")
        return self._get(
            f"/v1/accounts/{account_id}/dpoJobs/{dpo_job_id}:getMetricsFileEndpoint"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/dpoJobs/{dpo_job_id}:getMetricsFileEndpoint",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DpoJobGetMetricsFileEndpointResponse,
        )


class AsyncDpoJobsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncDpoJobsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncDpoJobsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDpoJobsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#with_streaming_response
        """
        return AsyncDpoJobsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        account_id: str | None = None,
        dataset: str,
        dpo_job_id: str | Omit = omit,
        display_name: str | Omit = omit,
        training_config: TrainingConfig | Omit = omit,
        wandb_config: WandbConfig | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DpoJob:
        """
        Args:
          dataset: The name of the dataset used for training.

          dpo_job_id: ID of the DPO job, a random ID will be generated if not specified.

          training_config: Common training configurations.

          wandb_config: The Weights & Biases team/user account for logging job progress.

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
            f"/v1/accounts/{account_id}/dpoJobs"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/dpoJobs",
            body=await async_maybe_transform(
                {
                    "dataset": dataset,
                    "display_name": display_name,
                    "training_config": training_config,
                    "wandb_config": wandb_config,
                },
                dpo_job_create_params.DpoJobCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"dpo_job_id": dpo_job_id}, dpo_job_create_params.DpoJobCreateParams),
            ),
            cast_to=DpoJob,
        )

    async def list(
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
    ) -> DpoJobListResponse:
        """Args:
          filter: Filter criteria for the returned jobs.

        See https://google.aip.dev/160 for the
              filter syntax specification.

          order_by: A comma-separated list of fields to order by. e.g. "foo,bar" The default sort
              order is ascending. To specify a descending order for a field, append a " desc"
              suffix. e.g. "foo desc,bar" Subfields are specified with a "." character. e.g.
              "foo.bar" If not specified, the default order is by "name".

          page_size: The maximum number of dpo jobs to return. The maximum page_size is 200, values
              above 200 will be coerced to 200. If unspecified, the default is 50.

          page_token: A page token, received from a previous ListDpoJobs call. Provide this to
              retrieve the subsequent page. When paginating, all other parameters provided to
              ListDpoJobs must match the call that provided the page token.

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
        return await self._get(
            f"/v1/accounts/{account_id}/dpoJobs"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/dpoJobs",
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
                    dpo_job_list_params.DpoJobListParams,
                ),
            ),
            cast_to=DpoJobListResponse,
        )

    async def delete(
        self,
        dpo_job_id: str,
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
        if not dpo_job_id:
            raise ValueError(f"Expected a non-empty value for `dpo_job_id` but received {dpo_job_id!r}")
        return await self._delete(
            f"/v1/accounts/{account_id}/dpoJobs/{dpo_job_id}"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/dpoJobs/{dpo_job_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def get(
        self,
        dpo_job_id: str,
        *,
        account_id: str | None = None,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DpoJob:
        """Args:
          read_mask: The fields to be returned in the response.

        If empty or "\\**", all fields will be
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
        if not dpo_job_id:
            raise ValueError(f"Expected a non-empty value for `dpo_job_id` but received {dpo_job_id!r}")
        return await self._get(
            f"/v1/accounts/{account_id}/dpoJobs/{dpo_job_id}"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/dpoJobs/{dpo_job_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"read_mask": read_mask}, dpo_job_get_params.DpoJobGetParams),
            ),
            cast_to=DpoJob,
        )

    async def get_metrics_file_endpoint(
        self,
        dpo_job_id: str,
        *,
        account_id: str | None = None,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DpoJobGetMetricsFileEndpointResponse:
        """
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
        if not dpo_job_id:
            raise ValueError(f"Expected a non-empty value for `dpo_job_id` but received {dpo_job_id!r}")
        return await self._get(
            f"/v1/accounts/{account_id}/dpoJobs/{dpo_job_id}:getMetricsFileEndpoint"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/dpoJobs/{dpo_job_id}:getMetricsFileEndpoint",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DpoJobGetMetricsFileEndpointResponse,
        )


class DpoJobsResourceWithRawResponse:
    def __init__(self, dpo_jobs: DpoJobsResource) -> None:
        self._dpo_jobs = dpo_jobs

        self.create = to_raw_response_wrapper(
            dpo_jobs.create,
        )
        self.list = to_raw_response_wrapper(
            dpo_jobs.list,
        )
        self.delete = to_raw_response_wrapper(
            dpo_jobs.delete,
        )
        self.get = to_raw_response_wrapper(
            dpo_jobs.get,
        )
        self.get_metrics_file_endpoint = to_raw_response_wrapper(
            dpo_jobs.get_metrics_file_endpoint,
        )


class AsyncDpoJobsResourceWithRawResponse:
    def __init__(self, dpo_jobs: AsyncDpoJobsResource) -> None:
        self._dpo_jobs = dpo_jobs

        self.create = async_to_raw_response_wrapper(
            dpo_jobs.create,
        )
        self.list = async_to_raw_response_wrapper(
            dpo_jobs.list,
        )
        self.delete = async_to_raw_response_wrapper(
            dpo_jobs.delete,
        )
        self.get = async_to_raw_response_wrapper(
            dpo_jobs.get,
        )
        self.get_metrics_file_endpoint = async_to_raw_response_wrapper(
            dpo_jobs.get_metrics_file_endpoint,
        )


class DpoJobsResourceWithStreamingResponse:
    def __init__(self, dpo_jobs: DpoJobsResource) -> None:
        self._dpo_jobs = dpo_jobs

        self.create = to_streamed_response_wrapper(
            dpo_jobs.create,
        )
        self.list = to_streamed_response_wrapper(
            dpo_jobs.list,
        )
        self.delete = to_streamed_response_wrapper(
            dpo_jobs.delete,
        )
        self.get = to_streamed_response_wrapper(
            dpo_jobs.get,
        )
        self.get_metrics_file_endpoint = to_streamed_response_wrapper(
            dpo_jobs.get_metrics_file_endpoint,
        )


class AsyncDpoJobsResourceWithStreamingResponse:
    def __init__(self, dpo_jobs: AsyncDpoJobsResource) -> None:
        self._dpo_jobs = dpo_jobs

        self.create = async_to_streamed_response_wrapper(
            dpo_jobs.create,
        )
        self.list = async_to_streamed_response_wrapper(
            dpo_jobs.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            dpo_jobs.delete,
        )
        self.get = async_to_streamed_response_wrapper(
            dpo_jobs.get,
        )
        self.get_metrics_file_endpoint = async_to_streamed_response_wrapper(
            dpo_jobs.get_metrics_file_endpoint,
        )
