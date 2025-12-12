# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import (
    reinforcement_fine_tuning_step_get_params,
    reinforcement_fine_tuning_step_list_params,
    reinforcement_fine_tuning_step_create_params,
)
from .._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..pagination import SyncCursorReinforcementFineTuningSteps, AsyncCursorReinforcementFineTuningSteps
from .._base_client import AsyncPaginator, make_request_options
from ..types.shared_params.wandb_config import WandbConfig
from ..types.shared_params.training_config import TrainingConfig
from ..types.reinforcement_fine_tuning_step import ReinforcementFineTuningStep

__all__ = ["ReinforcementFineTuningStepsResource", "AsyncReinforcementFineTuningStepsResource"]


class ReinforcementFineTuningStepsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ReinforcementFineTuningStepsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#accessing-raw-response-data-eg-headers
        """
        return ReinforcementFineTuningStepsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ReinforcementFineTuningStepsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#with_streaming_response
        """
        return ReinforcementFineTuningStepsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        account_id: str | None = None,
        rlor_trainer_job_id: str | Omit = omit,
        dataset: str | Omit = omit,
        display_name: str | Omit = omit,
        eval_auto_carveout: bool | Omit = omit,
        evaluation_dataset: str | Omit = omit,
        keep_alive: bool | Omit = omit,
        reward_weights: SequenceNotStr[str] | Omit = omit,
        training_config: TrainingConfig | Omit = omit,
        wandb_config: WandbConfig | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ReinforcementFineTuningStep:
        """
        Create Reinforcement Fine-tuning Step

        Args:
          rlor_trainer_job_id: ID of the RLOR trainer job, a random UUID will be generated if not specified.

          dataset: The name of the dataset used for training.

          eval_auto_carveout: Whether to auto-carve the dataset for eval.

          evaluation_dataset: The name of a separate dataset to use for evaluation.

          reward_weights: A list of reward metrics to use for training in format of
              "<reward_name>=<weight>".

          training_config: Common training configurations.

          wandb_config: The Weights & Biases team/user account for logging training progress.

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
            f"/v1/accounts/{account_id}/rlorTrainerJobs"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/rlorTrainerJobs",
            body=maybe_transform(
                {
                    "dataset": dataset,
                    "display_name": display_name,
                    "eval_auto_carveout": eval_auto_carveout,
                    "evaluation_dataset": evaluation_dataset,
                    "keep_alive": keep_alive,
                    "reward_weights": reward_weights,
                    "training_config": training_config,
                    "wandb_config": wandb_config,
                },
                reinforcement_fine_tuning_step_create_params.ReinforcementFineTuningStepCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"rlor_trainer_job_id": rlor_trainer_job_id},
                    reinforcement_fine_tuning_step_create_params.ReinforcementFineTuningStepCreateParams,
                ),
            ),
            cast_to=ReinforcementFineTuningStep,
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
    ) -> SyncCursorReinforcementFineTuningSteps[ReinforcementFineTuningStep]:
        """
        List Reinforcement Fine-tuning Steps

        Args:
          filter: Filter criteria for the returned jobs. See https://google.aip.dev/160 for the
              filter syntax specification.

          order_by: A comma-separated list of fields to order by. e.g. "foo,bar" The default sort
              order is ascending. To specify a descending order for a field, append a " desc"
              suffix. e.g. "foo desc,bar" Subfields are specified with a "." character. e.g.
              "foo.bar" If not specified, the default order is by "name".

          page_size: The maximum number of fine-tuning jobs to return. The maximum page_size is 200,
              values above 200 will be coerced to 200. If unspecified, the default is 50.

          page_token: A page token, received from a previous ListRlorTuningJobs call. Provide this to
              retrieve the subsequent page. When paginating, all other parameters provided to
              ListRlorTuningJobs must match the call that provided the page token.

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
            f"/v1/accounts/{account_id}/rlorTrainerJobs"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/rlorTrainerJobs",
            page=SyncCursorReinforcementFineTuningSteps[ReinforcementFineTuningStep],
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
                    reinforcement_fine_tuning_step_list_params.ReinforcementFineTuningStepListParams,
                ),
            ),
            model=ReinforcementFineTuningStep,
        )

    def delete(
        self,
        rlor_trainer_job_id: str,
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
        Delete Reinforcement Fine-tuning Step

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
        if not rlor_trainer_job_id:
            raise ValueError(
                f"Expected a non-empty value for `rlor_trainer_job_id` but received {rlor_trainer_job_id!r}"
            )
        return self._delete(
            f"/v1/accounts/{account_id}/rlorTrainerJobs/{rlor_trainer_job_id}"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/rlorTrainerJobs/{rlor_trainer_job_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def get(
        self,
        rlor_trainer_job_id: str,
        *,
        account_id: str | None = None,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ReinforcementFineTuningStep:
        """
        Get Reinforcement Fine-tuning Step

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
        if not rlor_trainer_job_id:
            raise ValueError(
                f"Expected a non-empty value for `rlor_trainer_job_id` but received {rlor_trainer_job_id!r}"
            )
        return self._get(
            f"/v1/accounts/{account_id}/rlorTrainerJobs/{rlor_trainer_job_id}"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/rlorTrainerJobs/{rlor_trainer_job_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"read_mask": read_mask},
                    reinforcement_fine_tuning_step_get_params.ReinforcementFineTuningStepGetParams,
                ),
            ),
            cast_to=ReinforcementFineTuningStep,
        )


class AsyncReinforcementFineTuningStepsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncReinforcementFineTuningStepsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncReinforcementFineTuningStepsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncReinforcementFineTuningStepsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#with_streaming_response
        """
        return AsyncReinforcementFineTuningStepsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        account_id: str | None = None,
        rlor_trainer_job_id: str | Omit = omit,
        dataset: str | Omit = omit,
        display_name: str | Omit = omit,
        eval_auto_carveout: bool | Omit = omit,
        evaluation_dataset: str | Omit = omit,
        keep_alive: bool | Omit = omit,
        reward_weights: SequenceNotStr[str] | Omit = omit,
        training_config: TrainingConfig | Omit = omit,
        wandb_config: WandbConfig | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ReinforcementFineTuningStep:
        """
        Create Reinforcement Fine-tuning Step

        Args:
          rlor_trainer_job_id: ID of the RLOR trainer job, a random UUID will be generated if not specified.

          dataset: The name of the dataset used for training.

          eval_auto_carveout: Whether to auto-carve the dataset for eval.

          evaluation_dataset: The name of a separate dataset to use for evaluation.

          reward_weights: A list of reward metrics to use for training in format of
              "<reward_name>=<weight>".

          training_config: Common training configurations.

          wandb_config: The Weights & Biases team/user account for logging training progress.

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
            f"/v1/accounts/{account_id}/rlorTrainerJobs"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/rlorTrainerJobs",
            body=await async_maybe_transform(
                {
                    "dataset": dataset,
                    "display_name": display_name,
                    "eval_auto_carveout": eval_auto_carveout,
                    "evaluation_dataset": evaluation_dataset,
                    "keep_alive": keep_alive,
                    "reward_weights": reward_weights,
                    "training_config": training_config,
                    "wandb_config": wandb_config,
                },
                reinforcement_fine_tuning_step_create_params.ReinforcementFineTuningStepCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"rlor_trainer_job_id": rlor_trainer_job_id},
                    reinforcement_fine_tuning_step_create_params.ReinforcementFineTuningStepCreateParams,
                ),
            ),
            cast_to=ReinforcementFineTuningStep,
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
    ) -> AsyncPaginator[
        ReinforcementFineTuningStep, AsyncCursorReinforcementFineTuningSteps[ReinforcementFineTuningStep]
    ]:
        """
        List Reinforcement Fine-tuning Steps

        Args:
          filter: Filter criteria for the returned jobs. See https://google.aip.dev/160 for the
              filter syntax specification.

          order_by: A comma-separated list of fields to order by. e.g. "foo,bar" The default sort
              order is ascending. To specify a descending order for a field, append a " desc"
              suffix. e.g. "foo desc,bar" Subfields are specified with a "." character. e.g.
              "foo.bar" If not specified, the default order is by "name".

          page_size: The maximum number of fine-tuning jobs to return. The maximum page_size is 200,
              values above 200 will be coerced to 200. If unspecified, the default is 50.

          page_token: A page token, received from a previous ListRlorTuningJobs call. Provide this to
              retrieve the subsequent page. When paginating, all other parameters provided to
              ListRlorTuningJobs must match the call that provided the page token.

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
            f"/v1/accounts/{account_id}/rlorTrainerJobs"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/rlorTrainerJobs",
            page=AsyncCursorReinforcementFineTuningSteps[ReinforcementFineTuningStep],
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
                    reinforcement_fine_tuning_step_list_params.ReinforcementFineTuningStepListParams,
                ),
            ),
            model=ReinforcementFineTuningStep,
        )

    async def delete(
        self,
        rlor_trainer_job_id: str,
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
        Delete Reinforcement Fine-tuning Step

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
        if not rlor_trainer_job_id:
            raise ValueError(
                f"Expected a non-empty value for `rlor_trainer_job_id` but received {rlor_trainer_job_id!r}"
            )
        return await self._delete(
            f"/v1/accounts/{account_id}/rlorTrainerJobs/{rlor_trainer_job_id}"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/rlorTrainerJobs/{rlor_trainer_job_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def get(
        self,
        rlor_trainer_job_id: str,
        *,
        account_id: str | None = None,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ReinforcementFineTuningStep:
        """
        Get Reinforcement Fine-tuning Step

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
        if not rlor_trainer_job_id:
            raise ValueError(
                f"Expected a non-empty value for `rlor_trainer_job_id` but received {rlor_trainer_job_id!r}"
            )
        return await self._get(
            f"/v1/accounts/{account_id}/rlorTrainerJobs/{rlor_trainer_job_id}"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/rlorTrainerJobs/{rlor_trainer_job_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"read_mask": read_mask},
                    reinforcement_fine_tuning_step_get_params.ReinforcementFineTuningStepGetParams,
                ),
            ),
            cast_to=ReinforcementFineTuningStep,
        )


class ReinforcementFineTuningStepsResourceWithRawResponse:
    def __init__(self, reinforcement_fine_tuning_steps: ReinforcementFineTuningStepsResource) -> None:
        self._reinforcement_fine_tuning_steps = reinforcement_fine_tuning_steps

        self.create = to_raw_response_wrapper(
            reinforcement_fine_tuning_steps.create,
        )
        self.list = to_raw_response_wrapper(
            reinforcement_fine_tuning_steps.list,
        )
        self.delete = to_raw_response_wrapper(
            reinforcement_fine_tuning_steps.delete,
        )
        self.get = to_raw_response_wrapper(
            reinforcement_fine_tuning_steps.get,
        )


class AsyncReinforcementFineTuningStepsResourceWithRawResponse:
    def __init__(self, reinforcement_fine_tuning_steps: AsyncReinforcementFineTuningStepsResource) -> None:
        self._reinforcement_fine_tuning_steps = reinforcement_fine_tuning_steps

        self.create = async_to_raw_response_wrapper(
            reinforcement_fine_tuning_steps.create,
        )
        self.list = async_to_raw_response_wrapper(
            reinforcement_fine_tuning_steps.list,
        )
        self.delete = async_to_raw_response_wrapper(
            reinforcement_fine_tuning_steps.delete,
        )
        self.get = async_to_raw_response_wrapper(
            reinforcement_fine_tuning_steps.get,
        )


class ReinforcementFineTuningStepsResourceWithStreamingResponse:
    def __init__(self, reinforcement_fine_tuning_steps: ReinforcementFineTuningStepsResource) -> None:
        self._reinforcement_fine_tuning_steps = reinforcement_fine_tuning_steps

        self.create = to_streamed_response_wrapper(
            reinforcement_fine_tuning_steps.create,
        )
        self.list = to_streamed_response_wrapper(
            reinforcement_fine_tuning_steps.list,
        )
        self.delete = to_streamed_response_wrapper(
            reinforcement_fine_tuning_steps.delete,
        )
        self.get = to_streamed_response_wrapper(
            reinforcement_fine_tuning_steps.get,
        )


class AsyncReinforcementFineTuningStepsResourceWithStreamingResponse:
    def __init__(self, reinforcement_fine_tuning_steps: AsyncReinforcementFineTuningStepsResource) -> None:
        self._reinforcement_fine_tuning_steps = reinforcement_fine_tuning_steps

        self.create = async_to_streamed_response_wrapper(
            reinforcement_fine_tuning_steps.create,
        )
        self.list = async_to_streamed_response_wrapper(
            reinforcement_fine_tuning_steps.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            reinforcement_fine_tuning_steps.delete,
        )
        self.get = async_to_streamed_response_wrapper(
            reinforcement_fine_tuning_steps.get,
        )
