# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import deployment_shape_get_params, deployment_shape_list_params
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
from ..pagination import SyncCursorDeploymentShapes, AsyncCursorDeploymentShapes
from .._base_client import AsyncPaginator, make_request_options
from ..types.deployment_shape import DeploymentShape

__all__ = ["DeploymentShapesResource", "AsyncDeploymentShapesResource"]


class DeploymentShapesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> DeploymentShapesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#accessing-raw-response-data-eg-headers
        """
        return DeploymentShapesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DeploymentShapesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#with_streaming_response
        """
        return DeploymentShapesResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        account_id: str | None = None,
        filter: str | Omit = omit,
        order_by: str | Omit = omit,
        page_size: int | Omit = omit,
        page_token: str | Omit = omit,
        read_mask: str | Omit = omit,
        target_model: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SyncCursorDeploymentShapes[DeploymentShape]:
        """
        List Deployment Shapes

        Args:
          filter: Only deployment satisfying the provided filter (if specified) will be returned.
              See https://google.aip.dev/160 for the filter grammar.

          order_by: A comma-separated list of fields to order by. e.g. "foo,bar" The default sort
              order is ascending. To specify a descending order for a field, append a " desc"
              suffix. e.g. "foo desc,bar" Subfields are specified with a "." character. e.g.
              "foo.bar" If not specified, the default order is by "create_time".

          page_size: The maximum number of deployments to return. The maximum page_size is 200,
              values above 200 will be coerced to 200. If unspecified, the default is 50.

          page_token: A page token, received from a previous ListDeploymentShapes call. Provide this
              to retrieve the subsequent page. When paginating, all other parameters provided
              to ListDeploymentShapes must match the call that provided the page token.

          read_mask: The fields to be returned in the response. If empty or "\\**", all fields will be
              returned.

          target_model: Target model that the returned deployment shapes should be compatible with.

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
            f"/v1/accounts/{account_id}/deploymentShapes"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/deploymentShapes",
            page=SyncCursorDeploymentShapes[DeploymentShape],
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
                        "target_model": target_model,
                    },
                    deployment_shape_list_params.DeploymentShapeListParams,
                ),
            ),
            model=DeploymentShape,
        )

    def get(
        self,
        deployment_shape_id: str,
        *,
        account_id: str | None = None,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DeploymentShape:
        """
        Get Deployment Shape

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
        if not deployment_shape_id:
            raise ValueError(
                f"Expected a non-empty value for `deployment_shape_id` but received {deployment_shape_id!r}"
            )
        return self._get(
            f"/v1/accounts/{account_id}/deploymentShapes/{deployment_shape_id}"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/deploymentShapes/{deployment_shape_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"read_mask": read_mask}, deployment_shape_get_params.DeploymentShapeGetParams),
            ),
            cast_to=DeploymentShape,
        )


class AsyncDeploymentShapesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncDeploymentShapesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncDeploymentShapesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDeploymentShapesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#with_streaming_response
        """
        return AsyncDeploymentShapesResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        account_id: str | None = None,
        filter: str | Omit = omit,
        order_by: str | Omit = omit,
        page_size: int | Omit = omit,
        page_token: str | Omit = omit,
        read_mask: str | Omit = omit,
        target_model: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[DeploymentShape, AsyncCursorDeploymentShapes[DeploymentShape]]:
        """
        List Deployment Shapes

        Args:
          filter: Only deployment satisfying the provided filter (if specified) will be returned.
              See https://google.aip.dev/160 for the filter grammar.

          order_by: A comma-separated list of fields to order by. e.g. "foo,bar" The default sort
              order is ascending. To specify a descending order for a field, append a " desc"
              suffix. e.g. "foo desc,bar" Subfields are specified with a "." character. e.g.
              "foo.bar" If not specified, the default order is by "create_time".

          page_size: The maximum number of deployments to return. The maximum page_size is 200,
              values above 200 will be coerced to 200. If unspecified, the default is 50.

          page_token: A page token, received from a previous ListDeploymentShapes call. Provide this
              to retrieve the subsequent page. When paginating, all other parameters provided
              to ListDeploymentShapes must match the call that provided the page token.

          read_mask: The fields to be returned in the response. If empty or "\\**", all fields will be
              returned.

          target_model: Target model that the returned deployment shapes should be compatible with.

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
            f"/v1/accounts/{account_id}/deploymentShapes"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/deploymentShapes",
            page=AsyncCursorDeploymentShapes[DeploymentShape],
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
                        "target_model": target_model,
                    },
                    deployment_shape_list_params.DeploymentShapeListParams,
                ),
            ),
            model=DeploymentShape,
        )

    async def get(
        self,
        deployment_shape_id: str,
        *,
        account_id: str | None = None,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DeploymentShape:
        """
        Get Deployment Shape

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
        if not deployment_shape_id:
            raise ValueError(
                f"Expected a non-empty value for `deployment_shape_id` but received {deployment_shape_id!r}"
            )
        return await self._get(
            f"/v1/accounts/{account_id}/deploymentShapes/{deployment_shape_id}"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/deploymentShapes/{deployment_shape_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"read_mask": read_mask}, deployment_shape_get_params.DeploymentShapeGetParams
                ),
            ),
            cast_to=DeploymentShape,
        )


class DeploymentShapesResourceWithRawResponse:
    def __init__(self, deployment_shapes: DeploymentShapesResource) -> None:
        self._deployment_shapes = deployment_shapes

        self.list = to_raw_response_wrapper(
            deployment_shapes.list,
        )
        self.get = to_raw_response_wrapper(
            deployment_shapes.get,
        )


class AsyncDeploymentShapesResourceWithRawResponse:
    def __init__(self, deployment_shapes: AsyncDeploymentShapesResource) -> None:
        self._deployment_shapes = deployment_shapes

        self.list = async_to_raw_response_wrapper(
            deployment_shapes.list,
        )
        self.get = async_to_raw_response_wrapper(
            deployment_shapes.get,
        )


class DeploymentShapesResourceWithStreamingResponse:
    def __init__(self, deployment_shapes: DeploymentShapesResource) -> None:
        self._deployment_shapes = deployment_shapes

        self.list = to_streamed_response_wrapper(
            deployment_shapes.list,
        )
        self.get = to_streamed_response_wrapper(
            deployment_shapes.get,
        )


class AsyncDeploymentShapesResourceWithStreamingResponse:
    def __init__(self, deployment_shapes: AsyncDeploymentShapesResource) -> None:
        self._deployment_shapes = deployment_shapes

        self.list = async_to_streamed_response_wrapper(
            deployment_shapes.list,
        )
        self.get = async_to_streamed_response_wrapper(
            deployment_shapes.get,
        )
