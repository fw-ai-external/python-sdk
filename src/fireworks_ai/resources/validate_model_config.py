# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import validate_model_config_validate_params
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

__all__ = ["ValidateModelConfigResource", "AsyncValidateModelConfigResource"]


class ValidateModelConfigResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ValidateModelConfigResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#accessing-raw-response-data-eg-headers
        """
        return ValidateModelConfigResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ValidateModelConfigResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#with_streaming_response
        """
        return ValidateModelConfigResourceWithStreamingResponse(self)

    def validate(
        self,
        *,
        config_json: str,
        tokenizer_config_json: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Validate Model Config

        Args:
          config_json: The config JSON of the model.

          tokenizer_config_json: The tokenizer config JSON of the model.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/validateModelConfig",
            body=maybe_transform(
                {
                    "config_json": config_json,
                    "tokenizer_config_json": tokenizer_config_json,
                },
                validate_model_config_validate_params.ValidateModelConfigValidateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncValidateModelConfigResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncValidateModelConfigResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncValidateModelConfigResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncValidateModelConfigResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#with_streaming_response
        """
        return AsyncValidateModelConfigResourceWithStreamingResponse(self)

    async def validate(
        self,
        *,
        config_json: str,
        tokenizer_config_json: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Validate Model Config

        Args:
          config_json: The config JSON of the model.

          tokenizer_config_json: The tokenizer config JSON of the model.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/validateModelConfig",
            body=await async_maybe_transform(
                {
                    "config_json": config_json,
                    "tokenizer_config_json": tokenizer_config_json,
                },
                validate_model_config_validate_params.ValidateModelConfigValidateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class ValidateModelConfigResourceWithRawResponse:
    def __init__(self, validate_model_config: ValidateModelConfigResource) -> None:
        self._validate_model_config = validate_model_config

        self.validate = to_raw_response_wrapper(
            validate_model_config.validate,
        )


class AsyncValidateModelConfigResourceWithRawResponse:
    def __init__(self, validate_model_config: AsyncValidateModelConfigResource) -> None:
        self._validate_model_config = validate_model_config

        self.validate = async_to_raw_response_wrapper(
            validate_model_config.validate,
        )


class ValidateModelConfigResourceWithStreamingResponse:
    def __init__(self, validate_model_config: ValidateModelConfigResource) -> None:
        self._validate_model_config = validate_model_config

        self.validate = to_streamed_response_wrapper(
            validate_model_config.validate,
        )


class AsyncValidateModelConfigResourceWithStreamingResponse:
    def __init__(self, validate_model_config: AsyncValidateModelConfigResource) -> None:
        self._validate_model_config = validate_model_config

        self.validate = async_to_streamed_response_wrapper(
            validate_model_config.validate,
        )
