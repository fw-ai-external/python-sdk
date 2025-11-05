# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from fireworks_ai import Fireworks, AsyncFireworks
from fireworks_ai.types import (
    DeployedModelGetResponse,
    DeployedModelListResponse,
    DeployedModelCreateResponse,
    DeployedModelUpdateResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDeployedModels:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Fireworks) -> None:
        deployed_model = client.deployed_models.create(
            account_id="account_id",
        )
        assert_matches_type(DeployedModelCreateResponse, deployed_model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Fireworks) -> None:
        deployed_model = client.deployed_models.create(
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
        assert_matches_type(DeployedModelCreateResponse, deployed_model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Fireworks) -> None:
        response = client.deployed_models.with_raw_response.create(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployed_model = response.parse()
        assert_matches_type(DeployedModelCreateResponse, deployed_model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Fireworks) -> None:
        with client.deployed_models.with_streaming_response.create(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployed_model = response.parse()
            assert_matches_type(DeployedModelCreateResponse, deployed_model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.deployed_models.with_raw_response.create(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: Fireworks) -> None:
        deployed_model = client.deployed_models.update(
            deployed_model_id="deployed_model_id",
            account_id="account_id",
        )
        assert_matches_type(DeployedModelUpdateResponse, deployed_model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: Fireworks) -> None:
        deployed_model = client.deployed_models.update(
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
        assert_matches_type(DeployedModelUpdateResponse, deployed_model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: Fireworks) -> None:
        response = client.deployed_models.with_raw_response.update(
            deployed_model_id="deployed_model_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployed_model = response.parse()
        assert_matches_type(DeployedModelUpdateResponse, deployed_model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: Fireworks) -> None:
        with client.deployed_models.with_streaming_response.update(
            deployed_model_id="deployed_model_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployed_model = response.parse()
            assert_matches_type(DeployedModelUpdateResponse, deployed_model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.deployed_models.with_raw_response.update(
                deployed_model_id="deployed_model_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployed_model_id` but received ''"):
            client.deployed_models.with_raw_response.update(
                deployed_model_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Fireworks) -> None:
        deployed_model = client.deployed_models.list(
            account_id="account_id",
        )
        assert_matches_type(DeployedModelListResponse, deployed_model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: Fireworks) -> None:
        deployed_model = client.deployed_models.list(
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(DeployedModelListResponse, deployed_model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Fireworks) -> None:
        response = client.deployed_models.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployed_model = response.parse()
        assert_matches_type(DeployedModelListResponse, deployed_model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Fireworks) -> None:
        with client.deployed_models.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployed_model = response.parse()
            assert_matches_type(DeployedModelListResponse, deployed_model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.deployed_models.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: Fireworks) -> None:
        deployed_model = client.deployed_models.delete(
            deployed_model_id="deployed_model_id",
            account_id="account_id",
        )
        assert_matches_type(object, deployed_model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: Fireworks) -> None:
        response = client.deployed_models.with_raw_response.delete(
            deployed_model_id="deployed_model_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployed_model = response.parse()
        assert_matches_type(object, deployed_model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: Fireworks) -> None:
        with client.deployed_models.with_streaming_response.delete(
            deployed_model_id="deployed_model_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployed_model = response.parse()
            assert_matches_type(object, deployed_model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.deployed_models.with_raw_response.delete(
                deployed_model_id="deployed_model_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployed_model_id` but received ''"):
            client.deployed_models.with_raw_response.delete(
                deployed_model_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get(self, client: Fireworks) -> None:
        deployed_model = client.deployed_models.get(
            deployed_model_id="deployed_model_id",
            account_id="account_id",
        )
        assert_matches_type(DeployedModelGetResponse, deployed_model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_with_all_params(self, client: Fireworks) -> None:
        deployed_model = client.deployed_models.get(
            deployed_model_id="deployed_model_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(DeployedModelGetResponse, deployed_model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get(self, client: Fireworks) -> None:
        response = client.deployed_models.with_raw_response.get(
            deployed_model_id="deployed_model_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployed_model = response.parse()
        assert_matches_type(DeployedModelGetResponse, deployed_model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get(self, client: Fireworks) -> None:
        with client.deployed_models.with_streaming_response.get(
            deployed_model_id="deployed_model_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployed_model = response.parse()
            assert_matches_type(DeployedModelGetResponse, deployed_model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.deployed_models.with_raw_response.get(
                deployed_model_id="deployed_model_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployed_model_id` but received ''"):
            client.deployed_models.with_raw_response.get(
                deployed_model_id="",
                account_id="account_id",
            )


class TestAsyncDeployedModels:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncFireworks) -> None:
        deployed_model = await async_client.deployed_models.create(
            account_id="account_id",
        )
        assert_matches_type(DeployedModelCreateResponse, deployed_model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncFireworks) -> None:
        deployed_model = await async_client.deployed_models.create(
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
        assert_matches_type(DeployedModelCreateResponse, deployed_model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncFireworks) -> None:
        response = await async_client.deployed_models.with_raw_response.create(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployed_model = await response.parse()
        assert_matches_type(DeployedModelCreateResponse, deployed_model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncFireworks) -> None:
        async with async_client.deployed_models.with_streaming_response.create(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployed_model = await response.parse()
            assert_matches_type(DeployedModelCreateResponse, deployed_model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.deployed_models.with_raw_response.create(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncFireworks) -> None:
        deployed_model = await async_client.deployed_models.update(
            deployed_model_id="deployed_model_id",
            account_id="account_id",
        )
        assert_matches_type(DeployedModelUpdateResponse, deployed_model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncFireworks) -> None:
        deployed_model = await async_client.deployed_models.update(
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
        assert_matches_type(DeployedModelUpdateResponse, deployed_model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncFireworks) -> None:
        response = await async_client.deployed_models.with_raw_response.update(
            deployed_model_id="deployed_model_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployed_model = await response.parse()
        assert_matches_type(DeployedModelUpdateResponse, deployed_model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncFireworks) -> None:
        async with async_client.deployed_models.with_streaming_response.update(
            deployed_model_id="deployed_model_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployed_model = await response.parse()
            assert_matches_type(DeployedModelUpdateResponse, deployed_model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.deployed_models.with_raw_response.update(
                deployed_model_id="deployed_model_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployed_model_id` but received ''"):
            await async_client.deployed_models.with_raw_response.update(
                deployed_model_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncFireworks) -> None:
        deployed_model = await async_client.deployed_models.list(
            account_id="account_id",
        )
        assert_matches_type(DeployedModelListResponse, deployed_model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncFireworks) -> None:
        deployed_model = await async_client.deployed_models.list(
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(DeployedModelListResponse, deployed_model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncFireworks) -> None:
        response = await async_client.deployed_models.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployed_model = await response.parse()
        assert_matches_type(DeployedModelListResponse, deployed_model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncFireworks) -> None:
        async with async_client.deployed_models.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployed_model = await response.parse()
            assert_matches_type(DeployedModelListResponse, deployed_model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.deployed_models.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncFireworks) -> None:
        deployed_model = await async_client.deployed_models.delete(
            deployed_model_id="deployed_model_id",
            account_id="account_id",
        )
        assert_matches_type(object, deployed_model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncFireworks) -> None:
        response = await async_client.deployed_models.with_raw_response.delete(
            deployed_model_id="deployed_model_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployed_model = await response.parse()
        assert_matches_type(object, deployed_model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncFireworks) -> None:
        async with async_client.deployed_models.with_streaming_response.delete(
            deployed_model_id="deployed_model_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployed_model = await response.parse()
            assert_matches_type(object, deployed_model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.deployed_models.with_raw_response.delete(
                deployed_model_id="deployed_model_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployed_model_id` but received ''"):
            await async_client.deployed_models.with_raw_response.delete(
                deployed_model_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get(self, async_client: AsyncFireworks) -> None:
        deployed_model = await async_client.deployed_models.get(
            deployed_model_id="deployed_model_id",
            account_id="account_id",
        )
        assert_matches_type(DeployedModelGetResponse, deployed_model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_with_all_params(self, async_client: AsyncFireworks) -> None:
        deployed_model = await async_client.deployed_models.get(
            deployed_model_id="deployed_model_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(DeployedModelGetResponse, deployed_model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncFireworks) -> None:
        response = await async_client.deployed_models.with_raw_response.get(
            deployed_model_id="deployed_model_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployed_model = await response.parse()
        assert_matches_type(DeployedModelGetResponse, deployed_model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncFireworks) -> None:
        async with async_client.deployed_models.with_streaming_response.get(
            deployed_model_id="deployed_model_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployed_model = await response.parse()
            assert_matches_type(DeployedModelGetResponse, deployed_model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.deployed_models.with_raw_response.get(
                deployed_model_id="deployed_model_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployed_model_id` but received ''"):
            await async_client.deployed_models.with_raw_response.get(
                deployed_model_id="",
                account_id="account_id",
            )
