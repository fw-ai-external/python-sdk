from __future__ import annotations

import time
import asyncio
from types import SimpleNamespace
from typing import Any, cast
from contextlib import contextmanager
from collections.abc import Generator, AsyncIterator

import httpx
import orjson
import pytest
from pyqwest.httpx import AsyncPyqwestTransport

import fireworks.training.sdk._core as tinker
from fireworks.training.sdk import types
from fireworks.training.sdk._core.lib import api_future_impl
from fireworks.training.sdk._core.proto import tinker_public_pb2
from fireworks.training.sdk._core._client import AsyncTrainingHTTPClient
from fireworks.training.sdk._core._exceptions import RequestFailedError
from fireworks.training.sdk._core.lib.api_future_impl import _UNCOMPUTED, _APIFuture
from fireworks.training.sdk.types.forward_backward_output import ForwardBackwardOutput
from fireworks.training.sdk._core.lib.internal_client_holder import BytesSemaphore
from fireworks.training.sdk._core.lib.client_connection_pool_type import ClientConnectionPoolType


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
        self._index = 0
        self._delay_applied = False
        self._never_finishes = asyncio.Event()
        self.started = asyncio.Event()

    def __aiter__(self) -> AsyncIterator[bytes]:
        return self

    async def __anext__(self) -> bytes:
        self.started.set()
        if self._delay and not self._delay_applied:
            self._delay_applied = True
            await asyncio.sleep(self._delay)
        if self._index < len(self._chunks):
            chunk = self._chunks[self._index]
            self._index += 1
            return chunk
        if self._stall:
            await self._never_finishes.wait()
        raise StopAsyncIteration


class _PyqwestResponse:
    def __init__(
        self,
        body: _ResponseBody,
        *,
        status: int = 200,
        content_type: str = "application/json",
    ) -> None:
        self.status = status
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
    def __init__(self, client: AsyncTrainingHTTPClient) -> None:
        self._client = client
        self._inflight_response_bytes_semaphore = BytesSemaphore(1024 * 1024)

    @contextmanager
    def aclient(
        self,
        client_pool_type: ClientConnectionPoolType,  # noqa: ARG002
    ) -> Generator[AsyncTrainingHTTPClient, None, None]:
        yield self._client

    def _should_pause_on_billing(
        self,
        status_code: int,
        detail: str,  # noqa: ARG002
    ) -> bool:
        return False

    def get_telemetry(self) -> None:
        return None


@pytest.mark.parametrize("status", [400, 401, 403, 409])
def test_future_error_telemetry_excludes_credentials(status: int, monkeypatch: Any) -> None:
    request = httpx.Request(
        "POST",
        "https://api.example.com/api/v1/retrieve_future",
        headers={
            "X-API-Key": "secret-key",
            "Authorization": "Bearer secret-token",
            "Cookie": "secret-cookie",
            "X-Custom-Credential": "secret-custom",
            "Content-Type": "application/json",
            "X-Request-Id": "request-1",
        },
    )
    response = httpx.Response(
        status,
        request=request,
        json={"error": "unavailable"},
        headers={"Set-Cookie": "secret-response", "X-Custom-Secret": "secret-reply", "X-Request-Id": "reply-1"},
    )
    error = tinker.APIStatusError("unavailable", response=response, body={"error": "unavailable"})
    transport_error = api_future_impl._rest_status_error_to_transport_error(error)
    events = []
    future = _make_future(cast(Any, None), "future-error")
    telemetry = SimpleNamespace(log=lambda *_args, **kwargs: events.append(kwargs["event_data"]))
    monkeypatch.setattr(future, "get_telemetry", lambda: telemetry)

    async def handle() -> None:
        await future._handle_transport_error(transport_error, api_future_impl._LoopState(), 1, time.time())

    if status == 400:
        asyncio.run(handle())
    else:
        with pytest.raises(ValueError, match="unavailable"):
            asyncio.run(handle())
    assert len(events) == 1
    assert events[0]["request_headers"] == {
        "content-type": "application/json",
        "content-length": "0",
        "x-request-id": "request-1",
    }
    assert events[0]["response_headers"]["x-request-id"] == "reply-1"
    assert "secret-" not in orjson.dumps(events).decode()
    assert request.headers["X-API-Key"] == "secret-key"
    assert response.headers["Set-Cookie"] == "secret-response"


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


def _client_for_transport(
    transport: Any,
    *,
    base_url: str = "http://test",
) -> tuple[AsyncTrainingHTTPClient, httpx.AsyncClient]:
    http_client = httpx.AsyncClient(transport=AsyncPyqwestTransport(transport=cast(Any, transport)))
    client = AsyncTrainingHTTPClient(
        base_url=base_url,
        api_key="tml-test-api-key",
        http_client=http_client,
        _client_config=types.ClientConfigResponse(use_pyqwest_transport=False),
    )
    return client, http_client


def test_stalled_body_closes_and_repolls_the_same_future(monkeypatch: Any) -> None:
    async def run() -> None:
        transport = _StallFirstTransport()
        client, http_client = _client_for_transport(transport)
        monkeypatch.setattr(api_future_impl, "_RETRIEVE_FUTURE_HEADER_TIMEOUT_SECONDS", 0.05)
        monkeypatch.setattr(api_future_impl, "_RETRIEVE_FUTURE_BODY_TIMEOUT_SECONDS", 0.05)
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
        monkeypatch.setattr(api_future_impl, "_RETRIEVE_FUTURE_HEADER_TIMEOUT_SECONDS", timeout)
        monkeypatch.setattr(api_future_impl, "_RETRIEVE_FUTURE_BODY_TIMEOUT_SECONDS", timeout)
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
        monkeypatch.setattr(api_future_impl, "_RETRIEVE_FUTURE_HEADER_TIMEOUT_SECONDS", 0.2)
        monkeypatch.setattr(api_future_impl, "_RETRIEVE_FUTURE_BODY_TIMEOUT_SECONDS", 0.2)
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


async def _future_exception(
    body: dict[str, Any],
    *,
    combined: bool = False,
    status: int = 200,
    base_url: str = "http://test",
) -> Exception:
    transport = _SingleResponseTransport(_PyqwestResponse(_ResponseBody([orjson.dumps(body)]), status=status))
    client, http_client = _client_for_transport(transport, base_url=base_url)
    future = _make_future(_Holder(client), "future-structured")

    class _DirectFuture:
        async def result_async(self, timeout: float | None = None) -> Any:
            return await future._result_async(timeout)

    awaitable = (
        api_future_impl._CombinedAPIFuture(
            futures=[_DirectFuture()],
            transform=lambda values: values[0],
            holder=object(),
        ).result_async()
        if combined
        else future._result_async()
    )
    try:
        await awaitable
    except Exception as exc:
        return exc
    finally:
        await http_client.aclose()
    raise AssertionError("future unexpectedly succeeded")


async def _status_error(body: dict[str, Any], *, path: str) -> Exception:
    transport = _SingleResponseTransport(_PyqwestResponse(_ResponseBody([b"{}"])))
    client, http_client = _client_for_transport(transport)
    response = httpx.Response(
        404,
        json=body,
        headers={"x-request-id": "request-1"},
        request=httpx.Request("POST", f"https://api.example.com{path}"),
    )
    try:
        return client._make_status_error("legacy public status message", body=body, response=response)
    finally:
        await http_client.aclose()


@pytest.mark.parametrize("combined", [False, True])
def test_future_failure_preserves_raw_tinker_fields(combined: bool) -> None:
    exc = asyncio.run(
        _future_exception(
            {
                "error": "human-readable failure",
                "category": "Future-Category/V2",
                "error_class": "Future.Class/V9",
            },
            combined=combined,
        )
    )

    assert isinstance(exc, RequestFailedError)
    assert exc.category is types.RequestErrorCategory.Unknown
    assert exc.args == (str(exc),)
    assert exc.__cause__ is None
    source = exc._fireworks_training_error_source
    assert (source.source, source.error, source.category, source.error_class) == (
        "tinker",
        "human-readable failure",
        "Future-Category/V2",
        "Future.Class/V9",
    )


@pytest.mark.parametrize(
    ("body", "expected"),
    [
        (
            {
                "error": "legacy message remains unchanged",
                "category": {"not": "a string"},
                "error_class": "x" * 129,
            },
            ("legacy message remains unchanged", None, None, True),
        ),
        (
            {"error": 7, "category": {"not": "a string"}, "error_class": "x" * 129},
            (None, None, None, True),
        ),
    ],
)
def test_future_failure_marks_invalid_source_fields(body: dict[str, Any], expected: Any) -> None:
    exc = asyncio.run(_future_exception(body))

    assert isinstance(exc, RequestFailedError)
    source = exc._fireworks_training_error_source
    assert (source.error, source.category, source.error_class, source.malformed) == expected


def test_direct_serverless_status_error_preserves_only_valid_gateway_envelope() -> None:
    body = {
        "error": {
            "code": "Future_Gateway_Code/V2",
            "type": "Future.Gateway.Type/V3",
            "message": "mutable diagnostic",
        }
    }
    exc = asyncio.run(
        _status_error(
            body,
            path="/training/v1/serverless/api/v1/create_model",
        )
    )

    assert type(exc) is tinker.NotFoundError
    assert str(exc) == "legacy public status message"
    assert exc.args == ("legacy public status message",)
    assert exc.response.headers["x-request-id"] == "request-1"
    assert exc.__cause__ is None
    source = exc._fireworks_training_error_source
    assert (source.source, source.code, source.type) == (
        "serverless_gateway",
        "Future_Gateway_Code/V2",
        "Future.Gateway.Type/V3",
    )

    dedicated = asyncio.run(
        _status_error(
            body,
            path="/training/v1/rlorTrainerJobs/acct/job/api/v1/create_model",
        )
    )
    assert not hasattr(dedicated, "_fireworks_training_error_source")

    malformed = asyncio.run(
        _status_error(
            {"error": {"code": 404, "type": "error"}},
            path="/training/v1/serverless/api/v1/create_model",
        )
    )
    assert malformed._fireworks_training_error_source.malformed


def test_retrieve_future_copies_final_serverless_http_context() -> None:
    exc = asyncio.run(
        _future_exception(
            {
                "error": {
                    "code": "NOT_FOUND",
                    "type": "error",
                    "message": "retrieve diagnostic",
                }
            },
            status=404,
            base_url="https://api.example.com/training/v1/serverless",
        )
    )

    source = exc._fireworks_training_error_source
    assert (source.code, source.type) == ("NOT_FOUND", "error")
    assert type(exc.__cause__) is tinker.NotFoundError
    assert exc.__cause__._fireworks_training_error_source == source


def test_retrieve_future_unmarked_serverless_capacity_409_fails_without_retry() -> None:
    exc = asyncio.run(
        _future_exception(
            {"detail": "model lifecycle is closing"},
            status=409,
            base_url="https://api.example.com/training/v1/serverless",
        )
    )

    assert isinstance(exc, ValueError)
    assert type(exc.__cause__) is tinker.ConflictError
    assert "model lifecycle is closing" in str(exc)


@pytest.mark.parametrize("state", ["FAILED", "EXPIRED"])
def test_retrieve_future_terminal_run_state_409_fails_without_retry(state: str) -> None:
    async def run() -> Exception:
        return await asyncio.wait_for(
            _future_exception(
                {
                    "detail": (
                        f"cannot resume training run run-example: run state is {state}, not READY or legacy UNSPECIFIED"
                    )
                },
                status=409,
                base_url="https://api.example.com/training/v1/serverless",
            ),
            timeout=1.0,
        )

    exc = asyncio.run(run())

    assert isinstance(exc, ValueError)
    assert type(exc.__cause__) is tinker.ConflictError
    assert f"run state is {state}" in str(exc)
