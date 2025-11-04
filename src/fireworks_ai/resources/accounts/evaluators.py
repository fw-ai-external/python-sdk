# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict

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
    GatewayEvaluator,
    evaluator_list_params,
    evaluator_create_params,
    evaluator_retrieve_params,
    evaluator_validate_upload_params,
    evaluator_get_upload_endpoint_params,
    evaluator_get_build_log_endpoint_params,
)
from ...types.accounts.gateway_evaluator import GatewayEvaluator
from ...types.accounts.evaluator_list_response import EvaluatorListResponse
from ...types.accounts.gateway_evaluator_param import GatewayEvaluatorParam
from ...types.accounts.evaluator_get_upload_endpoint_response import EvaluatorGetUploadEndpointResponse
from ...types.accounts.evaluator_get_build_log_endpoint_response import EvaluatorGetBuildLogEndpointResponse

__all__ = ["EvaluatorsResource", "AsyncEvaluatorsResource"]


class EvaluatorsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> EvaluatorsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/stainless-sdks/fireworks-ai-python#accessing-raw-response-data-eg-headers
        """
        return EvaluatorsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> EvaluatorsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stainless-sdks/fireworks-ai-python#with_streaming_response
        """
        return EvaluatorsResourceWithStreamingResponse(self)

    def create(
        self,
        account_id: str,
        *,
        evaluator: GatewayEvaluatorParam,
        evaluator_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayEvaluator:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._post(
            f"/v1/accounts/{account_id}/evaluators",
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
            cast_to=GatewayEvaluator,
        )

    def retrieve(
        self,
        evaluator_id: str,
        *,
        account_id: str,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayEvaluator:
        """Args:
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
        if not evaluator_id:
            raise ValueError(f"Expected a non-empty value for `evaluator_id` but received {evaluator_id!r}")
        return self._get(
            f"/v1/accounts/{account_id}/evaluators/{evaluator_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"read_mask": read_mask}, evaluator_retrieve_params.EvaluatorRetrieveParams),
            ),
            cast_to=GatewayEvaluator,
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
    ) -> EvaluatorListResponse:
        """Args:
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
        return self._get(
            f"/v1/accounts/{account_id}/evaluators",
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
            cast_to=EvaluatorListResponse,
        )

    def delete(
        self,
        evaluator_id: str,
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
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not evaluator_id:
            raise ValueError(f"Expected a non-empty value for `evaluator_id` but received {evaluator_id!r}")
        return self._delete(
            f"/v1/accounts/{account_id}/evaluators/{evaluator_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def get_build_log_endpoint(
        self,
        evaluator_id: str,
        *,
        account_id: str,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EvaluatorGetBuildLogEndpointResponse:
        """Args:
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
        if not evaluator_id:
            raise ValueError(f"Expected a non-empty value for `evaluator_id` but received {evaluator_id!r}")
        return self._get(
            f"/v1/accounts/{account_id}/evaluators/{evaluator_id}:getBuildLogEndpoint",
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

    def get_upload_endpoint(
        self,
        evaluator_id: str,
        *,
        account_id: str,
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
        Return the evaluator source code GCS upload sign url

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not evaluator_id:
            raise ValueError(f"Expected a non-empty value for `evaluator_id` but received {evaluator_id!r}")
        return self._post(
            f"/v1/accounts/{account_id}/evaluators/{evaluator_id}:getUploadEndpoint",
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
        Validate the evaluator source code upload is finished by the client side

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not evaluator_id:
            raise ValueError(f"Expected a non-empty value for `evaluator_id` but received {evaluator_id!r}")
        return self._post(
            f"/v1/accounts/{account_id}/evaluators/{evaluator_id}:validateUpload",
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

        For more information, see https://www.github.com/stainless-sdks/fireworks-ai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncEvaluatorsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncEvaluatorsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/stainless-sdks/fireworks-ai-python#with_streaming_response
        """
        return AsyncEvaluatorsResourceWithStreamingResponse(self)

    async def create(
        self,
        account_id: str,
        *,
        evaluator: GatewayEvaluatorParam,
        evaluator_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayEvaluator:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._post(
            f"/v1/accounts/{account_id}/evaluators",
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
            cast_to=GatewayEvaluator,
        )

    async def retrieve(
        self,
        evaluator_id: str,
        *,
        account_id: str,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayEvaluator:
        """Args:
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
        if not evaluator_id:
            raise ValueError(f"Expected a non-empty value for `evaluator_id` but received {evaluator_id!r}")
        return await self._get(
            f"/v1/accounts/{account_id}/evaluators/{evaluator_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"read_mask": read_mask}, evaluator_retrieve_params.EvaluatorRetrieveParams
                ),
            ),
            cast_to=GatewayEvaluator,
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
    ) -> EvaluatorListResponse:
        """Args:
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
        return await self._get(
            f"/v1/accounts/{account_id}/evaluators",
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
                    evaluator_list_params.EvaluatorListParams,
                ),
            ),
            cast_to=EvaluatorListResponse,
        )

    async def delete(
        self,
        evaluator_id: str,
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
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not evaluator_id:
            raise ValueError(f"Expected a non-empty value for `evaluator_id` but received {evaluator_id!r}")
        return await self._delete(
            f"/v1/accounts/{account_id}/evaluators/{evaluator_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def get_build_log_endpoint(
        self,
        evaluator_id: str,
        *,
        account_id: str,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EvaluatorGetBuildLogEndpointResponse:
        """Args:
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
        if not evaluator_id:
            raise ValueError(f"Expected a non-empty value for `evaluator_id` but received {evaluator_id!r}")
        return await self._get(
            f"/v1/accounts/{account_id}/evaluators/{evaluator_id}:getBuildLogEndpoint",
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

    async def get_upload_endpoint(
        self,
        evaluator_id: str,
        *,
        account_id: str,
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
        Return the evaluator source code GCS upload sign url

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not evaluator_id:
            raise ValueError(f"Expected a non-empty value for `evaluator_id` but received {evaluator_id!r}")
        return await self._post(
            f"/v1/accounts/{account_id}/evaluators/{evaluator_id}:getUploadEndpoint",
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
        Validate the evaluator source code upload is finished by the client side

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not evaluator_id:
            raise ValueError(f"Expected a non-empty value for `evaluator_id` but received {evaluator_id!r}")
        return await self._post(
            f"/v1/accounts/{account_id}/evaluators/{evaluator_id}:validateUpload",
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
        self.retrieve = to_raw_response_wrapper(
            evaluators.retrieve,
        )
        self.list = to_raw_response_wrapper(
            evaluators.list,
        )
        self.delete = to_raw_response_wrapper(
            evaluators.delete,
        )
        self.get_build_log_endpoint = to_raw_response_wrapper(
            evaluators.get_build_log_endpoint,
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
        self.retrieve = async_to_raw_response_wrapper(
            evaluators.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            evaluators.list,
        )
        self.delete = async_to_raw_response_wrapper(
            evaluators.delete,
        )
        self.get_build_log_endpoint = async_to_raw_response_wrapper(
            evaluators.get_build_log_endpoint,
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
        self.retrieve = to_streamed_response_wrapper(
            evaluators.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            evaluators.list,
        )
        self.delete = to_streamed_response_wrapper(
            evaluators.delete,
        )
        self.get_build_log_endpoint = to_streamed_response_wrapper(
            evaluators.get_build_log_endpoint,
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
        self.retrieve = async_to_streamed_response_wrapper(
            evaluators.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            evaluators.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            evaluators.delete,
        )
        self.get_build_log_endpoint = async_to_streamed_response_wrapper(
            evaluators.get_build_log_endpoint,
        )
        self.get_upload_endpoint = async_to_streamed_response_wrapper(
            evaluators.get_upload_endpoint,
        )
        self.validate_upload = async_to_streamed_response_wrapper(
            evaluators.validate_upload,
        )
