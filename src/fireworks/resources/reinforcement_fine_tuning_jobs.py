# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import (
    reinforcement_fine_tuning_job_get_params,
    reinforcement_fine_tuning_job_list_params,
    reinforcement_fine_tuning_job_create_params,
)
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
from ..types.reinforcement_fine_tuning_job import ReinforcementFineTuningJob
from ..types.reinforcement_fine_tuning_job_list_response import ReinforcementFineTuningJobListResponse

__all__ = ["ReinforcementFineTuningJobsResource", "AsyncReinforcementFineTuningJobsResource"]


class ReinforcementFineTuningJobsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ReinforcementFineTuningJobsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#accessing-raw-response-data-eg-headers
        """
        return ReinforcementFineTuningJobsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ReinforcementFineTuningJobsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#with_streaming_response
        """
        return ReinforcementFineTuningJobsResourceWithStreamingResponse(self)

    def create(
        self,
        account_id: str,
        *,
        dataset: str,
        evaluator: str,
        reinforcement_fine_tuning_job_id: str | Omit = omit,
        display_name: str | Omit = omit,
        eval_auto_carveout: bool | Omit = omit,
        evaluation_dataset: str | Omit = omit,
        inference_parameters: reinforcement_fine_tuning_job_create_params.InferenceParameters | Omit = omit,
        mcp_server: str | Omit = omit,
        training_config: reinforcement_fine_tuning_job_create_params.TrainingConfig | Omit = omit,
        wandb_config: reinforcement_fine_tuning_job_create_params.WandbConfig | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ReinforcementFineTuningJob:
        """
        Create Reinforcement Fine-tuning Job

        Args:
          dataset: The name of the dataset used for training.

          evaluator: The evaluator resource name to use for RLOR fine-tuning job.

          reinforcement_fine_tuning_job_id: ID of the reinforcement fine-tuning job, a random UUID will be generated if not
              specified.

          eval_auto_carveout: Whether to auto-carve the dataset for eval.

          evaluation_dataset: The name of a separate dataset to use for evaluation.

          inference_parameters: BIJ parameters.

          training_config: Common training configurations.

          wandb_config: The Weights & Biases team/user account for logging training progress.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._post(
            f"/v1/accounts/{account_id}/reinforcementFineTuningJobs"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/reinforcementFineTuningJobs",
            body=maybe_transform(
                {
                    "dataset": dataset,
                    "evaluator": evaluator,
                    "display_name": display_name,
                    "eval_auto_carveout": eval_auto_carveout,
                    "evaluation_dataset": evaluation_dataset,
                    "inference_parameters": inference_parameters,
                    "mcp_server": mcp_server,
                    "training_config": training_config,
                    "wandb_config": wandb_config,
                },
                reinforcement_fine_tuning_job_create_params.ReinforcementFineTuningJobCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"reinforcement_fine_tuning_job_id": reinforcement_fine_tuning_job_id},
                    reinforcement_fine_tuning_job_create_params.ReinforcementFineTuningJobCreateParams,
                ),
            ),
            cast_to=ReinforcementFineTuningJob,
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
    ) -> ReinforcementFineTuningJobListResponse:
        """
        List Reinforcement Fine-tuning Jobs

        Args:
          filter: Filter criteria for the returned jobs. See https://google.aip.dev/160 for the
              filter syntax specification.

          order_by: A comma-separated list of fields to order by. e.g. "foo,bar" The default sort
              order is ascending. To specify a descending order for a field, append a " desc"
              suffix. e.g. "foo desc,bar" Subfields are specified with a "." character. e.g.
              "foo.bar" If not specified, the default order is by "name".

          page_size: The maximum number of fine-tuning jobs to return. The maximum page_size is 200,
              values above 200 will be coerced to 200. If unspecified, the default is 50.

          page_token: A page token, received from a previous ListReinforcementLearningFineTuningJobs
              call. Provide this to retrieve the subsequent page. When paginating, all other
              parameters provided to ListReinforcementLearningFineTuningJobs must match the
              call that provided the page token.

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
            f"/v1/accounts/{account_id}/reinforcementFineTuningJobs"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/reinforcementFineTuningJobs",
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
                    reinforcement_fine_tuning_job_list_params.ReinforcementFineTuningJobListParams,
                ),
            ),
            cast_to=ReinforcementFineTuningJobListResponse,
        )

    def delete(
        self,
        reinforcement_fine_tuning_job_id: str,
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
        Delete Reinforcement Fine-tuning Job

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not reinforcement_fine_tuning_job_id:
            raise ValueError(
                f"Expected a non-empty value for `reinforcement_fine_tuning_job_id` but received {reinforcement_fine_tuning_job_id!r}"
            )
        return self._delete(
            f"/v1/accounts/{account_id}/reinforcementFineTuningJobs/{reinforcement_fine_tuning_job_id}"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/reinforcementFineTuningJobs/{reinforcement_fine_tuning_job_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def get(
        self,
        reinforcement_fine_tuning_job_id: str,
        *,
        account_id: str,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ReinforcementFineTuningJob:
        """
        Get Reinforcement Fine-tuning Job

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
        if not reinforcement_fine_tuning_job_id:
            raise ValueError(
                f"Expected a non-empty value for `reinforcement_fine_tuning_job_id` but received {reinforcement_fine_tuning_job_id!r}"
            )
        return self._get(
            f"/v1/accounts/{account_id}/reinforcementFineTuningJobs/{reinforcement_fine_tuning_job_id}"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/reinforcementFineTuningJobs/{reinforcement_fine_tuning_job_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"read_mask": read_mask},
                    reinforcement_fine_tuning_job_get_params.ReinforcementFineTuningJobGetParams,
                ),
            ),
            cast_to=ReinforcementFineTuningJob,
        )


class AsyncReinforcementFineTuningJobsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncReinforcementFineTuningJobsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncReinforcementFineTuningJobsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncReinforcementFineTuningJobsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#with_streaming_response
        """
        return AsyncReinforcementFineTuningJobsResourceWithStreamingResponse(self)

    async def create(
        self,
        account_id: str,
        *,
        dataset: str,
        evaluator: str,
        reinforcement_fine_tuning_job_id: str | Omit = omit,
        display_name: str | Omit = omit,
        eval_auto_carveout: bool | Omit = omit,
        evaluation_dataset: str | Omit = omit,
        inference_parameters: reinforcement_fine_tuning_job_create_params.InferenceParameters | Omit = omit,
        mcp_server: str | Omit = omit,
        training_config: reinforcement_fine_tuning_job_create_params.TrainingConfig | Omit = omit,
        wandb_config: reinforcement_fine_tuning_job_create_params.WandbConfig | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ReinforcementFineTuningJob:
        """
        Create Reinforcement Fine-tuning Job

        Args:
          dataset: The name of the dataset used for training.

          evaluator: The evaluator resource name to use for RLOR fine-tuning job.

          reinforcement_fine_tuning_job_id: ID of the reinforcement fine-tuning job, a random UUID will be generated if not
              specified.

          eval_auto_carveout: Whether to auto-carve the dataset for eval.

          evaluation_dataset: The name of a separate dataset to use for evaluation.

          inference_parameters: BIJ parameters.

          training_config: Common training configurations.

          wandb_config: The Weights & Biases team/user account for logging training progress.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._post(
            f"/v1/accounts/{account_id}/reinforcementFineTuningJobs"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/reinforcementFineTuningJobs",
            body=await async_maybe_transform(
                {
                    "dataset": dataset,
                    "evaluator": evaluator,
                    "display_name": display_name,
                    "eval_auto_carveout": eval_auto_carveout,
                    "evaluation_dataset": evaluation_dataset,
                    "inference_parameters": inference_parameters,
                    "mcp_server": mcp_server,
                    "training_config": training_config,
                    "wandb_config": wandb_config,
                },
                reinforcement_fine_tuning_job_create_params.ReinforcementFineTuningJobCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"reinforcement_fine_tuning_job_id": reinforcement_fine_tuning_job_id},
                    reinforcement_fine_tuning_job_create_params.ReinforcementFineTuningJobCreateParams,
                ),
            ),
            cast_to=ReinforcementFineTuningJob,
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
    ) -> ReinforcementFineTuningJobListResponse:
        """
        List Reinforcement Fine-tuning Jobs

        Args:
          filter: Filter criteria for the returned jobs. See https://google.aip.dev/160 for the
              filter syntax specification.

          order_by: A comma-separated list of fields to order by. e.g. "foo,bar" The default sort
              order is ascending. To specify a descending order for a field, append a " desc"
              suffix. e.g. "foo desc,bar" Subfields are specified with a "." character. e.g.
              "foo.bar" If not specified, the default order is by "name".

          page_size: The maximum number of fine-tuning jobs to return. The maximum page_size is 200,
              values above 200 will be coerced to 200. If unspecified, the default is 50.

          page_token: A page token, received from a previous ListReinforcementLearningFineTuningJobs
              call. Provide this to retrieve the subsequent page. When paginating, all other
              parameters provided to ListReinforcementLearningFineTuningJobs must match the
              call that provided the page token.

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
            f"/v1/accounts/{account_id}/reinforcementFineTuningJobs"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/reinforcementFineTuningJobs",
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
                    reinforcement_fine_tuning_job_list_params.ReinforcementFineTuningJobListParams,
                ),
            ),
            cast_to=ReinforcementFineTuningJobListResponse,
        )

    async def delete(
        self,
        reinforcement_fine_tuning_job_id: str,
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
        Delete Reinforcement Fine-tuning Job

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not reinforcement_fine_tuning_job_id:
            raise ValueError(
                f"Expected a non-empty value for `reinforcement_fine_tuning_job_id` but received {reinforcement_fine_tuning_job_id!r}"
            )
        return await self._delete(
            f"/v1/accounts/{account_id}/reinforcementFineTuningJobs/{reinforcement_fine_tuning_job_id}"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/reinforcementFineTuningJobs/{reinforcement_fine_tuning_job_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def get(
        self,
        reinforcement_fine_tuning_job_id: str,
        *,
        account_id: str,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ReinforcementFineTuningJob:
        """
        Get Reinforcement Fine-tuning Job

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
        if not reinforcement_fine_tuning_job_id:
            raise ValueError(
                f"Expected a non-empty value for `reinforcement_fine_tuning_job_id` but received {reinforcement_fine_tuning_job_id!r}"
            )
        return await self._get(
            f"/v1/accounts/{account_id}/reinforcementFineTuningJobs/{reinforcement_fine_tuning_job_id}"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/reinforcementFineTuningJobs/{reinforcement_fine_tuning_job_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"read_mask": read_mask},
                    reinforcement_fine_tuning_job_get_params.ReinforcementFineTuningJobGetParams,
                ),
            ),
            cast_to=ReinforcementFineTuningJob,
        )


class ReinforcementFineTuningJobsResourceWithRawResponse:
    def __init__(self, reinforcement_fine_tuning_jobs: ReinforcementFineTuningJobsResource) -> None:
        self._reinforcement_fine_tuning_jobs = reinforcement_fine_tuning_jobs

        self.create = to_raw_response_wrapper(
            reinforcement_fine_tuning_jobs.create,
        )
        self.list = to_raw_response_wrapper(
            reinforcement_fine_tuning_jobs.list,
        )
        self.delete = to_raw_response_wrapper(
            reinforcement_fine_tuning_jobs.delete,
        )
        self.get = to_raw_response_wrapper(
            reinforcement_fine_tuning_jobs.get,
        )


class AsyncReinforcementFineTuningJobsResourceWithRawResponse:
    def __init__(self, reinforcement_fine_tuning_jobs: AsyncReinforcementFineTuningJobsResource) -> None:
        self._reinforcement_fine_tuning_jobs = reinforcement_fine_tuning_jobs

        self.create = async_to_raw_response_wrapper(
            reinforcement_fine_tuning_jobs.create,
        )
        self.list = async_to_raw_response_wrapper(
            reinforcement_fine_tuning_jobs.list,
        )
        self.delete = async_to_raw_response_wrapper(
            reinforcement_fine_tuning_jobs.delete,
        )
        self.get = async_to_raw_response_wrapper(
            reinforcement_fine_tuning_jobs.get,
        )


class ReinforcementFineTuningJobsResourceWithStreamingResponse:
    def __init__(self, reinforcement_fine_tuning_jobs: ReinforcementFineTuningJobsResource) -> None:
        self._reinforcement_fine_tuning_jobs = reinforcement_fine_tuning_jobs

        self.create = to_streamed_response_wrapper(
            reinforcement_fine_tuning_jobs.create,
        )
        self.list = to_streamed_response_wrapper(
            reinforcement_fine_tuning_jobs.list,
        )
        self.delete = to_streamed_response_wrapper(
            reinforcement_fine_tuning_jobs.delete,
        )
        self.get = to_streamed_response_wrapper(
            reinforcement_fine_tuning_jobs.get,
        )


class AsyncReinforcementFineTuningJobsResourceWithStreamingResponse:
    def __init__(self, reinforcement_fine_tuning_jobs: AsyncReinforcementFineTuningJobsResource) -> None:
        self._reinforcement_fine_tuning_jobs = reinforcement_fine_tuning_jobs

        self.create = async_to_streamed_response_wrapper(
            reinforcement_fine_tuning_jobs.create,
        )
        self.list = async_to_streamed_response_wrapper(
            reinforcement_fine_tuning_jobs.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            reinforcement_fine_tuning_jobs.delete,
        )
        self.get = async_to_streamed_response_wrapper(
            reinforcement_fine_tuning_jobs.get,
        )
