# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from fireworks_ai import FireworksAI, AsyncFireworksAI
from fireworks_ai.types.accounts import (
    GatewayCluster,
    ClusterListResponse,
    ClusterGetConnectionInfoResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestClusters:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: FireworksAI) -> None:
        cluster = client.accounts.clusters.create(
            account_id="account_id",
            cluster={},
            cluster_id="clusterId",
        )
        assert_matches_type(GatewayCluster, cluster, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: FireworksAI) -> None:
        cluster = client.accounts.clusters.create(
            account_id="account_id",
            cluster={
                "display_name": "displayName",
                "eks_cluster": {
                    "aws_account_id": "awsAccountId",
                    "region": "region",
                    "cluster_name": "clusterName",
                    "fireworks_manager_role": "fireworksManagerRole",
                    "inference_role": "inferenceRole",
                    "load_balancer_controller_role": "loadBalancerControllerRole",
                    "metric_writer_role": "metricWriterRole",
                    "storage_bucket_name": "storageBucketName",
                    "workload_identity_pool_provider_id": "workloadIdentityPoolProviderId",
                },
                "fake_cluster": {
                    "cluster_name": "clusterName",
                    "location": "location",
                    "project_id": "projectId",
                },
            },
            cluster_id="clusterId",
        )
        assert_matches_type(GatewayCluster, cluster, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: FireworksAI) -> None:
        response = client.accounts.clusters.with_raw_response.create(
            account_id="account_id",
            cluster={},
            cluster_id="clusterId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cluster = response.parse()
        assert_matches_type(GatewayCluster, cluster, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: FireworksAI) -> None:
        with client.accounts.clusters.with_streaming_response.create(
            account_id="account_id",
            cluster={},
            cluster_id="clusterId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cluster = response.parse()
            assert_matches_type(GatewayCluster, cluster, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.clusters.with_raw_response.create(
                account_id="",
                cluster={},
                cluster_id="clusterId",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: FireworksAI) -> None:
        cluster = client.accounts.clusters.retrieve(
            cluster_id="cluster_id",
            account_id="account_id",
        )
        assert_matches_type(GatewayCluster, cluster, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: FireworksAI) -> None:
        cluster = client.accounts.clusters.retrieve(
            cluster_id="cluster_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(GatewayCluster, cluster, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: FireworksAI) -> None:
        response = client.accounts.clusters.with_raw_response.retrieve(
            cluster_id="cluster_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cluster = response.parse()
        assert_matches_type(GatewayCluster, cluster, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: FireworksAI) -> None:
        with client.accounts.clusters.with_streaming_response.retrieve(
            cluster_id="cluster_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cluster = response.parse()
            assert_matches_type(GatewayCluster, cluster, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.clusters.with_raw_response.retrieve(
                cluster_id="cluster_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `cluster_id` but received ''"):
            client.accounts.clusters.with_raw_response.retrieve(
                cluster_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: FireworksAI) -> None:
        cluster = client.accounts.clusters.update(
            cluster_id="cluster_id",
            account_id="account_id",
        )
        assert_matches_type(GatewayCluster, cluster, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: FireworksAI) -> None:
        cluster = client.accounts.clusters.update(
            cluster_id="cluster_id",
            account_id="account_id",
            display_name="displayName",
            eks_cluster={
                "aws_account_id": "awsAccountId",
                "region": "region",
                "cluster_name": "clusterName",
                "fireworks_manager_role": "fireworksManagerRole",
                "inference_role": "inferenceRole",
                "load_balancer_controller_role": "loadBalancerControllerRole",
                "metric_writer_role": "metricWriterRole",
                "storage_bucket_name": "storageBucketName",
                "workload_identity_pool_provider_id": "workloadIdentityPoolProviderId",
            },
            fake_cluster={
                "cluster_name": "clusterName",
                "location": "location",
                "project_id": "projectId",
            },
        )
        assert_matches_type(GatewayCluster, cluster, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: FireworksAI) -> None:
        response = client.accounts.clusters.with_raw_response.update(
            cluster_id="cluster_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cluster = response.parse()
        assert_matches_type(GatewayCluster, cluster, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: FireworksAI) -> None:
        with client.accounts.clusters.with_streaming_response.update(
            cluster_id="cluster_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cluster = response.parse()
            assert_matches_type(GatewayCluster, cluster, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.clusters.with_raw_response.update(
                cluster_id="cluster_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `cluster_id` but received ''"):
            client.accounts.clusters.with_raw_response.update(
                cluster_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: FireworksAI) -> None:
        cluster = client.accounts.clusters.list(
            account_id="account_id",
        )
        assert_matches_type(ClusterListResponse, cluster, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: FireworksAI) -> None:
        cluster = client.accounts.clusters.list(
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(ClusterListResponse, cluster, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: FireworksAI) -> None:
        response = client.accounts.clusters.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cluster = response.parse()
        assert_matches_type(ClusterListResponse, cluster, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: FireworksAI) -> None:
        with client.accounts.clusters.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cluster = response.parse()
            assert_matches_type(ClusterListResponse, cluster, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.clusters.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: FireworksAI) -> None:
        cluster = client.accounts.clusters.delete(
            cluster_id="cluster_id",
            account_id="account_id",
        )
        assert_matches_type(object, cluster, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: FireworksAI) -> None:
        response = client.accounts.clusters.with_raw_response.delete(
            cluster_id="cluster_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cluster = response.parse()
        assert_matches_type(object, cluster, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: FireworksAI) -> None:
        with client.accounts.clusters.with_streaming_response.delete(
            cluster_id="cluster_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cluster = response.parse()
            assert_matches_type(object, cluster, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.clusters.with_raw_response.delete(
                cluster_id="cluster_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `cluster_id` but received ''"):
            client.accounts.clusters.with_raw_response.delete(
                cluster_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_connection_info(self, client: FireworksAI) -> None:
        cluster = client.accounts.clusters.get_connection_info(
            cluster_id="cluster_id",
            account_id="account_id",
        )
        assert_matches_type(ClusterGetConnectionInfoResponse, cluster, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_connection_info_with_all_params(self, client: FireworksAI) -> None:
        cluster = client.accounts.clusters.get_connection_info(
            cluster_id="cluster_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(ClusterGetConnectionInfoResponse, cluster, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_connection_info(self, client: FireworksAI) -> None:
        response = client.accounts.clusters.with_raw_response.get_connection_info(
            cluster_id="cluster_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cluster = response.parse()
        assert_matches_type(ClusterGetConnectionInfoResponse, cluster, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_connection_info(self, client: FireworksAI) -> None:
        with client.accounts.clusters.with_streaming_response.get_connection_info(
            cluster_id="cluster_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cluster = response.parse()
            assert_matches_type(ClusterGetConnectionInfoResponse, cluster, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_connection_info(self, client: FireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.clusters.with_raw_response.get_connection_info(
                cluster_id="cluster_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `cluster_id` but received ''"):
            client.accounts.clusters.with_raw_response.get_connection_info(
                cluster_id="",
                account_id="account_id",
            )


class TestAsyncClusters:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncFireworksAI) -> None:
        cluster = await async_client.accounts.clusters.create(
            account_id="account_id",
            cluster={},
            cluster_id="clusterId",
        )
        assert_matches_type(GatewayCluster, cluster, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncFireworksAI) -> None:
        cluster = await async_client.accounts.clusters.create(
            account_id="account_id",
            cluster={
                "display_name": "displayName",
                "eks_cluster": {
                    "aws_account_id": "awsAccountId",
                    "region": "region",
                    "cluster_name": "clusterName",
                    "fireworks_manager_role": "fireworksManagerRole",
                    "inference_role": "inferenceRole",
                    "load_balancer_controller_role": "loadBalancerControllerRole",
                    "metric_writer_role": "metricWriterRole",
                    "storage_bucket_name": "storageBucketName",
                    "workload_identity_pool_provider_id": "workloadIdentityPoolProviderId",
                },
                "fake_cluster": {
                    "cluster_name": "clusterName",
                    "location": "location",
                    "project_id": "projectId",
                },
            },
            cluster_id="clusterId",
        )
        assert_matches_type(GatewayCluster, cluster, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.clusters.with_raw_response.create(
            account_id="account_id",
            cluster={},
            cluster_id="clusterId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cluster = await response.parse()
        assert_matches_type(GatewayCluster, cluster, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.clusters.with_streaming_response.create(
            account_id="account_id",
            cluster={},
            cluster_id="clusterId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cluster = await response.parse()
            assert_matches_type(GatewayCluster, cluster, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.clusters.with_raw_response.create(
                account_id="",
                cluster={},
                cluster_id="clusterId",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncFireworksAI) -> None:
        cluster = await async_client.accounts.clusters.retrieve(
            cluster_id="cluster_id",
            account_id="account_id",
        )
        assert_matches_type(GatewayCluster, cluster, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncFireworksAI) -> None:
        cluster = await async_client.accounts.clusters.retrieve(
            cluster_id="cluster_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(GatewayCluster, cluster, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.clusters.with_raw_response.retrieve(
            cluster_id="cluster_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cluster = await response.parse()
        assert_matches_type(GatewayCluster, cluster, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.clusters.with_streaming_response.retrieve(
            cluster_id="cluster_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cluster = await response.parse()
            assert_matches_type(GatewayCluster, cluster, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.clusters.with_raw_response.retrieve(
                cluster_id="cluster_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `cluster_id` but received ''"):
            await async_client.accounts.clusters.with_raw_response.retrieve(
                cluster_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncFireworksAI) -> None:
        cluster = await async_client.accounts.clusters.update(
            cluster_id="cluster_id",
            account_id="account_id",
        )
        assert_matches_type(GatewayCluster, cluster, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncFireworksAI) -> None:
        cluster = await async_client.accounts.clusters.update(
            cluster_id="cluster_id",
            account_id="account_id",
            display_name="displayName",
            eks_cluster={
                "aws_account_id": "awsAccountId",
                "region": "region",
                "cluster_name": "clusterName",
                "fireworks_manager_role": "fireworksManagerRole",
                "inference_role": "inferenceRole",
                "load_balancer_controller_role": "loadBalancerControllerRole",
                "metric_writer_role": "metricWriterRole",
                "storage_bucket_name": "storageBucketName",
                "workload_identity_pool_provider_id": "workloadIdentityPoolProviderId",
            },
            fake_cluster={
                "cluster_name": "clusterName",
                "location": "location",
                "project_id": "projectId",
            },
        )
        assert_matches_type(GatewayCluster, cluster, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.clusters.with_raw_response.update(
            cluster_id="cluster_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cluster = await response.parse()
        assert_matches_type(GatewayCluster, cluster, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.clusters.with_streaming_response.update(
            cluster_id="cluster_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cluster = await response.parse()
            assert_matches_type(GatewayCluster, cluster, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.clusters.with_raw_response.update(
                cluster_id="cluster_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `cluster_id` but received ''"):
            await async_client.accounts.clusters.with_raw_response.update(
                cluster_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncFireworksAI) -> None:
        cluster = await async_client.accounts.clusters.list(
            account_id="account_id",
        )
        assert_matches_type(ClusterListResponse, cluster, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncFireworksAI) -> None:
        cluster = await async_client.accounts.clusters.list(
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(ClusterListResponse, cluster, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.clusters.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cluster = await response.parse()
        assert_matches_type(ClusterListResponse, cluster, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.clusters.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cluster = await response.parse()
            assert_matches_type(ClusterListResponse, cluster, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.clusters.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncFireworksAI) -> None:
        cluster = await async_client.accounts.clusters.delete(
            cluster_id="cluster_id",
            account_id="account_id",
        )
        assert_matches_type(object, cluster, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.clusters.with_raw_response.delete(
            cluster_id="cluster_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cluster = await response.parse()
        assert_matches_type(object, cluster, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.clusters.with_streaming_response.delete(
            cluster_id="cluster_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cluster = await response.parse()
            assert_matches_type(object, cluster, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.clusters.with_raw_response.delete(
                cluster_id="cluster_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `cluster_id` but received ''"):
            await async_client.accounts.clusters.with_raw_response.delete(
                cluster_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_connection_info(self, async_client: AsyncFireworksAI) -> None:
        cluster = await async_client.accounts.clusters.get_connection_info(
            cluster_id="cluster_id",
            account_id="account_id",
        )
        assert_matches_type(ClusterGetConnectionInfoResponse, cluster, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_connection_info_with_all_params(self, async_client: AsyncFireworksAI) -> None:
        cluster = await async_client.accounts.clusters.get_connection_info(
            cluster_id="cluster_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(ClusterGetConnectionInfoResponse, cluster, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_connection_info(self, async_client: AsyncFireworksAI) -> None:
        response = await async_client.accounts.clusters.with_raw_response.get_connection_info(
            cluster_id="cluster_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cluster = await response.parse()
        assert_matches_type(ClusterGetConnectionInfoResponse, cluster, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_connection_info(self, async_client: AsyncFireworksAI) -> None:
        async with async_client.accounts.clusters.with_streaming_response.get_connection_info(
            cluster_id="cluster_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cluster = await response.parse()
            assert_matches_type(ClusterGetConnectionInfoResponse, cluster, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_connection_info(self, async_client: AsyncFireworksAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.clusters.with_raw_response.get_connection_info(
                cluster_id="cluster_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `cluster_id` but received ''"):
            await async_client.accounts.clusters.with_raw_response.get_connection_info(
                cluster_id="",
                account_id="account_id",
            )
