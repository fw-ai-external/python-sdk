# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from fireworks import Fireworks, AsyncFireworks
from tests.utils import assert_matches_type
from fireworks.pagination import SyncCursorLora, AsyncCursorLora
from fireworks.types.shared import DeployedModel

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestLora:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: Fireworks) -> None:
        lora = client.lora.update(
            deployed_model_id="deployed_model_id",
            account_id="account_id",
        )
        assert_matches_type(DeployedModel, lora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: Fireworks) -> None:
        lora = client.lora.update(
            deployed_model_id="deployed_model_id",
            account_id="account_id",
            default=True,
            deployment="deployment",
            description="description",
            display_name="displayName",
            model="model",
            public=True,
            serverless=True,
        )
        assert_matches_type(DeployedModel, lora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: Fireworks) -> None:
        response = client.lora.with_raw_response.update(
            deployed_model_id="deployed_model_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        lora = response.parse()
        assert_matches_type(DeployedModel, lora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: Fireworks) -> None:
        with client.lora.with_streaming_response.update(
            deployed_model_id="deployed_model_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            lora = response.parse()
            assert_matches_type(DeployedModel, lora, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.lora.with_raw_response.update(
                deployed_model_id="deployed_model_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployed_model_id` but received ''"):
            client.lora.with_raw_response.update(
                deployed_model_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Fireworks) -> None:
        lora = client.lora.list(
            account_id="account_id",
        )
        assert_matches_type(SyncCursorLora[DeployedModel], lora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: Fireworks) -> None:
        lora = client.lora.list(
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(SyncCursorLora[DeployedModel], lora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Fireworks) -> None:
        response = client.lora.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        lora = response.parse()
        assert_matches_type(SyncCursorLora[DeployedModel], lora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Fireworks) -> None:
        with client.lora.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            lora = response.parse()
            assert_matches_type(SyncCursorLora[DeployedModel], lora, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.lora.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get(self, client: Fireworks) -> None:
        lora = client.lora.get(
            deployed_model_id="deployed_model_id",
            account_id="account_id",
        )
        assert_matches_type(DeployedModel, lora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_with_all_params(self, client: Fireworks) -> None:
        lora = client.lora.get(
            deployed_model_id="deployed_model_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(DeployedModel, lora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get(self, client: Fireworks) -> None:
        response = client.lora.with_raw_response.get(
            deployed_model_id="deployed_model_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        lora = response.parse()
        assert_matches_type(DeployedModel, lora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get(self, client: Fireworks) -> None:
        with client.lora.with_streaming_response.get(
            deployed_model_id="deployed_model_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            lora = response.parse()
            assert_matches_type(DeployedModel, lora, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.lora.with_raw_response.get(
                deployed_model_id="deployed_model_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployed_model_id` but received ''"):
            client.lora.with_raw_response.get(
                deployed_model_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_load(self, client: Fireworks) -> None:
        lora = client.lora.load(
            account_id="account_id",
        )
        assert_matches_type(DeployedModel, lora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_load_with_all_params(self, client: Fireworks) -> None:
        lora = client.lora.load(
            account_id="account_id",
            replace_merged_addon=True,
            default=True,
            deployment="deployment",
            description="description",
            display_name="displayName",
            model="model",
            public=True,
            serverless=True,
        )
        assert_matches_type(DeployedModel, lora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_load(self, client: Fireworks) -> None:
        response = client.lora.with_raw_response.load(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        lora = response.parse()
        assert_matches_type(DeployedModel, lora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_load(self, client: Fireworks) -> None:
        with client.lora.with_streaming_response.load(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            lora = response.parse()
            assert_matches_type(DeployedModel, lora, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_load(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.lora.with_raw_response.load(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_unload(self, client: Fireworks) -> None:
        lora = client.lora.unload(
            deployed_model_id="deployed_model_id",
            account_id="account_id",
        )
        assert_matches_type(object, lora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_unload(self, client: Fireworks) -> None:
        response = client.lora.with_raw_response.unload(
            deployed_model_id="deployed_model_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        lora = response.parse()
        assert_matches_type(object, lora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_unload(self, client: Fireworks) -> None:
        with client.lora.with_streaming_response.unload(
            deployed_model_id="deployed_model_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            lora = response.parse()
            assert_matches_type(object, lora, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_unload(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.lora.with_raw_response.unload(
                deployed_model_id="deployed_model_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployed_model_id` but received ''"):
            client.lora.with_raw_response.unload(
                deployed_model_id="",
                account_id="account_id",
            )


class TestAsyncLora:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncFireworks) -> None:
        lora = await async_client.lora.update(
            deployed_model_id="deployed_model_id",
            account_id="account_id",
        )
        assert_matches_type(DeployedModel, lora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncFireworks) -> None:
        lora = await async_client.lora.update(
            deployed_model_id="deployed_model_id",
            account_id="account_id",
            default=True,
            deployment="deployment",
            description="description",
            display_name="displayName",
            model="model",
            public=True,
            serverless=True,
        )
        assert_matches_type(DeployedModel, lora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncFireworks) -> None:
        response = await async_client.lora.with_raw_response.update(
            deployed_model_id="deployed_model_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        lora = await response.parse()
        assert_matches_type(DeployedModel, lora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncFireworks) -> None:
        async with async_client.lora.with_streaming_response.update(
            deployed_model_id="deployed_model_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            lora = await response.parse()
            assert_matches_type(DeployedModel, lora, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.lora.with_raw_response.update(
                deployed_model_id="deployed_model_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployed_model_id` but received ''"):
            await async_client.lora.with_raw_response.update(
                deployed_model_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncFireworks) -> None:
        lora = await async_client.lora.list(
            account_id="account_id",
        )
        assert_matches_type(AsyncCursorLora[DeployedModel], lora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncFireworks) -> None:
        lora = await async_client.lora.list(
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(AsyncCursorLora[DeployedModel], lora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncFireworks) -> None:
        response = await async_client.lora.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        lora = await response.parse()
        assert_matches_type(AsyncCursorLora[DeployedModel], lora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncFireworks) -> None:
        async with async_client.lora.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            lora = await response.parse()
            assert_matches_type(AsyncCursorLora[DeployedModel], lora, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.lora.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get(self, async_client: AsyncFireworks) -> None:
        lora = await async_client.lora.get(
            deployed_model_id="deployed_model_id",
            account_id="account_id",
        )
        assert_matches_type(DeployedModel, lora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_with_all_params(self, async_client: AsyncFireworks) -> None:
        lora = await async_client.lora.get(
            deployed_model_id="deployed_model_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(DeployedModel, lora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncFireworks) -> None:
        response = await async_client.lora.with_raw_response.get(
            deployed_model_id="deployed_model_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        lora = await response.parse()
        assert_matches_type(DeployedModel, lora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncFireworks) -> None:
        async with async_client.lora.with_streaming_response.get(
            deployed_model_id="deployed_model_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            lora = await response.parse()
            assert_matches_type(DeployedModel, lora, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.lora.with_raw_response.get(
                deployed_model_id="deployed_model_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployed_model_id` but received ''"):
            await async_client.lora.with_raw_response.get(
                deployed_model_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_load(self, async_client: AsyncFireworks) -> None:
        lora = await async_client.lora.load(
            account_id="account_id",
        )
        assert_matches_type(DeployedModel, lora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_load_with_all_params(self, async_client: AsyncFireworks) -> None:
        lora = await async_client.lora.load(
            account_id="account_id",
            replace_merged_addon=True,
            default=True,
            deployment="deployment",
            description="description",
            display_name="displayName",
            model="model",
            public=True,
            serverless=True,
        )
        assert_matches_type(DeployedModel, lora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_load(self, async_client: AsyncFireworks) -> None:
        response = await async_client.lora.with_raw_response.load(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        lora = await response.parse()
        assert_matches_type(DeployedModel, lora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_load(self, async_client: AsyncFireworks) -> None:
        async with async_client.lora.with_streaming_response.load(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            lora = await response.parse()
            assert_matches_type(DeployedModel, lora, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_load(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.lora.with_raw_response.load(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_unload(self, async_client: AsyncFireworks) -> None:
        lora = await async_client.lora.unload(
            deployed_model_id="deployed_model_id",
            account_id="account_id",
        )
        assert_matches_type(object, lora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_unload(self, async_client: AsyncFireworks) -> None:
        response = await async_client.lora.with_raw_response.unload(
            deployed_model_id="deployed_model_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        lora = await response.parse()
        assert_matches_type(object, lora, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_unload(self, async_client: AsyncFireworks) -> None:
        async with async_client.lora.with_streaming_response.unload(
            deployed_model_id="deployed_model_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            lora = await response.parse()
            assert_matches_type(object, lora, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_unload(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.lora.with_raw_response.unload(
                deployed_model_id="deployed_model_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployed_model_id` but received ''"):
            await async_client.lora.with_raw_response.unload(
                deployed_model_id="",
                account_id="account_id",
            )
