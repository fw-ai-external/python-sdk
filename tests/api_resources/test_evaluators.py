# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from fireworks import Fireworks, AsyncFireworks
from tests.utils import assert_matches_type
from fireworks.types import (
    EvaluatorGetResponse,
    EvaluatorListResponse,
    EvaluatorCreateResponse,
    EvaluatorUpdateResponse,
    EvaluatorGetUploadEndpointResponse,
    EvaluatorGetBuildLogEndpointResponse,
    EvaluatorGetSourceCodeEndpointResponse,
)
from fireworks.pagination import SyncCursorEvaluators, AsyncCursorEvaluators

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestEvaluators:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Fireworks) -> None:
        evaluator = client.evaluators.create(
            account_id="account_id",
            evaluator={},
        )
        assert_matches_type(EvaluatorCreateResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Fireworks) -> None:
        evaluator = client.evaluators.create(
            account_id="account_id",
            evaluator={
                "commit_hash": "commitHash",
                "default_dataset": "defaultDataset",
                "description": "description",
                "display_name": "displayName",
                "entry_point": "entryPoint",
                "requirements": "requirements",
                "source": {
                    "github_repository_name": "githubRepositoryName",
                    "type": "TYPE_UNSPECIFIED",
                },
            },
            evaluator_id="evaluatorId",
        )
        assert_matches_type(EvaluatorCreateResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Fireworks) -> None:
        response = client.evaluators.with_raw_response.create(
            account_id="account_id",
            evaluator={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluator = response.parse()
        assert_matches_type(EvaluatorCreateResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Fireworks) -> None:
        with client.evaluators.with_streaming_response.create(
            account_id="account_id",
            evaluator={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluator = response.parse()
            assert_matches_type(EvaluatorCreateResponse, evaluator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.evaluators.with_raw_response.create(
                account_id="",
                evaluator={},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: Fireworks) -> None:
        evaluator = client.evaluators.update(
            evaluator_id="evaluator_id",
            account_id="account_id",
        )
        assert_matches_type(EvaluatorUpdateResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: Fireworks) -> None:
        evaluator = client.evaluators.update(
            evaluator_id="evaluator_id",
            account_id="account_id",
            prepare_code_upload=True,
            commit_hash="commitHash",
            default_dataset="defaultDataset",
            description="description",
            display_name="displayName",
            entry_point="entryPoint",
            requirements="requirements",
            source={
                "github_repository_name": "githubRepositoryName",
                "type": "TYPE_UNSPECIFIED",
            },
        )
        assert_matches_type(EvaluatorUpdateResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: Fireworks) -> None:
        response = client.evaluators.with_raw_response.update(
            evaluator_id="evaluator_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluator = response.parse()
        assert_matches_type(EvaluatorUpdateResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: Fireworks) -> None:
        with client.evaluators.with_streaming_response.update(
            evaluator_id="evaluator_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluator = response.parse()
            assert_matches_type(EvaluatorUpdateResponse, evaluator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.evaluators.with_raw_response.update(
                evaluator_id="evaluator_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluator_id` but received ''"):
            client.evaluators.with_raw_response.update(
                evaluator_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Fireworks) -> None:
        evaluator = client.evaluators.list(
            account_id="account_id",
        )
        assert_matches_type(SyncCursorEvaluators[EvaluatorListResponse], evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: Fireworks) -> None:
        evaluator = client.evaluators.list(
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(SyncCursorEvaluators[EvaluatorListResponse], evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Fireworks) -> None:
        response = client.evaluators.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluator = response.parse()
        assert_matches_type(SyncCursorEvaluators[EvaluatorListResponse], evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Fireworks) -> None:
        with client.evaluators.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluator = response.parse()
            assert_matches_type(SyncCursorEvaluators[EvaluatorListResponse], evaluator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.evaluators.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: Fireworks) -> None:
        evaluator = client.evaluators.delete(
            evaluator_id="evaluator_id",
            account_id="account_id",
        )
        assert_matches_type(object, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: Fireworks) -> None:
        response = client.evaluators.with_raw_response.delete(
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
        with client.evaluators.with_streaming_response.delete(
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
            client.evaluators.with_raw_response.delete(
                evaluator_id="evaluator_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluator_id` but received ''"):
            client.evaluators.with_raw_response.delete(
                evaluator_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get(self, client: Fireworks) -> None:
        evaluator = client.evaluators.get(
            evaluator_id="evaluator_id",
            account_id="account_id",
        )
        assert_matches_type(EvaluatorGetResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_with_all_params(self, client: Fireworks) -> None:
        evaluator = client.evaluators.get(
            evaluator_id="evaluator_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(EvaluatorGetResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get(self, client: Fireworks) -> None:
        response = client.evaluators.with_raw_response.get(
            evaluator_id="evaluator_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluator = response.parse()
        assert_matches_type(EvaluatorGetResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get(self, client: Fireworks) -> None:
        with client.evaluators.with_streaming_response.get(
            evaluator_id="evaluator_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluator = response.parse()
            assert_matches_type(EvaluatorGetResponse, evaluator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.evaluators.with_raw_response.get(
                evaluator_id="evaluator_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluator_id` but received ''"):
            client.evaluators.with_raw_response.get(
                evaluator_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_build_log_endpoint(self, client: Fireworks) -> None:
        evaluator = client.evaluators.get_build_log_endpoint(
            evaluator_id="evaluator_id",
            account_id="account_id",
        )
        assert_matches_type(EvaluatorGetBuildLogEndpointResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_build_log_endpoint_with_all_params(self, client: Fireworks) -> None:
        evaluator = client.evaluators.get_build_log_endpoint(
            evaluator_id="evaluator_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(EvaluatorGetBuildLogEndpointResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_build_log_endpoint(self, client: Fireworks) -> None:
        response = client.evaluators.with_raw_response.get_build_log_endpoint(
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
        with client.evaluators.with_streaming_response.get_build_log_endpoint(
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
            client.evaluators.with_raw_response.get_build_log_endpoint(
                evaluator_id="evaluator_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluator_id` but received ''"):
            client.evaluators.with_raw_response.get_build_log_endpoint(
                evaluator_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_source_code_endpoint(self, client: Fireworks) -> None:
        evaluator = client.evaluators.get_source_code_endpoint(
            evaluator_id="evaluator_id",
            account_id="account_id",
        )
        assert_matches_type(EvaluatorGetSourceCodeEndpointResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_source_code_endpoint_with_all_params(self, client: Fireworks) -> None:
        evaluator = client.evaluators.get_source_code_endpoint(
            evaluator_id="evaluator_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(EvaluatorGetSourceCodeEndpointResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_source_code_endpoint(self, client: Fireworks) -> None:
        response = client.evaluators.with_raw_response.get_source_code_endpoint(
            evaluator_id="evaluator_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluator = response.parse()
        assert_matches_type(EvaluatorGetSourceCodeEndpointResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_source_code_endpoint(self, client: Fireworks) -> None:
        with client.evaluators.with_streaming_response.get_source_code_endpoint(
            evaluator_id="evaluator_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluator = response.parse()
            assert_matches_type(EvaluatorGetSourceCodeEndpointResponse, evaluator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_source_code_endpoint(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.evaluators.with_raw_response.get_source_code_endpoint(
                evaluator_id="evaluator_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluator_id` but received ''"):
            client.evaluators.with_raw_response.get_source_code_endpoint(
                evaluator_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_upload_endpoint(self, client: Fireworks) -> None:
        evaluator = client.evaluators.get_upload_endpoint(
            evaluator_id="evaluator_id",
            account_id="account_id",
            filename_to_size={"foo": "string"},
        )
        assert_matches_type(EvaluatorGetUploadEndpointResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_upload_endpoint_with_all_params(self, client: Fireworks) -> None:
        evaluator = client.evaluators.get_upload_endpoint(
            evaluator_id="evaluator_id",
            account_id="account_id",
            filename_to_size={"foo": "string"},
            read_mask="readMask",
        )
        assert_matches_type(EvaluatorGetUploadEndpointResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_upload_endpoint(self, client: Fireworks) -> None:
        response = client.evaluators.with_raw_response.get_upload_endpoint(
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
        with client.evaluators.with_streaming_response.get_upload_endpoint(
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
            client.evaluators.with_raw_response.get_upload_endpoint(
                evaluator_id="evaluator_id",
                account_id="",
                filename_to_size={"foo": "string"},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluator_id` but received ''"):
            client.evaluators.with_raw_response.get_upload_endpoint(
                evaluator_id="",
                account_id="account_id",
                filename_to_size={"foo": "string"},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_validate_upload(self, client: Fireworks) -> None:
        evaluator = client.evaluators.validate_upload(
            evaluator_id="evaluator_id",
            account_id="account_id",
            body={},
        )
        assert_matches_type(object, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_validate_upload(self, client: Fireworks) -> None:
        response = client.evaluators.with_raw_response.validate_upload(
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
        with client.evaluators.with_streaming_response.validate_upload(
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
            client.evaluators.with_raw_response.validate_upload(
                evaluator_id="evaluator_id",
                account_id="",
                body={},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluator_id` but received ''"):
            client.evaluators.with_raw_response.validate_upload(
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
        evaluator = await async_client.evaluators.create(
            account_id="account_id",
            evaluator={},
        )
        assert_matches_type(EvaluatorCreateResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncFireworks) -> None:
        evaluator = await async_client.evaluators.create(
            account_id="account_id",
            evaluator={
                "commit_hash": "commitHash",
                "default_dataset": "defaultDataset",
                "description": "description",
                "display_name": "displayName",
                "entry_point": "entryPoint",
                "requirements": "requirements",
                "source": {
                    "github_repository_name": "githubRepositoryName",
                    "type": "TYPE_UNSPECIFIED",
                },
            },
            evaluator_id="evaluatorId",
        )
        assert_matches_type(EvaluatorCreateResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncFireworks) -> None:
        response = await async_client.evaluators.with_raw_response.create(
            account_id="account_id",
            evaluator={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluator = await response.parse()
        assert_matches_type(EvaluatorCreateResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncFireworks) -> None:
        async with async_client.evaluators.with_streaming_response.create(
            account_id="account_id",
            evaluator={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluator = await response.parse()
            assert_matches_type(EvaluatorCreateResponse, evaluator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.evaluators.with_raw_response.create(
                account_id="",
                evaluator={},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncFireworks) -> None:
        evaluator = await async_client.evaluators.update(
            evaluator_id="evaluator_id",
            account_id="account_id",
        )
        assert_matches_type(EvaluatorUpdateResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncFireworks) -> None:
        evaluator = await async_client.evaluators.update(
            evaluator_id="evaluator_id",
            account_id="account_id",
            prepare_code_upload=True,
            commit_hash="commitHash",
            default_dataset="defaultDataset",
            description="description",
            display_name="displayName",
            entry_point="entryPoint",
            requirements="requirements",
            source={
                "github_repository_name": "githubRepositoryName",
                "type": "TYPE_UNSPECIFIED",
            },
        )
        assert_matches_type(EvaluatorUpdateResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncFireworks) -> None:
        response = await async_client.evaluators.with_raw_response.update(
            evaluator_id="evaluator_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluator = await response.parse()
        assert_matches_type(EvaluatorUpdateResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncFireworks) -> None:
        async with async_client.evaluators.with_streaming_response.update(
            evaluator_id="evaluator_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluator = await response.parse()
            assert_matches_type(EvaluatorUpdateResponse, evaluator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.evaluators.with_raw_response.update(
                evaluator_id="evaluator_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluator_id` but received ''"):
            await async_client.evaluators.with_raw_response.update(
                evaluator_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncFireworks) -> None:
        evaluator = await async_client.evaluators.list(
            account_id="account_id",
        )
        assert_matches_type(AsyncCursorEvaluators[EvaluatorListResponse], evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncFireworks) -> None:
        evaluator = await async_client.evaluators.list(
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(AsyncCursorEvaluators[EvaluatorListResponse], evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncFireworks) -> None:
        response = await async_client.evaluators.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluator = await response.parse()
        assert_matches_type(AsyncCursorEvaluators[EvaluatorListResponse], evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncFireworks) -> None:
        async with async_client.evaluators.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluator = await response.parse()
            assert_matches_type(AsyncCursorEvaluators[EvaluatorListResponse], evaluator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.evaluators.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncFireworks) -> None:
        evaluator = await async_client.evaluators.delete(
            evaluator_id="evaluator_id",
            account_id="account_id",
        )
        assert_matches_type(object, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncFireworks) -> None:
        response = await async_client.evaluators.with_raw_response.delete(
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
        async with async_client.evaluators.with_streaming_response.delete(
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
            await async_client.evaluators.with_raw_response.delete(
                evaluator_id="evaluator_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluator_id` but received ''"):
            await async_client.evaluators.with_raw_response.delete(
                evaluator_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get(self, async_client: AsyncFireworks) -> None:
        evaluator = await async_client.evaluators.get(
            evaluator_id="evaluator_id",
            account_id="account_id",
        )
        assert_matches_type(EvaluatorGetResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_with_all_params(self, async_client: AsyncFireworks) -> None:
        evaluator = await async_client.evaluators.get(
            evaluator_id="evaluator_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(EvaluatorGetResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncFireworks) -> None:
        response = await async_client.evaluators.with_raw_response.get(
            evaluator_id="evaluator_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluator = await response.parse()
        assert_matches_type(EvaluatorGetResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncFireworks) -> None:
        async with async_client.evaluators.with_streaming_response.get(
            evaluator_id="evaluator_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluator = await response.parse()
            assert_matches_type(EvaluatorGetResponse, evaluator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.evaluators.with_raw_response.get(
                evaluator_id="evaluator_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluator_id` but received ''"):
            await async_client.evaluators.with_raw_response.get(
                evaluator_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_build_log_endpoint(self, async_client: AsyncFireworks) -> None:
        evaluator = await async_client.evaluators.get_build_log_endpoint(
            evaluator_id="evaluator_id",
            account_id="account_id",
        )
        assert_matches_type(EvaluatorGetBuildLogEndpointResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_build_log_endpoint_with_all_params(self, async_client: AsyncFireworks) -> None:
        evaluator = await async_client.evaluators.get_build_log_endpoint(
            evaluator_id="evaluator_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(EvaluatorGetBuildLogEndpointResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_build_log_endpoint(self, async_client: AsyncFireworks) -> None:
        response = await async_client.evaluators.with_raw_response.get_build_log_endpoint(
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
        async with async_client.evaluators.with_streaming_response.get_build_log_endpoint(
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
            await async_client.evaluators.with_raw_response.get_build_log_endpoint(
                evaluator_id="evaluator_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluator_id` but received ''"):
            await async_client.evaluators.with_raw_response.get_build_log_endpoint(
                evaluator_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_source_code_endpoint(self, async_client: AsyncFireworks) -> None:
        evaluator = await async_client.evaluators.get_source_code_endpoint(
            evaluator_id="evaluator_id",
            account_id="account_id",
        )
        assert_matches_type(EvaluatorGetSourceCodeEndpointResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_source_code_endpoint_with_all_params(self, async_client: AsyncFireworks) -> None:
        evaluator = await async_client.evaluators.get_source_code_endpoint(
            evaluator_id="evaluator_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(EvaluatorGetSourceCodeEndpointResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_source_code_endpoint(self, async_client: AsyncFireworks) -> None:
        response = await async_client.evaluators.with_raw_response.get_source_code_endpoint(
            evaluator_id="evaluator_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluator = await response.parse()
        assert_matches_type(EvaluatorGetSourceCodeEndpointResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_source_code_endpoint(self, async_client: AsyncFireworks) -> None:
        async with async_client.evaluators.with_streaming_response.get_source_code_endpoint(
            evaluator_id="evaluator_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluator = await response.parse()
            assert_matches_type(EvaluatorGetSourceCodeEndpointResponse, evaluator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_source_code_endpoint(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.evaluators.with_raw_response.get_source_code_endpoint(
                evaluator_id="evaluator_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluator_id` but received ''"):
            await async_client.evaluators.with_raw_response.get_source_code_endpoint(
                evaluator_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_upload_endpoint(self, async_client: AsyncFireworks) -> None:
        evaluator = await async_client.evaluators.get_upload_endpoint(
            evaluator_id="evaluator_id",
            account_id="account_id",
            filename_to_size={"foo": "string"},
        )
        assert_matches_type(EvaluatorGetUploadEndpointResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_upload_endpoint_with_all_params(self, async_client: AsyncFireworks) -> None:
        evaluator = await async_client.evaluators.get_upload_endpoint(
            evaluator_id="evaluator_id",
            account_id="account_id",
            filename_to_size={"foo": "string"},
            read_mask="readMask",
        )
        assert_matches_type(EvaluatorGetUploadEndpointResponse, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_upload_endpoint(self, async_client: AsyncFireworks) -> None:
        response = await async_client.evaluators.with_raw_response.get_upload_endpoint(
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
        async with async_client.evaluators.with_streaming_response.get_upload_endpoint(
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
            await async_client.evaluators.with_raw_response.get_upload_endpoint(
                evaluator_id="evaluator_id",
                account_id="",
                filename_to_size={"foo": "string"},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluator_id` but received ''"):
            await async_client.evaluators.with_raw_response.get_upload_endpoint(
                evaluator_id="",
                account_id="account_id",
                filename_to_size={"foo": "string"},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_validate_upload(self, async_client: AsyncFireworks) -> None:
        evaluator = await async_client.evaluators.validate_upload(
            evaluator_id="evaluator_id",
            account_id="account_id",
            body={},
        )
        assert_matches_type(object, evaluator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_validate_upload(self, async_client: AsyncFireworks) -> None:
        response = await async_client.evaluators.with_raw_response.validate_upload(
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
        async with async_client.evaluators.with_streaming_response.validate_upload(
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
            await async_client.evaluators.with_raw_response.validate_upload(
                evaluator_id="evaluator_id",
                account_id="",
                body={},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluator_id` but received ''"):
            await async_client.evaluators.with_raw_response.validate_upload(
                evaluator_id="",
                account_id="account_id",
                body={},
            )
