# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ..types import (
    supervised_fine_tuning_job_get_params,
    supervised_fine_tuning_job_list_params,
    supervised_fine_tuning_job_create_params,
    supervised_fine_tuning_job_resume_params,
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
from ..pagination import SyncCursorSupervisedFineTuningJobs, AsyncCursorSupervisedFineTuningJobs
from .._base_client import AsyncPaginator, make_request_options
from ..types.shared_params.wandb_config import WandbConfig
from ..types.supervised_fine_tuning_job import SupervisedFineTuningJob

__all__ = ["SupervisedFineTuningJobsResource", "AsyncSupervisedFineTuningJobsResource"]


class SupervisedFineTuningJobsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> SupervisedFineTuningJobsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#accessing-raw-response-data-eg-headers
        """
        return SupervisedFineTuningJobsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SupervisedFineTuningJobsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#with_streaming_response
        """
        return SupervisedFineTuningJobsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        account_id: str | None = None,
        dataset: str,
        supervised_fine_tuning_job_id: str | Omit = omit,
        aws_s3_config: supervised_fine_tuning_job_create_params.AwsS3Config | Omit = omit,
        base_model: str | Omit = omit,
        batch_size: int | Omit = omit,
        batch_size_samples: int | Omit = omit,
        display_name: str | Omit = omit,
        early_stop: bool | Omit = omit,
        epochs: int | Omit = omit,
        eval_auto_carveout: bool | Omit = omit,
        evaluation_dataset: str | Omit = omit,
        gradient_accumulation_steps: int | Omit = omit,
        is_turbo: bool | Omit = omit,
        jinja_template: str | Omit = omit,
        learning_rate: float | Omit = omit,
        learning_rate_warmup_steps: int | Omit = omit,
        lora_rank: int | Omit = omit,
        max_context_length: int | Omit = omit,
        metrics_file_signed_url: str | Omit = omit,
        mtp_enabled: bool | Omit = omit,
        mtp_freeze_base_model: bool | Omit = omit,
        mtp_num_draft_tokens: int | Omit = omit,
        nodes: int | Omit = omit,
        optimizer_weight_decay: float | Omit = omit,
        output_model: str | Omit = omit,
        region: Literal[
            "REGION_UNSPECIFIED",
            "US_IOWA_1",
            "US_VIRGINIA_1",
            "US_VIRGINIA_2",
            "US_ILLINOIS_1",
            "AP_TOKYO_1",
            "EU_LONDON_1",
            "US_ARIZONA_1",
            "US_TEXAS_1",
            "US_ILLINOIS_2",
            "EU_FRANKFURT_1",
            "US_TEXAS_2",
            "EU_PARIS_1",
            "EU_HELSINKI_1",
            "US_NEVADA_1",
            "EU_ICELAND_1",
            "EU_ICELAND_2",
            "US_WASHINGTON_1",
            "US_WASHINGTON_2",
            "EU_ICELAND_DEV_1",
            "US_WASHINGTON_3",
            "US_ARIZONA_2",
            "AP_TOKYO_2",
            "US_CALIFORNIA_1",
            "US_MISSOURI_1",
            "US_UTAH_1",
            "US_TEXAS_3",
            "US_ARIZONA_3",
            "US_GEORGIA_1",
            "US_GEORGIA_2",
            "US_WASHINGTON_4",
            "US_GEORGIA_3",
            "NA_BRITISHCOLUMBIA_1",
            "US_GEORGIA_4",
            "EU_ICELAND_3",
            "US_OHIO_1",
        ]
        | Omit = omit,
        wandb_config: WandbConfig | Omit = omit,
        warm_start_from: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SupervisedFineTuningJob:
        """
        Create Supervised Fine-tuning Job

        Args:
          dataset: The name of the dataset used for training.

          supervised_fine_tuning_job_id: ID of the supervised fine-tuning job, a random UUID will be generated if not
              specified.

          aws_s3_config: The AWS configuration for S3 dataset access.

          base_model: The name of the base model to be fine-tuned Only one of 'base_model' or
              'warm_start_from' should be specified.

          batch_size_samples: The number of samples per gradient batch.

          early_stop: Whether to stop training early if the validation loss does not improve.

          epochs: The number of epochs to train for.

          eval_auto_carveout: Whether to auto-carve the dataset for eval.

          evaluation_dataset: The name of a separate dataset to use for evaluation.

          is_turbo: Whether to run the fine-tuning job in turbo mode.

          learning_rate: The learning rate used for training.

          lora_rank: The rank of the LoRA layers.

          max_context_length: The maximum context length to use with the model.

          nodes: The number of nodes to use for the fine-tuning job.

          optimizer_weight_decay: Weight decay (L2 regularization) for optimizer.

          output_model: The model ID to be assigned to the resulting fine-tuned model. If not specified,
              the job ID will be used.

          region: The region where the fine-tuning job is located.

          wandb_config: The Weights & Biases team/user account for logging training progress.

          warm_start_from: The PEFT addon model in Fireworks format to be fine-tuned from Only one of
              'base_model' or 'warm_start_from' should be specified.

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
            f"/v1/accounts/{account_id}/supervisedFineTuningJobs"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/supervisedFineTuningJobs",
            body=maybe_transform(
                {
                    "dataset": dataset,
                    "aws_s3_config": aws_s3_config,
                    "base_model": base_model,
                    "batch_size": batch_size,
                    "batch_size_samples": batch_size_samples,
                    "display_name": display_name,
                    "early_stop": early_stop,
                    "epochs": epochs,
                    "eval_auto_carveout": eval_auto_carveout,
                    "evaluation_dataset": evaluation_dataset,
                    "gradient_accumulation_steps": gradient_accumulation_steps,
                    "is_turbo": is_turbo,
                    "jinja_template": jinja_template,
                    "learning_rate": learning_rate,
                    "learning_rate_warmup_steps": learning_rate_warmup_steps,
                    "lora_rank": lora_rank,
                    "max_context_length": max_context_length,
                    "metrics_file_signed_url": metrics_file_signed_url,
                    "mtp_enabled": mtp_enabled,
                    "mtp_freeze_base_model": mtp_freeze_base_model,
                    "mtp_num_draft_tokens": mtp_num_draft_tokens,
                    "nodes": nodes,
                    "optimizer_weight_decay": optimizer_weight_decay,
                    "output_model": output_model,
                    "region": region,
                    "wandb_config": wandb_config,
                    "warm_start_from": warm_start_from,
                },
                supervised_fine_tuning_job_create_params.SupervisedFineTuningJobCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"supervised_fine_tuning_job_id": supervised_fine_tuning_job_id},
                    supervised_fine_tuning_job_create_params.SupervisedFineTuningJobCreateParams,
                ),
            ),
            cast_to=SupervisedFineTuningJob,
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
    ) -> SyncCursorSupervisedFineTuningJobs[SupervisedFineTuningJob]:
        """
        List Supervised Fine-tuning Jobs

        Args:
          filter: Filter criteria for the returned jobs. See https://google.aip.dev/160 for the
              filter syntax specification.

          order_by: A comma-separated list of fields to order by. e.g. "foo,bar" The default sort
              order is ascending. To specify a descending order for a field, append a " desc"
              suffix. e.g. "foo desc,bar" Subfields are specified with a "." character. e.g.
              "foo.bar" If not specified, the default order is by "name".

          page_size: The maximum number of fine-tuning jobs to return. The maximum page_size is 200,
              values above 200 will be coerced to 200. If unspecified, the default is 50.

          page_token: A page token, received from a previous ListSupervisedFineTuningJobs call.
              Provide this to retrieve the subsequent page. When paginating, all other
              parameters provided to ListSupervisedFineTuningJobs must match the call that
              provided the page token.

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
            f"/v1/accounts/{account_id}/supervisedFineTuningJobs"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/supervisedFineTuningJobs",
            page=SyncCursorSupervisedFineTuningJobs[SupervisedFineTuningJob],
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
                    supervised_fine_tuning_job_list_params.SupervisedFineTuningJobListParams,
                ),
            ),
            model=SupervisedFineTuningJob,
        )

    def delete(
        self,
        supervised_fine_tuning_job_id: str,
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
        Delete Supervised Fine-tuning Job

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
        if not supervised_fine_tuning_job_id:
            raise ValueError(
                f"Expected a non-empty value for `supervised_fine_tuning_job_id` but received {supervised_fine_tuning_job_id!r}"
            )
        return self._delete(
            f"/v1/accounts/{account_id}/supervisedFineTuningJobs/{supervised_fine_tuning_job_id}"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/supervisedFineTuningJobs/{supervised_fine_tuning_job_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def get(
        self,
        supervised_fine_tuning_job_id: str,
        *,
        account_id: str | None = None,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SupervisedFineTuningJob:
        """
        Get Supervised Fine-tuning Job

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
        if not supervised_fine_tuning_job_id:
            raise ValueError(
                f"Expected a non-empty value for `supervised_fine_tuning_job_id` but received {supervised_fine_tuning_job_id!r}"
            )
        return self._get(
            f"/v1/accounts/{account_id}/supervisedFineTuningJobs/{supervised_fine_tuning_job_id}"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/supervisedFineTuningJobs/{supervised_fine_tuning_job_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"read_mask": read_mask}, supervised_fine_tuning_job_get_params.SupervisedFineTuningJobGetParams
                ),
            ),
            cast_to=SupervisedFineTuningJob,
        )

    def resume(
        self,
        supervised_fine_tuning_job_id: str,
        *,
        account_id: str | None = None,
        body: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SupervisedFineTuningJob:
        """
        Resume Supervised Fine-tuning Job

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
        if not supervised_fine_tuning_job_id:
            raise ValueError(
                f"Expected a non-empty value for `supervised_fine_tuning_job_id` but received {supervised_fine_tuning_job_id!r}"
            )
        return self._post(
            f"/v1/accounts/{account_id}/supervisedFineTuningJobs/{supervised_fine_tuning_job_id}:resume"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/supervisedFineTuningJobs/{supervised_fine_tuning_job_id}:resume",
            body=maybe_transform(body, supervised_fine_tuning_job_resume_params.SupervisedFineTuningJobResumeParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SupervisedFineTuningJob,
        )


class AsyncSupervisedFineTuningJobsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncSupervisedFineTuningJobsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncSupervisedFineTuningJobsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSupervisedFineTuningJobsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#with_streaming_response
        """
        return AsyncSupervisedFineTuningJobsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        account_id: str | None = None,
        dataset: str,
        supervised_fine_tuning_job_id: str | Omit = omit,
        aws_s3_config: supervised_fine_tuning_job_create_params.AwsS3Config | Omit = omit,
        base_model: str | Omit = omit,
        batch_size: int | Omit = omit,
        batch_size_samples: int | Omit = omit,
        display_name: str | Omit = omit,
        early_stop: bool | Omit = omit,
        epochs: int | Omit = omit,
        eval_auto_carveout: bool | Omit = omit,
        evaluation_dataset: str | Omit = omit,
        gradient_accumulation_steps: int | Omit = omit,
        is_turbo: bool | Omit = omit,
        jinja_template: str | Omit = omit,
        learning_rate: float | Omit = omit,
        learning_rate_warmup_steps: int | Omit = omit,
        lora_rank: int | Omit = omit,
        max_context_length: int | Omit = omit,
        metrics_file_signed_url: str | Omit = omit,
        mtp_enabled: bool | Omit = omit,
        mtp_freeze_base_model: bool | Omit = omit,
        mtp_num_draft_tokens: int | Omit = omit,
        nodes: int | Omit = omit,
        optimizer_weight_decay: float | Omit = omit,
        output_model: str | Omit = omit,
        region: Literal[
            "REGION_UNSPECIFIED",
            "US_IOWA_1",
            "US_VIRGINIA_1",
            "US_VIRGINIA_2",
            "US_ILLINOIS_1",
            "AP_TOKYO_1",
            "EU_LONDON_1",
            "US_ARIZONA_1",
            "US_TEXAS_1",
            "US_ILLINOIS_2",
            "EU_FRANKFURT_1",
            "US_TEXAS_2",
            "EU_PARIS_1",
            "EU_HELSINKI_1",
            "US_NEVADA_1",
            "EU_ICELAND_1",
            "EU_ICELAND_2",
            "US_WASHINGTON_1",
            "US_WASHINGTON_2",
            "EU_ICELAND_DEV_1",
            "US_WASHINGTON_3",
            "US_ARIZONA_2",
            "AP_TOKYO_2",
            "US_CALIFORNIA_1",
            "US_MISSOURI_1",
            "US_UTAH_1",
            "US_TEXAS_3",
            "US_ARIZONA_3",
            "US_GEORGIA_1",
            "US_GEORGIA_2",
            "US_WASHINGTON_4",
            "US_GEORGIA_3",
            "NA_BRITISHCOLUMBIA_1",
            "US_GEORGIA_4",
            "EU_ICELAND_3",
            "US_OHIO_1",
        ]
        | Omit = omit,
        wandb_config: WandbConfig | Omit = omit,
        warm_start_from: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SupervisedFineTuningJob:
        """
        Create Supervised Fine-tuning Job

        Args:
          dataset: The name of the dataset used for training.

          supervised_fine_tuning_job_id: ID of the supervised fine-tuning job, a random UUID will be generated if not
              specified.

          aws_s3_config: The AWS configuration for S3 dataset access.

          base_model: The name of the base model to be fine-tuned Only one of 'base_model' or
              'warm_start_from' should be specified.

          batch_size_samples: The number of samples per gradient batch.

          early_stop: Whether to stop training early if the validation loss does not improve.

          epochs: The number of epochs to train for.

          eval_auto_carveout: Whether to auto-carve the dataset for eval.

          evaluation_dataset: The name of a separate dataset to use for evaluation.

          is_turbo: Whether to run the fine-tuning job in turbo mode.

          learning_rate: The learning rate used for training.

          lora_rank: The rank of the LoRA layers.

          max_context_length: The maximum context length to use with the model.

          nodes: The number of nodes to use for the fine-tuning job.

          optimizer_weight_decay: Weight decay (L2 regularization) for optimizer.

          output_model: The model ID to be assigned to the resulting fine-tuned model. If not specified,
              the job ID will be used.

          region: The region where the fine-tuning job is located.

          wandb_config: The Weights & Biases team/user account for logging training progress.

          warm_start_from: The PEFT addon model in Fireworks format to be fine-tuned from Only one of
              'base_model' or 'warm_start_from' should be specified.

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
            f"/v1/accounts/{account_id}/supervisedFineTuningJobs"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/supervisedFineTuningJobs",
            body=await async_maybe_transform(
                {
                    "dataset": dataset,
                    "aws_s3_config": aws_s3_config,
                    "base_model": base_model,
                    "batch_size": batch_size,
                    "batch_size_samples": batch_size_samples,
                    "display_name": display_name,
                    "early_stop": early_stop,
                    "epochs": epochs,
                    "eval_auto_carveout": eval_auto_carveout,
                    "evaluation_dataset": evaluation_dataset,
                    "gradient_accumulation_steps": gradient_accumulation_steps,
                    "is_turbo": is_turbo,
                    "jinja_template": jinja_template,
                    "learning_rate": learning_rate,
                    "learning_rate_warmup_steps": learning_rate_warmup_steps,
                    "lora_rank": lora_rank,
                    "max_context_length": max_context_length,
                    "metrics_file_signed_url": metrics_file_signed_url,
                    "mtp_enabled": mtp_enabled,
                    "mtp_freeze_base_model": mtp_freeze_base_model,
                    "mtp_num_draft_tokens": mtp_num_draft_tokens,
                    "nodes": nodes,
                    "optimizer_weight_decay": optimizer_weight_decay,
                    "output_model": output_model,
                    "region": region,
                    "wandb_config": wandb_config,
                    "warm_start_from": warm_start_from,
                },
                supervised_fine_tuning_job_create_params.SupervisedFineTuningJobCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"supervised_fine_tuning_job_id": supervised_fine_tuning_job_id},
                    supervised_fine_tuning_job_create_params.SupervisedFineTuningJobCreateParams,
                ),
            ),
            cast_to=SupervisedFineTuningJob,
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
    ) -> AsyncPaginator[SupervisedFineTuningJob, AsyncCursorSupervisedFineTuningJobs[SupervisedFineTuningJob]]:
        """
        List Supervised Fine-tuning Jobs

        Args:
          filter: Filter criteria for the returned jobs. See https://google.aip.dev/160 for the
              filter syntax specification.

          order_by: A comma-separated list of fields to order by. e.g. "foo,bar" The default sort
              order is ascending. To specify a descending order for a field, append a " desc"
              suffix. e.g. "foo desc,bar" Subfields are specified with a "." character. e.g.
              "foo.bar" If not specified, the default order is by "name".

          page_size: The maximum number of fine-tuning jobs to return. The maximum page_size is 200,
              values above 200 will be coerced to 200. If unspecified, the default is 50.

          page_token: A page token, received from a previous ListSupervisedFineTuningJobs call.
              Provide this to retrieve the subsequent page. When paginating, all other
              parameters provided to ListSupervisedFineTuningJobs must match the call that
              provided the page token.

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
            f"/v1/accounts/{account_id}/supervisedFineTuningJobs"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/supervisedFineTuningJobs",
            page=AsyncCursorSupervisedFineTuningJobs[SupervisedFineTuningJob],
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
                    supervised_fine_tuning_job_list_params.SupervisedFineTuningJobListParams,
                ),
            ),
            model=SupervisedFineTuningJob,
        )

    async def delete(
        self,
        supervised_fine_tuning_job_id: str,
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
        Delete Supervised Fine-tuning Job

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
        if not supervised_fine_tuning_job_id:
            raise ValueError(
                f"Expected a non-empty value for `supervised_fine_tuning_job_id` but received {supervised_fine_tuning_job_id!r}"
            )
        return await self._delete(
            f"/v1/accounts/{account_id}/supervisedFineTuningJobs/{supervised_fine_tuning_job_id}"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/supervisedFineTuningJobs/{supervised_fine_tuning_job_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def get(
        self,
        supervised_fine_tuning_job_id: str,
        *,
        account_id: str | None = None,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SupervisedFineTuningJob:
        """
        Get Supervised Fine-tuning Job

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
        if not supervised_fine_tuning_job_id:
            raise ValueError(
                f"Expected a non-empty value for `supervised_fine_tuning_job_id` but received {supervised_fine_tuning_job_id!r}"
            )
        return await self._get(
            f"/v1/accounts/{account_id}/supervisedFineTuningJobs/{supervised_fine_tuning_job_id}"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/supervisedFineTuningJobs/{supervised_fine_tuning_job_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"read_mask": read_mask}, supervised_fine_tuning_job_get_params.SupervisedFineTuningJobGetParams
                ),
            ),
            cast_to=SupervisedFineTuningJob,
        )

    async def resume(
        self,
        supervised_fine_tuning_job_id: str,
        *,
        account_id: str | None = None,
        body: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SupervisedFineTuningJob:
        """
        Resume Supervised Fine-tuning Job

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
        if not supervised_fine_tuning_job_id:
            raise ValueError(
                f"Expected a non-empty value for `supervised_fine_tuning_job_id` but received {supervised_fine_tuning_job_id!r}"
            )
        return await self._post(
            f"/v1/accounts/{account_id}/supervisedFineTuningJobs/{supervised_fine_tuning_job_id}:resume"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/supervisedFineTuningJobs/{supervised_fine_tuning_job_id}:resume",
            body=await async_maybe_transform(
                body, supervised_fine_tuning_job_resume_params.SupervisedFineTuningJobResumeParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SupervisedFineTuningJob,
        )


class SupervisedFineTuningJobsResourceWithRawResponse:
    def __init__(self, supervised_fine_tuning_jobs: SupervisedFineTuningJobsResource) -> None:
        self._supervised_fine_tuning_jobs = supervised_fine_tuning_jobs

        self.create = to_raw_response_wrapper(
            supervised_fine_tuning_jobs.create,
        )
        self.list = to_raw_response_wrapper(
            supervised_fine_tuning_jobs.list,
        )
        self.delete = to_raw_response_wrapper(
            supervised_fine_tuning_jobs.delete,
        )
        self.get = to_raw_response_wrapper(
            supervised_fine_tuning_jobs.get,
        )
        self.resume = to_raw_response_wrapper(
            supervised_fine_tuning_jobs.resume,
        )


class AsyncSupervisedFineTuningJobsResourceWithRawResponse:
    def __init__(self, supervised_fine_tuning_jobs: AsyncSupervisedFineTuningJobsResource) -> None:
        self._supervised_fine_tuning_jobs = supervised_fine_tuning_jobs

        self.create = async_to_raw_response_wrapper(
            supervised_fine_tuning_jobs.create,
        )
        self.list = async_to_raw_response_wrapper(
            supervised_fine_tuning_jobs.list,
        )
        self.delete = async_to_raw_response_wrapper(
            supervised_fine_tuning_jobs.delete,
        )
        self.get = async_to_raw_response_wrapper(
            supervised_fine_tuning_jobs.get,
        )
        self.resume = async_to_raw_response_wrapper(
            supervised_fine_tuning_jobs.resume,
        )


class SupervisedFineTuningJobsResourceWithStreamingResponse:
    def __init__(self, supervised_fine_tuning_jobs: SupervisedFineTuningJobsResource) -> None:
        self._supervised_fine_tuning_jobs = supervised_fine_tuning_jobs

        self.create = to_streamed_response_wrapper(
            supervised_fine_tuning_jobs.create,
        )
        self.list = to_streamed_response_wrapper(
            supervised_fine_tuning_jobs.list,
        )
        self.delete = to_streamed_response_wrapper(
            supervised_fine_tuning_jobs.delete,
        )
        self.get = to_streamed_response_wrapper(
            supervised_fine_tuning_jobs.get,
        )
        self.resume = to_streamed_response_wrapper(
            supervised_fine_tuning_jobs.resume,
        )


class AsyncSupervisedFineTuningJobsResourceWithStreamingResponse:
    def __init__(self, supervised_fine_tuning_jobs: AsyncSupervisedFineTuningJobsResource) -> None:
        self._supervised_fine_tuning_jobs = supervised_fine_tuning_jobs

        self.create = async_to_streamed_response_wrapper(
            supervised_fine_tuning_jobs.create,
        )
        self.list = async_to_streamed_response_wrapper(
            supervised_fine_tuning_jobs.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            supervised_fine_tuning_jobs.delete,
        )
        self.get = async_to_streamed_response_wrapper(
            supervised_fine_tuning_jobs.get,
        )
        self.resume = async_to_streamed_response_wrapper(
            supervised_fine_tuning_jobs.resume,
        )
