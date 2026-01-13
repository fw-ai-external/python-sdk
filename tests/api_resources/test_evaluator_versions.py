# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from fireworks import Fireworks, AsyncFireworks
from tests.utils import assert_matches_type
from fireworks.types import (
    EvaluatorVersion,
    GetBuildLogEndpointResponse,
    GetSourceCodeEndpointResponse,
    EvaluatorVersionGetUploadEndpointResponse,
)
from fireworks.pagination import SyncCursorEvaluatorVersions, AsyncCursorEvaluatorVersions

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestEvaluatorVersions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Fireworks) -> None:
        evaluator_version = client.evaluator_versions.create(
            evaluator_id="evaluator_id",
            account_id="account_id",
            evaluator_version={},
        )
        assert_matches_type(EvaluatorVersion, evaluator_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Fireworks) -> None:
        evaluator_version = client.evaluator_versions.create(
            evaluator_id="evaluator_id",
            account_id="account_id",
            evaluator_version={
                "commit_hash": "commitHash",
                "entry_point": "entryPoint",
                "requirements": "requirements",
            },
            evaluator_version_id="evaluatorVersionId",
        )
        assert_matches_type(EvaluatorVersion, evaluator_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Fireworks) -> None:
        response = client.evaluator_versions.with_raw_response.create(
            evaluator_id="evaluator_id",
            account_id="account_id",
            evaluator_version={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluator_version = response.parse()
        assert_matches_type(EvaluatorVersion, evaluator_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Fireworks) -> None:
        with client.evaluator_versions.with_streaming_response.create(
            evaluator_id="evaluator_id",
            account_id="account_id",
            evaluator_version={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluator_version = response.parse()
            assert_matches_type(EvaluatorVersion, evaluator_version, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.evaluator_versions.with_raw_response.create(
                evaluator_id="evaluator_id",
                account_id="",
                evaluator_version={},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluator_id` but received ''"):
            client.evaluator_versions.with_raw_response.create(
                evaluator_id="",
                account_id="account_id",
                evaluator_version={},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Fireworks) -> None:
        evaluator_version = client.evaluator_versions.list(
            evaluator_id="evaluator_id",
            account_id="account_id",
        )
        assert_matches_type(SyncCursorEvaluatorVersions[EvaluatorVersion], evaluator_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: Fireworks) -> None:
        evaluator_version = client.evaluator_versions.list(
            evaluator_id="evaluator_id",
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(SyncCursorEvaluatorVersions[EvaluatorVersion], evaluator_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Fireworks) -> None:
        response = client.evaluator_versions.with_raw_response.list(
            evaluator_id="evaluator_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluator_version = response.parse()
        assert_matches_type(SyncCursorEvaluatorVersions[EvaluatorVersion], evaluator_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Fireworks) -> None:
        with client.evaluator_versions.with_streaming_response.list(
            evaluator_id="evaluator_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluator_version = response.parse()
            assert_matches_type(SyncCursorEvaluatorVersions[EvaluatorVersion], evaluator_version, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.evaluator_versions.with_raw_response.list(
                evaluator_id="evaluator_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluator_id` but received ''"):
            client.evaluator_versions.with_raw_response.list(
                evaluator_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: Fireworks) -> None:
        evaluator_version = client.evaluator_versions.delete(
            version_id="version_id",
            account_id="account_id",
            evaluator_id="evaluator_id",
        )
        assert_matches_type(object, evaluator_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: Fireworks) -> None:
        response = client.evaluator_versions.with_raw_response.delete(
            version_id="version_id",
            account_id="account_id",
            evaluator_id="evaluator_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluator_version = response.parse()
        assert_matches_type(object, evaluator_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: Fireworks) -> None:
        with client.evaluator_versions.with_streaming_response.delete(
            version_id="version_id",
            account_id="account_id",
            evaluator_id="evaluator_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluator_version = response.parse()
            assert_matches_type(object, evaluator_version, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.evaluator_versions.with_raw_response.delete(
                version_id="version_id",
                account_id="",
                evaluator_id="evaluator_id",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluator_id` but received ''"):
            client.evaluator_versions.with_raw_response.delete(
                version_id="version_id",
                account_id="account_id",
                evaluator_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `version_id` but received ''"):
            client.evaluator_versions.with_raw_response.delete(
                version_id="",
                account_id="account_id",
                evaluator_id="evaluator_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get(self, client: Fireworks) -> None:
        evaluator_version = client.evaluator_versions.get(
            version_id="version_id",
            account_id="account_id",
            evaluator_id="evaluator_id",
        )
        assert_matches_type(EvaluatorVersion, evaluator_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_with_all_params(self, client: Fireworks) -> None:
        evaluator_version = client.evaluator_versions.get(
            version_id="version_id",
            account_id="account_id",
            evaluator_id="evaluator_id",
            read_mask="readMask",
        )
        assert_matches_type(EvaluatorVersion, evaluator_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get(self, client: Fireworks) -> None:
        response = client.evaluator_versions.with_raw_response.get(
            version_id="version_id",
            account_id="account_id",
            evaluator_id="evaluator_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluator_version = response.parse()
        assert_matches_type(EvaluatorVersion, evaluator_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get(self, client: Fireworks) -> None:
        with client.evaluator_versions.with_streaming_response.get(
            version_id="version_id",
            account_id="account_id",
            evaluator_id="evaluator_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluator_version = response.parse()
            assert_matches_type(EvaluatorVersion, evaluator_version, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.evaluator_versions.with_raw_response.get(
                version_id="version_id",
                account_id="",
                evaluator_id="evaluator_id",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluator_id` but received ''"):
            client.evaluator_versions.with_raw_response.get(
                version_id="version_id",
                account_id="account_id",
                evaluator_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `version_id` but received ''"):
            client.evaluator_versions.with_raw_response.get(
                version_id="",
                account_id="account_id",
                evaluator_id="evaluator_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_build_log_endpoint(self, client: Fireworks) -> None:
        evaluator_version = client.evaluator_versions.get_build_log_endpoint(
            version_id="version_id",
            account_id="account_id",
            evaluator_id="evaluator_id",
        )
        assert_matches_type(GetBuildLogEndpointResponse, evaluator_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_build_log_endpoint_with_all_params(self, client: Fireworks) -> None:
        evaluator_version = client.evaluator_versions.get_build_log_endpoint(
            version_id="version_id",
            account_id="account_id",
            evaluator_id="evaluator_id",
            read_mask="readMask",
        )
        assert_matches_type(GetBuildLogEndpointResponse, evaluator_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_build_log_endpoint(self, client: Fireworks) -> None:
        response = client.evaluator_versions.with_raw_response.get_build_log_endpoint(
            version_id="version_id",
            account_id="account_id",
            evaluator_id="evaluator_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluator_version = response.parse()
        assert_matches_type(GetBuildLogEndpointResponse, evaluator_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_build_log_endpoint(self, client: Fireworks) -> None:
        with client.evaluator_versions.with_streaming_response.get_build_log_endpoint(
            version_id="version_id",
            account_id="account_id",
            evaluator_id="evaluator_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluator_version = response.parse()
            assert_matches_type(GetBuildLogEndpointResponse, evaluator_version, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_build_log_endpoint(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.evaluator_versions.with_raw_response.get_build_log_endpoint(
                version_id="version_id",
                account_id="",
                evaluator_id="evaluator_id",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluator_id` but received ''"):
            client.evaluator_versions.with_raw_response.get_build_log_endpoint(
                version_id="version_id",
                account_id="account_id",
                evaluator_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `version_id` but received ''"):
            client.evaluator_versions.with_raw_response.get_build_log_endpoint(
                version_id="",
                account_id="account_id",
                evaluator_id="evaluator_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_source_code_endpoint(self, client: Fireworks) -> None:
        evaluator_version = client.evaluator_versions.get_source_code_endpoint(
            version_id="version_id",
            account_id="account_id",
            evaluator_id="evaluator_id",
        )
        assert_matches_type(GetSourceCodeEndpointResponse, evaluator_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_source_code_endpoint_with_all_params(self, client: Fireworks) -> None:
        evaluator_version = client.evaluator_versions.get_source_code_endpoint(
            version_id="version_id",
            account_id="account_id",
            evaluator_id="evaluator_id",
            read_mask="readMask",
        )
        assert_matches_type(GetSourceCodeEndpointResponse, evaluator_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_source_code_endpoint(self, client: Fireworks) -> None:
        response = client.evaluator_versions.with_raw_response.get_source_code_endpoint(
            version_id="version_id",
            account_id="account_id",
            evaluator_id="evaluator_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluator_version = response.parse()
        assert_matches_type(GetSourceCodeEndpointResponse, evaluator_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_source_code_endpoint(self, client: Fireworks) -> None:
        with client.evaluator_versions.with_streaming_response.get_source_code_endpoint(
            version_id="version_id",
            account_id="account_id",
            evaluator_id="evaluator_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluator_version = response.parse()
            assert_matches_type(GetSourceCodeEndpointResponse, evaluator_version, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_source_code_endpoint(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.evaluator_versions.with_raw_response.get_source_code_endpoint(
                version_id="version_id",
                account_id="",
                evaluator_id="evaluator_id",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluator_id` but received ''"):
            client.evaluator_versions.with_raw_response.get_source_code_endpoint(
                version_id="version_id",
                account_id="account_id",
                evaluator_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `version_id` but received ''"):
            client.evaluator_versions.with_raw_response.get_source_code_endpoint(
                version_id="",
                account_id="account_id",
                evaluator_id="evaluator_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_upload_endpoint(self, client: Fireworks) -> None:
        evaluator_version = client.evaluator_versions.get_upload_endpoint(
            version_id="version_id",
            account_id="account_id",
            evaluator_id="evaluator_id",
            filename_to_size={"foo": "string"},
        )
        assert_matches_type(EvaluatorVersionGetUploadEndpointResponse, evaluator_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_upload_endpoint(self, client: Fireworks) -> None:
        response = client.evaluator_versions.with_raw_response.get_upload_endpoint(
            version_id="version_id",
            account_id="account_id",
            evaluator_id="evaluator_id",
            filename_to_size={"foo": "string"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluator_version = response.parse()
        assert_matches_type(EvaluatorVersionGetUploadEndpointResponse, evaluator_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_upload_endpoint(self, client: Fireworks) -> None:
        with client.evaluator_versions.with_streaming_response.get_upload_endpoint(
            version_id="version_id",
            account_id="account_id",
            evaluator_id="evaluator_id",
            filename_to_size={"foo": "string"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluator_version = response.parse()
            assert_matches_type(EvaluatorVersionGetUploadEndpointResponse, evaluator_version, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_upload_endpoint(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.evaluator_versions.with_raw_response.get_upload_endpoint(
                version_id="version_id",
                account_id="",
                evaluator_id="evaluator_id",
                filename_to_size={"foo": "string"},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluator_id` but received ''"):
            client.evaluator_versions.with_raw_response.get_upload_endpoint(
                version_id="version_id",
                account_id="account_id",
                evaluator_id="",
                filename_to_size={"foo": "string"},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `version_id` but received ''"):
            client.evaluator_versions.with_raw_response.get_upload_endpoint(
                version_id="",
                account_id="account_id",
                evaluator_id="evaluator_id",
                filename_to_size={"foo": "string"},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_validate_upload(self, client: Fireworks) -> None:
        evaluator_version = client.evaluator_versions.validate_upload(
            version_id="version_id",
            account_id="account_id",
            evaluator_id="evaluator_id",
        )
        assert_matches_type(object, evaluator_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_validate_upload_with_all_params(self, client: Fireworks) -> None:
        evaluator_version = client.evaluator_versions.validate_upload(
            version_id="version_id",
            account_id="account_id",
            evaluator_id="evaluator_id",
            auto_promote=True,
        )
        assert_matches_type(object, evaluator_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_validate_upload(self, client: Fireworks) -> None:
        response = client.evaluator_versions.with_raw_response.validate_upload(
            version_id="version_id",
            account_id="account_id",
            evaluator_id="evaluator_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluator_version = response.parse()
        assert_matches_type(object, evaluator_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_validate_upload(self, client: Fireworks) -> None:
        with client.evaluator_versions.with_streaming_response.validate_upload(
            version_id="version_id",
            account_id="account_id",
            evaluator_id="evaluator_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluator_version = response.parse()
            assert_matches_type(object, evaluator_version, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_validate_upload(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.evaluator_versions.with_raw_response.validate_upload(
                version_id="version_id",
                account_id="",
                evaluator_id="evaluator_id",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluator_id` but received ''"):
            client.evaluator_versions.with_raw_response.validate_upload(
                version_id="version_id",
                account_id="account_id",
                evaluator_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `version_id` but received ''"):
            client.evaluator_versions.with_raw_response.validate_upload(
                version_id="",
                account_id="account_id",
                evaluator_id="evaluator_id",
            )


class TestAsyncEvaluatorVersions:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncFireworks) -> None:
        evaluator_version = await async_client.evaluator_versions.create(
            evaluator_id="evaluator_id",
            account_id="account_id",
            evaluator_version={},
        )
        assert_matches_type(EvaluatorVersion, evaluator_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncFireworks) -> None:
        evaluator_version = await async_client.evaluator_versions.create(
            evaluator_id="evaluator_id",
            account_id="account_id",
            evaluator_version={
                "commit_hash": "commitHash",
                "entry_point": "entryPoint",
                "requirements": "requirements",
            },
            evaluator_version_id="evaluatorVersionId",
        )
        assert_matches_type(EvaluatorVersion, evaluator_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncFireworks) -> None:
        response = await async_client.evaluator_versions.with_raw_response.create(
            evaluator_id="evaluator_id",
            account_id="account_id",
            evaluator_version={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluator_version = await response.parse()
        assert_matches_type(EvaluatorVersion, evaluator_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncFireworks) -> None:
        async with async_client.evaluator_versions.with_streaming_response.create(
            evaluator_id="evaluator_id",
            account_id="account_id",
            evaluator_version={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluator_version = await response.parse()
            assert_matches_type(EvaluatorVersion, evaluator_version, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.evaluator_versions.with_raw_response.create(
                evaluator_id="evaluator_id",
                account_id="",
                evaluator_version={},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluator_id` but received ''"):
            await async_client.evaluator_versions.with_raw_response.create(
                evaluator_id="",
                account_id="account_id",
                evaluator_version={},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncFireworks) -> None:
        evaluator_version = await async_client.evaluator_versions.list(
            evaluator_id="evaluator_id",
            account_id="account_id",
        )
        assert_matches_type(AsyncCursorEvaluatorVersions[EvaluatorVersion], evaluator_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncFireworks) -> None:
        evaluator_version = await async_client.evaluator_versions.list(
            evaluator_id="evaluator_id",
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(AsyncCursorEvaluatorVersions[EvaluatorVersion], evaluator_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncFireworks) -> None:
        response = await async_client.evaluator_versions.with_raw_response.list(
            evaluator_id="evaluator_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluator_version = await response.parse()
        assert_matches_type(AsyncCursorEvaluatorVersions[EvaluatorVersion], evaluator_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncFireworks) -> None:
        async with async_client.evaluator_versions.with_streaming_response.list(
            evaluator_id="evaluator_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluator_version = await response.parse()
            assert_matches_type(AsyncCursorEvaluatorVersions[EvaluatorVersion], evaluator_version, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.evaluator_versions.with_raw_response.list(
                evaluator_id="evaluator_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluator_id` but received ''"):
            await async_client.evaluator_versions.with_raw_response.list(
                evaluator_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncFireworks) -> None:
        evaluator_version = await async_client.evaluator_versions.delete(
            version_id="version_id",
            account_id="account_id",
            evaluator_id="evaluator_id",
        )
        assert_matches_type(object, evaluator_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncFireworks) -> None:
        response = await async_client.evaluator_versions.with_raw_response.delete(
            version_id="version_id",
            account_id="account_id",
            evaluator_id="evaluator_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluator_version = await response.parse()
        assert_matches_type(object, evaluator_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncFireworks) -> None:
        async with async_client.evaluator_versions.with_streaming_response.delete(
            version_id="version_id",
            account_id="account_id",
            evaluator_id="evaluator_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluator_version = await response.parse()
            assert_matches_type(object, evaluator_version, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.evaluator_versions.with_raw_response.delete(
                version_id="version_id",
                account_id="",
                evaluator_id="evaluator_id",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluator_id` but received ''"):
            await async_client.evaluator_versions.with_raw_response.delete(
                version_id="version_id",
                account_id="account_id",
                evaluator_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `version_id` but received ''"):
            await async_client.evaluator_versions.with_raw_response.delete(
                version_id="",
                account_id="account_id",
                evaluator_id="evaluator_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get(self, async_client: AsyncFireworks) -> None:
        evaluator_version = await async_client.evaluator_versions.get(
            version_id="version_id",
            account_id="account_id",
            evaluator_id="evaluator_id",
        )
        assert_matches_type(EvaluatorVersion, evaluator_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_with_all_params(self, async_client: AsyncFireworks) -> None:
        evaluator_version = await async_client.evaluator_versions.get(
            version_id="version_id",
            account_id="account_id",
            evaluator_id="evaluator_id",
            read_mask="readMask",
        )
        assert_matches_type(EvaluatorVersion, evaluator_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncFireworks) -> None:
        response = await async_client.evaluator_versions.with_raw_response.get(
            version_id="version_id",
            account_id="account_id",
            evaluator_id="evaluator_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluator_version = await response.parse()
        assert_matches_type(EvaluatorVersion, evaluator_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncFireworks) -> None:
        async with async_client.evaluator_versions.with_streaming_response.get(
            version_id="version_id",
            account_id="account_id",
            evaluator_id="evaluator_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluator_version = await response.parse()
            assert_matches_type(EvaluatorVersion, evaluator_version, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.evaluator_versions.with_raw_response.get(
                version_id="version_id",
                account_id="",
                evaluator_id="evaluator_id",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluator_id` but received ''"):
            await async_client.evaluator_versions.with_raw_response.get(
                version_id="version_id",
                account_id="account_id",
                evaluator_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `version_id` but received ''"):
            await async_client.evaluator_versions.with_raw_response.get(
                version_id="",
                account_id="account_id",
                evaluator_id="evaluator_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_build_log_endpoint(self, async_client: AsyncFireworks) -> None:
        evaluator_version = await async_client.evaluator_versions.get_build_log_endpoint(
            version_id="version_id",
            account_id="account_id",
            evaluator_id="evaluator_id",
        )
        assert_matches_type(GetBuildLogEndpointResponse, evaluator_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_build_log_endpoint_with_all_params(self, async_client: AsyncFireworks) -> None:
        evaluator_version = await async_client.evaluator_versions.get_build_log_endpoint(
            version_id="version_id",
            account_id="account_id",
            evaluator_id="evaluator_id",
            read_mask="readMask",
        )
        assert_matches_type(GetBuildLogEndpointResponse, evaluator_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_build_log_endpoint(self, async_client: AsyncFireworks) -> None:
        response = await async_client.evaluator_versions.with_raw_response.get_build_log_endpoint(
            version_id="version_id",
            account_id="account_id",
            evaluator_id="evaluator_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluator_version = await response.parse()
        assert_matches_type(GetBuildLogEndpointResponse, evaluator_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_build_log_endpoint(self, async_client: AsyncFireworks) -> None:
        async with async_client.evaluator_versions.with_streaming_response.get_build_log_endpoint(
            version_id="version_id",
            account_id="account_id",
            evaluator_id="evaluator_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluator_version = await response.parse()
            assert_matches_type(GetBuildLogEndpointResponse, evaluator_version, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_build_log_endpoint(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.evaluator_versions.with_raw_response.get_build_log_endpoint(
                version_id="version_id",
                account_id="",
                evaluator_id="evaluator_id",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluator_id` but received ''"):
            await async_client.evaluator_versions.with_raw_response.get_build_log_endpoint(
                version_id="version_id",
                account_id="account_id",
                evaluator_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `version_id` but received ''"):
            await async_client.evaluator_versions.with_raw_response.get_build_log_endpoint(
                version_id="",
                account_id="account_id",
                evaluator_id="evaluator_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_source_code_endpoint(self, async_client: AsyncFireworks) -> None:
        evaluator_version = await async_client.evaluator_versions.get_source_code_endpoint(
            version_id="version_id",
            account_id="account_id",
            evaluator_id="evaluator_id",
        )
        assert_matches_type(GetSourceCodeEndpointResponse, evaluator_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_source_code_endpoint_with_all_params(self, async_client: AsyncFireworks) -> None:
        evaluator_version = await async_client.evaluator_versions.get_source_code_endpoint(
            version_id="version_id",
            account_id="account_id",
            evaluator_id="evaluator_id",
            read_mask="readMask",
        )
        assert_matches_type(GetSourceCodeEndpointResponse, evaluator_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_source_code_endpoint(self, async_client: AsyncFireworks) -> None:
        response = await async_client.evaluator_versions.with_raw_response.get_source_code_endpoint(
            version_id="version_id",
            account_id="account_id",
            evaluator_id="evaluator_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluator_version = await response.parse()
        assert_matches_type(GetSourceCodeEndpointResponse, evaluator_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_source_code_endpoint(self, async_client: AsyncFireworks) -> None:
        async with async_client.evaluator_versions.with_streaming_response.get_source_code_endpoint(
            version_id="version_id",
            account_id="account_id",
            evaluator_id="evaluator_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluator_version = await response.parse()
            assert_matches_type(GetSourceCodeEndpointResponse, evaluator_version, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_source_code_endpoint(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.evaluator_versions.with_raw_response.get_source_code_endpoint(
                version_id="version_id",
                account_id="",
                evaluator_id="evaluator_id",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluator_id` but received ''"):
            await async_client.evaluator_versions.with_raw_response.get_source_code_endpoint(
                version_id="version_id",
                account_id="account_id",
                evaluator_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `version_id` but received ''"):
            await async_client.evaluator_versions.with_raw_response.get_source_code_endpoint(
                version_id="",
                account_id="account_id",
                evaluator_id="evaluator_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_upload_endpoint(self, async_client: AsyncFireworks) -> None:
        evaluator_version = await async_client.evaluator_versions.get_upload_endpoint(
            version_id="version_id",
            account_id="account_id",
            evaluator_id="evaluator_id",
            filename_to_size={"foo": "string"},
        )
        assert_matches_type(EvaluatorVersionGetUploadEndpointResponse, evaluator_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_upload_endpoint(self, async_client: AsyncFireworks) -> None:
        response = await async_client.evaluator_versions.with_raw_response.get_upload_endpoint(
            version_id="version_id",
            account_id="account_id",
            evaluator_id="evaluator_id",
            filename_to_size={"foo": "string"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluator_version = await response.parse()
        assert_matches_type(EvaluatorVersionGetUploadEndpointResponse, evaluator_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_upload_endpoint(self, async_client: AsyncFireworks) -> None:
        async with async_client.evaluator_versions.with_streaming_response.get_upload_endpoint(
            version_id="version_id",
            account_id="account_id",
            evaluator_id="evaluator_id",
            filename_to_size={"foo": "string"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluator_version = await response.parse()
            assert_matches_type(EvaluatorVersionGetUploadEndpointResponse, evaluator_version, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_upload_endpoint(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.evaluator_versions.with_raw_response.get_upload_endpoint(
                version_id="version_id",
                account_id="",
                evaluator_id="evaluator_id",
                filename_to_size={"foo": "string"},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluator_id` but received ''"):
            await async_client.evaluator_versions.with_raw_response.get_upload_endpoint(
                version_id="version_id",
                account_id="account_id",
                evaluator_id="",
                filename_to_size={"foo": "string"},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `version_id` but received ''"):
            await async_client.evaluator_versions.with_raw_response.get_upload_endpoint(
                version_id="",
                account_id="account_id",
                evaluator_id="evaluator_id",
                filename_to_size={"foo": "string"},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_validate_upload(self, async_client: AsyncFireworks) -> None:
        evaluator_version = await async_client.evaluator_versions.validate_upload(
            version_id="version_id",
            account_id="account_id",
            evaluator_id="evaluator_id",
        )
        assert_matches_type(object, evaluator_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_validate_upload_with_all_params(self, async_client: AsyncFireworks) -> None:
        evaluator_version = await async_client.evaluator_versions.validate_upload(
            version_id="version_id",
            account_id="account_id",
            evaluator_id="evaluator_id",
            auto_promote=True,
        )
        assert_matches_type(object, evaluator_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_validate_upload(self, async_client: AsyncFireworks) -> None:
        response = await async_client.evaluator_versions.with_raw_response.validate_upload(
            version_id="version_id",
            account_id="account_id",
            evaluator_id="evaluator_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluator_version = await response.parse()
        assert_matches_type(object, evaluator_version, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_validate_upload(self, async_client: AsyncFireworks) -> None:
        async with async_client.evaluator_versions.with_streaming_response.validate_upload(
            version_id="version_id",
            account_id="account_id",
            evaluator_id="evaluator_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluator_version = await response.parse()
            assert_matches_type(object, evaluator_version, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_validate_upload(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.evaluator_versions.with_raw_response.validate_upload(
                version_id="version_id",
                account_id="",
                evaluator_id="evaluator_id",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `evaluator_id` but received ''"):
            await async_client.evaluator_versions.with_raw_response.validate_upload(
                version_id="version_id",
                account_id="account_id",
                evaluator_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `version_id` but received ''"):
            await async_client.evaluator_versions.with_raw_response.validate_upload(
                version_id="",
                account_id="account_id",
                evaluator_id="evaluator_id",
            )
