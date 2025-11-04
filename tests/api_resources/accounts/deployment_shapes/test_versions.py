# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from fireworks_ai import FireworksAI, AsyncFireworksAI
from fireworks_ai.types.accounts.deployment_shapes import (
    VersionListResponse,
    GatewayDeploymentShapeVersion,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestVersions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: FireworksAI) -> None:
        version = client.accounts.deployment_shapes.versions.retrieve(
            version_id="version_id",
            account_id="account_id",
            deployment_shape_id="deployment_shape_id",
        )
        assert_matches_type(GatewayDeploymentShapeVersion, version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: FireworksAI) -> None:
        version = client.accounts.deployment_shapes.versions.retrieve(
            version_id="version_id",
            account_id="account_id",
            deployment_shape_id="deployment_shape_id",
            read_mask="readMask",
        )
        assert_matches_type(GatewayDeploymentShapeVersion, version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: FireworksAI) -> None:
        response = client.accounts.deployment_shapes.versions.with_raw_response.retrieve(
            version_id="version_id",
            account_id="account_id",
            deployment_shape_id="deployment_shape_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        version = response.parse()
        assert_matches_type(GatewayDeploymentShapeVersion, version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: FireworksAI) -> None:
        with client.accounts.deployment_shapes.versions.with_streaming_response.retrieve(
            version_id="version_id",
            account_id="account_id",
            deployment_shape_id="deployment_shape_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            version = response.parse()
            assert_matches_type(GatewayDeploymentShapeVersion, version, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.deployment_shapes.versions.with_raw_response.retrieve(
                version_id="version_id",
                account_id="",
                deployment_shape_id="deployment_shape_id",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_shape_id` but received ''"):
            client.accounts.deployment_shapes.versions.with_raw_response.retrieve(
                version_id="version_id",
                account_id="account_id",
                deployment_shape_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `version_id` but received ''"):
            client.accounts.deployment_shapes.versions.with_raw_response.retrieve(
                version_id="",
                account_id="account_id",
                deployment_shape_id="deployment_shape_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: FireworksAI) -> None:
        version = client.accounts.deployment_shapes.versions.update(
            version_id="version_id",
            account_id="account_id",
            deployment_shape_id="deployment_shape_id",
        )
        assert_matches_type(GatewayDeploymentShapeVersion, version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: FireworksAI) -> None:
        version = client.accounts.deployment_shapes.versions.update(
            version_id="version_id",
            account_id="account_id",
            deployment_shape_id="deployment_shape_id",
            public=True,
            validated=True,
        )
        assert_matches_type(GatewayDeploymentShapeVersion, version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: FireworksAI) -> None:
        response = client.accounts.deployment_shapes.versions.with_raw_response.update(
            version_id="version_id",
            account_id="account_id",
            deployment_shape_id="deployment_shape_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        version = response.parse()
        assert_matches_type(GatewayDeploymentShapeVersion, version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: FireworksAI) -> None:
        with client.accounts.deployment_shapes.versions.with_streaming_response.update(
            version_id="version_id",
            account_id="account_id",
            deployment_shape_id="deployment_shape_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            version = response.parse()
            assert_matches_type(GatewayDeploymentShapeVersion, version, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.deployment_shapes.versions.with_raw_response.update(
                version_id="version_id",
                account_id="",
                deployment_shape_id="deployment_shape_id",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_shape_id` but received ''"):
            client.accounts.deployment_shapes.versions.with_raw_response.update(
                version_id="version_id",
                account_id="account_id",
                deployment_shape_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `version_id` but received ''"):
            client.accounts.deployment_shapes.versions.with_raw_response.update(
                version_id="",
                account_id="account_id",
                deployment_shape_id="deployment_shape_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: FireworksAI) -> None:
        version = client.accounts.deployment_shapes.versions.list(
            deployment_shape_id="deployment_shape_id",
            account_id="account_id",
        )
        assert_matches_type(VersionListResponse, version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: FireworksAI) -> None:
        version = client.accounts.deployment_shapes.versions.list(
            deployment_shape_id="deployment_shape_id",
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(VersionListResponse, version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: FireworksAI) -> None:
        response = client.accounts.deployment_shapes.versions.with_raw_response.list(
            deployment_shape_id="deployment_shape_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        version = response.parse()
        assert_matches_type(VersionListResponse, version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: FireworksAI) -> None:
        with client.accounts.deployment_shapes.versions.with_streaming_response.list(
            deployment_shape_id="deployment_shape_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            version = response.parse()
            assert_matches_type(VersionListResponse, version, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.deployment_shapes.versions.with_raw_response.list(
                deployment_shape_id="deployment_shape_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_shape_id` but received ''"):
            client.accounts.deployment_shapes.versions.with_raw_response.list(
                deployment_shape_id="",
                account_id="account_id",
            )


class TestAsyncVersions:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncFireworksAI) -> None:
        version = await async_client.accounts.deployment_shapes.versions.retrieve(
            version_id="version_id",
            account_id="account_id",
            deployment_shape_id="deployment_shape_id",
        )
        assert_matches_type(GatewayDeploymentShapeVersion, version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncFireworksAI) -> None:
        version = await async_client.accounts.deployment_shapes.versions.retrieve(
            version_id="version_id",
            account_id="account_id",
            deployment_shape_id="deployment_shape_id",
            read_mask="readMask",
        )
        assert_matches_type(GatewayDeploymentShapeVersion, version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.deployment_shapes.versions.with_raw_response.retrieve(
            version_id="version_id",
            account_id="account_id",
            deployment_shape_id="deployment_shape_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        version = await response.parse()
        assert_matches_type(GatewayDeploymentShapeVersion, version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.deployment_shapes.versions.with_streaming_response.retrieve(
            version_id="version_id",
            account_id="account_id",
            deployment_shape_id="deployment_shape_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            version = await response.parse()
            assert_matches_type(GatewayDeploymentShapeVersion, version, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.deployment_shapes.versions.with_raw_response.retrieve(
                version_id="version_id",
                account_id="",
                deployment_shape_id="deployment_shape_id",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_shape_id` but received ''"):
            await async_client.accounts.deployment_shapes.versions.with_raw_response.retrieve(
                version_id="version_id",
                account_id="account_id",
                deployment_shape_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `version_id` but received ''"):
            await async_client.accounts.deployment_shapes.versions.with_raw_response.retrieve(
                version_id="",
                account_id="account_id",
                deployment_shape_id="deployment_shape_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncFireworksAI) -> None:
        version = await async_client.accounts.deployment_shapes.versions.update(
            version_id="version_id",
            account_id="account_id",
            deployment_shape_id="deployment_shape_id",
        )
        assert_matches_type(GatewayDeploymentShapeVersion, version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncFireworksAI) -> None:
        version = await async_client.accounts.deployment_shapes.versions.update(
            version_id="version_id",
            account_id="account_id",
            deployment_shape_id="deployment_shape_id",
            public=True,
            validated=True,
        )
        assert_matches_type(GatewayDeploymentShapeVersion, version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.deployment_shapes.versions.with_raw_response.update(
            version_id="version_id",
            account_id="account_id",
            deployment_shape_id="deployment_shape_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        version = await response.parse()
        assert_matches_type(GatewayDeploymentShapeVersion, version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.deployment_shapes.versions.with_streaming_response.update(
            version_id="version_id",
            account_id="account_id",
            deployment_shape_id="deployment_shape_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            version = await response.parse()
            assert_matches_type(GatewayDeploymentShapeVersion, version, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.deployment_shapes.versions.with_raw_response.update(
                version_id="version_id",
                account_id="",
                deployment_shape_id="deployment_shape_id",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_shape_id` but received ''"):
            await async_client.accounts.deployment_shapes.versions.with_raw_response.update(
                version_id="version_id",
                account_id="account_id",
                deployment_shape_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `version_id` but received ''"):
            await async_client.accounts.deployment_shapes.versions.with_raw_response.update(
                version_id="",
                account_id="account_id",
                deployment_shape_id="deployment_shape_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncFireworksAI) -> None:
        version = await async_client.accounts.deployment_shapes.versions.list(
            deployment_shape_id="deployment_shape_id",
            account_id="account_id",
        )
        assert_matches_type(VersionListResponse, version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncFireworksAI) -> None:
        version = await async_client.accounts.deployment_shapes.versions.list(
            deployment_shape_id="deployment_shape_id",
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(VersionListResponse, version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.deployment_shapes.versions.with_raw_response.list(
            deployment_shape_id="deployment_shape_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        version = await response.parse()
        assert_matches_type(VersionListResponse, version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.deployment_shapes.versions.with_streaming_response.list(
            deployment_shape_id="deployment_shape_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            version = await response.parse()
            assert_matches_type(VersionListResponse, version, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.deployment_shapes.versions.with_raw_response.list(
                deployment_shape_id="deployment_shape_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_shape_id` but received ''"):
            await async_client.accounts.deployment_shapes.versions.with_raw_response.list(
                deployment_shape_id="",
                account_id="account_id",
            )
