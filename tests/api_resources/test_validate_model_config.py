# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from fireworks_ai import Fireworks, AsyncFireworks

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestValidateModelConfig:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_validate(self, client: Fireworks) -> None:
        validate_model_config = client.validate_model_config.validate(
            config_json="configJson",
        )
        assert_matches_type(object, validate_model_config, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_validate_with_all_params(self, client: Fireworks) -> None:
        validate_model_config = client.validate_model_config.validate(
            config_json="configJson",
            tokenizer_config_json="tokenizerConfigJson",
        )
        assert_matches_type(object, validate_model_config, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_validate(self, client: Fireworks) -> None:
        response = client.validate_model_config.with_raw_response.validate(
            config_json="configJson",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        validate_model_config = response.parse()
        assert_matches_type(object, validate_model_config, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_validate(self, client: Fireworks) -> None:
        with client.validate_model_config.with_streaming_response.validate(
            config_json="configJson",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            validate_model_config = response.parse()
            assert_matches_type(object, validate_model_config, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncValidateModelConfig:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_validate(self, async_client: AsyncFireworks) -> None:
        validate_model_config = await async_client.validate_model_config.validate(
            config_json="configJson",
        )
        assert_matches_type(object, validate_model_config, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_validate_with_all_params(self, async_client: AsyncFireworks) -> None:
        validate_model_config = await async_client.validate_model_config.validate(
            config_json="configJson",
            tokenizer_config_json="tokenizerConfigJson",
        )
        assert_matches_type(object, validate_model_config, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_validate(self, async_client: AsyncFireworks) -> None:
        response = await async_client.validate_model_config.with_raw_response.validate(
            config_json="configJson",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        validate_model_config = await response.parse()
        assert_matches_type(object, validate_model_config, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_validate(self, async_client: AsyncFireworks) -> None:
        async with async_client.validate_model_config.with_streaming_response.validate(
            config_json="configJson",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            validate_model_config = await response.parse()
            assert_matches_type(object, validate_model_config, path=["response"])

        assert cast(Any, response.is_closed) is True
