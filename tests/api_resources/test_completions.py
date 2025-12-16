# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from fireworks import Fireworks, AsyncFireworks
from tests.utils import assert_matches_type
from fireworks.types import CompletionCreateResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCompletions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_overload_1(self, client: Fireworks) -> None:
        completion = client.completions.create(
            model="model",
            prompt="string",
        )
        assert_matches_type(CompletionCreateResponse, completion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params_overload_1(self, client: Fireworks) -> None:
        completion = client.completions.create(
            model="model",
            prompt="string",
            context_length_exceeded_behavior="error",
            echo=True,
            echo_last=0,
            frequency_penalty=0,
            ignore_eos=True,
            images=["string"],
            logit_bias={"foo": 0},
            logprobs=0,
            max_completion_tokens=0,
            max_tokens=0,
            metadata={"foo": "string"},
            min_p=0,
            mirostat_lr=0,
            mirostat_target=0,
            n=0,
            perf_metrics_in_response=True,
            prediction={
                "content": "string",
                "type": "content",
            },
            presence_penalty=0,
            prompt_cache_isolation_key="prompt_cache_isolation_key",
            raw_output=True,
            reasoning_effort="low",
            repetition_penalty=0,
            response_format={
                "type": "json_object",
                "grammar": "grammar",
                "json_schema": "string",
                "schema": "string",
            },
            return_token_ids=True,
            seed=0,
            speculation="string",
            stop="string",
            stream=False,
            temperature=0,
            top_k=0,
            top_logprobs=0,
            top_p=0,
            typical_p=0,
            user="user",
        )
        assert_matches_type(CompletionCreateResponse, completion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_overload_1(self, client: Fireworks) -> None:
        response = client.completions.with_raw_response.create(
            model="model",
            prompt="string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        completion = response.parse()
        assert_matches_type(CompletionCreateResponse, completion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_overload_1(self, client: Fireworks) -> None:
        with client.completions.with_streaming_response.create(
            model="model",
            prompt="string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            completion = response.parse()
            assert_matches_type(CompletionCreateResponse, completion, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_overload_2(self, client: Fireworks) -> None:
        completion_stream = client.completions.create(
            model="model",
            prompt="string",
            stream=True,
        )
        completion_stream.response.close()

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params_overload_2(self, client: Fireworks) -> None:
        completion_stream = client.completions.create(
            model="model",
            prompt="string",
            stream=True,
            context_length_exceeded_behavior="error",
            echo=True,
            echo_last=0,
            frequency_penalty=0,
            ignore_eos=True,
            images=["string"],
            logit_bias={"foo": 0},
            logprobs=0,
            max_completion_tokens=0,
            max_tokens=0,
            metadata={"foo": "string"},
            min_p=0,
            mirostat_lr=0,
            mirostat_target=0,
            n=0,
            perf_metrics_in_response=True,
            prediction={
                "content": "string",
                "type": "content",
            },
            presence_penalty=0,
            prompt_cache_isolation_key="prompt_cache_isolation_key",
            raw_output=True,
            reasoning_effort="low",
            repetition_penalty=0,
            response_format={
                "type": "json_object",
                "grammar": "grammar",
                "json_schema": "string",
                "schema": "string",
            },
            return_token_ids=True,
            seed=0,
            speculation="string",
            stop="string",
            temperature=0,
            top_k=0,
            top_logprobs=0,
            top_p=0,
            typical_p=0,
            user="user",
        )
        completion_stream.response.close()

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_overload_2(self, client: Fireworks) -> None:
        response = client.completions.with_raw_response.create(
            model="model",
            prompt="string",
            stream=True,
        )

        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        stream = response.parse()
        stream.close()

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_overload_2(self, client: Fireworks) -> None:
        with client.completions.with_streaming_response.create(
            model="model",
            prompt="string",
            stream=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            stream = response.parse()
            stream.close()

        assert cast(Any, response.is_closed) is True


class TestAsyncCompletions:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_overload_1(self, async_client: AsyncFireworks) -> None:
        completion = await async_client.completions.create(
            model="model",
            prompt="string",
        )
        assert_matches_type(CompletionCreateResponse, completion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params_overload_1(self, async_client: AsyncFireworks) -> None:
        completion = await async_client.completions.create(
            model="model",
            prompt="string",
            context_length_exceeded_behavior="error",
            echo=True,
            echo_last=0,
            frequency_penalty=0,
            ignore_eos=True,
            images=["string"],
            logit_bias={"foo": 0},
            logprobs=0,
            max_completion_tokens=0,
            max_tokens=0,
            metadata={"foo": "string"},
            min_p=0,
            mirostat_lr=0,
            mirostat_target=0,
            n=0,
            perf_metrics_in_response=True,
            prediction={
                "content": "string",
                "type": "content",
            },
            presence_penalty=0,
            prompt_cache_isolation_key="prompt_cache_isolation_key",
            raw_output=True,
            reasoning_effort="low",
            repetition_penalty=0,
            response_format={
                "type": "json_object",
                "grammar": "grammar",
                "json_schema": "string",
                "schema": "string",
            },
            return_token_ids=True,
            seed=0,
            speculation="string",
            stop="string",
            stream=False,
            temperature=0,
            top_k=0,
            top_logprobs=0,
            top_p=0,
            typical_p=0,
            user="user",
        )
        assert_matches_type(CompletionCreateResponse, completion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_overload_1(self, async_client: AsyncFireworks) -> None:
        response = await async_client.completions.with_raw_response.create(
            model="model",
            prompt="string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        completion = await response.parse()
        assert_matches_type(CompletionCreateResponse, completion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_overload_1(self, async_client: AsyncFireworks) -> None:
        async with async_client.completions.with_streaming_response.create(
            model="model",
            prompt="string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            completion = await response.parse()
            assert_matches_type(CompletionCreateResponse, completion, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_overload_2(self, async_client: AsyncFireworks) -> None:
        completion_stream = await async_client.completions.create(
            model="model",
            prompt="string",
            stream=True,
        )
        await completion_stream.response.aclose()

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params_overload_2(self, async_client: AsyncFireworks) -> None:
        completion_stream = await async_client.completions.create(
            model="model",
            prompt="string",
            stream=True,
            context_length_exceeded_behavior="error",
            echo=True,
            echo_last=0,
            frequency_penalty=0,
            ignore_eos=True,
            images=["string"],
            logit_bias={"foo": 0},
            logprobs=0,
            max_completion_tokens=0,
            max_tokens=0,
            metadata={"foo": "string"},
            min_p=0,
            mirostat_lr=0,
            mirostat_target=0,
            n=0,
            perf_metrics_in_response=True,
            prediction={
                "content": "string",
                "type": "content",
            },
            presence_penalty=0,
            prompt_cache_isolation_key="prompt_cache_isolation_key",
            raw_output=True,
            reasoning_effort="low",
            repetition_penalty=0,
            response_format={
                "type": "json_object",
                "grammar": "grammar",
                "json_schema": "string",
                "schema": "string",
            },
            return_token_ids=True,
            seed=0,
            speculation="string",
            stop="string",
            temperature=0,
            top_k=0,
            top_logprobs=0,
            top_p=0,
            typical_p=0,
            user="user",
        )
        await completion_stream.response.aclose()

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_overload_2(self, async_client: AsyncFireworks) -> None:
        response = await async_client.completions.with_raw_response.create(
            model="model",
            prompt="string",
            stream=True,
        )

        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        stream = await response.parse()
        await stream.close()

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_overload_2(self, async_client: AsyncFireworks) -> None:
        async with async_client.completions.with_streaming_response.create(
            model="model",
            prompt="string",
            stream=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            stream = await response.parse()
            await stream.close()

        assert cast(Any, response.is_closed) is True
