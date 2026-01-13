# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict

import httpx

from ..types import (
    EvaluatorVersion,
    evaluator_version_get_params,
    evaluator_version_list_params,
    evaluator_version_create_params,
    evaluator_version_validate_upload_params,
    evaluator_version_get_upload_endpoint_params,
    evaluator_version_get_build_log_endpoint_params,
    evaluator_version_get_source_code_endpoint_params,
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
from ..pagination import SyncCursorEvaluatorVersions, AsyncCursorEvaluatorVersions
from .._base_client import AsyncPaginator, make_request_options
from ..types.evaluator_version import EvaluatorVersion
from ..types.evaluator_version_param import EvaluatorVersionParam
from ..types.get_build_log_endpoint_response import GetBuildLogEndpointResponse
from ..types.get_source_code_endpoint_response import GetSourceCodeEndpointResponse
from ..types.evaluator_version_get_upload_endpoint_response import EvaluatorVersionGetUploadEndpointResponse

__all__ = ["EvaluatorVersionsResource", "AsyncEvaluatorVersionsResource"]


class EvaluatorVersionsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> EvaluatorVersionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#accessing-raw-response-data-eg-headers
        """
        return EvaluatorVersionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> EvaluatorVersionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#with_streaming_response
        """
        return EvaluatorVersionsResourceWithStreamingResponse(self)

    def create(
        self,
        evaluator_id: str,
        *,
        account_id: str | None = None,
        evaluator_version: EvaluatorVersionParam,
        evaluator_version_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EvaluatorVersion:
        """Creates a new version for an existing evaluator.

        This is the first step in the
        version upload workflow:

        1. **Create version** (this endpoint) - Creates the version resource in BUILDING
           state
        2. **Get upload endpoint** - Call
           [GetEvaluatorVersionUploadEndpoint](/api-reference/get-evaluator-version-upload-endpoint)
           with the version name from step 1 to get signed upload URLs
        3. **Upload source code** - PUT your `.tar.gz` archive to the signed URL
        4. **Validate upload** - Call
           [ValidateEvaluatorVersionUpload](/api-reference/validate-evaluator-version-upload)
           to trigger the build
        5. **Monitor progress** - Poll
           [GetEvaluatorVersion](/api-reference/get-evaluator-version) until state is
           ACTIVE or BUILD_FAILED

        The response includes the full version resource name with the generated or
        provided version_id, which you'll use for subsequent API calls.

        If `auto_promote` is true (default) in step 4, the version automatically becomes
        the evaluator's current version upon successful build.

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
            f"/v1/accounts/{account_id}/evaluators/{evaluator_id}/versions"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/evaluators/{evaluator_id}/versions",
            body=maybe_transform(
                {
                    "evaluator_version": evaluator_version,
                    "evaluator_version_id": evaluator_version_id,
                },
                evaluator_version_create_params.EvaluatorVersionCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EvaluatorVersion,
        )

    def list(
        self,
        evaluator_id: str,
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
    ) -> SyncCursorEvaluatorVersions[EvaluatorVersion]:
        """
        Lists all versions for an evaluator, ordered by creation time (newest first).

        Args:
          order_by: Default order should be reverse chronological (newest first) per AIP-162.

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
        return self._get_api_list(
            f"/v1/accounts/{account_id}/evaluators/{evaluator_id}/versions"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/evaluators/{evaluator_id}/versions",
            page=SyncCursorEvaluatorVersions[EvaluatorVersion],
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
                    evaluator_version_list_params.EvaluatorVersionListParams,
                ),
            ),
            model=EvaluatorVersion,
        )

    def delete(
        self,
        version_id: str,
        *,
        account_id: str | None = None,
        evaluator_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """Permanently deletes an evaluator version.

        Cannot delete the current version of
        an evaluator - use UpdateEvaluator with `current_version_id` to switch to a
        different version first.

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
        if not version_id:
            raise ValueError(f"Expected a non-empty value for `version_id` but received {version_id!r}")
        return self._delete(
            f"/v1/accounts/{account_id}/evaluators/{evaluator_id}/versions/{version_id}"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/evaluators/{evaluator_id}/versions/{version_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def get(
        self,
        version_id: str,
        *,
        account_id: str | None = None,
        evaluator_id: str,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EvaluatorVersion:
        """Retrieves a specific evaluator version.

        Use this to monitor build progress after
        calling ValidateEvaluatorVersionUpload.

        Special version ID "latest" returns the most recently created version.

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
        if not version_id:
            raise ValueError(f"Expected a non-empty value for `version_id` but received {version_id!r}")
        return self._get(
            f"/v1/accounts/{account_id}/evaluators/{evaluator_id}/versions/{version_id}"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/evaluators/{evaluator_id}/versions/{version_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"read_mask": read_mask}, evaluator_version_get_params.EvaluatorVersionGetParams),
            ),
            cast_to=EvaluatorVersion,
        )

    def get_build_log_endpoint(
        self,
        version_id: str,
        *,
        account_id: str | None = None,
        evaluator_id: str,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GetBuildLogEndpointResponse:
        """
        Returns a signed URL for downloading the build log of a specific evaluator
        version. Useful for debugging BUILD_FAILED state or reviewing the build process.

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
        if not version_id:
            raise ValueError(f"Expected a non-empty value for `version_id` but received {version_id!r}")
        return self._get(
            f"/v1/accounts/{account_id}/evaluators/{evaluator_id}/versions/{version_id}:getBuildLogSignedUrl"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/evaluators/{evaluator_id}/versions/{version_id}:getBuildLogSignedUrl",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"read_mask": read_mask},
                    evaluator_version_get_build_log_endpoint_params.EvaluatorVersionGetBuildLogEndpointParams,
                ),
            ),
            cast_to=GetBuildLogEndpointResponse,
        )

    def get_source_code_endpoint(
        self,
        version_id: str,
        *,
        account_id: str | None = None,
        evaluator_id: str,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GetSourceCodeEndpointResponse:
        """
        Returns signed URLs for downloading the source code files of a specific
        evaluator version. Useful for reviewing or auditing the code that was uploaded
        for a version.

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
        if not version_id:
            raise ValueError(f"Expected a non-empty value for `version_id` but received {version_id!r}")
        return self._get(
            f"/v1/accounts/{account_id}/evaluators/{evaluator_id}/versions/{version_id}:getSourceCodeSignedUrl"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/evaluators/{evaluator_id}/versions/{version_id}:getSourceCodeSignedUrl",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"read_mask": read_mask},
                    evaluator_version_get_source_code_endpoint_params.EvaluatorVersionGetSourceCodeEndpointParams,
                ),
            ),
            cast_to=GetSourceCodeEndpointResponse,
        )

    def get_upload_endpoint(
        self,
        version_id: str,
        *,
        account_id: str | None = None,
        evaluator_id: str,
        filename_to_size: Dict[str, str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EvaluatorVersionGetUploadEndpointResponse:
        """
        Returns signed URLs for uploading source code for a specific version (**step 2**
        in the [CreateEvaluatorVersion](/api-reference/create-evaluator-version)
        workflow).

        The version must be in BUILDING state (immediately after creation). After
        receiving the signed URL, upload your `.tar.gz` archive using HTTP `PUT` with
        `Content-Type: application/octet-stream` header.

        Args:
          filename_to_size: Map of filename to file size for generating upload signed URLs. Typically
              contains a single entry like {"evaluator.tar.gz": 12345}.

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
        if not version_id:
            raise ValueError(f"Expected a non-empty value for `version_id` but received {version_id!r}")
        return self._post(
            f"/v1/accounts/{account_id}/evaluators/{evaluator_id}/versions/{version_id}:getUploadEndpoint"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/evaluators/{evaluator_id}/versions/{version_id}:getUploadEndpoint",
            body=maybe_transform(
                {"filename_to_size": filename_to_size},
                evaluator_version_get_upload_endpoint_params.EvaluatorVersionGetUploadEndpointParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EvaluatorVersionGetUploadEndpointResponse,
        )

    def validate_upload(
        self,
        version_id: str,
        *,
        account_id: str | None = None,
        evaluator_id: str,
        auto_promote: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Triggers server-side validation and build of the uploaded source code for a
        specific version (**step 4** in the
        [CreateEvaluatorVersion](/api-reference/create-evaluator-version) workflow).

        The version must be in BUILDING state with source code already uploaded. This
        kicks off an async build workflow - poll
        [GetEvaluatorVersion](/api-reference/get-evaluator-version) to monitor progress.

        Set `auto_promote: true` (default) to automatically set this version as current
        upon successful build, or `false` to manually promote later via
        [UpdateEvaluator](/api-reference/update-evaluator) with `current_version_id`.

        Args:
          auto_promote: If true (default), this version will automatically be set as the evaluator's
              current_version_id upon successful build. Set to false if you want to manually
              promote the version later using UpdateEvaluator with current_version_id.

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
        if not version_id:
            raise ValueError(f"Expected a non-empty value for `version_id` but received {version_id!r}")
        return self._post(
            f"/v1/accounts/{account_id}/evaluators/{evaluator_id}/versions/{version_id}:validateUpload"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/evaluators/{evaluator_id}/versions/{version_id}:validateUpload",
            body=maybe_transform(
                {"auto_promote": auto_promote},
                evaluator_version_validate_upload_params.EvaluatorVersionValidateUploadParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncEvaluatorVersionsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncEvaluatorVersionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncEvaluatorVersionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncEvaluatorVersionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#with_streaming_response
        """
        return AsyncEvaluatorVersionsResourceWithStreamingResponse(self)

    async def create(
        self,
        evaluator_id: str,
        *,
        account_id: str | None = None,
        evaluator_version: EvaluatorVersionParam,
        evaluator_version_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EvaluatorVersion:
        """Creates a new version for an existing evaluator.

        This is the first step in the
        version upload workflow:

        1. **Create version** (this endpoint) - Creates the version resource in BUILDING
           state
        2. **Get upload endpoint** - Call
           [GetEvaluatorVersionUploadEndpoint](/api-reference/get-evaluator-version-upload-endpoint)
           with the version name from step 1 to get signed upload URLs
        3. **Upload source code** - PUT your `.tar.gz` archive to the signed URL
        4. **Validate upload** - Call
           [ValidateEvaluatorVersionUpload](/api-reference/validate-evaluator-version-upload)
           to trigger the build
        5. **Monitor progress** - Poll
           [GetEvaluatorVersion](/api-reference/get-evaluator-version) until state is
           ACTIVE or BUILD_FAILED

        The response includes the full version resource name with the generated or
        provided version_id, which you'll use for subsequent API calls.

        If `auto_promote` is true (default) in step 4, the version automatically becomes
        the evaluator's current version upon successful build.

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
            f"/v1/accounts/{account_id}/evaluators/{evaluator_id}/versions"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/evaluators/{evaluator_id}/versions",
            body=await async_maybe_transform(
                {
                    "evaluator_version": evaluator_version,
                    "evaluator_version_id": evaluator_version_id,
                },
                evaluator_version_create_params.EvaluatorVersionCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EvaluatorVersion,
        )

    def list(
        self,
        evaluator_id: str,
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
    ) -> AsyncPaginator[EvaluatorVersion, AsyncCursorEvaluatorVersions[EvaluatorVersion]]:
        """
        Lists all versions for an evaluator, ordered by creation time (newest first).

        Args:
          order_by: Default order should be reverse chronological (newest first) per AIP-162.

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
        return self._get_api_list(
            f"/v1/accounts/{account_id}/evaluators/{evaluator_id}/versions"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/evaluators/{evaluator_id}/versions",
            page=AsyncCursorEvaluatorVersions[EvaluatorVersion],
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
                    evaluator_version_list_params.EvaluatorVersionListParams,
                ),
            ),
            model=EvaluatorVersion,
        )

    async def delete(
        self,
        version_id: str,
        *,
        account_id: str | None = None,
        evaluator_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """Permanently deletes an evaluator version.

        Cannot delete the current version of
        an evaluator - use UpdateEvaluator with `current_version_id` to switch to a
        different version first.

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
        if not version_id:
            raise ValueError(f"Expected a non-empty value for `version_id` but received {version_id!r}")
        return await self._delete(
            f"/v1/accounts/{account_id}/evaluators/{evaluator_id}/versions/{version_id}"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/evaluators/{evaluator_id}/versions/{version_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def get(
        self,
        version_id: str,
        *,
        account_id: str | None = None,
        evaluator_id: str,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EvaluatorVersion:
        """Retrieves a specific evaluator version.

        Use this to monitor build progress after
        calling ValidateEvaluatorVersionUpload.

        Special version ID "latest" returns the most recently created version.

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
        if not version_id:
            raise ValueError(f"Expected a non-empty value for `version_id` but received {version_id!r}")
        return await self._get(
            f"/v1/accounts/{account_id}/evaluators/{evaluator_id}/versions/{version_id}"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/evaluators/{evaluator_id}/versions/{version_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"read_mask": read_mask}, evaluator_version_get_params.EvaluatorVersionGetParams
                ),
            ),
            cast_to=EvaluatorVersion,
        )

    async def get_build_log_endpoint(
        self,
        version_id: str,
        *,
        account_id: str | None = None,
        evaluator_id: str,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GetBuildLogEndpointResponse:
        """
        Returns a signed URL for downloading the build log of a specific evaluator
        version. Useful for debugging BUILD_FAILED state or reviewing the build process.

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
        if not version_id:
            raise ValueError(f"Expected a non-empty value for `version_id` but received {version_id!r}")
        return await self._get(
            f"/v1/accounts/{account_id}/evaluators/{evaluator_id}/versions/{version_id}:getBuildLogSignedUrl"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/evaluators/{evaluator_id}/versions/{version_id}:getBuildLogSignedUrl",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"read_mask": read_mask},
                    evaluator_version_get_build_log_endpoint_params.EvaluatorVersionGetBuildLogEndpointParams,
                ),
            ),
            cast_to=GetBuildLogEndpointResponse,
        )

    async def get_source_code_endpoint(
        self,
        version_id: str,
        *,
        account_id: str | None = None,
        evaluator_id: str,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GetSourceCodeEndpointResponse:
        """
        Returns signed URLs for downloading the source code files of a specific
        evaluator version. Useful for reviewing or auditing the code that was uploaded
        for a version.

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
        if not version_id:
            raise ValueError(f"Expected a non-empty value for `version_id` but received {version_id!r}")
        return await self._get(
            f"/v1/accounts/{account_id}/evaluators/{evaluator_id}/versions/{version_id}:getSourceCodeSignedUrl"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/evaluators/{evaluator_id}/versions/{version_id}:getSourceCodeSignedUrl",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"read_mask": read_mask},
                    evaluator_version_get_source_code_endpoint_params.EvaluatorVersionGetSourceCodeEndpointParams,
                ),
            ),
            cast_to=GetSourceCodeEndpointResponse,
        )

    async def get_upload_endpoint(
        self,
        version_id: str,
        *,
        account_id: str | None = None,
        evaluator_id: str,
        filename_to_size: Dict[str, str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EvaluatorVersionGetUploadEndpointResponse:
        """
        Returns signed URLs for uploading source code for a specific version (**step 2**
        in the [CreateEvaluatorVersion](/api-reference/create-evaluator-version)
        workflow).

        The version must be in BUILDING state (immediately after creation). After
        receiving the signed URL, upload your `.tar.gz` archive using HTTP `PUT` with
        `Content-Type: application/octet-stream` header.

        Args:
          filename_to_size: Map of filename to file size for generating upload signed URLs. Typically
              contains a single entry like {"evaluator.tar.gz": 12345}.

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
        if not version_id:
            raise ValueError(f"Expected a non-empty value for `version_id` but received {version_id!r}")
        return await self._post(
            f"/v1/accounts/{account_id}/evaluators/{evaluator_id}/versions/{version_id}:getUploadEndpoint"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/evaluators/{evaluator_id}/versions/{version_id}:getUploadEndpoint",
            body=await async_maybe_transform(
                {"filename_to_size": filename_to_size},
                evaluator_version_get_upload_endpoint_params.EvaluatorVersionGetUploadEndpointParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EvaluatorVersionGetUploadEndpointResponse,
        )

    async def validate_upload(
        self,
        version_id: str,
        *,
        account_id: str | None = None,
        evaluator_id: str,
        auto_promote: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Triggers server-side validation and build of the uploaded source code for a
        specific version (**step 4** in the
        [CreateEvaluatorVersion](/api-reference/create-evaluator-version) workflow).

        The version must be in BUILDING state with source code already uploaded. This
        kicks off an async build workflow - poll
        [GetEvaluatorVersion](/api-reference/get-evaluator-version) to monitor progress.

        Set `auto_promote: true` (default) to automatically set this version as current
        upon successful build, or `false` to manually promote later via
        [UpdateEvaluator](/api-reference/update-evaluator) with `current_version_id`.

        Args:
          auto_promote: If true (default), this version will automatically be set as the evaluator's
              current_version_id upon successful build. Set to false if you want to manually
              promote the version later using UpdateEvaluator with current_version_id.

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
        if not version_id:
            raise ValueError(f"Expected a non-empty value for `version_id` but received {version_id!r}")
        return await self._post(
            f"/v1/accounts/{account_id}/evaluators/{evaluator_id}/versions/{version_id}:validateUpload"
            if self._client._base_url_overridden
            else f"https://api.fireworks.ai/v1/accounts/{account_id}/evaluators/{evaluator_id}/versions/{version_id}:validateUpload",
            body=await async_maybe_transform(
                {"auto_promote": auto_promote},
                evaluator_version_validate_upload_params.EvaluatorVersionValidateUploadParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class EvaluatorVersionsResourceWithRawResponse:
    def __init__(self, evaluator_versions: EvaluatorVersionsResource) -> None:
        self._evaluator_versions = evaluator_versions

        self.create = to_raw_response_wrapper(
            evaluator_versions.create,
        )
        self.list = to_raw_response_wrapper(
            evaluator_versions.list,
        )
        self.delete = to_raw_response_wrapper(
            evaluator_versions.delete,
        )
        self.get = to_raw_response_wrapper(
            evaluator_versions.get,
        )
        self.get_build_log_endpoint = to_raw_response_wrapper(
            evaluator_versions.get_build_log_endpoint,
        )
        self.get_source_code_endpoint = to_raw_response_wrapper(
            evaluator_versions.get_source_code_endpoint,
        )
        self.get_upload_endpoint = to_raw_response_wrapper(
            evaluator_versions.get_upload_endpoint,
        )
        self.validate_upload = to_raw_response_wrapper(
            evaluator_versions.validate_upload,
        )


class AsyncEvaluatorVersionsResourceWithRawResponse:
    def __init__(self, evaluator_versions: AsyncEvaluatorVersionsResource) -> None:
        self._evaluator_versions = evaluator_versions

        self.create = async_to_raw_response_wrapper(
            evaluator_versions.create,
        )
        self.list = async_to_raw_response_wrapper(
            evaluator_versions.list,
        )
        self.delete = async_to_raw_response_wrapper(
            evaluator_versions.delete,
        )
        self.get = async_to_raw_response_wrapper(
            evaluator_versions.get,
        )
        self.get_build_log_endpoint = async_to_raw_response_wrapper(
            evaluator_versions.get_build_log_endpoint,
        )
        self.get_source_code_endpoint = async_to_raw_response_wrapper(
            evaluator_versions.get_source_code_endpoint,
        )
        self.get_upload_endpoint = async_to_raw_response_wrapper(
            evaluator_versions.get_upload_endpoint,
        )
        self.validate_upload = async_to_raw_response_wrapper(
            evaluator_versions.validate_upload,
        )


class EvaluatorVersionsResourceWithStreamingResponse:
    def __init__(self, evaluator_versions: EvaluatorVersionsResource) -> None:
        self._evaluator_versions = evaluator_versions

        self.create = to_streamed_response_wrapper(
            evaluator_versions.create,
        )
        self.list = to_streamed_response_wrapper(
            evaluator_versions.list,
        )
        self.delete = to_streamed_response_wrapper(
            evaluator_versions.delete,
        )
        self.get = to_streamed_response_wrapper(
            evaluator_versions.get,
        )
        self.get_build_log_endpoint = to_streamed_response_wrapper(
            evaluator_versions.get_build_log_endpoint,
        )
        self.get_source_code_endpoint = to_streamed_response_wrapper(
            evaluator_versions.get_source_code_endpoint,
        )
        self.get_upload_endpoint = to_streamed_response_wrapper(
            evaluator_versions.get_upload_endpoint,
        )
        self.validate_upload = to_streamed_response_wrapper(
            evaluator_versions.validate_upload,
        )


class AsyncEvaluatorVersionsResourceWithStreamingResponse:
    def __init__(self, evaluator_versions: AsyncEvaluatorVersionsResource) -> None:
        self._evaluator_versions = evaluator_versions

        self.create = async_to_streamed_response_wrapper(
            evaluator_versions.create,
        )
        self.list = async_to_streamed_response_wrapper(
            evaluator_versions.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            evaluator_versions.delete,
        )
        self.get = async_to_streamed_response_wrapper(
            evaluator_versions.get,
        )
        self.get_build_log_endpoint = async_to_streamed_response_wrapper(
            evaluator_versions.get_build_log_endpoint,
        )
        self.get_source_code_endpoint = async_to_streamed_response_wrapper(
            evaluator_versions.get_source_code_endpoint,
        )
        self.get_upload_endpoint = async_to_streamed_response_wrapper(
            evaluator_versions.get_upload_endpoint,
        )
        self.validate_upload = async_to_streamed_response_wrapper(
            evaluator_versions.validate_upload,
        )
