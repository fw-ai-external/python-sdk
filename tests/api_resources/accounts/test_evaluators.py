# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from fireworks_ai import Fireworks, AsyncFireworks
from fireworks_ai.types.accounts import (
    GatewayEvaluator,
    EvaluatorListResponse,
    EvaluatorGetUploadEndpointResponse,
    EvaluatorGetBuildLogEndpointResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestEvaluators:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Fireworks) -> None:
        evaluator = client.accounts.evaluators.create(
            account_id="account_id",
            evaluator={},
        )
        assert_matches_type(GatewayEvaluator, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Fireworks) -> None:
        evaluator = client.accounts.evaluators.create(
            account_id="account_id",
            evaluator={
                "commit_hash": "commitHash",
                "criteria": [
                    {
                        "code_snippets": {
                            "entry_file": "entryFile",
                            "entry_func": "entryFunc",
                            "file_contents": {"foo": "string"},
                            "language": "language",
                        },
                        "description": "description",
                        "name": "name",
                        "type": "TYPE_UNSPECIFIED",
                    }
                ],
                "description": "description",
                "display_name": "displayName",
                "entry_point": "entryPoint",
                "multi_metrics": True,
                "requirements": "requirements",
                "rollup_settings": {
                    "criteria_weights": {"foo": 0},
                    "python_code": "pythonCode",
                    "skip_rollup": True,
                    "success_threshold": 0,
                },
            },
            evaluator_id="evaluatorId",
        )
        assert_matches_type(GatewayEvaluator, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Fireworks) -> None:
        response = client.accounts.evaluators.with_raw_response.create(
            account_id="account_id",
            evaluator={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluator = response.parse()
        assert_matches_type(GatewayEvaluator, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Fireworks) -> None:
        with client.accounts.evaluators.with_streaming_response.create(
            account_id="account_id",
            evaluator={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluator = response.parse()
            assert_matches_type(GatewayEvaluator, evaluator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.evaluators.with_raw_response.create(
                account_id="",
                evaluator={},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: Fireworks) -> None:
        evaluator = client.accounts.evaluators.retrieve(
            evaluator_id="evaluator_id",
            account_id="account_id",
        )
        assert_matches_type(GatewayEvaluator, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: Fireworks) -> None:
        evaluator = client.accounts.evaluators.retrieve(
            evaluator_id="evaluator_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(GatewayEvaluator, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: Fireworks) -> None:
        response = client.accounts.evaluators.with_raw_response.retrieve(
            evaluator_id="evaluator_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluator = response.parse()
        assert_matches_type(GatewayEvaluator, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: Fireworks) -> None:
        with client.accounts.evaluators.with_streaming_response.retrieve(
            evaluator_id="evaluator_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluator = response.parse()
            assert_matches_type(GatewayEvaluator, evaluator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.evaluators.with_raw_response.retrieve(
                evaluator_id="evaluator_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluator_id` but received ''"):
            client.accounts.evaluators.with_raw_response.retrieve(
                evaluator_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Fireworks) -> None:
        evaluator = client.accounts.evaluators.list(
            account_id="account_id",
        )
        assert_matches_type(EvaluatorListResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: Fireworks) -> None:
        evaluator = client.accounts.evaluators.list(
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(EvaluatorListResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Fireworks) -> None:
        response = client.accounts.evaluators.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluator = response.parse()
        assert_matches_type(EvaluatorListResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Fireworks) -> None:
        with client.accounts.evaluators.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluator = response.parse()
            assert_matches_type(EvaluatorListResponse, evaluator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.evaluators.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: Fireworks) -> None:
        evaluator = client.accounts.evaluators.delete(
            evaluator_id="evaluator_id",
            account_id="account_id",
        )
        assert_matches_type(object, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: Fireworks) -> None:
        response = client.accounts.evaluators.with_raw_response.delete(
            evaluator_id="evaluator_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluator = response.parse()
        assert_matches_type(object, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: Fireworks) -> None:
        with client.accounts.evaluators.with_streaming_response.delete(
            evaluator_id="evaluator_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluator = response.parse()
            assert_matches_type(object, evaluator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.evaluators.with_raw_response.delete(
                evaluator_id="evaluator_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluator_id` but received ''"):
            client.accounts.evaluators.with_raw_response.delete(
                evaluator_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_build_log_endpoint(self, client: Fireworks) -> None:
        evaluator = client.accounts.evaluators.get_build_log_endpoint(
            evaluator_id="evaluator_id",
            account_id="account_id",
        )
        assert_matches_type(EvaluatorGetBuildLogEndpointResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_build_log_endpoint_with_all_params(self, client: Fireworks) -> None:
        evaluator = client.accounts.evaluators.get_build_log_endpoint(
            evaluator_id="evaluator_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(EvaluatorGetBuildLogEndpointResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_build_log_endpoint(self, client: Fireworks) -> None:
        response = client.accounts.evaluators.with_raw_response.get_build_log_endpoint(
            evaluator_id="evaluator_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluator = response.parse()
        assert_matches_type(EvaluatorGetBuildLogEndpointResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_build_log_endpoint(self, client: Fireworks) -> None:
        with client.accounts.evaluators.with_streaming_response.get_build_log_endpoint(
            evaluator_id="evaluator_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluator = response.parse()
            assert_matches_type(EvaluatorGetBuildLogEndpointResponse, evaluator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_build_log_endpoint(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.evaluators.with_raw_response.get_build_log_endpoint(
                evaluator_id="evaluator_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluator_id` but received ''"):
            client.accounts.evaluators.with_raw_response.get_build_log_endpoint(
                evaluator_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_upload_endpoint(self, client: Fireworks) -> None:
        evaluator = client.accounts.evaluators.get_upload_endpoint(
            evaluator_id="evaluator_id",
            account_id="account_id",
            filename_to_size={"foo": "string"},
        )
        assert_matches_type(EvaluatorGetUploadEndpointResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_upload_endpoint_with_all_params(self, client: Fireworks) -> None:
        evaluator = client.accounts.evaluators.get_upload_endpoint(
            evaluator_id="evaluator_id",
            account_id="account_id",
            filename_to_size={"foo": "string"},
            read_mask="readMask",
        )
        assert_matches_type(EvaluatorGetUploadEndpointResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_upload_endpoint(self, client: Fireworks) -> None:
        response = client.accounts.evaluators.with_raw_response.get_upload_endpoint(
            evaluator_id="evaluator_id",
            account_id="account_id",
            filename_to_size={"foo": "string"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluator = response.parse()
        assert_matches_type(EvaluatorGetUploadEndpointResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_upload_endpoint(self, client: Fireworks) -> None:
        with client.accounts.evaluators.with_streaming_response.get_upload_endpoint(
            evaluator_id="evaluator_id",
            account_id="account_id",
            filename_to_size={"foo": "string"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluator = response.parse()
            assert_matches_type(EvaluatorGetUploadEndpointResponse, evaluator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_upload_endpoint(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.evaluators.with_raw_response.get_upload_endpoint(
                evaluator_id="evaluator_id",
                account_id="",
                filename_to_size={"foo": "string"},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluator_id` but received ''"):
            client.accounts.evaluators.with_raw_response.get_upload_endpoint(
                evaluator_id="",
                account_id="account_id",
                filename_to_size={"foo": "string"},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_validate_upload(self, client: Fireworks) -> None:
        evaluator = client.accounts.evaluators.validate_upload(
            evaluator_id="evaluator_id",
            account_id="account_id",
            body={},
        )
        assert_matches_type(object, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_validate_upload(self, client: Fireworks) -> None:
        response = client.accounts.evaluators.with_raw_response.validate_upload(
            evaluator_id="evaluator_id",
            account_id="account_id",
            body={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluator = response.parse()
        assert_matches_type(object, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_validate_upload(self, client: Fireworks) -> None:
        with client.accounts.evaluators.with_streaming_response.validate_upload(
            evaluator_id="evaluator_id",
            account_id="account_id",
            body={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluator = response.parse()
            assert_matches_type(object, evaluator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_validate_upload(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.evaluators.with_raw_response.validate_upload(
                evaluator_id="evaluator_id",
                account_id="",
                body={},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluator_id` but received ''"):
            client.accounts.evaluators.with_raw_response.validate_upload(
                evaluator_id="",
                account_id="account_id",
                body={},
            )


class TestAsyncEvaluators:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncFireworks) -> None:
        evaluator = await async_client.accounts.evaluators.create(
            account_id="account_id",
            evaluator={},
        )
        assert_matches_type(GatewayEvaluator, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncFireworks) -> None:
        evaluator = await async_client.accounts.evaluators.create(
            account_id="account_id",
            evaluator={
                "commit_hash": "commitHash",
                "criteria": [
                    {
                        "code_snippets": {
                            "entry_file": "entryFile",
                            "entry_func": "entryFunc",
                            "file_contents": {"foo": "string"},
                            "language": "language",
                        },
                        "description": "description",
                        "name": "name",
                        "type": "TYPE_UNSPECIFIED",
                    }
                ],
                "description": "description",
                "display_name": "displayName",
                "entry_point": "entryPoint",
                "multi_metrics": True,
                "requirements": "requirements",
                "rollup_settings": {
                    "criteria_weights": {"foo": 0},
                    "python_code": "pythonCode",
                    "skip_rollup": True,
                    "success_threshold": 0,
                },
            },
            evaluator_id="evaluatorId",
        )
        assert_matches_type(GatewayEvaluator, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncFireworks) -> None:
        response = await async_client.accounts.evaluators.with_raw_response.create(
            account_id="account_id",
            evaluator={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluator = await response.parse()
        assert_matches_type(GatewayEvaluator, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncFireworks) -> None:
        async with async_client.accounts.evaluators.with_streaming_response.create(
            account_id="account_id",
            evaluator={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluator = await response.parse()
            assert_matches_type(GatewayEvaluator, evaluator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.evaluators.with_raw_response.create(
                account_id="",
                evaluator={},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncFireworks) -> None:
        evaluator = await async_client.accounts.evaluators.retrieve(
            evaluator_id="evaluator_id",
            account_id="account_id",
        )
        assert_matches_type(GatewayEvaluator, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncFireworks) -> None:
        evaluator = await async_client.accounts.evaluators.retrieve(
            evaluator_id="evaluator_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(GatewayEvaluator, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncFireworks) -> None:
        response = await async_client.accounts.evaluators.with_raw_response.retrieve(
            evaluator_id="evaluator_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluator = await response.parse()
        assert_matches_type(GatewayEvaluator, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncFireworks) -> None:
        async with async_client.accounts.evaluators.with_streaming_response.retrieve(
            evaluator_id="evaluator_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluator = await response.parse()
            assert_matches_type(GatewayEvaluator, evaluator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.evaluators.with_raw_response.retrieve(
                evaluator_id="evaluator_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluator_id` but received ''"):
            await async_client.accounts.evaluators.with_raw_response.retrieve(
                evaluator_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncFireworks) -> None:
        evaluator = await async_client.accounts.evaluators.list(
            account_id="account_id",
        )
        assert_matches_type(EvaluatorListResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncFireworks) -> None:
        evaluator = await async_client.accounts.evaluators.list(
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(EvaluatorListResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncFireworks) -> None:
        response = await async_client.accounts.evaluators.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluator = await response.parse()
        assert_matches_type(EvaluatorListResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncFireworks) -> None:
        async with async_client.accounts.evaluators.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluator = await response.parse()
            assert_matches_type(EvaluatorListResponse, evaluator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.evaluators.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncFireworks) -> None:
        evaluator = await async_client.accounts.evaluators.delete(
            evaluator_id="evaluator_id",
            account_id="account_id",
        )
        assert_matches_type(object, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncFireworks) -> None:
        response = await async_client.accounts.evaluators.with_raw_response.delete(
            evaluator_id="evaluator_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluator = await response.parse()
        assert_matches_type(object, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncFireworks) -> None:
        async with async_client.accounts.evaluators.with_streaming_response.delete(
            evaluator_id="evaluator_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluator = await response.parse()
            assert_matches_type(object, evaluator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.evaluators.with_raw_response.delete(
                evaluator_id="evaluator_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluator_id` but received ''"):
            await async_client.accounts.evaluators.with_raw_response.delete(
                evaluator_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_build_log_endpoint(self, async_client: AsyncFireworks) -> None:
        evaluator = await async_client.accounts.evaluators.get_build_log_endpoint(
            evaluator_id="evaluator_id",
            account_id="account_id",
        )
        assert_matches_type(EvaluatorGetBuildLogEndpointResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_build_log_endpoint_with_all_params(self, async_client: AsyncFireworks) -> None:
        evaluator = await async_client.accounts.evaluators.get_build_log_endpoint(
            evaluator_id="evaluator_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(EvaluatorGetBuildLogEndpointResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_build_log_endpoint(self, async_client: AsyncFireworks) -> None:
        response = await async_client.accounts.evaluators.with_raw_response.get_build_log_endpoint(
            evaluator_id="evaluator_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluator = await response.parse()
        assert_matches_type(EvaluatorGetBuildLogEndpointResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_build_log_endpoint(self, async_client: AsyncFireworks) -> None:
        async with async_client.accounts.evaluators.with_streaming_response.get_build_log_endpoint(
            evaluator_id="evaluator_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluator = await response.parse()
            assert_matches_type(EvaluatorGetBuildLogEndpointResponse, evaluator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_build_log_endpoint(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.evaluators.with_raw_response.get_build_log_endpoint(
                evaluator_id="evaluator_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluator_id` but received ''"):
            await async_client.accounts.evaluators.with_raw_response.get_build_log_endpoint(
                evaluator_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_upload_endpoint(self, async_client: AsyncFireworks) -> None:
        evaluator = await async_client.accounts.evaluators.get_upload_endpoint(
            evaluator_id="evaluator_id",
            account_id="account_id",
            filename_to_size={"foo": "string"},
        )
        assert_matches_type(EvaluatorGetUploadEndpointResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_upload_endpoint_with_all_params(self, async_client: AsyncFireworks) -> None:
        evaluator = await async_client.accounts.evaluators.get_upload_endpoint(
            evaluator_id="evaluator_id",
            account_id="account_id",
            filename_to_size={"foo": "string"},
            read_mask="readMask",
        )
        assert_matches_type(EvaluatorGetUploadEndpointResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_upload_endpoint(self, async_client: AsyncFireworks) -> None:
        response = await async_client.accounts.evaluators.with_raw_response.get_upload_endpoint(
            evaluator_id="evaluator_id",
            account_id="account_id",
            filename_to_size={"foo": "string"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluator = await response.parse()
        assert_matches_type(EvaluatorGetUploadEndpointResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_upload_endpoint(self, async_client: AsyncFireworks) -> None:
        async with async_client.accounts.evaluators.with_streaming_response.get_upload_endpoint(
            evaluator_id="evaluator_id",
            account_id="account_id",
            filename_to_size={"foo": "string"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluator = await response.parse()
            assert_matches_type(EvaluatorGetUploadEndpointResponse, evaluator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_upload_endpoint(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.evaluators.with_raw_response.get_upload_endpoint(
                evaluator_id="evaluator_id",
                account_id="",
                filename_to_size={"foo": "string"},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluator_id` but received ''"):
            await async_client.accounts.evaluators.with_raw_response.get_upload_endpoint(
                evaluator_id="",
                account_id="account_id",
                filename_to_size={"foo": "string"},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_validate_upload(self, async_client: AsyncFireworks) -> None:
        evaluator = await async_client.accounts.evaluators.validate_upload(
            evaluator_id="evaluator_id",
            account_id="account_id",
            body={},
        )
        assert_matches_type(object, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_validate_upload(self, async_client: AsyncFireworks) -> None:
        response = await async_client.accounts.evaluators.with_raw_response.validate_upload(
            evaluator_id="evaluator_id",
            account_id="account_id",
            body={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluator = await response.parse()
        assert_matches_type(object, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_validate_upload(self, async_client: AsyncFireworks) -> None:
        async with async_client.accounts.evaluators.with_streaming_response.validate_upload(
            evaluator_id="evaluator_id",
            account_id="account_id",
            body={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluator = await response.parse()
            assert_matches_type(object, evaluator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_validate_upload(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.evaluators.with_raw_response.validate_upload(
                evaluator_id="evaluator_id",
                account_id="",
                body={},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluator_id` but received ''"):
            await async_client.accounts.evaluators.with_raw_response.validate_upload(
                evaluator_id="",
                account_id="account_id",
                body={},
            )
