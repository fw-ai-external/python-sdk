# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from fireworks import Fireworks, AsyncFireworks
from tests.utils import assert_matches_type
from fireworks.types import (
    Secret,
    SecretListResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSecrets:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Fireworks) -> None:
        secret = client.secrets.create(
            account_id="account_id",
            key_name="keyName",
            name="name",
        )
        assert_matches_type(Secret, secret, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Fireworks) -> None:
        secret = client.secrets.create(
            account_id="account_id",
            key_name="keyName",
            name="name",
            value="value",
        )
        assert_matches_type(Secret, secret, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Fireworks) -> None:
        response = client.secrets.with_raw_response.create(
            account_id="account_id",
            key_name="keyName",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        secret = response.parse()
        assert_matches_type(Secret, secret, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Fireworks) -> None:
        with client.secrets.with_streaming_response.create(
            account_id="account_id",
            key_name="keyName",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            secret = response.parse()
            assert_matches_type(Secret, secret, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.secrets.with_raw_response.create(
                account_id="",
                key_name="keyName",
                name="name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: Fireworks) -> None:
        secret = client.secrets.update(
            secret_id="secret_id",
            account_id="account_id",
            key_name="keyName",
        )
        assert_matches_type(Secret, secret, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: Fireworks) -> None:
        secret = client.secrets.update(
            secret_id="secret_id",
            account_id="account_id",
            key_name="keyName",
            value="value",
        )
        assert_matches_type(Secret, secret, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: Fireworks) -> None:
        response = client.secrets.with_raw_response.update(
            secret_id="secret_id",
            account_id="account_id",
            key_name="keyName",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        secret = response.parse()
        assert_matches_type(Secret, secret, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: Fireworks) -> None:
        with client.secrets.with_streaming_response.update(
            secret_id="secret_id",
            account_id="account_id",
            key_name="keyName",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            secret = response.parse()
            assert_matches_type(Secret, secret, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.secrets.with_raw_response.update(
                secret_id="secret_id",
                account_id="",
                key_name="keyName",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `secret_id` but received ''"):
            client.secrets.with_raw_response.update(
                secret_id="",
                account_id="account_id",
                key_name="keyName",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Fireworks) -> None:
        secret = client.secrets.list(
            account_id="account_id",
        )
        assert_matches_type(SecretListResponse, secret, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: Fireworks) -> None:
        secret = client.secrets.list(
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(SecretListResponse, secret, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Fireworks) -> None:
        response = client.secrets.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        secret = response.parse()
        assert_matches_type(SecretListResponse, secret, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Fireworks) -> None:
        with client.secrets.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            secret = response.parse()
            assert_matches_type(SecretListResponse, secret, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.secrets.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: Fireworks) -> None:
        secret = client.secrets.delete(
            secret_id="secret_id",
            account_id="account_id",
        )
        assert_matches_type(object, secret, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: Fireworks) -> None:
        response = client.secrets.with_raw_response.delete(
            secret_id="secret_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        secret = response.parse()
        assert_matches_type(object, secret, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: Fireworks) -> None:
        with client.secrets.with_streaming_response.delete(
            secret_id="secret_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            secret = response.parse()
            assert_matches_type(object, secret, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.secrets.with_raw_response.delete(
                secret_id="secret_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `secret_id` but received ''"):
            client.secrets.with_raw_response.delete(
                secret_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get(self, client: Fireworks) -> None:
        secret = client.secrets.get(
            secret_id="secret_id",
            account_id="account_id",
        )
        assert_matches_type(Secret, secret, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_with_all_params(self, client: Fireworks) -> None:
        secret = client.secrets.get(
            secret_id="secret_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(Secret, secret, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get(self, client: Fireworks) -> None:
        response = client.secrets.with_raw_response.get(
            secret_id="secret_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        secret = response.parse()
        assert_matches_type(Secret, secret, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get(self, client: Fireworks) -> None:
        with client.secrets.with_streaming_response.get(
            secret_id="secret_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            secret = response.parse()
            assert_matches_type(Secret, secret, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.secrets.with_raw_response.get(
                secret_id="secret_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `secret_id` but received ''"):
            client.secrets.with_raw_response.get(
                secret_id="",
                account_id="account_id",
            )


class TestAsyncSecrets:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncFireworks) -> None:
        secret = await async_client.secrets.create(
            account_id="account_id",
            key_name="keyName",
            name="name",
        )
        assert_matches_type(Secret, secret, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncFireworks) -> None:
        secret = await async_client.secrets.create(
            account_id="account_id",
            key_name="keyName",
            name="name",
            value="value",
        )
        assert_matches_type(Secret, secret, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncFireworks) -> None:
        response = await async_client.secrets.with_raw_response.create(
            account_id="account_id",
            key_name="keyName",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        secret = await response.parse()
        assert_matches_type(Secret, secret, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncFireworks) -> None:
        async with async_client.secrets.with_streaming_response.create(
            account_id="account_id",
            key_name="keyName",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            secret = await response.parse()
            assert_matches_type(Secret, secret, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.secrets.with_raw_response.create(
                account_id="",
                key_name="keyName",
                name="name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncFireworks) -> None:
        secret = await async_client.secrets.update(
            secret_id="secret_id",
            account_id="account_id",
            key_name="keyName",
        )
        assert_matches_type(Secret, secret, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncFireworks) -> None:
        secret = await async_client.secrets.update(
            secret_id="secret_id",
            account_id="account_id",
            key_name="keyName",
            value="value",
        )
        assert_matches_type(Secret, secret, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncFireworks) -> None:
        response = await async_client.secrets.with_raw_response.update(
            secret_id="secret_id",
            account_id="account_id",
            key_name="keyName",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        secret = await response.parse()
        assert_matches_type(Secret, secret, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncFireworks) -> None:
        async with async_client.secrets.with_streaming_response.update(
            secret_id="secret_id",
            account_id="account_id",
            key_name="keyName",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            secret = await response.parse()
            assert_matches_type(Secret, secret, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.secrets.with_raw_response.update(
                secret_id="secret_id",
                account_id="",
                key_name="keyName",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `secret_id` but received ''"):
            await async_client.secrets.with_raw_response.update(
                secret_id="",
                account_id="account_id",
                key_name="keyName",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncFireworks) -> None:
        secret = await async_client.secrets.list(
            account_id="account_id",
        )
        assert_matches_type(SecretListResponse, secret, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncFireworks) -> None:
        secret = await async_client.secrets.list(
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(SecretListResponse, secret, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncFireworks) -> None:
        response = await async_client.secrets.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        secret = await response.parse()
        assert_matches_type(SecretListResponse, secret, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncFireworks) -> None:
        async with async_client.secrets.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            secret = await response.parse()
            assert_matches_type(SecretListResponse, secret, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.secrets.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncFireworks) -> None:
        secret = await async_client.secrets.delete(
            secret_id="secret_id",
            account_id="account_id",
        )
        assert_matches_type(object, secret, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncFireworks) -> None:
        response = await async_client.secrets.with_raw_response.delete(
            secret_id="secret_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        secret = await response.parse()
        assert_matches_type(object, secret, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncFireworks) -> None:
        async with async_client.secrets.with_streaming_response.delete(
            secret_id="secret_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            secret = await response.parse()
            assert_matches_type(object, secret, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.secrets.with_raw_response.delete(
                secret_id="secret_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `secret_id` but received ''"):
            await async_client.secrets.with_raw_response.delete(
                secret_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get(self, async_client: AsyncFireworks) -> None:
        secret = await async_client.secrets.get(
            secret_id="secret_id",
            account_id="account_id",
        )
        assert_matches_type(Secret, secret, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_with_all_params(self, async_client: AsyncFireworks) -> None:
        secret = await async_client.secrets.get(
            secret_id="secret_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(Secret, secret, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncFireworks) -> None:
        response = await async_client.secrets.with_raw_response.get(
            secret_id="secret_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        secret = await response.parse()
        assert_matches_type(Secret, secret, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncFireworks) -> None:
        async with async_client.secrets.with_streaming_response.get(
            secret_id="secret_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            secret = await response.parse()
            assert_matches_type(Secret, secret, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.secrets.with_raw_response.get(
                secret_id="secret_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `secret_id` but received ''"):
            await async_client.secrets.with_raw_response.get(
                secret_id="",
                account_id="account_id",
            )
