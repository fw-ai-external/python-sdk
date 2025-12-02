# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import deployment_shape_version_get_params, deployment_shape_version_list_params
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
from ..types.deployment_shape_version_get_response import DeploymentShapeVersionGetResponse
from ..types.deployment_shape_version_list_response import DeploymentShapeVersionListResponse

__all__ = ["DeploymentShapeVersionsResource", "AsyncDeploymentShapeVersionsResource"]


class DeploymentShapeVersionsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> DeploymentShapeVersionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#accessing-raw-response-data-eg-headers
        """
        return DeploymentShapeVersionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DeploymentShapeVersionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#with_streaming_response
        """
        return DeploymentShapeVersionsResourceWithStreamingResponse(self)

    def list(
        self,
        deployment_shape_id: str,
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
    ) -> DeploymentShapeVersionListResponse:
        """
        List Deployment Shapes Versions

        Args:
          filter: Only deployment shape versions satisfying the provided filter (if specified)
              will be returned. See https://google.aip.dev/160 for the filter grammar.

          order_by: A comma-separated list of fields to order by. e.g. "foo,bar" The default sort
              order is ascending. To specify a descending order for a field, append a " desc"
              suffix. e.g. "foo desc,bar" Subfields are specified with a "." character. e.g.
              "foo.bar" If not specified, the default order is by "create_time".

          page_size: The maximum number of deployment shape versions to return. The maximum page_size
              is 200, values above 200 will be coerced to 200. If unspecified, the default
              is 50.

          page_token: A page token, received from a previous ListDeploymentShapeVersions call. Provide
              this to retrieve the subsequent page. When paginating, all other parameters
              provided to ListDeploymentShapeVersions must match the call that provided the
              page token.

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
            f"/v1/accounts/{account_id}/deploymentShapes/{deployment_shape_id}/versions"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/deploymentShapes/{deployment_shape_id}/versions",
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
                    deployment_shape_version_list_params.DeploymentShapeVersionListParams,
                ),
            ),
            cast_to=DeploymentShapeVersionListResponse,
        )

    def get(
        self,
        version_id: str,
        *,
        account_id: str | None = None,
        deployment_shape_id: str,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DeploymentShapeVersionGetResponse:
        """
        Get Deployment Shape Version

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
        if not version_id:
            raise ValueError(f"Expected a non-empty value for `version_id` but received {version_id!r}")
        return self._get(
            f"/v1/accounts/{account_id}/deploymentShapes/{deployment_shape_id}/versions/{version_id}"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/deploymentShapes/{deployment_shape_id}/versions/{version_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"read_mask": read_mask}, deployment_shape_version_get_params.DeploymentShapeVersionGetParams
                ),
            ),
            cast_to=DeploymentShapeVersionGetResponse,
        )


class AsyncDeploymentShapeVersionsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncDeploymentShapeVersionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncDeploymentShapeVersionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDeploymentShapeVersionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#with_streaming_response
        """
        return AsyncDeploymentShapeVersionsResourceWithStreamingResponse(self)

    async def list(
        self,
        deployment_shape_id: str,
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
    ) -> DeploymentShapeVersionListResponse:
        """
        List Deployment Shapes Versions

        Args:
          filter: Only deployment shape versions satisfying the provided filter (if specified)
              will be returned. See https://google.aip.dev/160 for the filter grammar.

          order_by: A comma-separated list of fields to order by. e.g. "foo,bar" The default sort
              order is ascending. To specify a descending order for a field, append a " desc"
              suffix. e.g. "foo desc,bar" Subfields are specified with a "." character. e.g.
              "foo.bar" If not specified, the default order is by "create_time".

          page_size: The maximum number of deployment shape versions to return. The maximum page_size
              is 200, values above 200 will be coerced to 200. If unspecified, the default
              is 50.

          page_token: A page token, received from a previous ListDeploymentShapeVersions call. Provide
              this to retrieve the subsequent page. When paginating, all other parameters
              provided to ListDeploymentShapeVersions must match the call that provided the
              page token.

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
            f"/v1/accounts/{account_id}/deploymentShapes/{deployment_shape_id}/versions"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/deploymentShapes/{deployment_shape_id}/versions",
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
                    deployment_shape_version_list_params.DeploymentShapeVersionListParams,
                ),
            ),
            cast_to=DeploymentShapeVersionListResponse,
        )

    async def get(
        self,
        version_id: str,
        *,
        account_id: str | None = None,
        deployment_shape_id: str,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DeploymentShapeVersionGetResponse:
        """
        Get Deployment Shape Version

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
        if not version_id:
            raise ValueError(f"Expected a non-empty value for `version_id` but received {version_id!r}")
        return await self._get(
            f"/v1/accounts/{account_id}/deploymentShapes/{deployment_shape_id}/versions/{version_id}"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/deploymentShapes/{deployment_shape_id}/versions/{version_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"read_mask": read_mask}, deployment_shape_version_get_params.DeploymentShapeVersionGetParams
                ),
            ),
            cast_to=DeploymentShapeVersionGetResponse,
        )


class DeploymentShapeVersionsResourceWithRawResponse:
    def __init__(self, deployment_shape_versions: DeploymentShapeVersionsResource) -> None:
        self._deployment_shape_versions = deployment_shape_versions

        self.list = to_raw_response_wrapper(
            deployment_shape_versions.list,
        )
        self.get = to_raw_response_wrapper(
            deployment_shape_versions.get,
        )


class AsyncDeploymentShapeVersionsResourceWithRawResponse:
    def __init__(self, deployment_shape_versions: AsyncDeploymentShapeVersionsResource) -> None:
        self._deployment_shape_versions = deployment_shape_versions

        self.list = async_to_raw_response_wrapper(
            deployment_shape_versions.list,
        )
        self.get = async_to_raw_response_wrapper(
            deployment_shape_versions.get,
        )


class DeploymentShapeVersionsResourceWithStreamingResponse:
    def __init__(self, deployment_shape_versions: DeploymentShapeVersionsResource) -> None:
        self._deployment_shape_versions = deployment_shape_versions

        self.list = to_streamed_response_wrapper(
            deployment_shape_versions.list,
        )
        self.get = to_streamed_response_wrapper(
            deployment_shape_versions.get,
        )


class AsyncDeploymentShapeVersionsResourceWithStreamingResponse:
    def __init__(self, deployment_shape_versions: AsyncDeploymentShapeVersionsResource) -> None:
        self._deployment_shape_versions = deployment_shape_versions

        self.list = async_to_streamed_response_wrapper(
            deployment_shape_versions.list,
        )
        self.get = async_to_streamed_response_wrapper(
            deployment_shape_versions.get,
        )
