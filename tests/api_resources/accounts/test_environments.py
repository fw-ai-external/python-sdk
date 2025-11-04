# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from fireworks_ai import Fireworks, AsyncFireworks
from fireworks_ai.types.accounts import (
    GatewayEnvironment,
    EnvironmentListResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestEnvironments:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Fireworks) -> None:
        environment = client.accounts.environments.create(
            account_id="account_id",
            environment={},
            environment_id="environmentId",
        )
        assert_matches_type(GatewayEnvironment, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Fireworks) -> None:
        environment = client.accounts.environments.create(
            account_id="account_id",
            environment={
                "annotations": {"foo": "string"},
                "base_image_ref": "baseImageRef",
                "display_name": "displayName",
                "shared": True,
            },
            environment_id="environmentId",
        )
        assert_matches_type(GatewayEnvironment, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Fireworks) -> None:
        response = client.accounts.environments.with_raw_response.create(
            account_id="account_id",
            environment={},
            environment_id="environmentId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        environment = response.parse()
        assert_matches_type(GatewayEnvironment, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Fireworks) -> None:
        with client.accounts.environments.with_streaming_response.create(
            account_id="account_id",
            environment={},
            environment_id="environmentId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            environment = response.parse()
            assert_matches_type(GatewayEnvironment, environment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.environments.with_raw_response.create(
                account_id="",
                environment={},
                environment_id="environmentId",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: Fireworks) -> None:
        environment = client.accounts.environments.retrieve(
            environment_id="environment_id",
            account_id="account_id",
        )
        assert_matches_type(GatewayEnvironment, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: Fireworks) -> None:
        environment = client.accounts.environments.retrieve(
            environment_id="environment_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(GatewayEnvironment, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: Fireworks) -> None:
        response = client.accounts.environments.with_raw_response.retrieve(
            environment_id="environment_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        environment = response.parse()
        assert_matches_type(GatewayEnvironment, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: Fireworks) -> None:
        with client.accounts.environments.with_streaming_response.retrieve(
            environment_id="environment_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            environment = response.parse()
            assert_matches_type(GatewayEnvironment, environment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.environments.with_raw_response.retrieve(
                environment_id="environment_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `environment_id` but received ''"):
            client.accounts.environments.with_raw_response.retrieve(
                environment_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: Fireworks) -> None:
        environment = client.accounts.environments.update(
            environment_id="environment_id",
            account_id="account_id",
        )
        assert_matches_type(GatewayEnvironment, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: Fireworks) -> None:
        environment = client.accounts.environments.update(
            environment_id="environment_id",
            account_id="account_id",
            annotations={"foo": "string"},
            base_image_ref="baseImageRef",
            display_name="displayName",
            shared=True,
        )
        assert_matches_type(GatewayEnvironment, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: Fireworks) -> None:
        response = client.accounts.environments.with_raw_response.update(
            environment_id="environment_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        environment = response.parse()
        assert_matches_type(GatewayEnvironment, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: Fireworks) -> None:
        with client.accounts.environments.with_streaming_response.update(
            environment_id="environment_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            environment = response.parse()
            assert_matches_type(GatewayEnvironment, environment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.environments.with_raw_response.update(
                environment_id="environment_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `environment_id` but received ''"):
            client.accounts.environments.with_raw_response.update(
                environment_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Fireworks) -> None:
        environment = client.accounts.environments.list(
            account_id="account_id",
        )
        assert_matches_type(EnvironmentListResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: Fireworks) -> None:
        environment = client.accounts.environments.list(
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(EnvironmentListResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Fireworks) -> None:
        response = client.accounts.environments.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        environment = response.parse()
        assert_matches_type(EnvironmentListResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Fireworks) -> None:
        with client.accounts.environments.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            environment = response.parse()
            assert_matches_type(EnvironmentListResponse, environment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.environments.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: Fireworks) -> None:
        environment = client.accounts.environments.delete(
            environment_id="environment_id",
            account_id="account_id",
        )
        assert_matches_type(object, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: Fireworks) -> None:
        response = client.accounts.environments.with_raw_response.delete(
            environment_id="environment_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        environment = response.parse()
        assert_matches_type(object, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: Fireworks) -> None:
        with client.accounts.environments.with_streaming_response.delete(
            environment_id="environment_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            environment = response.parse()
            assert_matches_type(object, environment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.environments.with_raw_response.delete(
                environment_id="environment_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `environment_id` but received ''"):
            client.accounts.environments.with_raw_response.delete(
                environment_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_connect(self, client: Fireworks) -> None:
        environment = client.accounts.environments.connect(
            environment_id="environment_id",
            account_id="account_id",
            connection={"node_pool_id": "nodePoolId"},
        )
        assert_matches_type(object, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_connect_with_all_params(self, client: Fireworks) -> None:
        environment = client.accounts.environments.connect(
            environment_id="environment_id",
            account_id="account_id",
            connection={
                "node_pool_id": "nodePoolId",
                "num_ranks": 0,
                "role": "role",
                "use_local_storage": True,
            },
            vscode_version="vscodeVersion",
        )
        assert_matches_type(object, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_connect(self, client: Fireworks) -> None:
        response = client.accounts.environments.with_raw_response.connect(
            environment_id="environment_id",
            account_id="account_id",
            connection={"node_pool_id": "nodePoolId"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        environment = response.parse()
        assert_matches_type(object, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_connect(self, client: Fireworks) -> None:
        with client.accounts.environments.with_streaming_response.connect(
            environment_id="environment_id",
            account_id="account_id",
            connection={"node_pool_id": "nodePoolId"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            environment = response.parse()
            assert_matches_type(object, environment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_connect(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.environments.with_raw_response.connect(
                environment_id="environment_id",
                account_id="",
                connection={"node_pool_id": "nodePoolId"},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `environment_id` but received ''"):
            client.accounts.environments.with_raw_response.connect(
                environment_id="",
                account_id="account_id",
                connection={"node_pool_id": "nodePoolId"},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_disconnect(self, client: Fireworks) -> None:
        environment = client.accounts.environments.disconnect(
            environment_id="environment_id",
            account_id="account_id",
        )
        assert_matches_type(object, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_disconnect_with_all_params(self, client: Fireworks) -> None:
        environment = client.accounts.environments.disconnect(
            environment_id="environment_id",
            account_id="account_id",
            force=True,
            reset_snapshots=True,
        )
        assert_matches_type(object, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_disconnect(self, client: Fireworks) -> None:
        response = client.accounts.environments.with_raw_response.disconnect(
            environment_id="environment_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        environment = response.parse()
        assert_matches_type(object, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_disconnect(self, client: Fireworks) -> None:
        with client.accounts.environments.with_streaming_response.disconnect(
            environment_id="environment_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            environment = response.parse()
            assert_matches_type(object, environment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_disconnect(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.environments.with_raw_response.disconnect(
                environment_id="environment_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `environment_id` but received ''"):
            client.accounts.environments.with_raw_response.disconnect(
                environment_id="",
                account_id="account_id",
            )


class TestAsyncEnvironments:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncFireworks) -> None:
        environment = await async_client.accounts.environments.create(
            account_id="account_id",
            environment={},
            environment_id="environmentId",
        )
        assert_matches_type(GatewayEnvironment, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncFireworks) -> None:
        environment = await async_client.accounts.environments.create(
            account_id="account_id",
            environment={
                "annotations": {"foo": "string"},
                "base_image_ref": "baseImageRef",
                "display_name": "displayName",
                "shared": True,
            },
            environment_id="environmentId",
        )
        assert_matches_type(GatewayEnvironment, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncFireworks) -> None:
        response = await async_client.accounts.environments.with_raw_response.create(
            account_id="account_id",
            environment={},
            environment_id="environmentId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        environment = await response.parse()
        assert_matches_type(GatewayEnvironment, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncFireworks) -> None:
        async with async_client.accounts.environments.with_streaming_response.create(
            account_id="account_id",
            environment={},
            environment_id="environmentId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            environment = await response.parse()
            assert_matches_type(GatewayEnvironment, environment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.environments.with_raw_response.create(
                account_id="",
                environment={},
                environment_id="environmentId",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncFireworks) -> None:
        environment = await async_client.accounts.environments.retrieve(
            environment_id="environment_id",
            account_id="account_id",
        )
        assert_matches_type(GatewayEnvironment, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncFireworks) -> None:
        environment = await async_client.accounts.environments.retrieve(
            environment_id="environment_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(GatewayEnvironment, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncFireworks) -> None:
        response = await async_client.accounts.environments.with_raw_response.retrieve(
            environment_id="environment_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        environment = await response.parse()
        assert_matches_type(GatewayEnvironment, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncFireworks) -> None:
        async with async_client.accounts.environments.with_streaming_response.retrieve(
            environment_id="environment_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            environment = await response.parse()
            assert_matches_type(GatewayEnvironment, environment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.environments.with_raw_response.retrieve(
                environment_id="environment_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `environment_id` but received ''"):
            await async_client.accounts.environments.with_raw_response.retrieve(
                environment_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncFireworks) -> None:
        environment = await async_client.accounts.environments.update(
            environment_id="environment_id",
            account_id="account_id",
        )
        assert_matches_type(GatewayEnvironment, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncFireworks) -> None:
        environment = await async_client.accounts.environments.update(
            environment_id="environment_id",
            account_id="account_id",
            annotations={"foo": "string"},
            base_image_ref="baseImageRef",
            display_name="displayName",
            shared=True,
        )
        assert_matches_type(GatewayEnvironment, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncFireworks) -> None:
        response = await async_client.accounts.environments.with_raw_response.update(
            environment_id="environment_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        environment = await response.parse()
        assert_matches_type(GatewayEnvironment, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncFireworks) -> None:
        async with async_client.accounts.environments.with_streaming_response.update(
            environment_id="environment_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            environment = await response.parse()
            assert_matches_type(GatewayEnvironment, environment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.environments.with_raw_response.update(
                environment_id="environment_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `environment_id` but received ''"):
            await async_client.accounts.environments.with_raw_response.update(
                environment_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncFireworks) -> None:
        environment = await async_client.accounts.environments.list(
            account_id="account_id",
        )
        assert_matches_type(EnvironmentListResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncFireworks) -> None:
        environment = await async_client.accounts.environments.list(
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(EnvironmentListResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncFireworks) -> None:
        response = await async_client.accounts.environments.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        environment = await response.parse()
        assert_matches_type(EnvironmentListResponse, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncFireworks) -> None:
        async with async_client.accounts.environments.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            environment = await response.parse()
            assert_matches_type(EnvironmentListResponse, environment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.environments.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncFireworks) -> None:
        environment = await async_client.accounts.environments.delete(
            environment_id="environment_id",
            account_id="account_id",
        )
        assert_matches_type(object, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncFireworks) -> None:
        response = await async_client.accounts.environments.with_raw_response.delete(
            environment_id="environment_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        environment = await response.parse()
        assert_matches_type(object, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncFireworks) -> None:
        async with async_client.accounts.environments.with_streaming_response.delete(
            environment_id="environment_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            environment = await response.parse()
            assert_matches_type(object, environment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.environments.with_raw_response.delete(
                environment_id="environment_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `environment_id` but received ''"):
            await async_client.accounts.environments.with_raw_response.delete(
                environment_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_connect(self, async_client: AsyncFireworks) -> None:
        environment = await async_client.accounts.environments.connect(
            environment_id="environment_id",
            account_id="account_id",
            connection={"node_pool_id": "nodePoolId"},
        )
        assert_matches_type(object, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_connect_with_all_params(self, async_client: AsyncFireworks) -> None:
        environment = await async_client.accounts.environments.connect(
            environment_id="environment_id",
            account_id="account_id",
            connection={
                "node_pool_id": "nodePoolId",
                "num_ranks": 0,
                "role": "role",
                "use_local_storage": True,
            },
            vscode_version="vscodeVersion",
        )
        assert_matches_type(object, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_connect(self, async_client: AsyncFireworks) -> None:
        response = await async_client.accounts.environments.with_raw_response.connect(
            environment_id="environment_id",
            account_id="account_id",
            connection={"node_pool_id": "nodePoolId"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        environment = await response.parse()
        assert_matches_type(object, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_connect(self, async_client: AsyncFireworks) -> None:
        async with async_client.accounts.environments.with_streaming_response.connect(
            environment_id="environment_id",
            account_id="account_id",
            connection={"node_pool_id": "nodePoolId"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            environment = await response.parse()
            assert_matches_type(object, environment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_connect(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.environments.with_raw_response.connect(
                environment_id="environment_id",
                account_id="",
                connection={"node_pool_id": "nodePoolId"},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `environment_id` but received ''"):
            await async_client.accounts.environments.with_raw_response.connect(
                environment_id="",
                account_id="account_id",
                connection={"node_pool_id": "nodePoolId"},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_disconnect(self, async_client: AsyncFireworks) -> None:
        environment = await async_client.accounts.environments.disconnect(
            environment_id="environment_id",
            account_id="account_id",
        )
        assert_matches_type(object, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_disconnect_with_all_params(self, async_client: AsyncFireworks) -> None:
        environment = await async_client.accounts.environments.disconnect(
            environment_id="environment_id",
            account_id="account_id",
            force=True,
            reset_snapshots=True,
        )
        assert_matches_type(object, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_disconnect(self, async_client: AsyncFireworks) -> None:
        response = await async_client.accounts.environments.with_raw_response.disconnect(
            environment_id="environment_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        environment = await response.parse()
        assert_matches_type(object, environment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_disconnect(self, async_client: AsyncFireworks) -> None:
        async with async_client.accounts.environments.with_streaming_response.disconnect(
            environment_id="environment_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            environment = await response.parse()
            assert_matches_type(object, environment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_disconnect(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.environments.with_raw_response.disconnect(
                environment_id="environment_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `environment_id` but received ''"):
            await async_client.accounts.environments.with_raw_response.disconnect(
                environment_id="",
                account_id="account_id",
            )
