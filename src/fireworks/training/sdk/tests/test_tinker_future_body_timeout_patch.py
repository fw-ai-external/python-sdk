from __future__ import annotations

import time
import asyncio
from typing import Any, cast
from contextlib import contextmanager
from collections.abc import Generator, AsyncIterator

import httpx
import orjson
from tinker import types
from tinker.lib import api_future_impl
from tinker.proto import tinker_public_pb2
from pyqwest.httpx import AsyncPyqwestTransport
from tinker._client import AsyncTinker
from tinker.lib.api_future_impl import _UNCOMPUTED, _APIFuture
from tinker.lib.internal_client_holder import BytesSemaphore
from tinker.types.forward_backward_output import ForwardBackwardOutput
from tinker.lib.client_connection_pool_type import ClientConnectionPoolType

from fireworks.training.sdk.patches import _tinker_future_body_timeout_patch


class _ResponseBody:
    def __init__(
        self,
        chunks: list[bytes],
        *,
        delay: float = 0,
        stall: bool = False,
    ) -> None:
        self._chunks = chunks
        self._delay = delay
        self._stall = stall
        self._never_finishes = asyncio.Event()
        self.started = asyncio.Event()

    async def __aiter__(self) -> AsyncIterator[bytes]:
        self.started.set()
        if self._delay:
            await asyncio.sleep(self._delay)
        for chunk in self._chunks:
            yield chunk
        if self._stall:
            await self._never_finishes.wait()


class _PyqwestResponse:
    def __init__(
        self,
        body: _ResponseBody,
        *,
        content_type: str = "application/json",
    ) -> None:
        self.status = 200
        self.headers = {"content-type": content_type}
        self.trailers: dict[str, str] = {}
        self.content = body
        self.closed = asyncio.Event()

    async def aclose(self) -> None:
        self.closed.set()


class _StallFirstTransport:
    def __init__(self) -> None:
        self.requests: list[Any] = []
        self.stalled_response = _PyqwestResponse(_ResponseBody([b'{"ok":'], stall=True))
        self.closed_before_retry = False

    async def execute(self, request: Any) -> _PyqwestResponse:
        self.requests.append(request)
        if len(self.requests) == 1:
            return self.stalled_response
        self.closed_before_retry = self.stalled_response.closed.is_set()
        return _PyqwestResponse(_ResponseBody([b'{"ok":true}']))


class _DelayedTransport:
    def __init__(self, *, header_delay: float, body_delay: float) -> None:
        self.header_delay = header_delay
        self.response = _PyqwestResponse(_ResponseBody([b'{"ok":true}'], delay=body_delay))
        self.requests: list[Any] = []

    async def execute(self, request: Any) -> _PyqwestResponse:
        self.requests.append(request)
        await asyncio.sleep(self.header_delay)
        return self.response


class _SingleResponseTransport:
    def __init__(self, response: _PyqwestResponse) -> None:
        self.response = response
        self.requests: list[Any] = []

    async def execute(self, request: Any) -> _PyqwestResponse:
        self.requests.append(request)
        return self.response


class _Holder:
    def __init__(self, client: AsyncTinker) -> None:
        self._client = client
        self._inflight_response_bytes_semaphore = BytesSemaphore(1024 * 1024)

    @contextmanager
    def aclient(
        self,
        client_pool_type: ClientConnectionPoolType,  # noqa: ARG002
    ) -> Generator[AsyncTinker, None, None]:
        yield self._client

    def _should_pause_on_billing(
        self,
        status_code: int,
        detail: str,  # noqa: ARG002
    ) -> bool:
        return False

    def get_telemetry(self) -> None:
        return None


def _make_future(
    holder: _Holder,
    request_id: str,
    model_cls: type[Any] = dict,
) -> _APIFuture[Any]:
    future = cast(Any, object.__new__(_APIFuture))
    future.model_cls = model_cls
    future.holder = holder
    future.untyped_future = types.UntypedAPIFuture(request_id=request_id)
    future.request_type = "Forward"
    future.request_start_time = time.time()
    future.request_future_start_time = time.time()
    future.request_queue_roundtrip_time = 0.0
    future._cached_result = _UNCOMPUTED
    future._queue_state_observer = None
    return cast(_APIFuture[Any], future)


def _client_for_transport(transport: Any) -> tuple[AsyncTinker, httpx.AsyncClient]:
    http_client = httpx.AsyncClient(transport=AsyncPyqwestTransport(transport=cast(Any, transport)))
    client = AsyncTinker(
        base_url="http://test",
        api_key="tml-test-api-key",
        http_client=http_client,
        _client_config=types.ClientConfigResponse(use_pyqwest_transport=False),
    )
    return client, http_client


def test_patch_is_installed_by_sdk_import() -> None:
    assert getattr(
        api_future_impl._APIFuture._fetch_via_rest,
        "_fireworks_body_timeout_patch",
        False,
    )


def test_stalled_body_closes_and_repolls_the_same_future(monkeypatch: Any) -> None:
    async def run() -> None:
        transport = _StallFirstTransport()
        client, http_client = _client_for_transport(transport)
        monkeypatch.setattr(
            api_future_impl._APIFuture,
            "_fetch_via_rest",
            _tinker_future_body_timeout_patch._make_fetch_via_rest(
                header_timeout_seconds=0.05,
                body_timeout_seconds=0.05,
            ),
        )
        request_id = "future-stalled-body"
        try:
            result = await asyncio.wait_for(
                _make_future(_Holder(client), request_id)._result_async(),
                timeout=3,
            )
        finally:
            await http_client.aclose()

        assert result == {"ok": True}
        assert len(transport.requests) == 2
        assert transport.stalled_response.closed.is_set()
        assert transport.closed_before_retry
        request_bodies = [orjson.loads(cast(bytes, request.content)) for request in transport.requests]
        assert [body["request_id"] for body in request_bodies] == [
            request_id,
            request_id,
        ]

    asyncio.run(run())


def test_header_and_body_have_independent_deadlines(monkeypatch: Any) -> None:
    async def run() -> None:
        timeout = 0.2
        transport = _DelayedTransport(
            header_delay=timeout * 0.6,
            body_delay=timeout * 0.6,
        )
        client, http_client = _client_for_transport(transport)
        monkeypatch.setattr(
            api_future_impl._APIFuture,
            "_fetch_via_rest",
            _tinker_future_body_timeout_patch._make_fetch_via_rest(
                header_timeout_seconds=timeout,
                body_timeout_seconds=timeout,
            ),
        )
        started = time.monotonic()
        try:
            result = await asyncio.wait_for(
                _make_future(_Holder(client), "future-two-deadlines")._result_async(),
                timeout=2,
            )
        finally:
            await http_client.aclose()
        elapsed = time.monotonic() - started

        assert result == {"ok": True}
        assert len(transport.requests) == 1
        assert transport.response.closed.is_set()
        assert elapsed > timeout

    asyncio.run(run())


def test_protobuf_result_still_deserializes(monkeypatch: Any) -> None:
    async def run() -> None:
        message = tinker_public_pb2.ForwardBackwardOutput(
            loss_fn_output_type="ArrayRecord",
            metrics={"loss": 1.25},
        )
        transport = _SingleResponseTransport(
            _PyqwestResponse(
                _ResponseBody([message.SerializeToString()]),
                content_type="application/x-protobuf",
            )
        )
        client, http_client = _client_for_transport(transport)
        monkeypatch.setattr(
            api_future_impl._APIFuture,
            "_fetch_via_rest",
            _tinker_future_body_timeout_patch._make_fetch_via_rest(
                header_timeout_seconds=0.2,
                body_timeout_seconds=0.2,
            ),
        )
        try:
            result = await _make_future(
                _Holder(client),
                "future-protobuf",
                model_cls=ForwardBackwardOutput,
            )._result_async()
        finally:
            await http_client.aclose()

        assert isinstance(result, ForwardBackwardOutput)
        assert result.loss_fn_output_type == "ArrayRecord"
        assert result.loss_fn_outputs == []
        assert result.metrics == {"loss": 1.25}
        assert len(transport.requests) == 1
        assert transport.response.closed.is_set()

    asyncio.run(run())
