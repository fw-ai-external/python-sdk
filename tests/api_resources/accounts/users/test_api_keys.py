# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from fireworks_ai import Fireworks, AsyncFireworks
from fireworks_ai._utils import parse_datetime
from fireworks_ai.types.accounts.users import (
    APIKey,
    APIKeyRetrieveAPIKeysResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAPIKeys:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_api_keys(self, client: Fireworks) -> None:
        api_key = client.accounts.users.api_keys.api_keys(
            user_id="user_id",
            account_id="account_id",
            api_key={},
        )
        assert_matches_type(APIKey, api_key, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_api_keys_with_all_params(self, client: Fireworks) -> None:
        api_key = client.accounts.users.api_keys.api_keys(
            user_id="user_id",
            account_id="account_id",
            api_key={
                "display_name": "displayName",
                "expire_time": parse_datetime("2019-12-27T18:11:19.117Z"),
            },
        )
        assert_matches_type(APIKey, api_key, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_api_keys(self, client: Fireworks) -> None:
        response = client.accounts.users.api_keys.with_raw_response.api_keys(
            user_id="user_id",
            account_id="account_id",
            api_key={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        api_key = response.parse()
        assert_matches_type(APIKey, api_key, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_api_keys(self, client: Fireworks) -> None:
        with client.accounts.users.api_keys.with_streaming_response.api_keys(
            user_id="user_id",
            account_id="account_id",
            api_key={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            api_key = response.parse()
            assert_matches_type(APIKey, api_key, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_api_keys(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.users.api_keys.with_raw_response.api_keys(
                user_id="user_id",
                account_id="",
                api_key={},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `user_id` but received ''"):
            client.accounts.users.api_keys.with_raw_response.api_keys(
                user_id="",
                account_id="account_id",
                api_key={},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_api_keys(self, client: Fireworks) -> None:
        api_key = client.accounts.users.api_keys.retrieve_api_keys(
            user_id="user_id",
            account_id="account_id",
        )
        assert_matches_type(APIKeyRetrieveAPIKeysResponse, api_key, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_api_keys_with_all_params(self, client: Fireworks) -> None:
        api_key = client.accounts.users.api_keys.retrieve_api_keys(
            user_id="user_id",
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(APIKeyRetrieveAPIKeysResponse, api_key, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_api_keys(self, client: Fireworks) -> None:
        response = client.accounts.users.api_keys.with_raw_response.retrieve_api_keys(
            user_id="user_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        api_key = response.parse()
        assert_matches_type(APIKeyRetrieveAPIKeysResponse, api_key, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_api_keys(self, client: Fireworks) -> None:
        with client.accounts.users.api_keys.with_streaming_response.retrieve_api_keys(
            user_id="user_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            api_key = response.parse()
            assert_matches_type(APIKeyRetrieveAPIKeysResponse, api_key, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve_api_keys(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.users.api_keys.with_raw_response.retrieve_api_keys(
                user_id="user_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `user_id` but received ''"):
            client.accounts.users.api_keys.with_raw_response.retrieve_api_keys(
                user_id="",
                account_id="account_id",
            )


class TestAsyncAPIKeys:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_api_keys(self, async_client: AsyncFireworks) -> None:
        api_key = await async_client.accounts.users.api_keys.api_keys(
            user_id="user_id",
            account_id="account_id",
            api_key={},
        )
        assert_matches_type(APIKey, api_key, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_api_keys_with_all_params(self, async_client: AsyncFireworks) -> None:
        api_key = await async_client.accounts.users.api_keys.api_keys(
            user_id="user_id",
            account_id="account_id",
            api_key={
                "display_name": "displayName",
                "expire_time": parse_datetime("2019-12-27T18:11:19.117Z"),
            },
        )
        assert_matches_type(APIKey, api_key, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_api_keys(self, async_client: AsyncFireworks) -> None:
        response = await async_client.accounts.users.api_keys.with_raw_response.api_keys(
            user_id="user_id",
            account_id="account_id",
            api_key={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        api_key = await response.parse()
        assert_matches_type(APIKey, api_key, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_api_keys(self, async_client: AsyncFireworks) -> None:
        async with async_client.accounts.users.api_keys.with_streaming_response.api_keys(
            user_id="user_id",
            account_id="account_id",
            api_key={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            api_key = await response.parse()
            assert_matches_type(APIKey, api_key, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_api_keys(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.users.api_keys.with_raw_response.api_keys(
                user_id="user_id",
                account_id="",
                api_key={},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `user_id` but received ''"):
            await async_client.accounts.users.api_keys.with_raw_response.api_keys(
                user_id="",
                account_id="account_id",
                api_key={},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_api_keys(self, async_client: AsyncFireworks) -> None:
        api_key = await async_client.accounts.users.api_keys.retrieve_api_keys(
            user_id="user_id",
            account_id="account_id",
        )
        assert_matches_type(APIKeyRetrieveAPIKeysResponse, api_key, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_api_keys_with_all_params(self, async_client: AsyncFireworks) -> None:
        api_key = await async_client.accounts.users.api_keys.retrieve_api_keys(
            user_id="user_id",
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(APIKeyRetrieveAPIKeysResponse, api_key, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_api_keys(self, async_client: AsyncFireworks) -> None:
        response = await async_client.accounts.users.api_keys.with_raw_response.retrieve_api_keys(
            user_id="user_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        api_key = await response.parse()
        assert_matches_type(APIKeyRetrieveAPIKeysResponse, api_key, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_api_keys(self, async_client: AsyncFireworks) -> None:
        async with async_client.accounts.users.api_keys.with_streaming_response.retrieve_api_keys(
            user_id="user_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            api_key = await response.parse()
            assert_matches_type(APIKeyRetrieveAPIKeysResponse, api_key, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve_api_keys(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.users.api_keys.with_raw_response.retrieve_api_keys(
                user_id="user_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `user_id` but received ''"):
            await async_client.accounts.users.api_keys.with_raw_response.retrieve_api_keys(
                user_id="",
                account_id="account_id",
            )
