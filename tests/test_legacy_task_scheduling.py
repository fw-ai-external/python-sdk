from __future__ import annotations

import asyncio
from typing import Any

import httpx
import pytest

from fireworks import AsyncFireworks

pytestmark = pytest.mark.filterwarnings("ignore:acreate\\(\\) is deprecated:DeprecationWarning")


@pytest.mark.parametrize("chat", [False, True])
@pytest.mark.parametrize("schedule", [False, True])
async def test_legacy_acreate_supports_task_scheduling(chat: bool, schedule: bool) -> None:
    calls: list[httpx.Request] = []

    def respond(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(
            200,
            json={
                "id": "result",
                "choices": [],
                "created": 0,
                "model": "test",
                "object": "chat.completion" if chat else "text_completion",
            },
        )

    async with AsyncFireworks(
        api_key="test", http_client=httpx.AsyncClient(transport=httpx.MockTransport(respond))
    ) as client:
        resource: Any = client.chat.completions if chat else client.completions
        kwargs = (
            {"model": "test", "messages": [{"role": "user", "content": "Hi"}]}
            if chat
            else {"model": "test", "prompt": "Hi"}
        )
        call = resource.acreate(**kwargs)
        try:
            result = await asyncio.create_task(call) if schedule else await call
        finally:
            # Also close the original coroutine when the pre-fix create_task rejects it.
            if hasattr(call, "close"):
                call.close()
            else:
                call._coro.close()
    assert result.id == "result"
    assert len(calls) == 1


@pytest.mark.parametrize("chat", [False, True])
async def test_scheduled_legacy_acreate_propagates_cancellation(chat: bool) -> None:
    started = asyncio.Event()
    cancelled = asyncio.Event()

    async def respond(_request: httpx.Request) -> httpx.Response:
        started.set()
        try:
            await asyncio.Event().wait()
        finally:
            cancelled.set()
        raise AssertionError("unreachable")

    async with AsyncFireworks(
        api_key="test", http_client=httpx.AsyncClient(transport=httpx.MockTransport(respond))
    ) as client:
        resource: Any = client.chat.completions if chat else client.completions
        kwargs = (
            {"model": "test", "messages": [{"role": "user", "content": "Hi"}]}
            if chat
            else {"model": "test", "prompt": "Hi"}
        )
        call = resource.acreate(**kwargs)
        try:
            task = asyncio.create_task(call)
        except TypeError:
            call._coro.close()
            raise
        await asyncio.wait_for(started.wait(), timeout=1)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
    assert cancelled.is_set()


@pytest.mark.parametrize("chat", [False, True])
async def test_legacy_acreate_still_supports_direct_stream_iteration(chat: bool) -> None:
    import json

    choice = {"index": 0, "delta": {"content": "Hi"}} if chat else {"index": 0, "text": "Hi"}
    chunk = {
        "id": "chunk",
        "choices": [choice],
        "created": 0,
        "model": "test",
        "object": "chat.completion.chunk" if chat else "text_completion",
    }

    def respond(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            text="data: " + json.dumps(chunk) + "\n\ndata: [DONE]\n\n",
        )

    async with AsyncFireworks(
        api_key="test", http_client=httpx.AsyncClient(transport=httpx.MockTransport(respond))
    ) as client:
        resource: Any = client.chat.completions if chat else client.completions
        kwargs = (
            {"model": "test", "messages": [{"role": "user", "content": "Hi"}]}
            if chat
            else {"model": "test", "prompt": "Hi"}
        )
        chunks = [item async for item in resource.acreate(stream=True, **kwargs)]
    assert len(chunks) == 1
    assert chunks[0].id == "chunk"
