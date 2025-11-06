# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from fireworks import Fireworks, AsyncFireworks
from tests.utils import assert_matches_type
from fireworks.types import (
    Deployment,
    DeploymentListResponse,
)
from fireworks._utils import parse_datetime

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDeployments:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Fireworks) -> None:
        deployment = client.deployments.create(
            account_id="account_id",
            base_model="baseModel",
        )
        assert_matches_type(Deployment, deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Fireworks) -> None:
        deployment = client.deployments.create(
            account_id="account_id",
            base_model="baseModel",
            deployment_id="deploymentId",
            disable_auto_deploy=True,
            disable_speculative_decoding=True,
            skip_shape_validation=True,
            validate_only=True,
            accelerator_count=0,
            accelerator_type="ACCELERATOR_TYPE_UNSPECIFIED",
            active_model_version="activeModelVersion",
            autoscaling_policy={
                "load_targets": {"foo": 0},
                "scale_down_window": "scaleDownWindow",
                "scale_to_zero_window": "scaleToZeroWindow",
                "scale_up_window": "scaleUpWindow",
            },
            auto_tune={"long_prompt": True},
            deployment_shape="deploymentShape",
            deployment_template="deploymentTemplate",
            description="description",
            direct_route_api_keys=["string"],
            direct_route_type="DIRECT_ROUTE_TYPE_UNSPECIFIED",
            disable_deployment_size_validation=True,
            display_name="displayName",
            draft_model="draftModel",
            draft_token_count=0,
            enable_addons=True,
            enable_hot_reload_latest_addon=True,
            enable_mtp=True,
            enable_session_affinity=True,
            expire_time=parse_datetime("2019-12-27T18:11:19.117Z"),
            max_replica_count=0,
            min_replica_count=0,
            ngram_speculation_length=0,
            placement={
                "multi_region": "MULTI_REGION_UNSPECIFIED",
                "region": "REGION_UNSPECIFIED",
                "regions": ["REGION_UNSPECIFIED"],
            },
            precision="PRECISION_UNSPECIFIED",
        )
        assert_matches_type(Deployment, deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Fireworks) -> None:
        response = client.deployments.with_raw_response.create(
            account_id="account_id",
            base_model="baseModel",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = response.parse()
        assert_matches_type(Deployment, deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Fireworks) -> None:
        with client.deployments.with_streaming_response.create(
            account_id="account_id",
            base_model="baseModel",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = response.parse()
            assert_matches_type(Deployment, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.deployments.with_raw_response.create(
                account_id="",
                base_model="baseModel",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: Fireworks) -> None:
        deployment = client.deployments.update(
            deployment_id="deployment_id",
            account_id="account_id",
            base_model="baseModel",
        )
        assert_matches_type(Deployment, deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: Fireworks) -> None:
        deployment = client.deployments.update(
            deployment_id="deployment_id",
            account_id="account_id",
            base_model="baseModel",
            accelerator_count=0,
            accelerator_type="ACCELERATOR_TYPE_UNSPECIFIED",
            active_model_version="activeModelVersion",
            autoscaling_policy={
                "load_targets": {"foo": 0},
                "scale_down_window": "scaleDownWindow",
                "scale_to_zero_window": "scaleToZeroWindow",
                "scale_up_window": "scaleUpWindow",
            },
            auto_tune={"long_prompt": True},
            deployment_shape="deploymentShape",
            deployment_template="deploymentTemplate",
            description="description",
            direct_route_api_keys=["string"],
            direct_route_type="DIRECT_ROUTE_TYPE_UNSPECIFIED",
            disable_deployment_size_validation=True,
            display_name="displayName",
            draft_model="draftModel",
            draft_token_count=0,
            enable_addons=True,
            enable_hot_reload_latest_addon=True,
            enable_mtp=True,
            enable_session_affinity=True,
            expire_time=parse_datetime("2019-12-27T18:11:19.117Z"),
            max_replica_count=0,
            min_replica_count=0,
            ngram_speculation_length=0,
            placement={
                "multi_region": "MULTI_REGION_UNSPECIFIED",
                "region": "REGION_UNSPECIFIED",
                "regions": ["REGION_UNSPECIFIED"],
            },
            precision="PRECISION_UNSPECIFIED",
        )
        assert_matches_type(Deployment, deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: Fireworks) -> None:
        response = client.deployments.with_raw_response.update(
            deployment_id="deployment_id",
            account_id="account_id",
            base_model="baseModel",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = response.parse()
        assert_matches_type(Deployment, deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: Fireworks) -> None:
        with client.deployments.with_streaming_response.update(
            deployment_id="deployment_id",
            account_id="account_id",
            base_model="baseModel",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = response.parse()
            assert_matches_type(Deployment, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.deployments.with_raw_response.update(
                deployment_id="deployment_id",
                account_id="",
                base_model="baseModel",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_id` but received ''"):
            client.deployments.with_raw_response.update(
                deployment_id="",
                account_id="account_id",
                base_model="baseModel",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Fireworks) -> None:
        deployment = client.deployments.list(
            account_id="account_id",
        )
        assert_matches_type(DeploymentListResponse, deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: Fireworks) -> None:
        deployment = client.deployments.list(
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
            show_deleted=True,
        )
        assert_matches_type(DeploymentListResponse, deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Fireworks) -> None:
        response = client.deployments.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = response.parse()
        assert_matches_type(DeploymentListResponse, deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Fireworks) -> None:
        with client.deployments.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = response.parse()
            assert_matches_type(DeploymentListResponse, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.deployments.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: Fireworks) -> None:
        deployment = client.deployments.delete(
            deployment_id="deployment_id",
            account_id="account_id",
        )
        assert_matches_type(object, deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_with_all_params(self, client: Fireworks) -> None:
        deployment = client.deployments.delete(
            deployment_id="deployment_id",
            account_id="account_id",
            hard=True,
            ignore_checks=True,
        )
        assert_matches_type(object, deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: Fireworks) -> None:
        response = client.deployments.with_raw_response.delete(
            deployment_id="deployment_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = response.parse()
        assert_matches_type(object, deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: Fireworks) -> None:
        with client.deployments.with_streaming_response.delete(
            deployment_id="deployment_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = response.parse()
            assert_matches_type(object, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.deployments.with_raw_response.delete(
                deployment_id="deployment_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_id` but received ''"):
            client.deployments.with_raw_response.delete(
                deployment_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get(self, client: Fireworks) -> None:
        deployment = client.deployments.get(
            deployment_id="deployment_id",
            account_id="account_id",
        )
        assert_matches_type(Deployment, deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_with_all_params(self, client: Fireworks) -> None:
        deployment = client.deployments.get(
            deployment_id="deployment_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(Deployment, deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get(self, client: Fireworks) -> None:
        response = client.deployments.with_raw_response.get(
            deployment_id="deployment_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = response.parse()
        assert_matches_type(Deployment, deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get(self, client: Fireworks) -> None:
        with client.deployments.with_streaming_response.get(
            deployment_id="deployment_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = response.parse()
            assert_matches_type(Deployment, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.deployments.with_raw_response.get(
                deployment_id="deployment_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_id` but received ''"):
            client.deployments.with_raw_response.get(
                deployment_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_undelete(self, client: Fireworks) -> None:
        deployment = client.deployments.undelete(
            deployment_id="deployment_id",
            account_id="account_id",
            body={},
        )
        assert_matches_type(Deployment, deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_undelete(self, client: Fireworks) -> None:
        response = client.deployments.with_raw_response.undelete(
            deployment_id="deployment_id",
            account_id="account_id",
            body={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = response.parse()
        assert_matches_type(Deployment, deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_undelete(self, client: Fireworks) -> None:
        with client.deployments.with_streaming_response.undelete(
            deployment_id="deployment_id",
            account_id="account_id",
            body={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = response.parse()
            assert_matches_type(Deployment, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_undelete(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.deployments.with_raw_response.undelete(
                deployment_id="deployment_id",
                account_id="",
                body={},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_id` but received ''"):
            client.deployments.with_raw_response.undelete(
                deployment_id="",
                account_id="account_id",
                body={},
            )


class TestAsyncDeployments:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncFireworks) -> None:
        deployment = await async_client.deployments.create(
            account_id="account_id",
            base_model="baseModel",
        )
        assert_matches_type(Deployment, deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncFireworks) -> None:
        deployment = await async_client.deployments.create(
            account_id="account_id",
            base_model="baseModel",
            deployment_id="deploymentId",
            disable_auto_deploy=True,
            disable_speculative_decoding=True,
            skip_shape_validation=True,
            validate_only=True,
            accelerator_count=0,
            accelerator_type="ACCELERATOR_TYPE_UNSPECIFIED",
            active_model_version="activeModelVersion",
            autoscaling_policy={
                "load_targets": {"foo": 0},
                "scale_down_window": "scaleDownWindow",
                "scale_to_zero_window": "scaleToZeroWindow",
                "scale_up_window": "scaleUpWindow",
            },
            auto_tune={"long_prompt": True},
            deployment_shape="deploymentShape",
            deployment_template="deploymentTemplate",
            description="description",
            direct_route_api_keys=["string"],
            direct_route_type="DIRECT_ROUTE_TYPE_UNSPECIFIED",
            disable_deployment_size_validation=True,
            display_name="displayName",
            draft_model="draftModel",
            draft_token_count=0,
            enable_addons=True,
            enable_hot_reload_latest_addon=True,
            enable_mtp=True,
            enable_session_affinity=True,
            expire_time=parse_datetime("2019-12-27T18:11:19.117Z"),
            max_replica_count=0,
            min_replica_count=0,
            ngram_speculation_length=0,
            placement={
                "multi_region": "MULTI_REGION_UNSPECIFIED",
                "region": "REGION_UNSPECIFIED",
                "regions": ["REGION_UNSPECIFIED"],
            },
            precision="PRECISION_UNSPECIFIED",
        )
        assert_matches_type(Deployment, deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncFireworks) -> None:
        response = await async_client.deployments.with_raw_response.create(
            account_id="account_id",
            base_model="baseModel",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = await response.parse()
        assert_matches_type(Deployment, deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncFireworks) -> None:
        async with async_client.deployments.with_streaming_response.create(
            account_id="account_id",
            base_model="baseModel",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = await response.parse()
            assert_matches_type(Deployment, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.deployments.with_raw_response.create(
                account_id="",
                base_model="baseModel",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncFireworks) -> None:
        deployment = await async_client.deployments.update(
            deployment_id="deployment_id",
            account_id="account_id",
            base_model="baseModel",
        )
        assert_matches_type(Deployment, deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncFireworks) -> None:
        deployment = await async_client.deployments.update(
            deployment_id="deployment_id",
            account_id="account_id",
            base_model="baseModel",
            accelerator_count=0,
            accelerator_type="ACCELERATOR_TYPE_UNSPECIFIED",
            active_model_version="activeModelVersion",
            autoscaling_policy={
                "load_targets": {"foo": 0},
                "scale_down_window": "scaleDownWindow",
                "scale_to_zero_window": "scaleToZeroWindow",
                "scale_up_window": "scaleUpWindow",
            },
            auto_tune={"long_prompt": True},
            deployment_shape="deploymentShape",
            deployment_template="deploymentTemplate",
            description="description",
            direct_route_api_keys=["string"],
            direct_route_type="DIRECT_ROUTE_TYPE_UNSPECIFIED",
            disable_deployment_size_validation=True,
            display_name="displayName",
            draft_model="draftModel",
            draft_token_count=0,
            enable_addons=True,
            enable_hot_reload_latest_addon=True,
            enable_mtp=True,
            enable_session_affinity=True,
            expire_time=parse_datetime("2019-12-27T18:11:19.117Z"),
            max_replica_count=0,
            min_replica_count=0,
            ngram_speculation_length=0,
            placement={
                "multi_region": "MULTI_REGION_UNSPECIFIED",
                "region": "REGION_UNSPECIFIED",
                "regions": ["REGION_UNSPECIFIED"],
            },
            precision="PRECISION_UNSPECIFIED",
        )
        assert_matches_type(Deployment, deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncFireworks) -> None:
        response = await async_client.deployments.with_raw_response.update(
            deployment_id="deployment_id",
            account_id="account_id",
            base_model="baseModel",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = await response.parse()
        assert_matches_type(Deployment, deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncFireworks) -> None:
        async with async_client.deployments.with_streaming_response.update(
            deployment_id="deployment_id",
            account_id="account_id",
            base_model="baseModel",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = await response.parse()
            assert_matches_type(Deployment, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.deployments.with_raw_response.update(
                deployment_id="deployment_id",
                account_id="",
                base_model="baseModel",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_id` but received ''"):
            await async_client.deployments.with_raw_response.update(
                deployment_id="",
                account_id="account_id",
                base_model="baseModel",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncFireworks) -> None:
        deployment = await async_client.deployments.list(
            account_id="account_id",
        )
        assert_matches_type(DeploymentListResponse, deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncFireworks) -> None:
        deployment = await async_client.deployments.list(
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
            show_deleted=True,
        )
        assert_matches_type(DeploymentListResponse, deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncFireworks) -> None:
        response = await async_client.deployments.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = await response.parse()
        assert_matches_type(DeploymentListResponse, deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncFireworks) -> None:
        async with async_client.deployments.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = await response.parse()
            assert_matches_type(DeploymentListResponse, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.deployments.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncFireworks) -> None:
        deployment = await async_client.deployments.delete(
            deployment_id="deployment_id",
            account_id="account_id",
        )
        assert_matches_type(object, deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_with_all_params(self, async_client: AsyncFireworks) -> None:
        deployment = await async_client.deployments.delete(
            deployment_id="deployment_id",
            account_id="account_id",
            hard=True,
            ignore_checks=True,
        )
        assert_matches_type(object, deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncFireworks) -> None:
        response = await async_client.deployments.with_raw_response.delete(
            deployment_id="deployment_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = await response.parse()
        assert_matches_type(object, deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncFireworks) -> None:
        async with async_client.deployments.with_streaming_response.delete(
            deployment_id="deployment_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = await response.parse()
            assert_matches_type(object, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.deployments.with_raw_response.delete(
                deployment_id="deployment_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_id` but received ''"):
            await async_client.deployments.with_raw_response.delete(
                deployment_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get(self, async_client: AsyncFireworks) -> None:
        deployment = await async_client.deployments.get(
            deployment_id="deployment_id",
            account_id="account_id",
        )
        assert_matches_type(Deployment, deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_with_all_params(self, async_client: AsyncFireworks) -> None:
        deployment = await async_client.deployments.get(
            deployment_id="deployment_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(Deployment, deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncFireworks) -> None:
        response = await async_client.deployments.with_raw_response.get(
            deployment_id="deployment_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = await response.parse()
        assert_matches_type(Deployment, deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncFireworks) -> None:
        async with async_client.deployments.with_streaming_response.get(
            deployment_id="deployment_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = await response.parse()
            assert_matches_type(Deployment, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.deployments.with_raw_response.get(
                deployment_id="deployment_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_id` but received ''"):
            await async_client.deployments.with_raw_response.get(
                deployment_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_undelete(self, async_client: AsyncFireworks) -> None:
        deployment = await async_client.deployments.undelete(
            deployment_id="deployment_id",
            account_id="account_id",
            body={},
        )
        assert_matches_type(Deployment, deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_undelete(self, async_client: AsyncFireworks) -> None:
        response = await async_client.deployments.with_raw_response.undelete(
            deployment_id="deployment_id",
            account_id="account_id",
            body={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = await response.parse()
        assert_matches_type(Deployment, deployment, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_undelete(self, async_client: AsyncFireworks) -> None:
        async with async_client.deployments.with_streaming_response.undelete(
            deployment_id="deployment_id",
            account_id="account_id",
            body={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = await response.parse()
            assert_matches_type(Deployment, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_undelete(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.deployments.with_raw_response.undelete(
                deployment_id="deployment_id",
                account_id="",
                body={},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_id` but received ''"):
            await async_client.deployments.with_raw_response.undelete(
                deployment_id="",
                account_id="account_id",
                body={},
            )
