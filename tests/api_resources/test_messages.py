# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from fireworks import Fireworks, AsyncFireworks
from tests.utils import assert_matches_type
from fireworks.types import MessageCreateResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestMessages:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Fireworks) -> None:
        message = client.messages.create(
            messages=[
                {
                    "content": "Hello, world",
                    "role": "user",
                }
            ],
            model="claude-opus-4-6",
        )
        assert_matches_type(MessageCreateResponse, message, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Fireworks) -> None:
        message = client.messages.create(
            messages=[
                {
                    "content": "Hello, world",
                    "role": "user",
                }
            ],
            model="claude-opus-4-6",
            max_tokens=1024,
            metadata={"user_id": "13803d75-b4b5-4c3e-b2a2-6f21399b021b"},
            output_config={
                "effort": "low",
                "format": {
                    "schema": {"foo": "bar"},
                    "type": "json_schema",
                },
            },
            raw_output=True,
            stop_sequences=["string"],
            stream=True,
            system=[
                {
                    "text": "Today's date is 2024-06-01.",
                    "type": "text",
                    "cache_control": {
                        "type": "ephemeral",
                        "ttl": "5m",
                    },
                    "citations": [
                        {
                            "cited_text": "cited_text",
                            "document_index": 0,
                            "document_title": "x",
                            "end_char_index": 0,
                            "start_char_index": 0,
                            "type": "char_location",
                        }
                    ],
                }
            ],
            temperature=1,
            thinking={
                "budget_tokens": 1024,
                "type": "enabled",
            },
            tool_choice={
                "type": "auto",
                "disable_parallel_tool_use": True,
            },
            tools=[
                {
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "location": "bar",
                            "unit": "bar",
                        },
                        "required": ["location"],
                    },
                    "name": "name",
                    "description": "Get the current weather in a given location",
                    "strict": True,
                    "type": "custom",
                }
            ],
            top_k=5,
            top_p=0.7,
        )
        assert_matches_type(MessageCreateResponse, message, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Fireworks) -> None:
        response = client.messages.with_raw_response.create(
            messages=[
                {
                    "content": "Hello, world",
                    "role": "user",
                }
            ],
            model="claude-opus-4-6",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        message = response.parse()
        assert_matches_type(MessageCreateResponse, message, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Fireworks) -> None:
        with client.messages.with_streaming_response.create(
            messages=[
                {
                    "content": "Hello, world",
                    "role": "user",
                }
            ],
            model="claude-opus-4-6",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            message = response.parse()
            assert_matches_type(MessageCreateResponse, message, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncMessages:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncFireworks) -> None:
        message = await async_client.messages.create(
            messages=[
                {
                    "content": "Hello, world",
                    "role": "user",
                }
            ],
            model="claude-opus-4-6",
        )
        assert_matches_type(MessageCreateResponse, message, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncFireworks) -> None:
        message = await async_client.messages.create(
            messages=[
                {
                    "content": "Hello, world",
                    "role": "user",
                }
            ],
            model="claude-opus-4-6",
            max_tokens=1024,
            metadata={"user_id": "13803d75-b4b5-4c3e-b2a2-6f21399b021b"},
            output_config={
                "effort": "low",
                "format": {
                    "schema": {"foo": "bar"},
                    "type": "json_schema",
                },
            },
            raw_output=True,
            stop_sequences=["string"],
            stream=True,
            system=[
                {
                    "text": "Today's date is 2024-06-01.",
                    "type": "text",
                    "cache_control": {
                        "type": "ephemeral",
                        "ttl": "5m",
                    },
                    "citations": [
                        {
                            "cited_text": "cited_text",
                            "document_index": 0,
                            "document_title": "x",
                            "end_char_index": 0,
                            "start_char_index": 0,
                            "type": "char_location",
                        }
                    ],
                }
            ],
            temperature=1,
            thinking={
                "budget_tokens": 1024,
                "type": "enabled",
            },
            tool_choice={
                "type": "auto",
                "disable_parallel_tool_use": True,
            },
            tools=[
                {
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "location": "bar",
                            "unit": "bar",
                        },
                        "required": ["location"],
                    },
                    "name": "name",
                    "description": "Get the current weather in a given location",
                    "strict": True,
                    "type": "custom",
                }
            ],
            top_k=5,
            top_p=0.7,
        )
        assert_matches_type(MessageCreateResponse, message, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncFireworks) -> None:
        response = await async_client.messages.with_raw_response.create(
            messages=[
                {
                    "content": "Hello, world",
                    "role": "user",
                }
            ],
            model="claude-opus-4-6",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        message = await response.parse()
        assert_matches_type(MessageCreateResponse, message, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncFireworks) -> None:
        async with async_client.messages.with_streaming_response.create(
            messages=[
                {
                    "content": "Hello, world",
                    "role": "user",
                }
            ],
            model="claude-opus-4-6",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            message = await response.parse()
            assert_matches_type(MessageCreateResponse, message, path=["response"])

        assert cast(Any, response.is_closed) is True
