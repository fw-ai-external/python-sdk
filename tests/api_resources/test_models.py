# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from fireworks_ai import Fireworks, AsyncFireworks
from fireworks_ai.types import (
    ModelGetResponse,
    ModelListResponse,
    ModelCreateResponse,
    ModelUpdateResponse,
    ModelGetUploadEndpointResponse,
    ModelGetDownloadEndpointResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestModels:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Fireworks) -> None:
        model = client.models.create(
            account_id="account_id",
            model_id="modelId",
        )
        assert_matches_type(ModelCreateResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Fireworks) -> None:
        model = client.models.create(
            account_id="account_id",
            model_id="modelId",
            cluster="cluster",
            model={
                "base_model_details": {
                    "checkpoint_format": "CHECKPOINT_FORMAT_UNSPECIFIED",
                    "model_type": "modelType",
                    "moe": True,
                    "parameter_count": "parameterCount",
                    "supports_fireattention": True,
                    "supports_mtp": True,
                    "tunable": True,
                    "world_size": 0,
                },
                "context_length": 0,
                "conversation_config": {
                    "style": "style",
                    "system": "system",
                    "template": "template",
                },
                "default_draft_model": "defaultDraftModel",
                "default_draft_token_count": 0,
                "deprecation_date": {
                    "day": 0,
                    "month": 0,
                    "year": 0,
                },
                "description": "description",
                "display_name": "displayName",
                "github_url": "githubUrl",
                "hugging_face_url": "huggingFaceUrl",
                "kind": "KIND_UNSPECIFIED",
                "peft_details": {
                    "base_model": "baseModel",
                    "r": 0,
                    "target_modules": ["string"],
                    "merge_addon_model_name": "mergeAddonModelName",
                },
                "public": True,
                "snapshot_type": "FULL_SNAPSHOT",
                "supports_image_input": True,
                "supports_lora": True,
                "supports_tools": True,
                "teft_details": {},
                "training_context_length": 0,
                "use_hf_apply_chat_template": True,
            },
        )
        assert_matches_type(ModelCreateResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Fireworks) -> None:
        response = client.models.with_raw_response.create(
            account_id="account_id",
            model_id="modelId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = response.parse()
        assert_matches_type(ModelCreateResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Fireworks) -> None:
        with client.models.with_streaming_response.create(
            account_id="account_id",
            model_id="modelId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = response.parse()
            assert_matches_type(ModelCreateResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.models.with_raw_response.create(
                account_id="",
                model_id="modelId",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: Fireworks) -> None:
        model = client.models.update(
            model_id="model_id",
            account_id="account_id",
        )
        assert_matches_type(ModelUpdateResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: Fireworks) -> None:
        model = client.models.update(
            model_id="model_id",
            account_id="account_id",
            base_model_details={
                "checkpoint_format": "CHECKPOINT_FORMAT_UNSPECIFIED",
                "model_type": "modelType",
                "moe": True,
                "parameter_count": "parameterCount",
                "supports_fireattention": True,
                "supports_mtp": True,
                "tunable": True,
                "world_size": 0,
            },
            context_length=0,
            conversation_config={
                "style": "style",
                "system": "system",
                "template": "template",
            },
            default_draft_model="defaultDraftModel",
            default_draft_token_count=0,
            deprecation_date={
                "day": 0,
                "month": 0,
                "year": 0,
            },
            description="description",
            display_name="displayName",
            github_url="githubUrl",
            hugging_face_url="huggingFaceUrl",
            kind="KIND_UNSPECIFIED",
            peft_details={
                "base_model": "baseModel",
                "r": 0,
                "target_modules": ["string"],
                "merge_addon_model_name": "mergeAddonModelName",
            },
            public=True,
            snapshot_type="FULL_SNAPSHOT",
            supports_image_input=True,
            supports_lora=True,
            supports_tools=True,
            teft_details={},
            training_context_length=0,
            use_hf_apply_chat_template=True,
        )
        assert_matches_type(ModelUpdateResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: Fireworks) -> None:
        response = client.models.with_raw_response.update(
            model_id="model_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = response.parse()
        assert_matches_type(ModelUpdateResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: Fireworks) -> None:
        with client.models.with_streaming_response.update(
            model_id="model_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = response.parse()
            assert_matches_type(ModelUpdateResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.models.with_raw_response.update(
                model_id="model_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_id` but received ''"):
            client.models.with_raw_response.update(
                model_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Fireworks) -> None:
        model = client.models.list(
            account_id="account_id",
        )
        assert_matches_type(ModelListResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: Fireworks) -> None:
        model = client.models.list(
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(ModelListResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Fireworks) -> None:
        response = client.models.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = response.parse()
        assert_matches_type(ModelListResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Fireworks) -> None:
        with client.models.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = response.parse()
            assert_matches_type(ModelListResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.models.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: Fireworks) -> None:
        model = client.models.delete(
            model_id="model_id",
            account_id="account_id",
        )
        assert_matches_type(object, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: Fireworks) -> None:
        response = client.models.with_raw_response.delete(
            model_id="model_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = response.parse()
        assert_matches_type(object, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: Fireworks) -> None:
        with client.models.with_streaming_response.delete(
            model_id="model_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = response.parse()
            assert_matches_type(object, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.models.with_raw_response.delete(
                model_id="model_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_id` but received ''"):
            client.models.with_raw_response.delete(
                model_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get(self, client: Fireworks) -> None:
        model = client.models.get(
            model_id="model_id",
            account_id="account_id",
        )
        assert_matches_type(ModelGetResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_with_all_params(self, client: Fireworks) -> None:
        model = client.models.get(
            model_id="model_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(ModelGetResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get(self, client: Fireworks) -> None:
        response = client.models.with_raw_response.get(
            model_id="model_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = response.parse()
        assert_matches_type(ModelGetResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get(self, client: Fireworks) -> None:
        with client.models.with_streaming_response.get(
            model_id="model_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = response.parse()
            assert_matches_type(ModelGetResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.models.with_raw_response.get(
                model_id="model_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_id` but received ''"):
            client.models.with_raw_response.get(
                model_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_download_endpoint(self, client: Fireworks) -> None:
        model = client.models.get_download_endpoint(
            model_id="model_id",
            account_id="account_id",
        )
        assert_matches_type(ModelGetDownloadEndpointResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_download_endpoint_with_all_params(self, client: Fireworks) -> None:
        model = client.models.get_download_endpoint(
            model_id="model_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(ModelGetDownloadEndpointResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_download_endpoint(self, client: Fireworks) -> None:
        response = client.models.with_raw_response.get_download_endpoint(
            model_id="model_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = response.parse()
        assert_matches_type(ModelGetDownloadEndpointResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_download_endpoint(self, client: Fireworks) -> None:
        with client.models.with_streaming_response.get_download_endpoint(
            model_id="model_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = response.parse()
            assert_matches_type(ModelGetDownloadEndpointResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_download_endpoint(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.models.with_raw_response.get_download_endpoint(
                model_id="model_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_id` but received ''"):
            client.models.with_raw_response.get_download_endpoint(
                model_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_upload_endpoint(self, client: Fireworks) -> None:
        model = client.models.get_upload_endpoint(
            model_id="model_id",
            account_id="account_id",
            filename_to_size={"foo": "string"},
        )
        assert_matches_type(ModelGetUploadEndpointResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_upload_endpoint_with_all_params(self, client: Fireworks) -> None:
        model = client.models.get_upload_endpoint(
            model_id="model_id",
            account_id="account_id",
            filename_to_size={"foo": "string"},
            enable_resumable_upload=True,
            read_mask="readMask",
        )
        assert_matches_type(ModelGetUploadEndpointResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_upload_endpoint(self, client: Fireworks) -> None:
        response = client.models.with_raw_response.get_upload_endpoint(
            model_id="model_id",
            account_id="account_id",
            filename_to_size={"foo": "string"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = response.parse()
        assert_matches_type(ModelGetUploadEndpointResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_upload_endpoint(self, client: Fireworks) -> None:
        with client.models.with_streaming_response.get_upload_endpoint(
            model_id="model_id",
            account_id="account_id",
            filename_to_size={"foo": "string"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = response.parse()
            assert_matches_type(ModelGetUploadEndpointResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_upload_endpoint(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.models.with_raw_response.get_upload_endpoint(
                model_id="model_id",
                account_id="",
                filename_to_size={"foo": "string"},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_id` but received ''"):
            client.models.with_raw_response.get_upload_endpoint(
                model_id="",
                account_id="account_id",
                filename_to_size={"foo": "string"},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_prepare(self, client: Fireworks) -> None:
        model = client.models.prepare(
            model_id="model_id",
            account_id="account_id",
        )
        assert_matches_type(object, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_prepare_with_all_params(self, client: Fireworks) -> None:
        model = client.models.prepare(
            model_id="model_id",
            account_id="account_id",
            precision="PRECISION_UNSPECIFIED",
            read_mask="readMask",
        )
        assert_matches_type(object, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_prepare(self, client: Fireworks) -> None:
        response = client.models.with_raw_response.prepare(
            model_id="model_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = response.parse()
        assert_matches_type(object, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_prepare(self, client: Fireworks) -> None:
        with client.models.with_streaming_response.prepare(
            model_id="model_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = response.parse()
            assert_matches_type(object, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_prepare(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.models.with_raw_response.prepare(
                model_id="model_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_id` but received ''"):
            client.models.with_raw_response.prepare(
                model_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_validate_upload(self, client: Fireworks) -> None:
        model = client.models.validate_upload(
            model_id="model_id",
            account_id="account_id",
        )
        assert_matches_type(object, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_validate_upload_with_all_params(self, client: Fireworks) -> None:
        model = client.models.validate_upload(
            model_id="model_id",
            account_id="account_id",
            config_only=True,
            skip_hf_config_validation=True,
            trust_remote_code=True,
        )
        assert_matches_type(object, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_validate_upload(self, client: Fireworks) -> None:
        response = client.models.with_raw_response.validate_upload(
            model_id="model_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = response.parse()
        assert_matches_type(object, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_validate_upload(self, client: Fireworks) -> None:
        with client.models.with_streaming_response.validate_upload(
            model_id="model_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = response.parse()
            assert_matches_type(object, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_validate_upload(self, client: Fireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.models.with_raw_response.validate_upload(
                model_id="model_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_id` but received ''"):
            client.models.with_raw_response.validate_upload(
                model_id="",
                account_id="account_id",
            )


class TestAsyncModels:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncFireworks) -> None:
        model = await async_client.models.create(
            account_id="account_id",
            model_id="modelId",
        )
        assert_matches_type(ModelCreateResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncFireworks) -> None:
        model = await async_client.models.create(
            account_id="account_id",
            model_id="modelId",
            cluster="cluster",
            model={
                "base_model_details": {
                    "checkpoint_format": "CHECKPOINT_FORMAT_UNSPECIFIED",
                    "model_type": "modelType",
                    "moe": True,
                    "parameter_count": "parameterCount",
                    "supports_fireattention": True,
                    "supports_mtp": True,
                    "tunable": True,
                    "world_size": 0,
                },
                "context_length": 0,
                "conversation_config": {
                    "style": "style",
                    "system": "system",
                    "template": "template",
                },
                "default_draft_model": "defaultDraftModel",
                "default_draft_token_count": 0,
                "deprecation_date": {
                    "day": 0,
                    "month": 0,
                    "year": 0,
                },
                "description": "description",
                "display_name": "displayName",
                "github_url": "githubUrl",
                "hugging_face_url": "huggingFaceUrl",
                "kind": "KIND_UNSPECIFIED",
                "peft_details": {
                    "base_model": "baseModel",
                    "r": 0,
                    "target_modules": ["string"],
                    "merge_addon_model_name": "mergeAddonModelName",
                },
                "public": True,
                "snapshot_type": "FULL_SNAPSHOT",
                "supports_image_input": True,
                "supports_lora": True,
                "supports_tools": True,
                "teft_details": {},
                "training_context_length": 0,
                "use_hf_apply_chat_template": True,
            },
        )
        assert_matches_type(ModelCreateResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncFireworks) -> None:
        response = await async_client.models.with_raw_response.create(
            account_id="account_id",
            model_id="modelId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = await response.parse()
        assert_matches_type(ModelCreateResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncFireworks) -> None:
        async with async_client.models.with_streaming_response.create(
            account_id="account_id",
            model_id="modelId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = await response.parse()
            assert_matches_type(ModelCreateResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.models.with_raw_response.create(
                account_id="",
                model_id="modelId",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncFireworks) -> None:
        model = await async_client.models.update(
            model_id="model_id",
            account_id="account_id",
        )
        assert_matches_type(ModelUpdateResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncFireworks) -> None:
        model = await async_client.models.update(
            model_id="model_id",
            account_id="account_id",
            base_model_details={
                "checkpoint_format": "CHECKPOINT_FORMAT_UNSPECIFIED",
                "model_type": "modelType",
                "moe": True,
                "parameter_count": "parameterCount",
                "supports_fireattention": True,
                "supports_mtp": True,
                "tunable": True,
                "world_size": 0,
            },
            context_length=0,
            conversation_config={
                "style": "style",
                "system": "system",
                "template": "template",
            },
            default_draft_model="defaultDraftModel",
            default_draft_token_count=0,
            deprecation_date={
                "day": 0,
                "month": 0,
                "year": 0,
            },
            description="description",
            display_name="displayName",
            github_url="githubUrl",
            hugging_face_url="huggingFaceUrl",
            kind="KIND_UNSPECIFIED",
            peft_details={
                "base_model": "baseModel",
                "r": 0,
                "target_modules": ["string"],
                "merge_addon_model_name": "mergeAddonModelName",
            },
            public=True,
            snapshot_type="FULL_SNAPSHOT",
            supports_image_input=True,
            supports_lora=True,
            supports_tools=True,
            teft_details={},
            training_context_length=0,
            use_hf_apply_chat_template=True,
        )
        assert_matches_type(ModelUpdateResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncFireworks) -> None:
        response = await async_client.models.with_raw_response.update(
            model_id="model_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = await response.parse()
        assert_matches_type(ModelUpdateResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncFireworks) -> None:
        async with async_client.models.with_streaming_response.update(
            model_id="model_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = await response.parse()
            assert_matches_type(ModelUpdateResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.models.with_raw_response.update(
                model_id="model_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_id` but received ''"):
            await async_client.models.with_raw_response.update(
                model_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncFireworks) -> None:
        model = await async_client.models.list(
            account_id="account_id",
        )
        assert_matches_type(ModelListResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncFireworks) -> None:
        model = await async_client.models.list(
            account_id="account_id",
            filter="filter",
            order_by="orderBy",
            page_size=0,
            page_token="pageToken",
            read_mask="readMask",
        )
        assert_matches_type(ModelListResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncFireworks) -> None:
        response = await async_client.models.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = await response.parse()
        assert_matches_type(ModelListResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncFireworks) -> None:
        async with async_client.models.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = await response.parse()
            assert_matches_type(ModelListResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.models.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncFireworks) -> None:
        model = await async_client.models.delete(
            model_id="model_id",
            account_id="account_id",
        )
        assert_matches_type(object, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncFireworks) -> None:
        response = await async_client.models.with_raw_response.delete(
            model_id="model_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = await response.parse()
        assert_matches_type(object, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncFireworks) -> None:
        async with async_client.models.with_streaming_response.delete(
            model_id="model_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = await response.parse()
            assert_matches_type(object, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.models.with_raw_response.delete(
                model_id="model_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_id` but received ''"):
            await async_client.models.with_raw_response.delete(
                model_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get(self, async_client: AsyncFireworks) -> None:
        model = await async_client.models.get(
            model_id="model_id",
            account_id="account_id",
        )
        assert_matches_type(ModelGetResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_with_all_params(self, async_client: AsyncFireworks) -> None:
        model = await async_client.models.get(
            model_id="model_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(ModelGetResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncFireworks) -> None:
        response = await async_client.models.with_raw_response.get(
            model_id="model_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = await response.parse()
        assert_matches_type(ModelGetResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncFireworks) -> None:
        async with async_client.models.with_streaming_response.get(
            model_id="model_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = await response.parse()
            assert_matches_type(ModelGetResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.models.with_raw_response.get(
                model_id="model_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_id` but received ''"):
            await async_client.models.with_raw_response.get(
                model_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_download_endpoint(self, async_client: AsyncFireworks) -> None:
        model = await async_client.models.get_download_endpoint(
            model_id="model_id",
            account_id="account_id",
        )
        assert_matches_type(ModelGetDownloadEndpointResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_download_endpoint_with_all_params(self, async_client: AsyncFireworks) -> None:
        model = await async_client.models.get_download_endpoint(
            model_id="model_id",
            account_id="account_id",
            read_mask="readMask",
        )
        assert_matches_type(ModelGetDownloadEndpointResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_download_endpoint(self, async_client: AsyncFireworks) -> None:
        response = await async_client.models.with_raw_response.get_download_endpoint(
            model_id="model_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = await response.parse()
        assert_matches_type(ModelGetDownloadEndpointResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_download_endpoint(self, async_client: AsyncFireworks) -> None:
        async with async_client.models.with_streaming_response.get_download_endpoint(
            model_id="model_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = await response.parse()
            assert_matches_type(ModelGetDownloadEndpointResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_download_endpoint(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.models.with_raw_response.get_download_endpoint(
                model_id="model_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_id` but received ''"):
            await async_client.models.with_raw_response.get_download_endpoint(
                model_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_upload_endpoint(self, async_client: AsyncFireworks) -> None:
        model = await async_client.models.get_upload_endpoint(
            model_id="model_id",
            account_id="account_id",
            filename_to_size={"foo": "string"},
        )
        assert_matches_type(ModelGetUploadEndpointResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_upload_endpoint_with_all_params(self, async_client: AsyncFireworks) -> None:
        model = await async_client.models.get_upload_endpoint(
            model_id="model_id",
            account_id="account_id",
            filename_to_size={"foo": "string"},
            enable_resumable_upload=True,
            read_mask="readMask",
        )
        assert_matches_type(ModelGetUploadEndpointResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_upload_endpoint(self, async_client: AsyncFireworks) -> None:
        response = await async_client.models.with_raw_response.get_upload_endpoint(
            model_id="model_id",
            account_id="account_id",
            filename_to_size={"foo": "string"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = await response.parse()
        assert_matches_type(ModelGetUploadEndpointResponse, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_upload_endpoint(self, async_client: AsyncFireworks) -> None:
        async with async_client.models.with_streaming_response.get_upload_endpoint(
            model_id="model_id",
            account_id="account_id",
            filename_to_size={"foo": "string"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = await response.parse()
            assert_matches_type(ModelGetUploadEndpointResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_upload_endpoint(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.models.with_raw_response.get_upload_endpoint(
                model_id="model_id",
                account_id="",
                filename_to_size={"foo": "string"},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_id` but received ''"):
            await async_client.models.with_raw_response.get_upload_endpoint(
                model_id="",
                account_id="account_id",
                filename_to_size={"foo": "string"},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_prepare(self, async_client: AsyncFireworks) -> None:
        model = await async_client.models.prepare(
            model_id="model_id",
            account_id="account_id",
        )
        assert_matches_type(object, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_prepare_with_all_params(self, async_client: AsyncFireworks) -> None:
        model = await async_client.models.prepare(
            model_id="model_id",
            account_id="account_id",
            precision="PRECISION_UNSPECIFIED",
            read_mask="readMask",
        )
        assert_matches_type(object, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_prepare(self, async_client: AsyncFireworks) -> None:
        response = await async_client.models.with_raw_response.prepare(
            model_id="model_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = await response.parse()
        assert_matches_type(object, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_prepare(self, async_client: AsyncFireworks) -> None:
        async with async_client.models.with_streaming_response.prepare(
            model_id="model_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = await response.parse()
            assert_matches_type(object, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_prepare(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.models.with_raw_response.prepare(
                model_id="model_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_id` but received ''"):
            await async_client.models.with_raw_response.prepare(
                model_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_validate_upload(self, async_client: AsyncFireworks) -> None:
        model = await async_client.models.validate_upload(
            model_id="model_id",
            account_id="account_id",
        )
        assert_matches_type(object, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_validate_upload_with_all_params(self, async_client: AsyncFireworks) -> None:
        model = await async_client.models.validate_upload(
            model_id="model_id",
            account_id="account_id",
            config_only=True,
            skip_hf_config_validation=True,
            trust_remote_code=True,
        )
        assert_matches_type(object, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_validate_upload(self, async_client: AsyncFireworks) -> None:
        response = await async_client.models.with_raw_response.validate_upload(
            model_id="model_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = await response.parse()
        assert_matches_type(object, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_validate_upload(self, async_client: AsyncFireworks) -> None:
        async with async_client.models.with_streaming_response.validate_upload(
            model_id="model_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = await response.parse()
            assert_matches_type(object, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_validate_upload(self, async_client: AsyncFireworks) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.models.with_raw_response.validate_upload(
                model_id="model_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_id` but received ''"):
            await async_client.models.with_raw_response.validate_upload(
                model_id="",
                account_id="account_id",
            )
