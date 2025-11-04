# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
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
    identity_provider_list_params,
    identity_provider_create_params,
    identity_provider_delete_params,
    identity_provider_update_params,
    identity_provider_retrieve_params,
)
from ...types.accounts.gateway_identity_provider import GatewayIdentityProvider
from ...types.accounts.gateway_oidc_config_param import GatewayOidcConfigParam
from ...types.accounts.gateway_saml_config_param import GatewaySAMLConfigParam
from ...types.accounts.identity_provider_list_response import IdentityProviderListResponse

__all__ = ["IdentityProvidersResource", "AsyncIdentityProvidersResource"]


class IdentityProvidersResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> IdentityProvidersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#accessing-raw-response-data-eg-headers
        """
        return IdentityProvidersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> IdentityProvidersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#with_streaming_response
        """
        return IdentityProvidersResourceWithStreamingResponse(self)

    def create(
        self,
        account_id: str,
        *,
        display_name: str | Omit = omit,
        oidc_config: GatewayOidcConfigParam | Omit = omit,
        saml_config: GatewaySAMLConfigParam | Omit = omit,
        tenant_domains: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayIdentityProvider:
        """
        Create Identity Provider

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._post(
            f"/v1/accounts/{account_id}/identityProviders",
            body=maybe_transform(
                {
                    "display_name": display_name,
                    "oidc_config": oidc_config,
                    "saml_config": saml_config,
                    "tenant_domains": tenant_domains,
                },
                identity_provider_create_params.IdentityProviderCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GatewayIdentityProvider,
        )

    def retrieve(
        self,
        identity_provider_id: str,
        *,
        account_id: str,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayIdentityProvider:
        """
        Get Identity Provider

        Args:
          read_mask: The fields to be returned in the response. If empty or "\\**", all fields will be
              returned.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not identity_provider_id:
            raise ValueError(
                f"Expected a non-empty value for `identity_provider_id` but received {identity_provider_id!r}"
            )
        return self._get(
            f"/v1/accounts/{account_id}/identityProviders/{identity_provider_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"read_mask": read_mask}, identity_provider_retrieve_params.IdentityProviderRetrieveParams
                ),
            ),
            cast_to=GatewayIdentityProvider,
        )

    def update(
        self,
        identity_provider_id: str,
        *,
        account_id: str,
        display_name: str | Omit = omit,
        oidc_config: GatewayOidcConfigParam | Omit = omit,
        saml_config: GatewaySAMLConfigParam | Omit = omit,
        tenant_domains: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayIdentityProvider:
        """
        Update Identity Provider

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not identity_provider_id:
            raise ValueError(
                f"Expected a non-empty value for `identity_provider_id` but received {identity_provider_id!r}"
            )
        return self._patch(
            f"/v1/accounts/{account_id}/identityProviders/{identity_provider_id}",
            body=maybe_transform(
                {
                    "display_name": display_name,
                    "oidc_config": oidc_config,
                    "saml_config": saml_config,
                    "tenant_domains": tenant_domains,
                },
                identity_provider_update_params.IdentityProviderUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GatewayIdentityProvider,
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
    ) -> IdentityProviderListResponse:
        """
        List Identity Providers

        Args:
          filter: Filter expression

          order_by: Order by

          page_size: Page size

          page_token: Page token

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
            f"/v1/accounts/{account_id}/identityProviders",
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
                    identity_provider_list_params.IdentityProviderListParams,
                ),
            ),
            cast_to=IdentityProviderListResponse,
        )

    def delete(
        self,
        identity_provider_id: str,
        *,
        account_id: str,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Delete Identity Provider

        Args:
          read_mask: The fields to be returned in the response. If empty or "\\**", all fields will be
              returned.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not identity_provider_id:
            raise ValueError(
                f"Expected a non-empty value for `identity_provider_id` but received {identity_provider_id!r}"
            )
        return self._delete(
            f"/v1/accounts/{account_id}/identityProviders/{identity_provider_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"read_mask": read_mask}, identity_provider_delete_params.IdentityProviderDeleteParams
                ),
            ),
            cast_to=object,
        )


class AsyncIdentityProvidersResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncIdentityProvidersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncIdentityProvidersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncIdentityProvidersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#with_streaming_response
        """
        return AsyncIdentityProvidersResourceWithStreamingResponse(self)

    async def create(
        self,
        account_id: str,
        *,
        display_name: str | Omit = omit,
        oidc_config: GatewayOidcConfigParam | Omit = omit,
        saml_config: GatewaySAMLConfigParam | Omit = omit,
        tenant_domains: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayIdentityProvider:
        """
        Create Identity Provider

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._post(
            f"/v1/accounts/{account_id}/identityProviders",
            body=await async_maybe_transform(
                {
                    "display_name": display_name,
                    "oidc_config": oidc_config,
                    "saml_config": saml_config,
                    "tenant_domains": tenant_domains,
                },
                identity_provider_create_params.IdentityProviderCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GatewayIdentityProvider,
        )

    async def retrieve(
        self,
        identity_provider_id: str,
        *,
        account_id: str,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayIdentityProvider:
        """
        Get Identity Provider

        Args:
          read_mask: The fields to be returned in the response. If empty or "\\**", all fields will be
              returned.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not identity_provider_id:
            raise ValueError(
                f"Expected a non-empty value for `identity_provider_id` but received {identity_provider_id!r}"
            )
        return await self._get(
            f"/v1/accounts/{account_id}/identityProviders/{identity_provider_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"read_mask": read_mask}, identity_provider_retrieve_params.IdentityProviderRetrieveParams
                ),
            ),
            cast_to=GatewayIdentityProvider,
        )

    async def update(
        self,
        identity_provider_id: str,
        *,
        account_id: str,
        display_name: str | Omit = omit,
        oidc_config: GatewayOidcConfigParam | Omit = omit,
        saml_config: GatewaySAMLConfigParam | Omit = omit,
        tenant_domains: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GatewayIdentityProvider:
        """
        Update Identity Provider

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not identity_provider_id:
            raise ValueError(
                f"Expected a non-empty value for `identity_provider_id` but received {identity_provider_id!r}"
            )
        return await self._patch(
            f"/v1/accounts/{account_id}/identityProviders/{identity_provider_id}",
            body=await async_maybe_transform(
                {
                    "display_name": display_name,
                    "oidc_config": oidc_config,
                    "saml_config": saml_config,
                    "tenant_domains": tenant_domains,
                },
                identity_provider_update_params.IdentityProviderUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GatewayIdentityProvider,
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
    ) -> IdentityProviderListResponse:
        """
        List Identity Providers

        Args:
          filter: Filter expression

          order_by: Order by

          page_size: Page size

          page_token: Page token

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
            f"/v1/accounts/{account_id}/identityProviders",
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
                    identity_provider_list_params.IdentityProviderListParams,
                ),
            ),
            cast_to=IdentityProviderListResponse,
        )

    async def delete(
        self,
        identity_provider_id: str,
        *,
        account_id: str,
        read_mask: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Delete Identity Provider

        Args:
          read_mask: The fields to be returned in the response. If empty or "\\**", all fields will be
              returned.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not identity_provider_id:
            raise ValueError(
                f"Expected a non-empty value for `identity_provider_id` but received {identity_provider_id!r}"
            )
        return await self._delete(
            f"/v1/accounts/{account_id}/identityProviders/{identity_provider_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"read_mask": read_mask}, identity_provider_delete_params.IdentityProviderDeleteParams
                ),
            ),
            cast_to=object,
        )


class IdentityProvidersResourceWithRawResponse:
    def __init__(self, identity_providers: IdentityProvidersResource) -> None:
        self._identity_providers = identity_providers

        self.create = to_raw_response_wrapper(
            identity_providers.create,
        )
        self.retrieve = to_raw_response_wrapper(
            identity_providers.retrieve,
        )
        self.update = to_raw_response_wrapper(
            identity_providers.update,
        )
        self.list = to_raw_response_wrapper(
            identity_providers.list,
        )
        self.delete = to_raw_response_wrapper(
            identity_providers.delete,
        )


class AsyncIdentityProvidersResourceWithRawResponse:
    def __init__(self, identity_providers: AsyncIdentityProvidersResource) -> None:
        self._identity_providers = identity_providers

        self.create = async_to_raw_response_wrapper(
            identity_providers.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            identity_providers.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            identity_providers.update,
        )
        self.list = async_to_raw_response_wrapper(
            identity_providers.list,
        )
        self.delete = async_to_raw_response_wrapper(
            identity_providers.delete,
        )


class IdentityProvidersResourceWithStreamingResponse:
    def __init__(self, identity_providers: IdentityProvidersResource) -> None:
        self._identity_providers = identity_providers

        self.create = to_streamed_response_wrapper(
            identity_providers.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            identity_providers.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            identity_providers.update,
        )
        self.list = to_streamed_response_wrapper(
            identity_providers.list,
        )
        self.delete = to_streamed_response_wrapper(
            identity_providers.delete,
        )


class AsyncIdentityProvidersResourceWithStreamingResponse:
    def __init__(self, identity_providers: AsyncIdentityProvidersResource) -> None:
        self._identity_providers = identity_providers

        self.create = async_to_streamed_response_wrapper(
            identity_providers.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            identity_providers.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            identity_providers.update,
        )
        self.list = async_to_streamed_response_wrapper(
            identity_providers.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            identity_providers.delete,
        )
