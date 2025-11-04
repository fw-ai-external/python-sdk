# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

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
from ...types.accounts import aws_iam_role_binding_list_params, aws_iam_role_binding_create_params
from ...types.accounts.gateway_aws_iam_role_binding import GatewayAwsIamRoleBinding
from ...types.accounts.aws_iam_role_binding_list_response import AwsIamRoleBindingListResponse

__all__ = ["AwsIamRoleBindingsResource", "AsyncAwsIamRoleBindingsResource"]


class AwsIamRoleBindingsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AwsIamRoleBindingsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#accessing-raw-response-data-eg-headers
        """
        return AwsIamRoleBindingsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AwsIamRoleBindingsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#with_streaming_response
        """
        return AwsIamRoleBindingsResourceWithStreamingResponse(self)

    def create(
        self,
        account_id: str,
        *,
        principal: str,
        role: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayAwsIamRoleBinding:
        """
        Create Aws Iam Role Binding

        Args:
          principal: The principal that is allowed to assume the AWS IAM role. This must be the email
              address of the user.

          role: The AWS IAM role ARN that is allowed to be assumed by the principal.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._post(
            f"/v1/accounts/{account_id}/awsIamRoleBindings",
            body=maybe_transform(
                {
                    "principal": principal,
                    "role": role,
                },
                aws_iam_role_binding_create_params.AwsIamRoleBindingCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GatewayAwsIamRoleBinding,
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
    ) -> AwsIamRoleBindingListResponse:
        """
        List Aws Iam Role Bindings

        Args:
          filter: Only bindings satisfying the provided filter (if specified) will be returned.
              See https://google.aip.dev/160 for the filter grammar.

          order_by: A comma-separated list of fields to order by. e.g. "foo,bar" The default sort
              order is ascending. To specify a descending order for a field, append a " desc"
              suffix. e.g. "foo desc,bar" Subfields are specified with a "." character. e.g.
              "foo.bar" If not specified, the default order is by "name".

          page_size: The maximum number of bindings to return. The maximum page_size is 200, values
              above 200 will be coerced to 200. If unspecified, the default is 50.

          page_token: A page token, received from a previous ListAwsIamRoleBindings call. Provide this
              to retrieve the subsequent page. When paginating, all other parameters provided
              to ListAwsIamRoleBindings must match the call that provided the page token.

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
            f"/v1/accounts/{account_id}/awsIamRoleBindings",
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
                    aws_iam_role_binding_list_params.AwsIamRoleBindingListParams,
                ),
            ),
            cast_to=AwsIamRoleBindingListResponse,
        )


class AsyncAwsIamRoleBindingsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAwsIamRoleBindingsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncAwsIamRoleBindingsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAwsIamRoleBindingsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#with_streaming_response
        """
        return AsyncAwsIamRoleBindingsResourceWithStreamingResponse(self)

    async def create(
        self,
        account_id: str,
        *,
        principal: str,
        role: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayAwsIamRoleBinding:
        """
        Create Aws Iam Role Binding

        Args:
          principal: The principal that is allowed to assume the AWS IAM role. This must be the email
              address of the user.

          role: The AWS IAM role ARN that is allowed to be assumed by the principal.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._post(
            f"/v1/accounts/{account_id}/awsIamRoleBindings",
            body=await async_maybe_transform(
                {
                    "principal": principal,
                    "role": role,
                },
                aws_iam_role_binding_create_params.AwsIamRoleBindingCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GatewayAwsIamRoleBinding,
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
    ) -> AwsIamRoleBindingListResponse:
        """
        List Aws Iam Role Bindings

        Args:
          filter: Only bindings satisfying the provided filter (if specified) will be returned.
              See https://google.aip.dev/160 for the filter grammar.

          order_by: A comma-separated list of fields to order by. e.g. "foo,bar" The default sort
              order is ascending. To specify a descending order for a field, append a " desc"
              suffix. e.g. "foo desc,bar" Subfields are specified with a "." character. e.g.
              "foo.bar" If not specified, the default order is by "name".

          page_size: The maximum number of bindings to return. The maximum page_size is 200, values
              above 200 will be coerced to 200. If unspecified, the default is 50.

          page_token: A page token, received from a previous ListAwsIamRoleBindings call. Provide this
              to retrieve the subsequent page. When paginating, all other parameters provided
              to ListAwsIamRoleBindings must match the call that provided the page token.

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
            f"/v1/accounts/{account_id}/awsIamRoleBindings",
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
                    aws_iam_role_binding_list_params.AwsIamRoleBindingListParams,
                ),
            ),
            cast_to=AwsIamRoleBindingListResponse,
        )


class AwsIamRoleBindingsResourceWithRawResponse:
    def __init__(self, aws_iam_role_bindings: AwsIamRoleBindingsResource) -> None:
        self._aws_iam_role_bindings = aws_iam_role_bindings

        self.create = to_raw_response_wrapper(
            aws_iam_role_bindings.create,
        )
        self.list = to_raw_response_wrapper(
            aws_iam_role_bindings.list,
        )


class AsyncAwsIamRoleBindingsResourceWithRawResponse:
    def __init__(self, aws_iam_role_bindings: AsyncAwsIamRoleBindingsResource) -> None:
        self._aws_iam_role_bindings = aws_iam_role_bindings

        self.create = async_to_raw_response_wrapper(
            aws_iam_role_bindings.create,
        )
        self.list = async_to_raw_response_wrapper(
            aws_iam_role_bindings.list,
        )


class AwsIamRoleBindingsResourceWithStreamingResponse:
    def __init__(self, aws_iam_role_bindings: AwsIamRoleBindingsResource) -> None:
        self._aws_iam_role_bindings = aws_iam_role_bindings

        self.create = to_streamed_response_wrapper(
            aws_iam_role_bindings.create,
        )
        self.list = to_streamed_response_wrapper(
            aws_iam_role_bindings.list,
        )


class AsyncAwsIamRoleBindingsResourceWithStreamingResponse:
    def __init__(self, aws_iam_role_bindings: AsyncAwsIamRoleBindingsResource) -> None:
        self._aws_iam_role_bindings = aws_iam_role_bindings

        self.create = async_to_streamed_response_wrapper(
            aws_iam_role_bindings.create,
        )
        self.list = async_to_streamed_response_wrapper(
            aws_iam_role_bindings.list,
        )
