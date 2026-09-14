# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

# NOTE: the match() method, its params/response types, and the
# match_for_model() convenience wrapper below are hand-written in the
# surrounding generated style, matching the OpenAPI entry added in PR #47681.
# The Stainless codegen pipeline that used to regenerate this folder is
# currently unwired (removed in PR #26426), so SDK additions are made by hand
# per the PR #47065 precedent. If stlc generation is ever restored, match()
# will be superseded by generated code and match_for_model() — which has no
# spec counterpart — must be re-added by hand.
from ..types import (
    deployment_shape_version_get_params,
    deployment_shape_version_list_params,
    deployment_shape_version_match_params,
)
from .._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from .._utils import path_template, maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..pagination import SyncCursorDeploymentShapeVersions, AsyncCursorDeploymentShapeVersions
from .._base_client import AsyncPaginator, make_request_options
from ..types.deployment_shape_version import DeploymentShapeVersion
from ..types.deployment_shape_version_match_response import DeploymentShapeVersionMatchResponse

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
    ) -> SyncCursorDeploymentShapeVersions[DeploymentShapeVersion]:
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
        return self._get_api_list(
            ("https://api.fireworks.ai" if not self._client._base_url_overridden else "")
            + path_template(
                "/v1/accounts/{account_id}/deploymentShapes/{deployment_shape_id}/versions",
                account_id=account_id,
                deployment_shape_id=deployment_shape_id,
            ),
            page=SyncCursorDeploymentShapeVersions[DeploymentShapeVersion],
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
            model=DeploymentShapeVersion,
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
    ) -> DeploymentShapeVersion:
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
            ("https://api.fireworks.ai" if not self._client._base_url_overridden else "")
            + path_template(
                "/v1/accounts/{account_id}/deploymentShapes/{deployment_shape_id}/versions/{version_id}",
                account_id=account_id,
                deployment_shape_id=deployment_shape_id,
                version_id=version_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"read_mask": read_mask}, deployment_shape_version_get_params.DeploymentShapeVersionGetParams
                ),
            ),
            cast_to=DeploymentShapeVersion,
        )

    # NOTE: hand-written in generated style (see module top note).
    def match(
        self,
        *,
        account_id: str | None = None,
        create_deployment_request: deployment_shape_version_match_params.CreateDeploymentRequest,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DeploymentShapeVersionMatchResponse:
        """
        Match Deployment Shape Versions

        Returns the deployment shape versions compatible with the provided
        deployment create request. Use this to discover a validated shape before
        creating a deployment with `deployment_shape` set - shapeless deployments
        (raw accelerator type/count) skip validated-configuration checks and are
        far more likely to fail at creation.

        Args:
          create_deployment_request: The deployment create request to match deployment shape
              versions for. Only `parent`, `deployment.baseModel`, and
              `deployment.enableAddons` are typed (and camelCased on the wire) by this
              hand-written method; other keys pass through verbatim, so send them in
              their wire (camelCase) form if needed.

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
            ("https://api.fireworks.ai" if not self._client._base_url_overridden else "")
            + path_template("/v1/accounts/{account_id}/deploymentShapeVersions:match", account_id=account_id),
            body=maybe_transform(
                {
                    "create_deployment_request": create_deployment_request,
                },
                deployment_shape_version_match_params.DeploymentShapeVersionMatchParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeploymentShapeVersionMatchResponse,
        )

    # NOTE: hand-written convenience method with no OpenAPI counterpart —
    # no generator will ever emit it; see the module top note.
    def match_for_model(
        self,
        model: str,
        *,
        account_id: str | None = None,
        enable_addons: bool = False,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DeploymentShapeVersionMatchResponse:
        """
        Discover deployment shape versions for a model in one call.

        Pass any model name — a full resource path like
        `accounts/fireworks/models/gemma-4-31b-it` or a LoRA addon like
        `accounts/palo-alto-networks/models/sft-gemma-4-31b-it-clickfix`. The
        server resolves PEFT addons and live-merge models to their base model,
        scopes results to shapes your account can deploy, and requires
        MULTI_LORA-capable shapes when `enable_addons` is true. No client-side
        model lookup is performed.

        The happy path end to end:

        ```python
        match = client.deployment_shape_versions.match_for_model("accounts/fireworks/models/gemma-4-31b-it")
        shape = match.deployment_shape_versions[0].snapshot  # pick a shape
        deployment = client.deployments.create(
            base_model="accounts/fireworks/models/gemma-4-31b-it",
            deployment_shape=shape.name,
        )
        ```

        An empty `deployment_shape_versions` list means no validated shape fits
        the model for your account.

        Args:
          model: The base model the deployment will serve. A full resource path
              such as `accounts/fireworks/models/gemma-4-31b-it` or a LoRA addon
              such as `accounts/palo-alto-networks/models/sft-gemma-4-31b-it-clickfix`.

          enable_addons: If true, LORA addons are enabled for the deployment. Only
              MULTI_LORA-capable shapes will be matched.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if account_id is None:
            account_id = self._client._get_account_id_path_param()
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self.match(
            account_id=account_id,
            create_deployment_request={
                "parent": f"accounts/{account_id}",
                "deployment": {
                    "base_model": model,
                    "enable_addons": enable_addons,
                },
            },
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
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
    ) -> AsyncPaginator[DeploymentShapeVersion, AsyncCursorDeploymentShapeVersions[DeploymentShapeVersion]]:
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
        return self._get_api_list(
            ("https://api.fireworks.ai" if not self._client._base_url_overridden else "")
            + path_template(
                "/v1/accounts/{account_id}/deploymentShapes/{deployment_shape_id}/versions",
                account_id=account_id,
                deployment_shape_id=deployment_shape_id,
            ),
            page=AsyncCursorDeploymentShapeVersions[DeploymentShapeVersion],
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
            model=DeploymentShapeVersion,
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
    ) -> DeploymentShapeVersion:
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
            ("https://api.fireworks.ai" if not self._client._base_url_overridden else "")
            + path_template(
                "/v1/accounts/{account_id}/deploymentShapes/{deployment_shape_id}/versions/{version_id}",
                account_id=account_id,
                deployment_shape_id=deployment_shape_id,
                version_id=version_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"read_mask": read_mask}, deployment_shape_version_get_params.DeploymentShapeVersionGetParams
                ),
            ),
            cast_to=DeploymentShapeVersion,
        )

    # NOTE: hand-written in generated style (see module top note).
    async def match(
        self,
        *,
        account_id: str | None = None,
        create_deployment_request: deployment_shape_version_match_params.CreateDeploymentRequest,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DeploymentShapeVersionMatchResponse:
        """
        Match Deployment Shape Versions

        Returns the deployment shape versions compatible with the provided
        deployment create request. Use this to discover a validated shape before
        creating a deployment with `deployment_shape` set - shapeless deployments
        (raw accelerator type/count) skip validated-configuration checks and are
        far more likely to fail at creation.

        Args:
          create_deployment_request: The deployment create request to match deployment shape
              versions for. Only `parent`, `deployment.baseModel`, and
              `deployment.enableAddons` are typed (and camelCased on the wire) by this
              hand-written method; other keys pass through verbatim, so send them in
              their wire (camelCase) form if needed.

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
            ("https://api.fireworks.ai" if not self._client._base_url_overridden else "")
            + path_template("/v1/accounts/{account_id}/deploymentShapeVersions:match", account_id=account_id),
            body=await async_maybe_transform(
                {
                    "create_deployment_request": create_deployment_request,
                },
                deployment_shape_version_match_params.DeploymentShapeVersionMatchParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeploymentShapeVersionMatchResponse,
        )

    # NOTE: hand-written convenience method with no OpenAPI counterpart —
    # no generator will ever emit it; see the module top note.
    async def match_for_model(
        self,
        model: str,
        *,
        account_id: str | None = None,
        enable_addons: bool = False,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DeploymentShapeVersionMatchResponse:
        """
        Discover deployment shape versions for a model in one call.

        Pass any model name — a full resource path like
        `accounts/fireworks/models/gemma-4-31b-it` or a LoRA addon like
        `accounts/palo-alto-networks/models/sft-gemma-4-31b-it-clickfix`. The
        server resolves PEFT addons and live-merge models to their base model,
        scopes results to shapes your account can deploy, and requires
        MULTI_LORA-capable shapes when `enable_addons` is true. No client-side
        model lookup is performed.

        The happy path end to end:

        ```python
        match = await async_client.deployment_shape_versions.match_for_model("accounts/fireworks/models/gemma-4-31b-it")
        shape = match.deployment_shape_versions[0].snapshot  # pick a shape
        deployment = await async_client.deployments.create(
            base_model="accounts/fireworks/models/gemma-4-31b-it",
            deployment_shape=shape.name,
        )
        ```

        An empty `deployment_shape_versions` list means no validated shape fits
        the model for your account.

        Args:
          model: The base model the deployment will serve. A full resource path
              such as `accounts/fireworks/models/gemma-4-31b-it` or a LoRA addon
              such as `accounts/palo-alto-networks/models/sft-gemma-4-31b-it-clickfix`.

          enable_addons: If true, LORA addons are enabled for the deployment. Only
              MULTI_LORA-capable shapes will be matched.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if account_id is None:
            account_id = self._client._get_account_id_path_param()
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self.match(
            account_id=account_id,
            create_deployment_request={
                "parent": f"accounts/{account_id}",
                "deployment": {
                    "base_model": model,
                    "enable_addons": enable_addons,
                },
            },
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
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
        self.match = to_raw_response_wrapper(
            deployment_shape_versions.match,
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
        self.match = async_to_raw_response_wrapper(
            deployment_shape_versions.match,
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
        self.match = to_streamed_response_wrapper(
            deployment_shape_versions.match,
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
        self.match = async_to_streamed_response_wrapper(
            deployment_shape_versions.match,
        )
