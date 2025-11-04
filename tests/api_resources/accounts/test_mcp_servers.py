# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from fireworks_ai import Fireworks, AsyncFireworks
from fireworks_ai.types.accounts import (
    GatewayMcpServer,
    McpServerListResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestMcpServers:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Fireworks) -> None:
        mcp_server = client.accounts.mcp_servers.create(
            account_id="account_id",
            mcp_server_id="mcpServerId",
        )
        assert_matches_type(GatewayMcpServer, mcp_server, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Fireworks) -> None:
        mcp_server = client.accounts.mcp_servers.create(
            account_id="account_id",
            mcp_server_id="mcpServerId",
            annotations={"foo": "string"},
            api_key_secret="apiKeySecret",
            authentication_type="AUTHENTICATION_TYPE_UNSPECIFIED",
            description="description",
            display_name="displayName",
            endpoint_url="endpointUrl",
            max_qps=0,
            public=True,
            remote_hosted=True,
            simulated=True,
        )
        assert_matches_type(GatewayMcpServer, mcp_server, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Fireworks) -> None:
        response = client.accounts.mcp_servers.with_raw_response.create(
            account_id="account_id",
            mcp_server_id="mcpServerId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        mcp_server = response.parse()
        assert_matches_type(GatewayMcpServer, mcp_server, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Fireworks) -> None:
        with client.accounts.mcp_servers.with_streaming_response.create(
            account_id="account_id",
            mcp_server_id="mcpServerId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            mcp_server = response.parse()
            assert_matches_type(GatewayMcpServer, mcp_server, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.mcp_servers.with_raw_response.create(
                account_id="",
                mcp_server_id="mcpServerId",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: Fireworks) -> None:
        mcp_server = client.accounts.mcp_servers.retrieve(
            mcp_server_id="mcp_server_id",
            account_id="account_id",
        )
        assert_matches_type(GatewayMcpServer, mcp_server, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: Fireworks) -> None:
        mcp_server = client.accounts.mcp_servers.retrieve(
            mcp_server_id="mcp_server_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(GatewayMcpServer, mcp_server, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: Fireworks) -> None:
        response = client.accounts.mcp_servers.with_raw_response.retrieve(
            mcp_server_id="mcp_server_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        mcp_server = response.parse()
        assert_matches_type(GatewayMcpServer, mcp_server, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: Fireworks) -> None:
        with client.accounts.mcp_servers.with_streaming_response.retrieve(
            mcp_server_id="mcp_server_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            mcp_server = response.parse()
            assert_matches_type(GatewayMcpServer, mcp_server, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.mcp_servers.with_raw_response.retrieve(
                mcp_server_id="mcp_server_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `mcp_server_id` but received ''"):
            client.accounts.mcp_servers.with_raw_response.retrieve(
                mcp_server_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: Fireworks) -> None:
        mcp_server = client.accounts.mcp_servers.update(
            mcp_server_id="mcp_server_id",
            account_id="account_id",
        )
        assert_matches_type(GatewayMcpServer, mcp_server, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: Fireworks) -> None:
        mcp_server = client.accounts.mcp_servers.update(
            mcp_server_id="mcp_server_id",
            account_id="account_id",
            annotations={"foo": "string"},
            api_key_secret="apiKeySecret",
            authentication_type="AUTHENTICATION_TYPE_UNSPECIFIED",
            description="description",
            display_name="displayName",
            endpoint_url="endpointUrl",
            max_qps=0,
            public=True,
            remote_hosted=True,
            simulated=True,
        )
        assert_matches_type(GatewayMcpServer, mcp_server, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: Fireworks) -> None:
        response = client.accounts.mcp_servers.with_raw_response.update(
            mcp_server_id="mcp_server_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        mcp_server = response.parse()
        assert_matches_type(GatewayMcpServer, mcp_server, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: Fireworks) -> None:
        with client.accounts.mcp_servers.with_streaming_response.update(
            mcp_server_id="mcp_server_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            mcp_server = response.parse()
            assert_matches_type(GatewayMcpServer, mcp_server, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.mcp_servers.with_raw_response.update(
                mcp_server_id="mcp_server_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `mcp_server_id` but received ''"):
            client.accounts.mcp_servers.with_raw_response.update(
                mcp_server_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Fireworks) -> None:
        mcp_server = client.accounts.mcp_servers.list(
            account_id="account_id",
        )
        assert_matches_type(McpServerListResponse, mcp_server, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: Fireworks) -> None:
        mcp_server = client.accounts.mcp_servers.list(
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(McpServerListResponse, mcp_server, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Fireworks) -> None:
        response = client.accounts.mcp_servers.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        mcp_server = response.parse()
        assert_matches_type(McpServerListResponse, mcp_server, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Fireworks) -> None:
        with client.accounts.mcp_servers.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            mcp_server = response.parse()
            assert_matches_type(McpServerListResponse, mcp_server, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.mcp_servers.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: Fireworks) -> None:
        mcp_server = client.accounts.mcp_servers.delete(
            mcp_server_id="mcp_server_id",
            account_id="account_id",
        )
        assert_matches_type(object, mcp_server, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: Fireworks) -> None:
        response = client.accounts.mcp_servers.with_raw_response.delete(
            mcp_server_id="mcp_server_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        mcp_server = response.parse()
        assert_matches_type(object, mcp_server, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: Fireworks) -> None:
        with client.accounts.mcp_servers.with_streaming_response.delete(
            mcp_server_id="mcp_server_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            mcp_server = response.parse()
            assert_matches_type(object, mcp_server, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.mcp_servers.with_raw_response.delete(
                mcp_server_id="mcp_server_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `mcp_server_id` but received ''"):
            client.accounts.mcp_servers.with_raw_response.delete(
                mcp_server_id="",
                account_id="account_id",
            )


class TestAsyncMcpServers:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncFireworks) -> None:
        mcp_server = await async_client.accounts.mcp_servers.create(
            account_id="account_id",
            mcp_server_id="mcpServerId",
        )
        assert_matches_type(GatewayMcpServer, mcp_server, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncFireworks) -> None:
        mcp_server = await async_client.accounts.mcp_servers.create(
            account_id="account_id",
            mcp_server_id="mcpServerId",
            annotations={"foo": "string"},
            api_key_secret="apiKeySecret",
            authentication_type="AUTHENTICATION_TYPE_UNSPECIFIED",
            description="description",
            display_name="displayName",
            endpoint_url="endpointUrl",
            max_qps=0,
            public=True,
            remote_hosted=True,
            simulated=True,
        )
        assert_matches_type(GatewayMcpServer, mcp_server, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncFireworks) -> None:
        response = await async_client.accounts.mcp_servers.with_raw_response.create(
            account_id="account_id",
            mcp_server_id="mcpServerId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        mcp_server = await response.parse()
        assert_matches_type(GatewayMcpServer, mcp_server, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncFireworks) -> None:
        async with async_client.accounts.mcp_servers.with_streaming_response.create(
            account_id="account_id",
            mcp_server_id="mcpServerId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            mcp_server = await response.parse()
            assert_matches_type(GatewayMcpServer, mcp_server, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.mcp_servers.with_raw_response.create(
                account_id="",
                mcp_server_id="mcpServerId",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncFireworks) -> None:
        mcp_server = await async_client.accounts.mcp_servers.retrieve(
            mcp_server_id="mcp_server_id",
            account_id="account_id",
        )
        assert_matches_type(GatewayMcpServer, mcp_server, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncFireworks) -> None:
        mcp_server = await async_client.accounts.mcp_servers.retrieve(
            mcp_server_id="mcp_server_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(GatewayMcpServer, mcp_server, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncFireworks) -> None:
        response = await async_client.accounts.mcp_servers.with_raw_response.retrieve(
            mcp_server_id="mcp_server_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        mcp_server = await response.parse()
        assert_matches_type(GatewayMcpServer, mcp_server, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncFireworks) -> None:
        async with async_client.accounts.mcp_servers.with_streaming_response.retrieve(
            mcp_server_id="mcp_server_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            mcp_server = await response.parse()
            assert_matches_type(GatewayMcpServer, mcp_server, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.mcp_servers.with_raw_response.retrieve(
                mcp_server_id="mcp_server_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `mcp_server_id` but received ''"):
            await async_client.accounts.mcp_servers.with_raw_response.retrieve(
                mcp_server_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncFireworks) -> None:
        mcp_server = await async_client.accounts.mcp_servers.update(
            mcp_server_id="mcp_server_id",
            account_id="account_id",
        )
        assert_matches_type(GatewayMcpServer, mcp_server, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncFireworks) -> None:
        mcp_server = await async_client.accounts.mcp_servers.update(
            mcp_server_id="mcp_server_id",
            account_id="account_id",
            annotations={"foo": "string"},
            api_key_secret="apiKeySecret",
            authentication_type="AUTHENTICATION_TYPE_UNSPECIFIED",
            description="description",
            display_name="displayName",
            endpoint_url="endpointUrl",
            max_qps=0,
            public=True,
            remote_hosted=True,
            simulated=True,
        )
        assert_matches_type(GatewayMcpServer, mcp_server, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncFireworks) -> None:
        response = await async_client.accounts.mcp_servers.with_raw_response.update(
            mcp_server_id="mcp_server_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        mcp_server = await response.parse()
        assert_matches_type(GatewayMcpServer, mcp_server, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncFireworks) -> None:
        async with async_client.accounts.mcp_servers.with_streaming_response.update(
            mcp_server_id="mcp_server_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            mcp_server = await response.parse()
            assert_matches_type(GatewayMcpServer, mcp_server, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.mcp_servers.with_raw_response.update(
                mcp_server_id="mcp_server_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `mcp_server_id` but received ''"):
            await async_client.accounts.mcp_servers.with_raw_response.update(
                mcp_server_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncFireworks) -> None:
        mcp_server = await async_client.accounts.mcp_servers.list(
            account_id="account_id",
        )
        assert_matches_type(McpServerListResponse, mcp_server, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncFireworks) -> None:
        mcp_server = await async_client.accounts.mcp_servers.list(
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(McpServerListResponse, mcp_server, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncFireworks) -> None:
        response = await async_client.accounts.mcp_servers.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        mcp_server = await response.parse()
        assert_matches_type(McpServerListResponse, mcp_server, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncFireworks) -> None:
        async with async_client.accounts.mcp_servers.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            mcp_server = await response.parse()
            assert_matches_type(McpServerListResponse, mcp_server, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.mcp_servers.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncFireworks) -> None:
        mcp_server = await async_client.accounts.mcp_servers.delete(
            mcp_server_id="mcp_server_id",
            account_id="account_id",
        )
        assert_matches_type(object, mcp_server, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncFireworks) -> None:
        response = await async_client.accounts.mcp_servers.with_raw_response.delete(
            mcp_server_id="mcp_server_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        mcp_server = await response.parse()
        assert_matches_type(object, mcp_server, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncFireworks) -> None:
        async with async_client.accounts.mcp_servers.with_streaming_response.delete(
            mcp_server_id="mcp_server_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            mcp_server = await response.parse()
            assert_matches_type(object, mcp_server, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.mcp_servers.with_raw_response.delete(
                mcp_server_id="mcp_server_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `mcp_server_id` but received ''"):
            await async_client.accounts.mcp_servers.with_raw_response.delete(
                mcp_server_id="",
                account_id="account_id",
            )
