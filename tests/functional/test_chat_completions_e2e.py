"""End-to-end tests for chat completions against the live Fireworks API.

These tests require FIREWORKS_API_KEY to be set in the environment.
Run with: pytest tests/functional/ -m e2e --timeout=60 -v
"""

from __future__ import annotations

import os

import pytest

from fireworks import Fireworks, AsyncFireworks

pytestmark = [
    pytest.mark.e2e,
    pytest.mark.timeout(60),
    pytest.mark.skipif(
        not os.environ.get("FIREWORKS_API_KEY"),
        reason="FIREWORKS_API_KEY not set",
    ),
]

# Use a high-traffic model that's reliably warm (serverless models may 503 during cold start).
# Override via E2E_TEST_MODEL env var if needed.
TEST_MODEL = os.environ.get("E2E_TEST_MODEL", "accounts/fireworks/models/llama-v3p3-70b-instruct")


class TestChatCompletionsE2E:
    """Sync client tests for chat completions."""

    def test_basic_completion(self) -> None:
        client = Fireworks()
        response = client.chat.completions.create(
            model=TEST_MODEL,
            messages=[{"role": "user", "content": "Say the word 'hello' and nothing else."}],
            max_tokens=10,
        )
        assert response.choices, "Expected at least one choice"
        assert response.choices[0].message.content, "Expected non-empty content"
        assert response.model, "Expected model field to be set"
        assert response.usage, "Expected usage info"

    def test_completion_with_system_message(self) -> None:
        client = Fireworks()
        response = client.chat.completions.create(
            model=TEST_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Reply in exactly one word."},
                {"role": "user", "content": "What color is the sky?"},
            ],
            max_tokens=10,
            temperature=0,
        )
        assert response.choices
        assert response.choices[0].message.content

    def test_completion_with_parameters(self) -> None:
        client = Fireworks()
        response = client.chat.completions.create(
            model=TEST_MODEL,
            messages=[{"role": "user", "content": "Count to 3."}],
            max_tokens=20,
            temperature=0,
            top_p=1.0,
            n=1,
        )
        assert response.choices
        assert len(response.choices) == 1

    def test_streaming_completion(self) -> None:
        client = Fireworks()
        chunks: list[object] = []
        with client.chat.completions.create(
            model=TEST_MODEL,
            messages=[{"role": "user", "content": "Say hello"}],
            max_tokens=10,
            stream=True,
        ) as stream:
            for chunk in stream:
                chunks.append(chunk)
        assert len(chunks) > 0, "Expected at least one streamed chunk"

    def test_multi_turn_conversation(self) -> None:
        client = Fireworks()
        response = client.chat.completions.create(
            model=TEST_MODEL,
            messages=[
                {"role": "user", "content": "My name is Alice."},
                {"role": "assistant", "content": "Nice to meet you, Alice!"},
                {"role": "user", "content": "What is my name?"},
            ],
            max_tokens=20,
            temperature=0,
        )
        assert response.choices
        content = response.choices[0].message.content
        assert isinstance(content, str)
        assert "alice" in content.lower(), f"Expected 'alice' in response, got: {content}"

    def test_raw_response(self) -> None:
        client = Fireworks()
        response = client.chat.completions.with_raw_response.create(
            model=TEST_MODEL,
            messages=[{"role": "user", "content": "Say hello"}],
            max_tokens=10,
        )
        assert response.status_code == 200
        assert response.headers.get("content-type")
        parsed = response.parse()
        assert parsed.choices


class TestAsyncChatCompletionsE2E:
    """Async client tests for chat completions."""

    async def test_basic_completion(self) -> None:
        async with AsyncFireworks() as client:
            response = await client.chat.completions.create(
                model=TEST_MODEL,
                messages=[{"role": "user", "content": "Say the word 'hello' and nothing else."}],
                max_tokens=10,
            )
            assert response.choices
            assert response.choices[0].message.content

    async def test_streaming_completion(self) -> None:
        async with AsyncFireworks() as client:
            chunks: list[object] = []
            stream = await client.chat.completions.create(
                model=TEST_MODEL,
                messages=[{"role": "user", "content": "Say hello"}],
                max_tokens=10,
                stream=True,
            )
            async for chunk in stream:
                chunks.append(chunk)
            assert len(chunks) > 0, "Expected at least one streamed chunk"


class TestCompletionsE2E:
    """Sync client tests for legacy completions endpoint."""

    def test_basic_completion(self) -> None:
        client = Fireworks()
        response = client.completions.create(
            model=TEST_MODEL,
            prompt="The capital of France is",
            max_tokens=10,
        )
        assert response.choices, "Expected at least one choice"
        assert response.choices[0].text, "Expected non-empty text"


class TestModelsE2E:
    """Tests for model listing."""

    def test_list_models(self) -> None:
        client = Fireworks()
        models = client.models.list(account_id="fireworks")
        model_list = list(models)
        assert len(model_list) > 0, "Expected at least one model"
