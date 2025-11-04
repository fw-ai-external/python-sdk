# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from fireworks_ai import FireworksAI, AsyncFireworksAI
from fireworks_ai.types.accounts import (
    GatewayNodePool,
    GatewayNodePoolStats,
    NodePoolRetrieveNodePoolsResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestNodePools:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: FireworksAI) -> None:
        node_pool = client.accounts.node_pools.retrieve(
            node_pool_id="node_pool_id",
            account_id="account_id",
        )
        assert_matches_type(GatewayNodePool, node_pool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: FireworksAI) -> None:
        node_pool = client.accounts.node_pools.retrieve(
            node_pool_id="node_pool_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(GatewayNodePool, node_pool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: FireworksAI) -> None:
        response = client.accounts.node_pools.with_raw_response.retrieve(
            node_pool_id="node_pool_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        node_pool = response.parse()
        assert_matches_type(GatewayNodePool, node_pool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: FireworksAI) -> None:
        with client.accounts.node_pools.with_streaming_response.retrieve(
            node_pool_id="node_pool_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            node_pool = response.parse()
            assert_matches_type(GatewayNodePool, node_pool, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.node_pools.with_raw_response.retrieve(
                node_pool_id="node_pool_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `node_pool_id` but received ''"):
            client.accounts.node_pools.with_raw_response.retrieve(
                node_pool_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: FireworksAI) -> None:
        node_pool = client.accounts.node_pools.update(
            node_pool_id="node_pool_id",
            account_id="account_id",
        )
        assert_matches_type(GatewayNodePool, node_pool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: FireworksAI) -> None:
        node_pool = client.accounts.node_pools.update(
            node_pool_id="node_pool_id",
            account_id="account_id",
            annotations={"foo": "string"},
            display_name="displayName",
            eks_node_pool={
                "instance_type": "instanceType",
                "launch_template": "launchTemplate",
                "node_group_name": "nodeGroupName",
                "node_role": "nodeRole",
                "placement_group": "placementGroup",
                "spot": True,
                "subnet_ids": ["string"],
                "zone": "zone",
            },
            fake_node_pool={
                "machine_type": "machineType",
                "num_nodes": 0,
                "service_account": "serviceAccount",
            },
            max_node_count=0,
            min_node_count=0,
            overprovision_node_count=0,
        )
        assert_matches_type(GatewayNodePool, node_pool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: FireworksAI) -> None:
        response = client.accounts.node_pools.with_raw_response.update(
            node_pool_id="node_pool_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        node_pool = response.parse()
        assert_matches_type(GatewayNodePool, node_pool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: FireworksAI) -> None:
        with client.accounts.node_pools.with_streaming_response.update(
            node_pool_id="node_pool_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            node_pool = response.parse()
            assert_matches_type(GatewayNodePool, node_pool, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.node_pools.with_raw_response.update(
                node_pool_id="node_pool_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `node_pool_id` but received ''"):
            client.accounts.node_pools.with_raw_response.update(
                node_pool_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: FireworksAI) -> None:
        node_pool = client.accounts.node_pools.delete(
            node_pool_id="node_pool_id",
            account_id="account_id",
        )
        assert_matches_type(object, node_pool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: FireworksAI) -> None:
        response = client.accounts.node_pools.with_raw_response.delete(
            node_pool_id="node_pool_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        node_pool = response.parse()
        assert_matches_type(object, node_pool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: FireworksAI) -> None:
        with client.accounts.node_pools.with_streaming_response.delete(
            node_pool_id="node_pool_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            node_pool = response.parse()
            assert_matches_type(object, node_pool, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.node_pools.with_raw_response.delete(
                node_pool_id="node_pool_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `node_pool_id` but received ''"):
            client.accounts.node_pools.with_raw_response.delete(
                node_pool_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_node_pools(self, client: FireworksAI) -> None:
        node_pool = client.accounts.node_pools.node_pools(
            account_id="account_id",
            node_pool={},
            node_pool_id="nodePoolId",
        )
        assert_matches_type(GatewayNodePool, node_pool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_node_pools_with_all_params(self, client: FireworksAI) -> None:
        node_pool = client.accounts.node_pools.node_pools(
            account_id="account_id",
            node_pool={
                "annotations": {"foo": "string"},
                "display_name": "displayName",
                "eks_node_pool": {
                    "instance_type": "instanceType",
                    "launch_template": "launchTemplate",
                    "node_group_name": "nodeGroupName",
                    "node_role": "nodeRole",
                    "placement_group": "placementGroup",
                    "spot": True,
                    "subnet_ids": ["string"],
                    "zone": "zone",
                },
                "fake_node_pool": {
                    "machine_type": "machineType",
                    "num_nodes": 0,
                    "service_account": "serviceAccount",
                },
                "max_node_count": 0,
                "min_node_count": 0,
                "overprovision_node_count": 0,
            },
            node_pool_id="nodePoolId",
        )
        assert_matches_type(GatewayNodePool, node_pool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_node_pools(self, client: FireworksAI) -> None:
        response = client.accounts.node_pools.with_raw_response.node_pools(
            account_id="account_id",
            node_pool={},
            node_pool_id="nodePoolId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        node_pool = response.parse()
        assert_matches_type(GatewayNodePool, node_pool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_node_pools(self, client: FireworksAI) -> None:
        with client.accounts.node_pools.with_streaming_response.node_pools(
            account_id="account_id",
            node_pool={},
            node_pool_id="nodePoolId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            node_pool = response.parse()
            assert_matches_type(GatewayNodePool, node_pool, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_node_pools(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.node_pools.with_raw_response.node_pools(
                account_id="",
                node_pool={},
                node_pool_id="nodePoolId",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_node_pool_id_get_stats(self, client: FireworksAI) -> None:
        node_pool = client.accounts.node_pools.retrieve_node_pool_id_get_stats(
            node_pool_id="node_pool_id",
            account_id="account_id",
        )
        assert_matches_type(GatewayNodePoolStats, node_pool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_node_pool_id_get_stats_with_all_params(self, client: FireworksAI) -> None:
        node_pool = client.accounts.node_pools.retrieve_node_pool_id_get_stats(
            node_pool_id="node_pool_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(GatewayNodePoolStats, node_pool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_node_pool_id_get_stats(self, client: FireworksAI) -> None:
        response = client.accounts.node_pools.with_raw_response.retrieve_node_pool_id_get_stats(
            node_pool_id="node_pool_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        node_pool = response.parse()
        assert_matches_type(GatewayNodePoolStats, node_pool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_node_pool_id_get_stats(self, client: FireworksAI) -> None:
        with client.accounts.node_pools.with_streaming_response.retrieve_node_pool_id_get_stats(
            node_pool_id="node_pool_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            node_pool = response.parse()
            assert_matches_type(GatewayNodePoolStats, node_pool, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve_node_pool_id_get_stats(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.node_pools.with_raw_response.retrieve_node_pool_id_get_stats(
                node_pool_id="node_pool_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `node_pool_id` but received ''"):
            client.accounts.node_pools.with_raw_response.retrieve_node_pool_id_get_stats(
                node_pool_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_node_pools(self, client: FireworksAI) -> None:
        node_pool = client.accounts.node_pools.retrieve_node_pools(
            account_id="account_id",
        )
        assert_matches_type(NodePoolRetrieveNodePoolsResponse, node_pool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_node_pools_with_all_params(self, client: FireworksAI) -> None:
        node_pool = client.accounts.node_pools.retrieve_node_pools(
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(NodePoolRetrieveNodePoolsResponse, node_pool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_node_pools(self, client: FireworksAI) -> None:
        response = client.accounts.node_pools.with_raw_response.retrieve_node_pools(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        node_pool = response.parse()
        assert_matches_type(NodePoolRetrieveNodePoolsResponse, node_pool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_node_pools(self, client: FireworksAI) -> None:
        with client.accounts.node_pools.with_streaming_response.retrieve_node_pools(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            node_pool = response.parse()
            assert_matches_type(NodePoolRetrieveNodePoolsResponse, node_pool, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve_node_pools(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.node_pools.with_raw_response.retrieve_node_pools(
                account_id="",
            )


class TestAsyncNodePools:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncFireworksAI) -> None:
        node_pool = await async_client.accounts.node_pools.retrieve(
            node_pool_id="node_pool_id",
            account_id="account_id",
        )
        assert_matches_type(GatewayNodePool, node_pool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncFireworksAI) -> None:
        node_pool = await async_client.accounts.node_pools.retrieve(
            node_pool_id="node_pool_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(GatewayNodePool, node_pool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.node_pools.with_raw_response.retrieve(
            node_pool_id="node_pool_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        node_pool = await response.parse()
        assert_matches_type(GatewayNodePool, node_pool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.node_pools.with_streaming_response.retrieve(
            node_pool_id="node_pool_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            node_pool = await response.parse()
            assert_matches_type(GatewayNodePool, node_pool, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.node_pools.with_raw_response.retrieve(
                node_pool_id="node_pool_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `node_pool_id` but received ''"):
            await async_client.accounts.node_pools.with_raw_response.retrieve(
                node_pool_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncFireworksAI) -> None:
        node_pool = await async_client.accounts.node_pools.update(
            node_pool_id="node_pool_id",
            account_id="account_id",
        )
        assert_matches_type(GatewayNodePool, node_pool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncFireworksAI) -> None:
        node_pool = await async_client.accounts.node_pools.update(
            node_pool_id="node_pool_id",
            account_id="account_id",
            annotations={"foo": "string"},
            display_name="displayName",
            eks_node_pool={
                "instance_type": "instanceType",
                "launch_template": "launchTemplate",
                "node_group_name": "nodeGroupName",
                "node_role": "nodeRole",
                "placement_group": "placementGroup",
                "spot": True,
                "subnet_ids": ["string"],
                "zone": "zone",
            },
            fake_node_pool={
                "machine_type": "machineType",
                "num_nodes": 0,
                "service_account": "serviceAccount",
            },
            max_node_count=0,
            min_node_count=0,
            overprovision_node_count=0,
        )
        assert_matches_type(GatewayNodePool, node_pool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.node_pools.with_raw_response.update(
            node_pool_id="node_pool_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        node_pool = await response.parse()
        assert_matches_type(GatewayNodePool, node_pool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.node_pools.with_streaming_response.update(
            node_pool_id="node_pool_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            node_pool = await response.parse()
            assert_matches_type(GatewayNodePool, node_pool, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.node_pools.with_raw_response.update(
                node_pool_id="node_pool_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `node_pool_id` but received ''"):
            await async_client.accounts.node_pools.with_raw_response.update(
                node_pool_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncFireworksAI) -> None:
        node_pool = await async_client.accounts.node_pools.delete(
            node_pool_id="node_pool_id",
            account_id="account_id",
        )
        assert_matches_type(object, node_pool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.node_pools.with_raw_response.delete(
            node_pool_id="node_pool_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        node_pool = await response.parse()
        assert_matches_type(object, node_pool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.node_pools.with_streaming_response.delete(
            node_pool_id="node_pool_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            node_pool = await response.parse()
            assert_matches_type(object, node_pool, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.node_pools.with_raw_response.delete(
                node_pool_id="node_pool_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `node_pool_id` but received ''"):
            await async_client.accounts.node_pools.with_raw_response.delete(
                node_pool_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_node_pools(self, async_client: AsyncFireworksAI) -> None:
        node_pool = await async_client.accounts.node_pools.node_pools(
            account_id="account_id",
            node_pool={},
            node_pool_id="nodePoolId",
        )
        assert_matches_type(GatewayNodePool, node_pool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_node_pools_with_all_params(self, async_client: AsyncFireworksAI) -> None:
        node_pool = await async_client.accounts.node_pools.node_pools(
            account_id="account_id",
            node_pool={
                "annotations": {"foo": "string"},
                "display_name": "displayName",
                "eks_node_pool": {
                    "instance_type": "instanceType",
                    "launch_template": "launchTemplate",
                    "node_group_name": "nodeGroupName",
                    "node_role": "nodeRole",
                    "placement_group": "placementGroup",
                    "spot": True,
                    "subnet_ids": ["string"],
                    "zone": "zone",
                },
                "fake_node_pool": {
                    "machine_type": "machineType",
                    "num_nodes": 0,
                    "service_account": "serviceAccount",
                },
                "max_node_count": 0,
                "min_node_count": 0,
                "overprovision_node_count": 0,
            },
            node_pool_id="nodePoolId",
        )
        assert_matches_type(GatewayNodePool, node_pool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_node_pools(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.node_pools.with_raw_response.node_pools(
            account_id="account_id",
            node_pool={},
            node_pool_id="nodePoolId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        node_pool = await response.parse()
        assert_matches_type(GatewayNodePool, node_pool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_node_pools(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.node_pools.with_streaming_response.node_pools(
            account_id="account_id",
            node_pool={},
            node_pool_id="nodePoolId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            node_pool = await response.parse()
            assert_matches_type(GatewayNodePool, node_pool, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_node_pools(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.node_pools.with_raw_response.node_pools(
                account_id="",
                node_pool={},
                node_pool_id="nodePoolId",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_node_pool_id_get_stats(self, async_client: AsyncFireworksAI) -> None:
        node_pool = await async_client.accounts.node_pools.retrieve_node_pool_id_get_stats(
            node_pool_id="node_pool_id",
            account_id="account_id",
        )
        assert_matches_type(GatewayNodePoolStats, node_pool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_node_pool_id_get_stats_with_all_params(self, async_client: AsyncFireworksAI) -> None:
        node_pool = await async_client.accounts.node_pools.retrieve_node_pool_id_get_stats(
            node_pool_id="node_pool_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(GatewayNodePoolStats, node_pool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_node_pool_id_get_stats(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.node_pools.with_raw_response.retrieve_node_pool_id_get_stats(
            node_pool_id="node_pool_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        node_pool = await response.parse()
        assert_matches_type(GatewayNodePoolStats, node_pool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_node_pool_id_get_stats(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.node_pools.with_streaming_response.retrieve_node_pool_id_get_stats(
            node_pool_id="node_pool_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            node_pool = await response.parse()
            assert_matches_type(GatewayNodePoolStats, node_pool, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve_node_pool_id_get_stats(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.node_pools.with_raw_response.retrieve_node_pool_id_get_stats(
                node_pool_id="node_pool_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `node_pool_id` but received ''"):
            await async_client.accounts.node_pools.with_raw_response.retrieve_node_pool_id_get_stats(
                node_pool_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_node_pools(self, async_client: AsyncFireworksAI) -> None:
        node_pool = await async_client.accounts.node_pools.retrieve_node_pools(
            account_id="account_id",
        )
        assert_matches_type(NodePoolRetrieveNodePoolsResponse, node_pool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_node_pools_with_all_params(self, async_client: AsyncFireworksAI) -> None:
        node_pool = await async_client.accounts.node_pools.retrieve_node_pools(
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(NodePoolRetrieveNodePoolsResponse, node_pool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_node_pools(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.node_pools.with_raw_response.retrieve_node_pools(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        node_pool = await response.parse()
        assert_matches_type(NodePoolRetrieveNodePoolsResponse, node_pool, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_node_pools(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.node_pools.with_streaming_response.retrieve_node_pools(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            node_pool = await response.parse()
            assert_matches_type(NodePoolRetrieveNodePoolsResponse, node_pool, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve_node_pools(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.node_pools.with_raw_response.retrieve_node_pools(
                account_id="",
            )
