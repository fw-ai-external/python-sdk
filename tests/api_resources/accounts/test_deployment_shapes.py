# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from fireworks_ai import Fireworks, AsyncFireworks
from fireworks_ai.types.accounts import (
    GatewayDeploymentShape,
    DeploymentShapeListResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDeploymentShapes:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Fireworks) -> None:
        deployment_shape = client.accounts.deployment_shapes.create(
            account_id="account_id",
            base_model="baseModel",
        )
        assert_matches_type(GatewayDeploymentShape, deployment_shape, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Fireworks) -> None:
        deployment_shape = client.accounts.deployment_shapes.create(
            account_id="account_id",
            base_model="baseModel",
            deployment_shape_id="deploymentShapeId",
            disable_size_validation=True,
            accelerator_count=0,
            accelerator_type="ACCELERATOR_TYPE_UNSPECIFIED",
            description="description",
            display_name="displayName",
            draft_model="draftModel",
            draft_token_count=0,
            enable_addons=True,
            enable_session_affinity=True,
            ngram_speculation_length=0,
            precision="PRECISION_UNSPECIFIED",
            preset_type="PRESET_TYPE_UNSPECIFIED",
        )
        assert_matches_type(GatewayDeploymentShape, deployment_shape, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Fireworks) -> None:
        response = client.accounts.deployment_shapes.with_raw_response.create(
            account_id="account_id",
            base_model="baseModel",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment_shape = response.parse()
        assert_matches_type(GatewayDeploymentShape, deployment_shape, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Fireworks) -> None:
        with client.accounts.deployment_shapes.with_streaming_response.create(
            account_id="account_id",
            base_model="baseModel",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment_shape = response.parse()
            assert_matches_type(GatewayDeploymentShape, deployment_shape, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.deployment_shapes.with_raw_response.create(
                account_id="",
                base_model="baseModel",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: Fireworks) -> None:
        deployment_shape = client.accounts.deployment_shapes.retrieve(
            deployment_shape_id="deployment_shape_id",
            account_id="account_id",
        )
        assert_matches_type(GatewayDeploymentShape, deployment_shape, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: Fireworks) -> None:
        deployment_shape = client.accounts.deployment_shapes.retrieve(
            deployment_shape_id="deployment_shape_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(GatewayDeploymentShape, deployment_shape, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: Fireworks) -> None:
        response = client.accounts.deployment_shapes.with_raw_response.retrieve(
            deployment_shape_id="deployment_shape_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment_shape = response.parse()
        assert_matches_type(GatewayDeploymentShape, deployment_shape, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: Fireworks) -> None:
        with client.accounts.deployment_shapes.with_streaming_response.retrieve(
            deployment_shape_id="deployment_shape_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment_shape = response.parse()
            assert_matches_type(GatewayDeploymentShape, deployment_shape, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.deployment_shapes.with_raw_response.retrieve(
                deployment_shape_id="deployment_shape_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_shape_id` but received ''"):
            client.accounts.deployment_shapes.with_raw_response.retrieve(
                deployment_shape_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: Fireworks) -> None:
        deployment_shape = client.accounts.deployment_shapes.update(
            deployment_shape_id="deployment_shape_id",
            account_id="account_id",
            base_model="baseModel",
        )
        assert_matches_type(GatewayDeploymentShape, deployment_shape, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: Fireworks) -> None:
        deployment_shape = client.accounts.deployment_shapes.update(
            deployment_shape_id="deployment_shape_id",
            account_id="account_id",
            base_model="baseModel",
            disable_size_validation=True,
            from_latest_validated=True,
            accelerator_count=0,
            accelerator_type="ACCELERATOR_TYPE_UNSPECIFIED",
            description="description",
            display_name="displayName",
            draft_model="draftModel",
            draft_token_count=0,
            enable_addons=True,
            enable_session_affinity=True,
            ngram_speculation_length=0,
            precision="PRECISION_UNSPECIFIED",
            preset_type="PRESET_TYPE_UNSPECIFIED",
        )
        assert_matches_type(GatewayDeploymentShape, deployment_shape, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: Fireworks) -> None:
        response = client.accounts.deployment_shapes.with_raw_response.update(
            deployment_shape_id="deployment_shape_id",
            account_id="account_id",
            base_model="baseModel",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment_shape = response.parse()
        assert_matches_type(GatewayDeploymentShape, deployment_shape, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: Fireworks) -> None:
        with client.accounts.deployment_shapes.with_streaming_response.update(
            deployment_shape_id="deployment_shape_id",
            account_id="account_id",
            base_model="baseModel",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment_shape = response.parse()
            assert_matches_type(GatewayDeploymentShape, deployment_shape, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.deployment_shapes.with_raw_response.update(
                deployment_shape_id="deployment_shape_id",
                account_id="",
                base_model="baseModel",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_shape_id` but received ''"):
            client.accounts.deployment_shapes.with_raw_response.update(
                deployment_shape_id="",
                account_id="account_id",
                base_model="baseModel",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Fireworks) -> None:
        deployment_shape = client.accounts.deployment_shapes.list(
            account_id="account_id",
        )
        assert_matches_type(DeploymentShapeListResponse, deployment_shape, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: Fireworks) -> None:
        deployment_shape = client.accounts.deployment_shapes.list(
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
            target_model="targetModel",
        )
        assert_matches_type(DeploymentShapeListResponse, deployment_shape, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Fireworks) -> None:
        response = client.accounts.deployment_shapes.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment_shape = response.parse()
        assert_matches_type(DeploymentShapeListResponse, deployment_shape, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Fireworks) -> None:
        with client.accounts.deployment_shapes.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment_shape = response.parse()
            assert_matches_type(DeploymentShapeListResponse, deployment_shape, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.deployment_shapes.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: Fireworks) -> None:
        deployment_shape = client.accounts.deployment_shapes.delete(
            deployment_shape_id="deployment_shape_id",
            account_id="account_id",
        )
        assert_matches_type(object, deployment_shape, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: Fireworks) -> None:
        response = client.accounts.deployment_shapes.with_raw_response.delete(
            deployment_shape_id="deployment_shape_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment_shape = response.parse()
        assert_matches_type(object, deployment_shape, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: Fireworks) -> None:
        with client.accounts.deployment_shapes.with_streaming_response.delete(
            deployment_shape_id="deployment_shape_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment_shape = response.parse()
            assert_matches_type(object, deployment_shape, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.deployment_shapes.with_raw_response.delete(
                deployment_shape_id="deployment_shape_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_shape_id` but received ''"):
            client.accounts.deployment_shapes.with_raw_response.delete(
                deployment_shape_id="",
                account_id="account_id",
            )


class TestAsyncDeploymentShapes:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncFireworks) -> None:
        deployment_shape = await async_client.accounts.deployment_shapes.create(
            account_id="account_id",
            base_model="baseModel",
        )
        assert_matches_type(GatewayDeploymentShape, deployment_shape, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncFireworks) -> None:
        deployment_shape = await async_client.accounts.deployment_shapes.create(
            account_id="account_id",
            base_model="baseModel",
            deployment_shape_id="deploymentShapeId",
            disable_size_validation=True,
            accelerator_count=0,
            accelerator_type="ACCELERATOR_TYPE_UNSPECIFIED",
            description="description",
            display_name="displayName",
            draft_model="draftModel",
            draft_token_count=0,
            enable_addons=True,
            enable_session_affinity=True,
            ngram_speculation_length=0,
            precision="PRECISION_UNSPECIFIED",
            preset_type="PRESET_TYPE_UNSPECIFIED",
        )
        assert_matches_type(GatewayDeploymentShape, deployment_shape, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncFireworks) -> None:
        response = await async_client.accounts.deployment_shapes.with_raw_response.create(
            account_id="account_id",
            base_model="baseModel",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment_shape = await response.parse()
        assert_matches_type(GatewayDeploymentShape, deployment_shape, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncFireworks) -> None:
        async with async_client.accounts.deployment_shapes.with_streaming_response.create(
            account_id="account_id",
            base_model="baseModel",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment_shape = await response.parse()
            assert_matches_type(GatewayDeploymentShape, deployment_shape, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.deployment_shapes.with_raw_response.create(
                account_id="",
                base_model="baseModel",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncFireworks) -> None:
        deployment_shape = await async_client.accounts.deployment_shapes.retrieve(
            deployment_shape_id="deployment_shape_id",
            account_id="account_id",
        )
        assert_matches_type(GatewayDeploymentShape, deployment_shape, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncFireworks) -> None:
        deployment_shape = await async_client.accounts.deployment_shapes.retrieve(
            deployment_shape_id="deployment_shape_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(GatewayDeploymentShape, deployment_shape, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncFireworks) -> None:
        response = await async_client.accounts.deployment_shapes.with_raw_response.retrieve(
            deployment_shape_id="deployment_shape_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment_shape = await response.parse()
        assert_matches_type(GatewayDeploymentShape, deployment_shape, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncFireworks) -> None:
        async with async_client.accounts.deployment_shapes.with_streaming_response.retrieve(
            deployment_shape_id="deployment_shape_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment_shape = await response.parse()
            assert_matches_type(GatewayDeploymentShape, deployment_shape, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.deployment_shapes.with_raw_response.retrieve(
                deployment_shape_id="deployment_shape_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_shape_id` but received ''"):
            await async_client.accounts.deployment_shapes.with_raw_response.retrieve(
                deployment_shape_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncFireworks) -> None:
        deployment_shape = await async_client.accounts.deployment_shapes.update(
            deployment_shape_id="deployment_shape_id",
            account_id="account_id",
            base_model="baseModel",
        )
        assert_matches_type(GatewayDeploymentShape, deployment_shape, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncFireworks) -> None:
        deployment_shape = await async_client.accounts.deployment_shapes.update(
            deployment_shape_id="deployment_shape_id",
            account_id="account_id",
            base_model="baseModel",
            disable_size_validation=True,
            from_latest_validated=True,
            accelerator_count=0,
            accelerator_type="ACCELERATOR_TYPE_UNSPECIFIED",
            description="description",
            display_name="displayName",
            draft_model="draftModel",
            draft_token_count=0,
            enable_addons=True,
            enable_session_affinity=True,
            ngram_speculation_length=0,
            precision="PRECISION_UNSPECIFIED",
            preset_type="PRESET_TYPE_UNSPECIFIED",
        )
        assert_matches_type(GatewayDeploymentShape, deployment_shape, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncFireworks) -> None:
        response = await async_client.accounts.deployment_shapes.with_raw_response.update(
            deployment_shape_id="deployment_shape_id",
            account_id="account_id",
            base_model="baseModel",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment_shape = await response.parse()
        assert_matches_type(GatewayDeploymentShape, deployment_shape, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncFireworks) -> None:
        async with async_client.accounts.deployment_shapes.with_streaming_response.update(
            deployment_shape_id="deployment_shape_id",
            account_id="account_id",
            base_model="baseModel",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment_shape = await response.parse()
            assert_matches_type(GatewayDeploymentShape, deployment_shape, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.deployment_shapes.with_raw_response.update(
                deployment_shape_id="deployment_shape_id",
                account_id="",
                base_model="baseModel",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_shape_id` but received ''"):
            await async_client.accounts.deployment_shapes.with_raw_response.update(
                deployment_shape_id="",
                account_id="account_id",
                base_model="baseModel",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncFireworks) -> None:
        deployment_shape = await async_client.accounts.deployment_shapes.list(
            account_id="account_id",
        )
        assert_matches_type(DeploymentShapeListResponse, deployment_shape, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncFireworks) -> None:
        deployment_shape = await async_client.accounts.deployment_shapes.list(
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
            target_model="targetModel",
        )
        assert_matches_type(DeploymentShapeListResponse, deployment_shape, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncFireworks) -> None:
        response = await async_client.accounts.deployment_shapes.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment_shape = await response.parse()
        assert_matches_type(DeploymentShapeListResponse, deployment_shape, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncFireworks) -> None:
        async with async_client.accounts.deployment_shapes.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment_shape = await response.parse()
            assert_matches_type(DeploymentShapeListResponse, deployment_shape, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.deployment_shapes.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncFireworks) -> None:
        deployment_shape = await async_client.accounts.deployment_shapes.delete(
            deployment_shape_id="deployment_shape_id",
            account_id="account_id",
        )
        assert_matches_type(object, deployment_shape, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncFireworks) -> None:
        response = await async_client.accounts.deployment_shapes.with_raw_response.delete(
            deployment_shape_id="deployment_shape_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment_shape = await response.parse()
        assert_matches_type(object, deployment_shape, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncFireworks) -> None:
        async with async_client.accounts.deployment_shapes.with_streaming_response.delete(
            deployment_shape_id="deployment_shape_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment_shape = await response.parse()
            assert_matches_type(object, deployment_shape, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.deployment_shapes.with_raw_response.delete(
                deployment_shape_id="deployment_shape_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_shape_id` but received ''"):
            await async_client.accounts.deployment_shapes.with_raw_response.delete(
                deployment_shape_id="",
                account_id="account_id",
            )
