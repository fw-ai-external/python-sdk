# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from fireworks import Fireworks, AsyncFireworks
from tests.utils import assert_matches_type
from fireworks.types import (
    DeploymentShapeVersionGetResponse,
    DeploymentShapeVersionListResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDeploymentShapeVersions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Fireworks) -> None:
        deployment_shape_version = client.deployment_shape_versions.list(
            deployment_shape_id="deployment_shape_id",
            account_id="account_id",
        )
        assert_matches_type(DeploymentShapeVersionListResponse, deployment_shape_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: Fireworks) -> None:
        deployment_shape_version = client.deployment_shape_versions.list(
            deployment_shape_id="deployment_shape_id",
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(DeploymentShapeVersionListResponse, deployment_shape_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Fireworks) -> None:
        response = client.deployment_shape_versions.with_raw_response.list(
            deployment_shape_id="deployment_shape_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment_shape_version = response.parse()
        assert_matches_type(DeploymentShapeVersionListResponse, deployment_shape_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Fireworks) -> None:
        with client.deployment_shape_versions.with_streaming_response.list(
            deployment_shape_id="deployment_shape_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment_shape_version = response.parse()
            assert_matches_type(DeploymentShapeVersionListResponse, deployment_shape_version, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.deployment_shape_versions.with_raw_response.list(
                deployment_shape_id="deployment_shape_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_shape_id` but received ''"):
            client.deployment_shape_versions.with_raw_response.list(
                deployment_shape_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get(self, client: Fireworks) -> None:
        deployment_shape_version = client.deployment_shape_versions.get(
            version_id="version_id",
            account_id="account_id",
            deployment_shape_id="deployment_shape_id",
        )
        assert_matches_type(DeploymentShapeVersionGetResponse, deployment_shape_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_with_all_params(self, client: Fireworks) -> None:
        deployment_shape_version = client.deployment_shape_versions.get(
            version_id="version_id",
            account_id="account_id",
            deployment_shape_id="deployment_shape_id",
            read_mask="readMask",
        )
        assert_matches_type(DeploymentShapeVersionGetResponse, deployment_shape_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get(self, client: Fireworks) -> None:
        response = client.deployment_shape_versions.with_raw_response.get(
            version_id="version_id",
            account_id="account_id",
            deployment_shape_id="deployment_shape_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment_shape_version = response.parse()
        assert_matches_type(DeploymentShapeVersionGetResponse, deployment_shape_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get(self, client: Fireworks) -> None:
        with client.deployment_shape_versions.with_streaming_response.get(
            version_id="version_id",
            account_id="account_id",
            deployment_shape_id="deployment_shape_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment_shape_version = response.parse()
            assert_matches_type(DeploymentShapeVersionGetResponse, deployment_shape_version, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.deployment_shape_versions.with_raw_response.get(
                version_id="version_id",
                account_id="",
                deployment_shape_id="deployment_shape_id",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_shape_id` but received ''"):
            client.deployment_shape_versions.with_raw_response.get(
                version_id="version_id",
                account_id="account_id",
                deployment_shape_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `version_id` but received ''"):
            client.deployment_shape_versions.with_raw_response.get(
                version_id="",
                account_id="account_id",
                deployment_shape_id="deployment_shape_id",
            )


class TestAsyncDeploymentShapeVersions:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncFireworks) -> None:
        deployment_shape_version = await async_client.deployment_shape_versions.list(
            deployment_shape_id="deployment_shape_id",
            account_id="account_id",
        )
        assert_matches_type(DeploymentShapeVersionListResponse, deployment_shape_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncFireworks) -> None:
        deployment_shape_version = await async_client.deployment_shape_versions.list(
            deployment_shape_id="deployment_shape_id",
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(DeploymentShapeVersionListResponse, deployment_shape_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncFireworks) -> None:
        response = await async_client.deployment_shape_versions.with_raw_response.list(
            deployment_shape_id="deployment_shape_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment_shape_version = await response.parse()
        assert_matches_type(DeploymentShapeVersionListResponse, deployment_shape_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncFireworks) -> None:
        async with async_client.deployment_shape_versions.with_streaming_response.list(
            deployment_shape_id="deployment_shape_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment_shape_version = await response.parse()
            assert_matches_type(DeploymentShapeVersionListResponse, deployment_shape_version, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.deployment_shape_versions.with_raw_response.list(
                deployment_shape_id="deployment_shape_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_shape_id` but received ''"):
            await async_client.deployment_shape_versions.with_raw_response.list(
                deployment_shape_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get(self, async_client: AsyncFireworks) -> None:
        deployment_shape_version = await async_client.deployment_shape_versions.get(
            version_id="version_id",
            account_id="account_id",
            deployment_shape_id="deployment_shape_id",
        )
        assert_matches_type(DeploymentShapeVersionGetResponse, deployment_shape_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_with_all_params(self, async_client: AsyncFireworks) -> None:
        deployment_shape_version = await async_client.deployment_shape_versions.get(
            version_id="version_id",
            account_id="account_id",
            deployment_shape_id="deployment_shape_id",
            read_mask="readMask",
        )
        assert_matches_type(DeploymentShapeVersionGetResponse, deployment_shape_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncFireworks) -> None:
        response = await async_client.deployment_shape_versions.with_raw_response.get(
            version_id="version_id",
            account_id="account_id",
            deployment_shape_id="deployment_shape_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment_shape_version = await response.parse()
        assert_matches_type(DeploymentShapeVersionGetResponse, deployment_shape_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncFireworks) -> None:
        async with async_client.deployment_shape_versions.with_streaming_response.get(
            version_id="version_id",
            account_id="account_id",
            deployment_shape_id="deployment_shape_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment_shape_version = await response.parse()
            assert_matches_type(DeploymentShapeVersionGetResponse, deployment_shape_version, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.deployment_shape_versions.with_raw_response.get(
                version_id="version_id",
                account_id="",
                deployment_shape_id="deployment_shape_id",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_shape_id` but received ''"):
            await async_client.deployment_shape_versions.with_raw_response.get(
                version_id="version_id",
                account_id="account_id",
                deployment_shape_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `version_id` but received ''"):
            await async_client.deployment_shape_versions.with_raw_response.get(
                version_id="",
                account_id="account_id",
                deployment_shape_id="deployment_shape_id",
            )
