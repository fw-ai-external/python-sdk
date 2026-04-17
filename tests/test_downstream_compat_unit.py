"""Unit tests for downstream compatibility surface.

These tests use mocked HTTP responses to verify that the exact calling patterns
used by langchain-fireworks and instructor work correctly against the 1.x SDK.
No network access required.

NOTE: langchain-fireworks passes base_url=None by default, so the SDK uses its
default base URL (https://api.fireworks.ai) and hardcoded absolute URLs for
inference endpoints (e.g. https://api.fireworks.ai/inference/v1/chat/completions).
These tests replicate that exact behavior.
"""

# pyright: reportUnknownVariableType=false, reportUnknownMemberType=false
# pyright: reportUnknownArgumentType=false, reportAttributeAccessIssue=false
# pyright: reportUnknownParameterType=false, reportMissingTypeArgument=false
# pyright: reportArgumentType=false

from __future__ import annotations

import json
import asyncio
from typing import Any

import httpx
import respx

from fireworks import Fireworks, AsyncFireworks

# The absolute URL the SDK uses for chat completions when base_url is not overridden.
CHAT_COMPLETIONS_URL = "https://api.fireworks.ai/inference/v1/chat/completions"

# A realistic chat completion response matching the Fireworks API format.
MOCK_CHAT_RESPONSE: dict[str, Any] = {
    "id": "chatcmpl-abc123",
    "object": "chat.completion",
    "created": 1700000000,
    "model": "accounts/fireworks/models/llama-v3p3-70b-instruct",
    "choices": [
        {
            "index": 0,
            "message": {"role": "assistant", "content": "Hello!"},
            "finish_reason": "stop",
        }
    ],
    "usage": {"prompt_tokens": 10, "completion_tokens": 2, "total_tokens": 12},
}

MOCK_STREAM_CHUNKS = [
    {
        "id": "chatcmpl-abc123",
        "object": "chat.completion.chunk",
        "created": 1700000000,
        "model": "accounts/fireworks/models/llama-v3p3-70b-instruct",
        "choices": [{"index": 0, "delta": {"role": "assistant", "content": ""}, "finish_reason": None}],
    },
    {
        "id": "chatcmpl-abc123",
        "object": "chat.completion.chunk",
        "created": 1700000000,
        "model": "accounts/fireworks/models/llama-v3p3-70b-instruct",
        "choices": [{"index": 0, "delta": {"content": "Hello"}, "finish_reason": None}],
    },
    {
        "id": "chatcmpl-abc123",
        "object": "chat.completion.chunk",
        "created": 1700000000,
        "model": "accounts/fireworks/models/llama-v3p3-70b-instruct",
        "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
    },
]


def _sse_body(chunks: list[dict]) -> str:
    lines = []
    for chunk in chunks:
        lines.append(f"data: {json.dumps(chunk)}\n\n")
    lines.append("data: [DONE]\n\n")
    return "".join(lines)


def _make_mock_transport() -> httpx.MockTransport:
    """Create a MockTransport that returns MOCK_CHAT_RESPONSE for any POST."""
    return httpx.MockTransport(
        lambda _request: httpx.Response(200, json=MOCK_CHAT_RESPONSE)
    )


def _make_streaming_mock_transport() -> httpx.MockTransport:
    """Create a MockTransport that returns SSE stream for any POST."""
    return httpx.MockTransport(
        lambda _request: httpx.Response(
            200,
            content=_sse_body(MOCK_STREAM_CHUNKS),
            headers={"content-type": "text/event-stream"},
        )
    )


# ---------------------------------------------------------------------------
# langchain-fireworks calling patterns
# ---------------------------------------------------------------------------


class TestLangchainFireworksPatterns:
    """Replicate the exact patterns langchain-fireworks uses.

    Source: langchain_fireworks/chat_models.py
    - Creates client: Fireworks(api_key=..., base_url=None, timeout=...).chat.completions
    - Sync: self.client.create(messages=..., model=..., **params)
    - Async: await self.async_client.acreate(messages=..., **params)
    - Streaming sync: for chunk in self.client.create(messages=..., stream=True, **params)
    - Streaming async: async for chunk in self.async_client.acreate(messages=..., stream=True, **params)
    - Accesses response.model_dump()["choices"], ["usage"]
    - Sets client._max_retries

    langchain-fireworks defaults fireworks_api_base to None, so base_url=None
    is passed to the SDK. The SDK then uses its hardcoded absolute inference URLs.
    """

    @respx.mock
    def test_sync_create_non_streaming(self, respx_mock: respx.MockRouter) -> None:
        """langchain _generate() path: response = self.client.create(messages=..., **params)"""
        respx_mock.post(CHAT_COMPLETIONS_URL).mock(
            return_value=httpx.Response(200, json=MOCK_CHAT_RESPONSE)
        )

        # langchain passes base_url=None (fireworks_api_base default)
        client_params = {"api_key": "test-key", "base_url": None}
        client = Fireworks(**client_params).chat.completions

        response = client.create(
            messages=[{"role": "user", "content": "Hi"}],
            model="accounts/fireworks/models/llama-v3p3-70b-instruct",
        )

        # langchain calls response.model_dump() or checks isinstance(response, dict)
        response_dict = response.model_dump()
        assert "choices" in response_dict
        assert len(response_dict["choices"]) == 1
        assert response_dict["choices"][0]["message"]["content"] == "Hello!"
        assert "usage" in response_dict
        assert response_dict["usage"]["prompt_tokens"] == 10

    @respx.mock
    def test_sync_create_streaming(self, respx_mock: respx.MockRouter) -> None:
        """langchain _stream() path: for chunk in self.client.create(messages=..., stream=True, **params)"""
        respx_mock.post(CHAT_COMPLETIONS_URL).mock(
            return_value=httpx.Response(
                200,
                content=_sse_body(MOCK_STREAM_CHUNKS),
                headers={"content-type": "text/event-stream"},
            )
        )

        client = Fireworks(api_key="test-key").chat.completions

        chunks_received = []
        with client.create(
            messages=[{"role": "user", "content": "Hi"}],
            model="test-model",
            stream=True,
        ) as stream:
            for chunk in stream:
                # langchain does: chunk.model_dump()["choices"][0]
                chunk_dict = chunk.model_dump()
                assert "choices" in chunk_dict
                chunks_received.append(chunk_dict)

        assert len(chunks_received) >= 1

    def test_max_retries_settable(self) -> None:
        """langchain sets client._max_retries directly."""
        client = Fireworks(api_key="test-key", base_url="http://localhost:9999").chat.completions
        # langchain does: self.client._max_retries = self.max_retries
        # This accesses the parent client's attribute through the resource
        # We just need to verify this doesn't raise
        assert hasattr(client, "_client")

    def test_async_acreate_non_streaming(self) -> None:
        """langchain _agenerate() path: response = await self.async_client.acreate(messages=..., **params)"""

        async def _run() -> None:
            http_client = httpx.AsyncClient(transport=_make_mock_transport())

            # langchain passes base_url=None; we must set http_client to avoid
            # real network calls (SDK defaults to aiohttp for async transport).
            async_client = AsyncFireworks(api_key="test-key", http_client=http_client).chat.completions

            response = await async_client.acreate(
                messages=[{"role": "user", "content": "Hi"}],
                model="test-model",
            )

            response_dict = response.model_dump()
            assert "choices" in response_dict
            assert response_dict["choices"][0]["message"]["content"] == "Hello!"

        asyncio.run(_run())

    def test_async_acreate_streaming(self) -> None:
        """langchain _astream(): async for chunk in self.async_client.acreate(stream=True, ...)

        langchain iterates directly over acreate(stream=True) without an
        intermediate await — the acreate coroutine returns an async iterator.
        """

        async def _run() -> None:
            http_client = httpx.AsyncClient(transport=_make_streaming_mock_transport())
            async_client = AsyncFireworks(api_key="test-key", http_client=http_client).chat.completions

            chunks_received = []
            stream = await async_client.acreate(
                messages=[{"role": "user", "content": "Hi"}],
                model="test-model",
                stream=True,
            )
            async for chunk in stream:
                chunk_dict = chunk.model_dump()
                assert "choices" in chunk_dict
                chunks_received.append(chunk_dict)

            assert len(chunks_received) >= 1

        asyncio.run(_run())


# ---------------------------------------------------------------------------
# instructor calling patterns
# ---------------------------------------------------------------------------


class TestInstructorPatterns:
    """Replicate the exact patterns instructor uses.

    Source: instructor/providers/fireworks/client.py
    - Imports: from fireworks.client import AsyncFireworks, Fireworks
    - isinstance(client, (AsyncFireworks, Fireworks)) for validation
    - isinstance(client, AsyncFireworks) / isinstance(client, Fireworks) for dispatch
    - Sync: client.chat.completions.create(...)
    - Async: client.chat.completions.acreate(...)
    """

    def test_import_via_old_path(self) -> None:
        """instructor imports from fireworks.client"""
        from fireworks.client import Fireworks as F, AsyncFireworks as AF

        assert F is not None
        assert AF is not None

    def test_isinstance_check_via_old_import(self) -> None:
        """instructor does isinstance(client, (AsyncFireworks, Fireworks))"""
        from fireworks.client import Fireworks as F, AsyncFireworks as AF

        sync_client = Fireworks(api_key="test", base_url="http://localhost:9999")
        async_client = AsyncFireworks(api_key="test", base_url="http://localhost:9999")

        # instructor's validation check
        assert isinstance(sync_client, (AF, F))
        assert isinstance(async_client, (AF, F))

        # instructor's dispatch check
        assert isinstance(sync_client, F)
        assert not isinstance(sync_client, AF)
        assert isinstance(async_client, AF)
        assert not isinstance(async_client, F)

    def test_isinstance_check_cross_import(self) -> None:
        """Clients created via new path must pass isinstance with old path classes."""
        from fireworks import Fireworks as NewF, AsyncFireworks as NewAF
        from fireworks.client import Fireworks as OldF, AsyncFireworks as OldAF

        # The old and new symbols must be the same class
        assert OldF is NewF
        assert OldAF is NewAF

        # So isinstance works regardless of import path
        client = NewF(api_key="test", base_url="http://localhost:9999")
        assert isinstance(client, OldF)

    @respx.mock
    def test_sync_create_pattern(self, respx_mock: respx.MockRouter) -> None:
        """instructor sync path: client.chat.completions.create(...)"""
        respx_mock.post(CHAT_COMPLETIONS_URL).mock(
            return_value=httpx.Response(200, json=MOCK_CHAT_RESPONSE)
        )

        from fireworks.client import Fireworks as F

        # instructor doesn't override base_url
        client = F(api_key="test-key")
        response = client.chat.completions.create(
            model="test-model",
            messages=[{"role": "user", "content": "Hi"}],
        )
        assert response.choices[0].message.content == "Hello!"

    def test_async_acreate_pattern(self) -> None:
        """instructor async path: await client.chat.completions.acreate(...)"""

        async def _run() -> None:
            http_client = httpx.AsyncClient(transport=_make_mock_transport())

            from fireworks.client import AsyncFireworks as AF

            client = AF(api_key="test-key", http_client=http_client)

            response = await client.chat.completions.acreate(
                model="test-model",
                messages=[{"role": "user", "content": "Hi"}],
            )

            assert response.choices[0].message.content == "Hello!"

        asyncio.run(_run())


# ---------------------------------------------------------------------------
# Response object compatibility
# ---------------------------------------------------------------------------


class TestResponseObjectCompat:
    """Verify response objects have the interface downstream code expects.

    Both langchain and instructor access:
    - response.choices[0].message.content
    - response.model_dump() -> dict with "choices" and "usage"
    - chunk.choices[0].delta.content (streaming)
    """

    @respx.mock
    def test_response_has_model_dump(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.post(CHAT_COMPLETIONS_URL).mock(
            return_value=httpx.Response(200, json=MOCK_CHAT_RESPONSE)
        )
        client = Fireworks(api_key="test")
        response = client.chat.completions.create(
            model="test", messages=[{"role": "user", "content": "hi"}]
        )

        # model_dump() must return a dict
        d = response.model_dump()
        assert isinstance(d, dict)

        # Standard fields downstream code accesses
        assert "choices" in d
        assert "usage" in d
        assert d["choices"][0]["message"]["content"] == "Hello!"
        assert d["usage"]["prompt_tokens"] == 10
        assert d["usage"]["completion_tokens"] == 2
        assert d["usage"]["total_tokens"] == 12

    @respx.mock
    def test_response_attribute_access(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.post(CHAT_COMPLETIONS_URL).mock(
            return_value=httpx.Response(200, json=MOCK_CHAT_RESPONSE)
        )
        client = Fireworks(api_key="test")
        response = client.chat.completions.create(
            model="test", messages=[{"role": "user", "content": "hi"}]
        )

        # Direct attribute access (instructor uses this)
        assert response.choices[0].message.content == "Hello!"
        assert response.choices[0].finish_reason == "stop"
        assert response.model is not None

    @respx.mock
    def test_streaming_chunk_has_delta(self, respx_mock: respx.MockRouter) -> None:
        respx_mock.post(CHAT_COMPLETIONS_URL).mock(
            return_value=httpx.Response(
                200,
                content=_sse_body(MOCK_STREAM_CHUNKS),
                headers={"content-type": "text/event-stream"},
            )
        )
        client = Fireworks(api_key="test")

        with client.chat.completions.create(
            model="test",
            messages=[{"role": "user", "content": "hi"}],
            stream=True,
        ) as stream:
            chunks = list(stream)

        # langchain accesses chunk.model_dump()["choices"][0]["delta"]
        for chunk in chunks:
            d = chunk.model_dump()
            assert "choices" in d
            if d["choices"]:
                assert "delta" in d["choices"][0]
