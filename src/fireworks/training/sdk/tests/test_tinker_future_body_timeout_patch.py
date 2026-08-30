from __future__ import annotations

import time
import asyncio
import contextlib
from typing import Any, cast
from contextlib import contextmanager
from collections.abc import Generator, AsyncIterator

import httpx
import orjson
import pytest
import tinker
from tinker import types
from tinker.lib import api_future_impl
from tinker.proto import tinker_public_pb2
from pyqwest.httpx import AsyncPyqwestTransport
from tinker._client import AsyncTinker
from tinker._response import AsyncAPIResponse
from tinker._exceptions import RequestFailedError
from tinker.lib.api_future_impl import _UNCOMPUTED, _APIFuture
from tinker.lib.internal_client_holder import BytesSemaphore
from tinker.types.forward_backward_output import ForwardBackwardOutput
from tinker.lib.client_connection_pool_type import ClientConnectionPoolType

from fireworks.training.sdk.patches import _tinker_structured_error_patch, _tinker_future_body_timeout_patch


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


def _client_for_transport(
    transport: Any,
    *,
    base_url: str = "http://test",
) -> tuple[AsyncTinker, httpx.AsyncClient]:
    http_client = httpx.AsyncClient(transport=AsyncPyqwestTransport(transport=cast(Any, transport)))
    client = AsyncTinker(
        base_url=base_url,
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


def test_structured_error_patch_has_independent_idempotence_guard() -> None:
    from fireworks.training.sdk.patches import _tinker_structured_error_patch

    for method in (
        AsyncAPIResponse.json,
        api_future_impl._APIFuture._fetch_via_rest,
        AsyncTinker._make_status_error,
        api_future_impl._APIFuture._handle_outcome,
        api_future_impl._APIFuture._handle_transport_error,
    ):
        assert getattr(method, "_fireworks_structured_error_patch", False)
    assert _tinker_structured_error_patch._apply_tinker_structured_error_patch() is False


def test_future_source_capture_does_not_depend_on_body_timeout_override(
    monkeypatch: Any,
) -> None:
    body = {
        "error": "native future failure",
        "category": "Future-Category/V2",
        "error_class": "Future.Class/V9",
    }

    async def native_like_fetch(self: Any, state: Any, iteration: int) -> Any:  # noqa: ARG001
        response = object.__new__(AsyncAPIResponse)
        response.http_response = httpx.Response(
            200,
            content=orjson.dumps(body),
            request=httpx.Request("POST", "https://api.example.com/future/retrieve"),
        )
        result = await response.json()
        error_category = api_future_impl.RequestErrorCategory.Unknown
        with contextlib.suppress(Exception):
            error_category = api_future_impl.RequestErrorCategory(result.get("category"))
        return api_future_impl._Failed(
            error_message=result["error"],
            error_category=error_category,
        )

    monkeypatch.setattr(
        api_future_impl._APIFuture,
        "_fetch_via_rest",
        _tinker_structured_error_patch._make_fetch_via_rest_with_source_capture(native_like_fetch),
    )

    exc = asyncio.run(_future_exception({"unused": True}))

    assert isinstance(exc, RequestFailedError)
    source = exc._fireworks_training_error_source
    assert (source.error, source.category, source.error_class) == (
        "native future failure",
        "Future-Category/V2",
        "Future.Class/V9",
    )


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
