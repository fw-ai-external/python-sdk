# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable
from datetime import datetime

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
    batch_job_list_params,
    batch_job_cancel_params,
    batch_job_create_params,
    batch_job_update_params,
    batch_job_get_logs_params,
    batch_job_retrieve_params,
)
from ...types.accounts.gateway_batch_job import GatewayBatchJob
from ...types.accounts.batch_job_list_response import BatchJobListResponse
from ...types.accounts.batch_job_get_logs_response import BatchJobGetLogsResponse
from ...types.accounts.gateway_shell_executor_param import GatewayShellExecutorParam
from ...types.accounts.gateway_python_executor_param import GatewayPythonExecutorParam
from ...types.accounts.gateway_notebook_executor_param import GatewayNotebookExecutorParam

__all__ = ["BatchJobsResource", "AsyncBatchJobsResource"]


class BatchJobsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> BatchJobsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#accessing-raw-response-data-eg-headers
        """
        return BatchJobsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> BatchJobsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#with_streaming_response
        """
        return BatchJobsResourceWithStreamingResponse(self)

    def create(
        self,
        account_id: str,
        *,
        node_pool_id: str,
        annotations: Dict[str, str] | Omit = omit,
        display_name: str | Omit = omit,
        environment_id: str | Omit = omit,
        env_vars: Dict[str, str] | Omit = omit,
        image_ref: str | Omit = omit,
        notebook_executor: GatewayNotebookExecutorParam | Omit = omit,
        num_ranks: int | Omit = omit,
        python_executor: GatewayPythonExecutorParam | Omit = omit,
        role: str | Omit = omit,
        shared: bool | Omit = omit,
        shell_executor: GatewayShellExecutorParam | Omit = omit,
        snapshot_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayBatchJob:
        """Create Batch Job

        Args:
          annotations: Arbitrary, user-specified metadata.

        Keys and values must adhere to Kubernetes
              constraints:
              https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/#syntax-and-character-set
              Additionally, the "fireworks.ai/" prefix is reserved.

          display_name: Human-readable display name of the batch job. e.g. "My Batch Job" Must be fewer
              than 64 characters long.

          environment_id: The ID of the environment that this batch job should use. e.g. my-env If
              specified, image_ref must not be specified.

          env_vars: Environment variables to be passed during this job's execution.

          image_ref: The container image used by this job. If specified, environment_id and
              snapshot_id must not be specified.

          notebook_executor: Execute a notebook file.

          num_ranks: For GPU node pools: one GPU per rank w/ host packing, for CPU node pools: one
              host per rank.

          python_executor: Execute a Python process.

          role: The ARN of the AWS IAM role that the batch job should assume. If not specified,
              the connection will fall back to the node pool's node_role.

          shared: Whether the batch job is shared with all users in the account. This allows all
              users to update, delete, clone, and create environments using the batch job.

          shell_executor: Execute a shell script.

          snapshot_id: The ID of the snapshot used by this batch job. If specified, environment_id must
              be specified and image_ref must not be specified.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._post(
            f"/v1/accounts/{account_id}/batchJobs",
            body=maybe_transform(
                {
                    "node_pool_id": node_pool_id,
                    "annotations": annotations,
                    "display_name": display_name,
                    "environment_id": environment_id,
                    "env_vars": env_vars,
                    "image_ref": image_ref,
                    "notebook_executor": notebook_executor,
                    "num_ranks": num_ranks,
                    "python_executor": python_executor,
                    "role": role,
                    "shared": shared,
                    "shell_executor": shell_executor,
                    "snapshot_id": snapshot_id,
                },
                batch_job_create_params.BatchJobCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GatewayBatchJob,
        )

    def retrieve(
        self,
        batch_job_id: str,
        *,
        account_id: str,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayBatchJob:
        """Get Batch Job

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
        if not batch_job_id:
            raise ValueError(f"Expected a non-empty value for `batch_job_id` but received {batch_job_id!r}")
        return self._get(
            f"/v1/accounts/{account_id}/batchJobs/{batch_job_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"read_mask": read_mask}, batch_job_retrieve_params.BatchJobRetrieveParams),
            ),
            cast_to=GatewayBatchJob,
        )

    def update(
        self,
        batch_job_id: str,
        *,
        account_id: str,
        node_pool_id: str,
        annotations: Dict[str, str] | Omit = omit,
        display_name: str | Omit = omit,
        environment_id: str | Omit = omit,
        env_vars: Dict[str, str] | Omit = omit,
        image_ref: str | Omit = omit,
        notebook_executor: GatewayNotebookExecutorParam | Omit = omit,
        num_ranks: int | Omit = omit,
        python_executor: GatewayPythonExecutorParam | Omit = omit,
        role: str | Omit = omit,
        shared: bool | Omit = omit,
        shell_executor: GatewayShellExecutorParam | Omit = omit,
        snapshot_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayBatchJob:
        """Update Batch Job

        Args:
          annotations: Arbitrary, user-specified metadata.

        Keys and values must adhere to Kubernetes
              constraints:
              https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/#syntax-and-character-set
              Additionally, the "fireworks.ai/" prefix is reserved.

          display_name: Human-readable display name of the batch job. e.g. "My Batch Job" Must be fewer
              than 64 characters long.

          environment_id: The ID of the environment that this batch job should use. e.g. my-env If
              specified, image_ref must not be specified.

          env_vars: Environment variables to be passed during this job's execution.

          image_ref: The container image used by this job. If specified, environment_id and
              snapshot_id must not be specified.

          notebook_executor: Execute a notebook file.

          num_ranks: For GPU node pools: one GPU per rank w/ host packing, for CPU node pools: one
              host per rank.

          python_executor: Execute a Python process.

          role: The ARN of the AWS IAM role that the batch job should assume. If not specified,
              the connection will fall back to the node pool's node_role.

          shared: Whether the batch job is shared with all users in the account. This allows all
              users to update, delete, clone, and create environments using the batch job.

          shell_executor: Execute a shell script.

          snapshot_id: The ID of the snapshot used by this batch job. If specified, environment_id must
              be specified and image_ref must not be specified.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not batch_job_id:
            raise ValueError(f"Expected a non-empty value for `batch_job_id` but received {batch_job_id!r}")
        return self._patch(
            f"/v1/accounts/{account_id}/batchJobs/{batch_job_id}",
            body=maybe_transform(
                {
                    "node_pool_id": node_pool_id,
                    "annotations": annotations,
                    "display_name": display_name,
                    "environment_id": environment_id,
                    "env_vars": env_vars,
                    "image_ref": image_ref,
                    "notebook_executor": notebook_executor,
                    "num_ranks": num_ranks,
                    "python_executor": python_executor,
                    "role": role,
                    "shared": shared,
                    "shell_executor": shell_executor,
                    "snapshot_id": snapshot_id,
                },
                batch_job_update_params.BatchJobUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GatewayBatchJob,
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
    ) -> BatchJobListResponse:
        """
        List Batch Jobs

        Args:
          filter: Only batch jobs satisfying the provided filter (if specified) will be returned.
              See https://google.aip.dev/160 for the filter grammar.

          order_by: A comma-separated list of fields to order by. e.g. "foo,bar" The default sort
              order is ascending. To specify a descending order for a field, append a " desc"
              suffix. e.g. "foo desc,bar" Subfields are specified with a "." character. e.g.
              "foo.bar" If not specified, the default order is by "create_time desc".

          page_size: The maximum number of batch jobs to return. The maximum page_size is 200, values
              above 200 will be coerced to 200. If unspecified, the default is 50.

          page_token: A page token, received from a previous ListBatchJobs call. Provide this to
              retrieve the subsequent page. When paginating, all other parameters provided to
              ListBatchJobs must match the call that provided the page token.

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
            f"/v1/accounts/{account_id}/batchJobs",
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
                    batch_job_list_params.BatchJobListParams,
                ),
            ),
            cast_to=BatchJobListResponse,
        )

    def delete(
        self,
        batch_job_id: str,
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
        Delete Batch Job

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not batch_job_id:
            raise ValueError(f"Expected a non-empty value for `batch_job_id` but received {batch_job_id!r}")
        return self._delete(
            f"/v1/accounts/{account_id}/batchJobs/{batch_job_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def cancel(
        self,
        batch_job_id: str,
        *,
        account_id: str,
        body: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Cancels an existing batch job if it is queued, pending, or running.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not batch_job_id:
            raise ValueError(f"Expected a non-empty value for `batch_job_id` but received {batch_job_id!r}")
        return self._post(
            f"/v1/accounts/{account_id}/batchJobs/{batch_job_id}:cancel",
            body=maybe_transform(body, batch_job_cancel_params.BatchJobCancelParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def get_logs(
        self,
        batch_job_id: str,
        *,
        account_id: str,
        filter: str | Omit = omit,
        page_size: int | Omit = omit,
        page_token: str | Omit = omit,
        ranks: Iterable[int] | Omit = omit,
        read_mask: str | Omit = omit,
        start_from_head: bool | Omit = omit,
        start_time: Union[str, datetime] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BatchJobGetLogsResponse:
        """
        Get Batch Job Logs

        Args:
          filter: Only entries matching this filter will be returned. Currently only basic
              substring match is performed.

          page_size: The maximum number of log entries to return. The maximum page_size is 10,000,
              values above 10,000 will be coerced to 10,000. If unspecified, the default
              is 100.

          page_token: A page token, received from a previous GetBatchJobLogsRequest call. Provide this
              to retrieve the subsequent page. When paginating, all other parameters provided
              to GetBatchJobLogsRequest must match the call that provided the page token.

          ranks: Ranks, for which to fetch logs.

          read_mask: The fields to be returned in the response. If empty or "\\**", all fields will be
              returned.

          start_from_head: Pagination direction, time-wise reverse direction by default (false).

          start_time: Entries before this timestamp won't be returned. If not specified, up to
              page_size last records will be returned.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not batch_job_id:
            raise ValueError(f"Expected a non-empty value for `batch_job_id` but received {batch_job_id!r}")
        return self._get(
            f"/v1/accounts/{account_id}/batchJobs/{batch_job_id}:getLogs",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "filter": filter,
                        "page_size": page_size,
                        "page_token": page_token,
                        "ranks": ranks,
                        "read_mask": read_mask,
                        "start_from_head": start_from_head,
                        "start_time": start_time,
                    },
                    batch_job_get_logs_params.BatchJobGetLogsParams,
                ),
            ),
            cast_to=BatchJobGetLogsResponse,
        )


class AsyncBatchJobsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncBatchJobsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncBatchJobsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncBatchJobsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#with_streaming_response
        """
        return AsyncBatchJobsResourceWithStreamingResponse(self)

    async def create(
        self,
        account_id: str,
        *,
        node_pool_id: str,
        annotations: Dict[str, str] | Omit = omit,
        display_name: str | Omit = omit,
        environment_id: str | Omit = omit,
        env_vars: Dict[str, str] | Omit = omit,
        image_ref: str | Omit = omit,
        notebook_executor: GatewayNotebookExecutorParam | Omit = omit,
        num_ranks: int | Omit = omit,
        python_executor: GatewayPythonExecutorParam | Omit = omit,
        role: str | Omit = omit,
        shared: bool | Omit = omit,
        shell_executor: GatewayShellExecutorParam | Omit = omit,
        snapshot_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayBatchJob:
        """Create Batch Job

        Args:
          annotations: Arbitrary, user-specified metadata.

        Keys and values must adhere to Kubernetes
              constraints:
              https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/#syntax-and-character-set
              Additionally, the "fireworks.ai/" prefix is reserved.

          display_name: Human-readable display name of the batch job. e.g. "My Batch Job" Must be fewer
              than 64 characters long.

          environment_id: The ID of the environment that this batch job should use. e.g. my-env If
              specified, image_ref must not be specified.

          env_vars: Environment variables to be passed during this job's execution.

          image_ref: The container image used by this job. If specified, environment_id and
              snapshot_id must not be specified.

          notebook_executor: Execute a notebook file.

          num_ranks: For GPU node pools: one GPU per rank w/ host packing, for CPU node pools: one
              host per rank.

          python_executor: Execute a Python process.

          role: The ARN of the AWS IAM role that the batch job should assume. If not specified,
              the connection will fall back to the node pool's node_role.

          shared: Whether the batch job is shared with all users in the account. This allows all
              users to update, delete, clone, and create environments using the batch job.

          shell_executor: Execute a shell script.

          snapshot_id: The ID of the snapshot used by this batch job. If specified, environment_id must
              be specified and image_ref must not be specified.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._post(
            f"/v1/accounts/{account_id}/batchJobs",
            body=await async_maybe_transform(
                {
                    "node_pool_id": node_pool_id,
                    "annotations": annotations,
                    "display_name": display_name,
                    "environment_id": environment_id,
                    "env_vars": env_vars,
                    "image_ref": image_ref,
                    "notebook_executor": notebook_executor,
                    "num_ranks": num_ranks,
                    "python_executor": python_executor,
                    "role": role,
                    "shared": shared,
                    "shell_executor": shell_executor,
                    "snapshot_id": snapshot_id,
                },
                batch_job_create_params.BatchJobCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GatewayBatchJob,
        )

    async def retrieve(
        self,
        batch_job_id: str,
        *,
        account_id: str,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayBatchJob:
        """Get Batch Job

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
        if not batch_job_id:
            raise ValueError(f"Expected a non-empty value for `batch_job_id` but received {batch_job_id!r}")
        return await self._get(
            f"/v1/accounts/{account_id}/batchJobs/{batch_job_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"read_mask": read_mask}, batch_job_retrieve_params.BatchJobRetrieveParams
                ),
            ),
            cast_to=GatewayBatchJob,
        )

    async def update(
        self,
        batch_job_id: str,
        *,
        account_id: str,
        node_pool_id: str,
        annotations: Dict[str, str] | Omit = omit,
        display_name: str | Omit = omit,
        environment_id: str | Omit = omit,
        env_vars: Dict[str, str] | Omit = omit,
        image_ref: str | Omit = omit,
        notebook_executor: GatewayNotebookExecutorParam | Omit = omit,
        num_ranks: int | Omit = omit,
        python_executor: GatewayPythonExecutorParam | Omit = omit,
        role: str | Omit = omit,
        shared: bool | Omit = omit,
        shell_executor: GatewayShellExecutorParam | Omit = omit,
        snapshot_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayBatchJob:
        """Update Batch Job

        Args:
          annotations: Arbitrary, user-specified metadata.

        Keys and values must adhere to Kubernetes
              constraints:
              https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/#syntax-and-character-set
              Additionally, the "fireworks.ai/" prefix is reserved.

          display_name: Human-readable display name of the batch job. e.g. "My Batch Job" Must be fewer
              than 64 characters long.

          environment_id: The ID of the environment that this batch job should use. e.g. my-env If
              specified, image_ref must not be specified.

          env_vars: Environment variables to be passed during this job's execution.

          image_ref: The container image used by this job. If specified, environment_id and
              snapshot_id must not be specified.

          notebook_executor: Execute a notebook file.

          num_ranks: For GPU node pools: one GPU per rank w/ host packing, for CPU node pools: one
              host per rank.

          python_executor: Execute a Python process.

          role: The ARN of the AWS IAM role that the batch job should assume. If not specified,
              the connection will fall back to the node pool's node_role.

          shared: Whether the batch job is shared with all users in the account. This allows all
              users to update, delete, clone, and create environments using the batch job.

          shell_executor: Execute a shell script.

          snapshot_id: The ID of the snapshot used by this batch job. If specified, environment_id must
              be specified and image_ref must not be specified.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not batch_job_id:
            raise ValueError(f"Expected a non-empty value for `batch_job_id` but received {batch_job_id!r}")
        return await self._patch(
            f"/v1/accounts/{account_id}/batchJobs/{batch_job_id}",
            body=await async_maybe_transform(
                {
                    "node_pool_id": node_pool_id,
                    "annotations": annotations,
                    "display_name": display_name,
                    "environment_id": environment_id,
                    "env_vars": env_vars,
                    "image_ref": image_ref,
                    "notebook_executor": notebook_executor,
                    "num_ranks": num_ranks,
                    "python_executor": python_executor,
                    "role": role,
                    "shared": shared,
                    "shell_executor": shell_executor,
                    "snapshot_id": snapshot_id,
                },
                batch_job_update_params.BatchJobUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GatewayBatchJob,
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
    ) -> BatchJobListResponse:
        """
        List Batch Jobs

        Args:
          filter: Only batch jobs satisfying the provided filter (if specified) will be returned.
              See https://google.aip.dev/160 for the filter grammar.

          order_by: A comma-separated list of fields to order by. e.g. "foo,bar" The default sort
              order is ascending. To specify a descending order for a field, append a " desc"
              suffix. e.g. "foo desc,bar" Subfields are specified with a "." character. e.g.
              "foo.bar" If not specified, the default order is by "create_time desc".

          page_size: The maximum number of batch jobs to return. The maximum page_size is 200, values
              above 200 will be coerced to 200. If unspecified, the default is 50.

          page_token: A page token, received from a previous ListBatchJobs call. Provide this to
              retrieve the subsequent page. When paginating, all other parameters provided to
              ListBatchJobs must match the call that provided the page token.

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
            f"/v1/accounts/{account_id}/batchJobs",
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
                    batch_job_list_params.BatchJobListParams,
                ),
            ),
            cast_to=BatchJobListResponse,
        )

    async def delete(
        self,
        batch_job_id: str,
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
        Delete Batch Job

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not batch_job_id:
            raise ValueError(f"Expected a non-empty value for `batch_job_id` but received {batch_job_id!r}")
        return await self._delete(
            f"/v1/accounts/{account_id}/batchJobs/{batch_job_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def cancel(
        self,
        batch_job_id: str,
        *,
        account_id: str,
        body: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Cancels an existing batch job if it is queued, pending, or running.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not batch_job_id:
            raise ValueError(f"Expected a non-empty value for `batch_job_id` but received {batch_job_id!r}")
        return await self._post(
            f"/v1/accounts/{account_id}/batchJobs/{batch_job_id}:cancel",
            body=await async_maybe_transform(body, batch_job_cancel_params.BatchJobCancelParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def get_logs(
        self,
        batch_job_id: str,
        *,
        account_id: str,
        filter: str | Omit = omit,
        page_size: int | Omit = omit,
        page_token: str | Omit = omit,
        ranks: Iterable[int] | Omit = omit,
        read_mask: str | Omit = omit,
        start_from_head: bool | Omit = omit,
        start_time: Union[str, datetime] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BatchJobGetLogsResponse:
        """
        Get Batch Job Logs

        Args:
          filter: Only entries matching this filter will be returned. Currently only basic
              substring match is performed.

          page_size: The maximum number of log entries to return. The maximum page_size is 10,000,
              values above 10,000 will be coerced to 10,000. If unspecified, the default
              is 100.

          page_token: A page token, received from a previous GetBatchJobLogsRequest call. Provide this
              to retrieve the subsequent page. When paginating, all other parameters provided
              to GetBatchJobLogsRequest must match the call that provided the page token.

          ranks: Ranks, for which to fetch logs.

          read_mask: The fields to be returned in the response. If empty or "\\**", all fields will be
              returned.

          start_from_head: Pagination direction, time-wise reverse direction by default (false).

          start_time: Entries before this timestamp won't be returned. If not specified, up to
              page_size last records will be returned.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not batch_job_id:
            raise ValueError(f"Expected a non-empty value for `batch_job_id` but received {batch_job_id!r}")
        return await self._get(
            f"/v1/accounts/{account_id}/batchJobs/{batch_job_id}:getLogs",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "filter": filter,
                        "page_size": page_size,
                        "page_token": page_token,
                        "ranks": ranks,
                        "read_mask": read_mask,
                        "start_from_head": start_from_head,
                        "start_time": start_time,
                    },
                    batch_job_get_logs_params.BatchJobGetLogsParams,
                ),
            ),
            cast_to=BatchJobGetLogsResponse,
        )


class BatchJobsResourceWithRawResponse:
    def __init__(self, batch_jobs: BatchJobsResource) -> None:
        self._batch_jobs = batch_jobs

        self.create = to_raw_response_wrapper(
            batch_jobs.create,
        )
        self.retrieve = to_raw_response_wrapper(
            batch_jobs.retrieve,
        )
        self.update = to_raw_response_wrapper(
            batch_jobs.update,
        )
        self.list = to_raw_response_wrapper(
            batch_jobs.list,
        )
        self.delete = to_raw_response_wrapper(
            batch_jobs.delete,
        )
        self.cancel = to_raw_response_wrapper(
            batch_jobs.cancel,
        )
        self.get_logs = to_raw_response_wrapper(
            batch_jobs.get_logs,
        )


class AsyncBatchJobsResourceWithRawResponse:
    def __init__(self, batch_jobs: AsyncBatchJobsResource) -> None:
        self._batch_jobs = batch_jobs

        self.create = async_to_raw_response_wrapper(
            batch_jobs.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            batch_jobs.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            batch_jobs.update,
        )
        self.list = async_to_raw_response_wrapper(
            batch_jobs.list,
        )
        self.delete = async_to_raw_response_wrapper(
            batch_jobs.delete,
        )
        self.cancel = async_to_raw_response_wrapper(
            batch_jobs.cancel,
        )
        self.get_logs = async_to_raw_response_wrapper(
            batch_jobs.get_logs,
        )


class BatchJobsResourceWithStreamingResponse:
    def __init__(self, batch_jobs: BatchJobsResource) -> None:
        self._batch_jobs = batch_jobs

        self.create = to_streamed_response_wrapper(
            batch_jobs.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            batch_jobs.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            batch_jobs.update,
        )
        self.list = to_streamed_response_wrapper(
            batch_jobs.list,
        )
        self.delete = to_streamed_response_wrapper(
            batch_jobs.delete,
        )
        self.cancel = to_streamed_response_wrapper(
            batch_jobs.cancel,
        )
        self.get_logs = to_streamed_response_wrapper(
            batch_jobs.get_logs,
        )


class AsyncBatchJobsResourceWithStreamingResponse:
    def __init__(self, batch_jobs: AsyncBatchJobsResource) -> None:
        self._batch_jobs = batch_jobs

        self.create = async_to_streamed_response_wrapper(
            batch_jobs.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            batch_jobs.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            batch_jobs.update,
        )
        self.list = async_to_streamed_response_wrapper(
            batch_jobs.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            batch_jobs.delete,
        )
        self.cancel = async_to_streamed_response_wrapper(
            batch_jobs.cancel,
        )
        self.get_logs = async_to_streamed_response_wrapper(
            batch_jobs.get_logs,
        )
