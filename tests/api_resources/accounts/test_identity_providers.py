# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from fireworks_ai import FireworksAI, AsyncFireworksAI
from fireworks_ai.types.accounts import (
    GatewayIdentityProvider,
    IdentityProviderListResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestIdentityProviders:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: FireworksAI) -> None:
        identity_provider = client.accounts.identity_providers.create(
            account_id="account_id",
        )
        assert_matches_type(GatewayIdentityProvider, identity_provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: FireworksAI) -> None:
        identity_provider = client.accounts.identity_providers.create(
            account_id="account_id",
            display_name="displayName",
            oidc_config={
                "client_id": "clientId",
                "client_secret": "clientSecret",
                "issuer_url": "issuerUrl",
            },
            saml_config={"metadata_url": "metadataUrl"},
            tenant_domains=["string"],
        )
        assert_matches_type(GatewayIdentityProvider, identity_provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: FireworksAI) -> None:
        response = client.accounts.identity_providers.with_raw_response.create(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        identity_provider = response.parse()
        assert_matches_type(GatewayIdentityProvider, identity_provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: FireworksAI) -> None:
        with client.accounts.identity_providers.with_streaming_response.create(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            identity_provider = response.parse()
            assert_matches_type(GatewayIdentityProvider, identity_provider, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.identity_providers.with_raw_response.create(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: FireworksAI) -> None:
        identity_provider = client.accounts.identity_providers.retrieve(
            identity_provider_id="identity_provider_id",
            account_id="account_id",
        )
        assert_matches_type(GatewayIdentityProvider, identity_provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: FireworksAI) -> None:
        identity_provider = client.accounts.identity_providers.retrieve(
            identity_provider_id="identity_provider_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(GatewayIdentityProvider, identity_provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: FireworksAI) -> None:
        response = client.accounts.identity_providers.with_raw_response.retrieve(
            identity_provider_id="identity_provider_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        identity_provider = response.parse()
        assert_matches_type(GatewayIdentityProvider, identity_provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: FireworksAI) -> None:
        with client.accounts.identity_providers.with_streaming_response.retrieve(
            identity_provider_id="identity_provider_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            identity_provider = response.parse()
            assert_matches_type(GatewayIdentityProvider, identity_provider, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.identity_providers.with_raw_response.retrieve(
                identity_provider_id="identity_provider_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `identity_provider_id` but received ''"):
            client.accounts.identity_providers.with_raw_response.retrieve(
                identity_provider_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: FireworksAI) -> None:
        identity_provider = client.accounts.identity_providers.update(
            identity_provider_id="identity_provider_id",
            account_id="account_id",
        )
        assert_matches_type(GatewayIdentityProvider, identity_provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: FireworksAI) -> None:
        identity_provider = client.accounts.identity_providers.update(
            identity_provider_id="identity_provider_id",
            account_id="account_id",
            display_name="displayName",
            oidc_config={
                "client_id": "clientId",
                "client_secret": "clientSecret",
                "issuer_url": "issuerUrl",
            },
            saml_config={"metadata_url": "metadataUrl"},
            tenant_domains=["string"],
        )
        assert_matches_type(GatewayIdentityProvider, identity_provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: FireworksAI) -> None:
        response = client.accounts.identity_providers.with_raw_response.update(
            identity_provider_id="identity_provider_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        identity_provider = response.parse()
        assert_matches_type(GatewayIdentityProvider, identity_provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: FireworksAI) -> None:
        with client.accounts.identity_providers.with_streaming_response.update(
            identity_provider_id="identity_provider_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            identity_provider = response.parse()
            assert_matches_type(GatewayIdentityProvider, identity_provider, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.identity_providers.with_raw_response.update(
                identity_provider_id="identity_provider_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `identity_provider_id` but received ''"):
            client.accounts.identity_providers.with_raw_response.update(
                identity_provider_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: FireworksAI) -> None:
        identity_provider = client.accounts.identity_providers.list(
            account_id="account_id",
        )
        assert_matches_type(IdentityProviderListResponse, identity_provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: FireworksAI) -> None:
        identity_provider = client.accounts.identity_providers.list(
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(IdentityProviderListResponse, identity_provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: FireworksAI) -> None:
        response = client.accounts.identity_providers.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        identity_provider = response.parse()
        assert_matches_type(IdentityProviderListResponse, identity_provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: FireworksAI) -> None:
        with client.accounts.identity_providers.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            identity_provider = response.parse()
            assert_matches_type(IdentityProviderListResponse, identity_provider, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.identity_providers.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: FireworksAI) -> None:
        identity_provider = client.accounts.identity_providers.delete(
            identity_provider_id="identity_provider_id",
            account_id="account_id",
        )
        assert_matches_type(object, identity_provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_with_all_params(self, client: FireworksAI) -> None:
        identity_provider = client.accounts.identity_providers.delete(
            identity_provider_id="identity_provider_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(object, identity_provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: FireworksAI) -> None:
        response = client.accounts.identity_providers.with_raw_response.delete(
            identity_provider_id="identity_provider_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        identity_provider = response.parse()
        assert_matches_type(object, identity_provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: FireworksAI) -> None:
        with client.accounts.identity_providers.with_streaming_response.delete(
            identity_provider_id="identity_provider_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            identity_provider = response.parse()
            assert_matches_type(object, identity_provider, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.identity_providers.with_raw_response.delete(
                identity_provider_id="identity_provider_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `identity_provider_id` but received ''"):
            client.accounts.identity_providers.with_raw_response.delete(
                identity_provider_id="",
                account_id="account_id",
            )


class TestAsyncIdentityProviders:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncFireworksAI) -> None:
        identity_provider = await async_client.accounts.identity_providers.create(
            account_id="account_id",
        )
        assert_matches_type(GatewayIdentityProvider, identity_provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncFireworksAI) -> None:
        identity_provider = await async_client.accounts.identity_providers.create(
            account_id="account_id",
            display_name="displayName",
            oidc_config={
                "client_id": "clientId",
                "client_secret": "clientSecret",
                "issuer_url": "issuerUrl",
            },
            saml_config={"metadata_url": "metadataUrl"},
            tenant_domains=["string"],
        )
        assert_matches_type(GatewayIdentityProvider, identity_provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.identity_providers.with_raw_response.create(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        identity_provider = await response.parse()
        assert_matches_type(GatewayIdentityProvider, identity_provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.identity_providers.with_streaming_response.create(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            identity_provider = await response.parse()
            assert_matches_type(GatewayIdentityProvider, identity_provider, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.identity_providers.with_raw_response.create(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncFireworksAI) -> None:
        identity_provider = await async_client.accounts.identity_providers.retrieve(
            identity_provider_id="identity_provider_id",
            account_id="account_id",
        )
        assert_matches_type(GatewayIdentityProvider, identity_provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncFireworksAI) -> None:
        identity_provider = await async_client.accounts.identity_providers.retrieve(
            identity_provider_id="identity_provider_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(GatewayIdentityProvider, identity_provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.identity_providers.with_raw_response.retrieve(
            identity_provider_id="identity_provider_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        identity_provider = await response.parse()
        assert_matches_type(GatewayIdentityProvider, identity_provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.identity_providers.with_streaming_response.retrieve(
            identity_provider_id="identity_provider_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            identity_provider = await response.parse()
            assert_matches_type(GatewayIdentityProvider, identity_provider, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.identity_providers.with_raw_response.retrieve(
                identity_provider_id="identity_provider_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `identity_provider_id` but received ''"):
            await async_client.accounts.identity_providers.with_raw_response.retrieve(
                identity_provider_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncFireworksAI) -> None:
        identity_provider = await async_client.accounts.identity_providers.update(
            identity_provider_id="identity_provider_id",
            account_id="account_id",
        )
        assert_matches_type(GatewayIdentityProvider, identity_provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncFireworksAI) -> None:
        identity_provider = await async_client.accounts.identity_providers.update(
            identity_provider_id="identity_provider_id",
            account_id="account_id",
            display_name="displayName",
            oidc_config={
                "client_id": "clientId",
                "client_secret": "clientSecret",
                "issuer_url": "issuerUrl",
            },
            saml_config={"metadata_url": "metadataUrl"},
            tenant_domains=["string"],
        )
        assert_matches_type(GatewayIdentityProvider, identity_provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.identity_providers.with_raw_response.update(
            identity_provider_id="identity_provider_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        identity_provider = await response.parse()
        assert_matches_type(GatewayIdentityProvider, identity_provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.identity_providers.with_streaming_response.update(
            identity_provider_id="identity_provider_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            identity_provider = await response.parse()
            assert_matches_type(GatewayIdentityProvider, identity_provider, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.identity_providers.with_raw_response.update(
                identity_provider_id="identity_provider_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `identity_provider_id` but received ''"):
            await async_client.accounts.identity_providers.with_raw_response.update(
                identity_provider_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncFireworksAI) -> None:
        identity_provider = await async_client.accounts.identity_providers.list(
            account_id="account_id",
        )
        assert_matches_type(IdentityProviderListResponse, identity_provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncFireworksAI) -> None:
        identity_provider = await async_client.accounts.identity_providers.list(
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(IdentityProviderListResponse, identity_provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.identity_providers.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        identity_provider = await response.parse()
        assert_matches_type(IdentityProviderListResponse, identity_provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.identity_providers.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            identity_provider = await response.parse()
            assert_matches_type(IdentityProviderListResponse, identity_provider, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.identity_providers.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncFireworksAI) -> None:
        identity_provider = await async_client.accounts.identity_providers.delete(
            identity_provider_id="identity_provider_id",
            account_id="account_id",
        )
        assert_matches_type(object, identity_provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_with_all_params(self, async_client: AsyncFireworksAI) -> None:
        identity_provider = await async_client.accounts.identity_providers.delete(
            identity_provider_id="identity_provider_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(object, identity_provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.identity_providers.with_raw_response.delete(
            identity_provider_id="identity_provider_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        identity_provider = await response.parse()
        assert_matches_type(object, identity_provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.identity_providers.with_streaming_response.delete(
            identity_provider_id="identity_provider_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            identity_provider = await response.parse()
            assert_matches_type(object, identity_provider, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.identity_providers.with_raw_response.delete(
                identity_provider_id="identity_provider_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `identity_provider_id` but received ''"):
            await async_client.accounts.identity_providers.with_raw_response.delete(
                identity_provider_id="",
                account_id="account_id",
            )
