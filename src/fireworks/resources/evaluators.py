# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable

import httpx

from ..types import (
    evaluator_get_params,
    evaluator_list_params,
    evaluator_create_params,
    evaluator_update_params,
    evaluator_validate_upload_params,
    evaluator_get_upload_endpoint_params,
    evaluator_get_build_log_endpoint_params,
    evaluator_get_source_code_endpoint_params,
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
from ..pagination import SyncCursorEvaluators, AsyncCursorEvaluators
from .._base_client import AsyncPaginator, make_request_options
from ..types.criterion_param import CriterionParam
from ..types.rollup_settings_param import RollupSettingsParam
from ..types.evaluator_get_response import EvaluatorGetResponse
from ..types.evaluator_source_param import EvaluatorSourceParam
from ..types.evaluator_list_response import EvaluatorListResponse
from ..types.evaluator_create_response import EvaluatorCreateResponse
from ..types.evaluator_update_response import EvaluatorUpdateResponse
from ..types.evaluator_get_upload_endpoint_response import EvaluatorGetUploadEndpointResponse
from ..types.evaluator_get_build_log_endpoint_response import EvaluatorGetBuildLogEndpointResponse
from ..types.evaluator_get_source_code_endpoint_response import EvaluatorGetSourceCodeEndpointResponse

__all__ = ["EvaluatorsResource", "AsyncEvaluatorsResource"]


class EvaluatorsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> EvaluatorsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#accessing-raw-response-data-eg-headers
        """
        return EvaluatorsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> EvaluatorsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#with_streaming_response
        """
        return EvaluatorsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        account_id: str | None = None,
        evaluator: evaluator_create_params.Evaluator,
        evaluator_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EvaluatorCreateResponse:
        """Creates a custom evaluator for scoring model outputs.

        Evaluators use the
        [Eval Protocol](https://evalprotocol.io) to define test cases, run model
        inference, and score responses. They are used with evaluation jobs and
        Reinforcement Fine-Tuning (RFT).

        ## Source Code Requirements

        Your project should contain:

        - `requirements.txt` - Python dependencies for your evaluator
        - `test_*.py` - Pytest test file(s) with
          [`@evaluation_test`](https://evalprotocol.io/reference/evaluation-test)
          decorated functions
        - Any additional code/modules your evaluator needs

        ## Workflow

        **Recommended:** Use the
        [`ep upload`](https://evalprotocol.io/reference/cli#ep-upload) CLI command to
        handle all these steps automatically.

        If using the API directly:

        1. Call this endpoint to create the evaluator resource
        2. Package your source directory as a `.tar.gz` (respecting `.gitignore`)
        3. Call
           [Get Evaluator Upload Endpoint](/api-reference/get-evaluator-upload-endpoint)
           to get a signed upload URL
        4. `PUT` the tar.gz file to the signed URL
        5. Call [Validate Evaluator Upload](/api-reference/validate-evaluator-upload) to
           trigger server-side validation
        6. Poll [Get Evaluator](/api-reference/get-evaluator) until ready

        Once active, reference the evaluator in
        [Create Evaluation Job](/api-reference/create-evaluation-job) or
        [Create Reinforcement Fine-tuning Job](/api-reference/create-reinforcement-fine-tuning-job).

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
        return self._post(
            f"/v1/accounts/{account_id}/evaluatorsV2"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/evaluatorsV2",
            body=maybe_transform(
                {
                    "evaluator": evaluator,
                    "evaluator_id": evaluator_id,
                },
                evaluator_create_params.EvaluatorCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EvaluatorCreateResponse,
        )

    def update(
        self,
        evaluator_id: str,
        *,
        account_id: str | None = None,
        prepare_code_upload: bool | Omit = omit,
        commit_hash: str | Omit = omit,
        criteria: Iterable[CriterionParam] | Omit = omit,
        default_dataset: str | Omit = omit,
        description: str | Omit = omit,
        display_name: str | Omit = omit,
        entry_point: str | Omit = omit,
        multi_metrics: bool | Omit = omit,
        requirements: str | Omit = omit,
        rollup_settings: RollupSettingsParam | Omit = omit,
        source: EvaluatorSourceParam | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EvaluatorUpdateResponse:
        """
        Updates evaluator metadata (display_name, description, default_dataset).
        Changing `requirements` or `entry_point` triggers a rebuild. To upload new
        source code, set `prepare_code_upload: true` then follow the upload flow.

        Args:
          prepare_code_upload: If true, prepare a new code upload/build attempt by transitioning the evaluator
              to BUILDING state. Can be used without update_mask.

          multi_metrics: If true, the criteria will report multiple metric-score pairs Otherwise, each
              criteria will report the score assigned to the criteria name as metric.

          rollup_settings: Strategy for metrics reports summary/rollup. e.g. {metric1: 1, metric2: 0.3},
              rollup_settings could be criteria_weights: {metric1: 0.5, metric2: 0.5}, then
              final score will be 0.5 _ 1 + 0.5 _ 0.3 = 0.65 If skip_rollup is true, the
              rollup step will be skipped since the criteria will also report the rollup score
              and metrics altogether.

          source: Source information for the evaluator codebase.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if account_id is None:
            account_id = self._client._get_account_id_path_param()
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not evaluator_id:
            raise ValueError(f"Expected a non-empty value for `evaluator_id` but received {evaluator_id!r}")
        return self._patch(
            f"/v1/accounts/{account_id}/evaluators/{evaluator_id}"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/evaluators/{evaluator_id}",
            body=maybe_transform(
                {
                    "commit_hash": commit_hash,
                    "criteria": criteria,
                    "default_dataset": default_dataset,
                    "description": description,
                    "display_name": display_name,
                    "entry_point": entry_point,
                    "multi_metrics": multi_metrics,
                    "requirements": requirements,
                    "rollup_settings": rollup_settings,
                    "source": source,
                },
                evaluator_update_params.EvaluatorUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"prepare_code_upload": prepare_code_upload}, evaluator_update_params.EvaluatorUpdateParams
                ),
            ),
            cast_to=EvaluatorUpdateResponse,
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
    ) -> SyncCursorEvaluators[EvaluatorListResponse]:
        """
        Lists all evaluators for an account with pagination support.

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
        return self._get_api_list(
            f"/v1/accounts/{account_id}/evaluators"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/evaluators",
            page=SyncCursorEvaluators[EvaluatorListResponse],
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
                    evaluator_list_params.EvaluatorListParams,
                ),
            ),
            model=EvaluatorListResponse,
        )

    def delete(
        self,
        evaluator_id: str,
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
        Deletes an evaluator and its associated versions and build artifacts.

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
        if not evaluator_id:
            raise ValueError(f"Expected a non-empty value for `evaluator_id` but received {evaluator_id!r}")
        return self._delete(
            f"/v1/accounts/{account_id}/evaluators/{evaluator_id}"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/evaluators/{evaluator_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def get(
        self,
        evaluator_id: str,
        *,
        account_id: str | None = None,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EvaluatorGetResponse:
        """Retrieves an evaluator by name.

        Use this to monitor build progress after
        creation (**step 6** in the [Create Evaluator](/api-reference/create-evaluator)
        workflow).

        Possible states:

        - `BUILDING` - Environment is being prepared
        - `ACTIVE` - Evaluator is ready to use
        - `BUILD_FAILED` - Check build logs via
          [Get Evaluator Build Log Endpoint](/api-reference/get-evaluator-build-log-endpoint)

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
        if not evaluator_id:
            raise ValueError(f"Expected a non-empty value for `evaluator_id` but received {evaluator_id!r}")
        return self._get(
            f"/v1/accounts/{account_id}/evaluators/{evaluator_id}"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/evaluators/{evaluator_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"read_mask": read_mask}, evaluator_get_params.EvaluatorGetParams),
            ),
            cast_to=EvaluatorGetResponse,
        )

    def get_build_log_endpoint(
        self,
        evaluator_id: str,
        *,
        account_id: str | None = None,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EvaluatorGetBuildLogEndpointResponse:
        """Returns a signed URL to download the evaluator's build logs.

        Useful for
        debugging `BUILD_FAILED` state.

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
        if not evaluator_id:
            raise ValueError(f"Expected a non-empty value for `evaluator_id` but received {evaluator_id!r}")
        return self._get(
            f"/v1/accounts/{account_id}/evaluators/{evaluator_id}:getBuildLogEndpoint"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/evaluators/{evaluator_id}:getBuildLogEndpoint",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"read_mask": read_mask}, evaluator_get_build_log_endpoint_params.EvaluatorGetBuildLogEndpointParams
                ),
            ),
            cast_to=EvaluatorGetBuildLogEndpointResponse,
        )

    def get_source_code_endpoint(
        self,
        evaluator_id: str,
        *,
        account_id: str | None = None,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EvaluatorGetSourceCodeEndpointResponse:
        """Returns a signed URL to download the evaluator's source code archive.

        Useful for
        debugging or reviewing the uploaded code.

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
        if not evaluator_id:
            raise ValueError(f"Expected a non-empty value for `evaluator_id` but received {evaluator_id!r}")
        return self._get(
            f"/v1/accounts/{account_id}/evaluators/{evaluator_id}:getSourceCodeSignedUrl"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/evaluators/{evaluator_id}:getSourceCodeSignedUrl",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"read_mask": read_mask},
                    evaluator_get_source_code_endpoint_params.EvaluatorGetSourceCodeEndpointParams,
                ),
            ),
            cast_to=EvaluatorGetSourceCodeEndpointResponse,
        )

    def get_upload_endpoint(
        self,
        evaluator_id: str,
        *,
        account_id: str | None = None,
        filename_to_size: Dict[str, str],
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EvaluatorGetUploadEndpointResponse:
        """
        Returns signed URLs for uploading evaluator source code (**step 3** in the
        [Create Evaluator](/api-reference/create-evaluator) workflow). After receiving
        the signed URL, upload your `.tar.gz` archive using HTTP `PUT` with
        `Content-Type: application/octet-stream` header.

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
        if not evaluator_id:
            raise ValueError(f"Expected a non-empty value for `evaluator_id` but received {evaluator_id!r}")
        return self._post(
            f"/v1/accounts/{account_id}/evaluators/{evaluator_id}:getUploadEndpoint"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/evaluators/{evaluator_id}:getUploadEndpoint",
            body=maybe_transform(
                {
                    "filename_to_size": filename_to_size,
                    "read_mask": read_mask,
                },
                evaluator_get_upload_endpoint_params.EvaluatorGetUploadEndpointParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EvaluatorGetUploadEndpointResponse,
        )

    def validate_upload(
        self,
        evaluator_id: str,
        *,
        account_id: str | None = None,
        body: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Triggers server-side validation of the uploaded source code (**step 5** in the
        [Create Evaluator](/api-reference/create-evaluator) workflow). The server
        extracts and processes the archive, then builds the evaluator environment. Poll
        [Get Evaluator](/api-reference/get-evaluator) to monitor progress.

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
        if not evaluator_id:
            raise ValueError(f"Expected a non-empty value for `evaluator_id` but received {evaluator_id!r}")
        return self._post(
            f"/v1/accounts/{account_id}/evaluators/{evaluator_id}:validateUpload"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/evaluators/{evaluator_id}:validateUpload",
            body=maybe_transform(body, evaluator_validate_upload_params.EvaluatorValidateUploadParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncEvaluatorsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncEvaluatorsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncEvaluatorsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncEvaluatorsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#with_streaming_response
        """
        return AsyncEvaluatorsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        account_id: str | None = None,
        evaluator: evaluator_create_params.Evaluator,
        evaluator_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EvaluatorCreateResponse:
        """Creates a custom evaluator for scoring model outputs.

        Evaluators use the
        [Eval Protocol](https://evalprotocol.io) to define test cases, run model
        inference, and score responses. They are used with evaluation jobs and
        Reinforcement Fine-Tuning (RFT).

        ## Source Code Requirements

        Your project should contain:

        - `requirements.txt` - Python dependencies for your evaluator
        - `test_*.py` - Pytest test file(s) with
          [`@evaluation_test`](https://evalprotocol.io/reference/evaluation-test)
          decorated functions
        - Any additional code/modules your evaluator needs

        ## Workflow

        **Recommended:** Use the
        [`ep upload`](https://evalprotocol.io/reference/cli#ep-upload) CLI command to
        handle all these steps automatically.

        If using the API directly:

        1. Call this endpoint to create the evaluator resource
        2. Package your source directory as a `.tar.gz` (respecting `.gitignore`)
        3. Call
           [Get Evaluator Upload Endpoint](/api-reference/get-evaluator-upload-endpoint)
           to get a signed upload URL
        4. `PUT` the tar.gz file to the signed URL
        5. Call [Validate Evaluator Upload](/api-reference/validate-evaluator-upload) to
           trigger server-side validation
        6. Poll [Get Evaluator](/api-reference/get-evaluator) until ready

        Once active, reference the evaluator in
        [Create Evaluation Job](/api-reference/create-evaluation-job) or
        [Create Reinforcement Fine-tuning Job](/api-reference/create-reinforcement-fine-tuning-job).

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
        return await self._post(
            f"/v1/accounts/{account_id}/evaluatorsV2"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/evaluatorsV2",
            body=await async_maybe_transform(
                {
                    "evaluator": evaluator,
                    "evaluator_id": evaluator_id,
                },
                evaluator_create_params.EvaluatorCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EvaluatorCreateResponse,
        )

    async def update(
        self,
        evaluator_id: str,
        *,
        account_id: str | None = None,
        prepare_code_upload: bool | Omit = omit,
        commit_hash: str | Omit = omit,
        criteria: Iterable[CriterionParam] | Omit = omit,
        default_dataset: str | Omit = omit,
        description: str | Omit = omit,
        display_name: str | Omit = omit,
        entry_point: str | Omit = omit,
        multi_metrics: bool | Omit = omit,
        requirements: str | Omit = omit,
        rollup_settings: RollupSettingsParam | Omit = omit,
        source: EvaluatorSourceParam | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EvaluatorUpdateResponse:
        """
        Updates evaluator metadata (display_name, description, default_dataset).
        Changing `requirements` or `entry_point` triggers a rebuild. To upload new
        source code, set `prepare_code_upload: true` then follow the upload flow.

        Args:
          prepare_code_upload: If true, prepare a new code upload/build attempt by transitioning the evaluator
              to BUILDING state. Can be used without update_mask.

          multi_metrics: If true, the criteria will report multiple metric-score pairs Otherwise, each
              criteria will report the score assigned to the criteria name as metric.

          rollup_settings: Strategy for metrics reports summary/rollup. e.g. {metric1: 1, metric2: 0.3},
              rollup_settings could be criteria_weights: {metric1: 0.5, metric2: 0.5}, then
              final score will be 0.5 _ 1 + 0.5 _ 0.3 = 0.65 If skip_rollup is true, the
              rollup step will be skipped since the criteria will also report the rollup score
              and metrics altogether.

          source: Source information for the evaluator codebase.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if account_id is None:
            account_id = self._client._get_account_id_path_param()
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not evaluator_id:
            raise ValueError(f"Expected a non-empty value for `evaluator_id` but received {evaluator_id!r}")
        return await self._patch(
            f"/v1/accounts/{account_id}/evaluators/{evaluator_id}"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/evaluators/{evaluator_id}",
            body=await async_maybe_transform(
                {
                    "commit_hash": commit_hash,
                    "criteria": criteria,
                    "default_dataset": default_dataset,
                    "description": description,
                    "display_name": display_name,
                    "entry_point": entry_point,
                    "multi_metrics": multi_metrics,
                    "requirements": requirements,
                    "rollup_settings": rollup_settings,
                    "source": source,
                },
                evaluator_update_params.EvaluatorUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"prepare_code_upload": prepare_code_upload}, evaluator_update_params.EvaluatorUpdateParams
                ),
            ),
            cast_to=EvaluatorUpdateResponse,
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
    ) -> AsyncPaginator[EvaluatorListResponse, AsyncCursorEvaluators[EvaluatorListResponse]]:
        """
        Lists all evaluators for an account with pagination support.

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
        return self._get_api_list(
            f"/v1/accounts/{account_id}/evaluators"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/evaluators",
            page=AsyncCursorEvaluators[EvaluatorListResponse],
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
                    evaluator_list_params.EvaluatorListParams,
                ),
            ),
            model=EvaluatorListResponse,
        )

    async def delete(
        self,
        evaluator_id: str,
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
        Deletes an evaluator and its associated versions and build artifacts.

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
        if not evaluator_id:
            raise ValueError(f"Expected a non-empty value for `evaluator_id` but received {evaluator_id!r}")
        return await self._delete(
            f"/v1/accounts/{account_id}/evaluators/{evaluator_id}"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/evaluators/{evaluator_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def get(
        self,
        evaluator_id: str,
        *,
        account_id: str | None = None,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EvaluatorGetResponse:
        """Retrieves an evaluator by name.

        Use this to monitor build progress after
        creation (**step 6** in the [Create Evaluator](/api-reference/create-evaluator)
        workflow).

        Possible states:

        - `BUILDING` - Environment is being prepared
        - `ACTIVE` - Evaluator is ready to use
        - `BUILD_FAILED` - Check build logs via
          [Get Evaluator Build Log Endpoint](/api-reference/get-evaluator-build-log-endpoint)

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
        if not evaluator_id:
            raise ValueError(f"Expected a non-empty value for `evaluator_id` but received {evaluator_id!r}")
        return await self._get(
            f"/v1/accounts/{account_id}/evaluators/{evaluator_id}"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/evaluators/{evaluator_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"read_mask": read_mask}, evaluator_get_params.EvaluatorGetParams),
            ),
            cast_to=EvaluatorGetResponse,
        )

    async def get_build_log_endpoint(
        self,
        evaluator_id: str,
        *,
        account_id: str | None = None,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EvaluatorGetBuildLogEndpointResponse:
        """Returns a signed URL to download the evaluator's build logs.

        Useful for
        debugging `BUILD_FAILED` state.

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
        if not evaluator_id:
            raise ValueError(f"Expected a non-empty value for `evaluator_id` but received {evaluator_id!r}")
        return await self._get(
            f"/v1/accounts/{account_id}/evaluators/{evaluator_id}:getBuildLogEndpoint"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/evaluators/{evaluator_id}:getBuildLogEndpoint",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"read_mask": read_mask}, evaluator_get_build_log_endpoint_params.EvaluatorGetBuildLogEndpointParams
                ),
            ),
            cast_to=EvaluatorGetBuildLogEndpointResponse,
        )

    async def get_source_code_endpoint(
        self,
        evaluator_id: str,
        *,
        account_id: str | None = None,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EvaluatorGetSourceCodeEndpointResponse:
        """Returns a signed URL to download the evaluator's source code archive.

        Useful for
        debugging or reviewing the uploaded code.

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
        if not evaluator_id:
            raise ValueError(f"Expected a non-empty value for `evaluator_id` but received {evaluator_id!r}")
        return await self._get(
            f"/v1/accounts/{account_id}/evaluators/{evaluator_id}:getSourceCodeSignedUrl"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/evaluators/{evaluator_id}:getSourceCodeSignedUrl",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"read_mask": read_mask},
                    evaluator_get_source_code_endpoint_params.EvaluatorGetSourceCodeEndpointParams,
                ),
            ),
            cast_to=EvaluatorGetSourceCodeEndpointResponse,
        )

    async def get_upload_endpoint(
        self,
        evaluator_id: str,
        *,
        account_id: str | None = None,
        filename_to_size: Dict[str, str],
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EvaluatorGetUploadEndpointResponse:
        """
        Returns signed URLs for uploading evaluator source code (**step 3** in the
        [Create Evaluator](/api-reference/create-evaluator) workflow). After receiving
        the signed URL, upload your `.tar.gz` archive using HTTP `PUT` with
        `Content-Type: application/octet-stream` header.

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
        if not evaluator_id:
            raise ValueError(f"Expected a non-empty value for `evaluator_id` but received {evaluator_id!r}")
        return await self._post(
            f"/v1/accounts/{account_id}/evaluators/{evaluator_id}:getUploadEndpoint"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/evaluators/{evaluator_id}:getUploadEndpoint",
            body=await async_maybe_transform(
                {
                    "filename_to_size": filename_to_size,
                    "read_mask": read_mask,
                },
                evaluator_get_upload_endpoint_params.EvaluatorGetUploadEndpointParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EvaluatorGetUploadEndpointResponse,
        )

    async def validate_upload(
        self,
        evaluator_id: str,
        *,
        account_id: str | None = None,
        body: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Triggers server-side validation of the uploaded source code (**step 5** in the
        [Create Evaluator](/api-reference/create-evaluator) workflow). The server
        extracts and processes the archive, then builds the evaluator environment. Poll
        [Get Evaluator](/api-reference/get-evaluator) to monitor progress.

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
        if not evaluator_id:
            raise ValueError(f"Expected a non-empty value for `evaluator_id` but received {evaluator_id!r}")
        return await self._post(
            f"/v1/accounts/{account_id}/evaluators/{evaluator_id}:validateUpload"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/evaluators/{evaluator_id}:validateUpload",
            body=await async_maybe_transform(body, evaluator_validate_upload_params.EvaluatorValidateUploadParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class EvaluatorsResourceWithRawResponse:
    def __init__(self, evaluators: EvaluatorsResource) -> None:
        self._evaluators = evaluators

        self.create = to_raw_response_wrapper(
            evaluators.create,
        )
        self.update = to_raw_response_wrapper(
            evaluators.update,
        )
        self.list = to_raw_response_wrapper(
            evaluators.list,
        )
        self.delete = to_raw_response_wrapper(
            evaluators.delete,
        )
        self.get = to_raw_response_wrapper(
            evaluators.get,
        )
        self.get_build_log_endpoint = to_raw_response_wrapper(
            evaluators.get_build_log_endpoint,
        )
        self.get_source_code_endpoint = to_raw_response_wrapper(
            evaluators.get_source_code_endpoint,
        )
        self.get_upload_endpoint = to_raw_response_wrapper(
            evaluators.get_upload_endpoint,
        )
        self.validate_upload = to_raw_response_wrapper(
            evaluators.validate_upload,
        )


class AsyncEvaluatorsResourceWithRawResponse:
    def __init__(self, evaluators: AsyncEvaluatorsResource) -> None:
        self._evaluators = evaluators

        self.create = async_to_raw_response_wrapper(
            evaluators.create,
        )
        self.update = async_to_raw_response_wrapper(
            evaluators.update,
        )
        self.list = async_to_raw_response_wrapper(
            evaluators.list,
        )
        self.delete = async_to_raw_response_wrapper(
            evaluators.delete,
        )
        self.get = async_to_raw_response_wrapper(
            evaluators.get,
        )
        self.get_build_log_endpoint = async_to_raw_response_wrapper(
            evaluators.get_build_log_endpoint,
        )
        self.get_source_code_endpoint = async_to_raw_response_wrapper(
            evaluators.get_source_code_endpoint,
        )
        self.get_upload_endpoint = async_to_raw_response_wrapper(
            evaluators.get_upload_endpoint,
        )
        self.validate_upload = async_to_raw_response_wrapper(
            evaluators.validate_upload,
        )


class EvaluatorsResourceWithStreamingResponse:
    def __init__(self, evaluators: EvaluatorsResource) -> None:
        self._evaluators = evaluators

        self.create = to_streamed_response_wrapper(
            evaluators.create,
        )
        self.update = to_streamed_response_wrapper(
            evaluators.update,
        )
        self.list = to_streamed_response_wrapper(
            evaluators.list,
        )
        self.delete = to_streamed_response_wrapper(
            evaluators.delete,
        )
        self.get = to_streamed_response_wrapper(
            evaluators.get,
        )
        self.get_build_log_endpoint = to_streamed_response_wrapper(
            evaluators.get_build_log_endpoint,
        )
        self.get_source_code_endpoint = to_streamed_response_wrapper(
            evaluators.get_source_code_endpoint,
        )
        self.get_upload_endpoint = to_streamed_response_wrapper(
            evaluators.get_upload_endpoint,
        )
        self.validate_upload = to_streamed_response_wrapper(
            evaluators.validate_upload,
        )


class AsyncEvaluatorsResourceWithStreamingResponse:
    def __init__(self, evaluators: AsyncEvaluatorsResource) -> None:
        self._evaluators = evaluators

        self.create = async_to_streamed_response_wrapper(
            evaluators.create,
        )
        self.update = async_to_streamed_response_wrapper(
            evaluators.update,
        )
        self.list = async_to_streamed_response_wrapper(
            evaluators.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            evaluators.delete,
        )
        self.get = async_to_streamed_response_wrapper(
            evaluators.get,
        )
        self.get_build_log_endpoint = async_to_streamed_response_wrapper(
            evaluators.get_build_log_endpoint,
        )
        self.get_source_code_endpoint = async_to_streamed_response_wrapper(
            evaluators.get_source_code_endpoint,
        )
        self.get_upload_endpoint = async_to_streamed_response_wrapper(
            evaluators.get_upload_endpoint,
        )
        self.validate_upload = async_to_streamed_response_wrapper(
            evaluators.validate_upload,
        )
