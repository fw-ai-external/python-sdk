"""Synthetic loopback protocol tests, not customer incident reproductions."""

from __future__ import annotations

import json
import asyncio
from typing import Any, AsyncIterator
from pathlib import Path
from contextlib import asynccontextmanager

import httpx
import pytest
from openai import APIError, AsyncOpenAI
from aiohttp import web

from fireworks.training.sdk import TITOError, TITOSidecar, TITOFailureTraceConfig
from tests_training.test_tito import FakeSampler, FakeRenderer, _engine, _first_request
from fireworks.training.sdk._sse import _SSEDecoder, _SSEProtocolError, _SSETruncationError
from fireworks.training.sdk.sampling import ServerMetrics, DeploymentSampler, SamplingRequestError
from fireworks.training.sdk.concurrency import AdaptiveConcurrencyController
from fireworks.training.sdk.tito._engine import _LinearTrajectoryCore
from fireworks.training.sdk.tito._failure_trace import _FailureTraceRecorder
from fireworks.training.sdk.sampling_observability import extract_request_id


def _event(value: Any) -> bytes:
    return ("data: " + json.dumps(value, ensure_ascii=False) + "\r\n\r\n").encode()


def _completion(finish: str | None = "stop", tokens: tuple[int, ...] = (197, 3)) -> bytes:
    return _event(
        {
            "id": "synthetic-completion-id",
            "choices": [
                {
                    "text": "a",
                    "finish_reason": finish,
                    "raw_output": {"completion_token_ids": list(tokens)},
                    "logprobs": {"content": [{"logprob": -0.2, "sampling_logprob": -0.2} for _ in tokens]},
                }
            ],
        }
    )


_DONE = b"data: [DONE]\r\n\r\n"
_ERROR = _event({"error": {"code": "synthetic_failure", "type": "server_error", "message": "private-payload"}})


@asynccontextmanager
async def _upstream(
    responses: list[bytes], *, disconnect: bool = False
) -> AsyncIterator[tuple[str, list[dict[str, Any]]]]:
    calls: list[dict[str, Any]] = []

    async def handle(request: web.Request) -> web.StreamResponse:
        calls.append(await request.json())
        wire = responses[min(len(calls) - 1, len(responses) - 1)]
        headers = {"content-type": "text/event-stream", "x-request-id": "synthetic-response-id"}
        if disconnect:
            headers["content-length"] = str(len(wire) + 100)
        response = web.StreamResponse(headers=headers)
        await response.prepare(request)
        for offset in range(0, len(wire), 7):
            await response.write(wire[offset : offset + 7])
        if disconnect:
            assert request.transport is not None
            request.transport.close()
        else:
            await response.write_eof()
        return response

    app = web.Application()
    app.router.add_post("/inference/v1/completions", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    try:
        assert runner.addresses
        yield f"http://127.0.0.1:{runner.addresses[0][1]}", calls
    finally:
        await runner.cleanup()


@pytest.mark.parametrize(
    "error", [_ERROR, b"event: error\n" + _ERROR, b"event: error\ndata: broken\n\n", b"event: error\n\n"]
)
@pytest.mark.parametrize("done", [b"", _DONE])
async def test_stream_errors_override_complete_tokens(error: bytes, done: bytes) -> None:
    async with _upstream([_completion() + error + done]) as (url, calls):
        sampler = DeploymentSampler(inference_url=url, model="synthetic", api_key="unused")
        try:
            with pytest.raises(SamplingRequestError) as failure:
                await sampler.sample_with_prompt_tokens_result([1], logical_request_id="logical-test")
            record = failure.value.as_error_record()
            assert record["final_error_kind"] == "upstream_stream"
            assert record["wire_status"] == 200
            assert record["final_status"] is None
            assert record["request_id"] == "synthetic-response-id"
            assert record["upstream_response_id"] == "synthetic-completion-id"
            assert record["logical_request_id"] == "logical-test"
            assert record["attempts"] == 1
            assert len(calls) == 1
            assert "private-payload" not in repr(record) + str(failure.value)
        finally:
            sampler.close()


@pytest.mark.parametrize("finish", ["error", "cancelled", "content_filter"])
async def test_unsuccessful_finish_cannot_become_success(finish: str) -> None:
    async with _upstream([_completion(finish) + _DONE]) as (url, calls):
        sampler = DeploymentSampler(inference_url=url, model="synthetic", api_key="unused")
        try:
            with pytest.raises(SamplingRequestError) as failure:
                await sampler.sample_with_prompt_tokens_result([1])
            assert failure.value.upstream_finish_reason == finish
            assert len(calls) == 1
        finally:
            sampler.close()


async def test_done_and_raw_tokens_do_not_invent_a_finish() -> None:
    async with _upstream([_completion(None) + _DONE]) as (url, calls):
        sampler = DeploymentSampler(inference_url=url, model="synthetic", api_key="unused")
        sampler._RETRY_MAX_ATTEMPTS = 1
        try:
            with pytest.raises(SamplingRequestError) as failure:
                await sampler.sample_with_prompt_tokens_result([1])
            assert isinstance(failure.value.__cause__, _SSETruncationError)
            assert failure.value.wire_status == 200
            assert failure.value.request_id == "synthetic-response-id"
            assert len(calls) == 1
            mapped = _LinearTrajectoryCore._operation_error(failure.value, "inference")
            assert mapped.context["phase"] == "inference"
            assert mapped.context["transport_hop"] == "sidecar_to_inference"
            assert mapped.context["retry_scope"] == "logical_request"
            assert mapped.status == 502 and mapped.should_retry is False
        finally:
            sampler.close()


async def test_malformed_json_is_not_hidden_by_a_later_complete_chunk() -> None:
    async with _upstream([b"data: broken\n\n" + _completion() + _DONE]) as (url, calls):
        sampler = DeploymentSampler(inference_url=url, model="synthetic", api_key="unused")
        try:
            with pytest.raises(_SSEProtocolError) as failure:
                await sampler.sample_with_prompt_tokens_result([1])
            assert failure.value.code == "tito_sdk_sampling_parse_error"
            assert failure.value.origin == "sdk_parser"
            assert failure.value.server_attempts[0].status_code == 200
            assert len(calls) == 1
        finally:
            sampler.close()


@pytest.mark.parametrize("stream", [False, True])
@pytest.mark.parametrize("fault", [_ERROR, b"data: malformed-json\n\n"])
async def test_error_stream_never_commits_a_turn(tmp_path: Any, stream: bool, fault: bytes) -> None:
    async with _upstream([_completion() + fault + _DONE, _completion("stop", (198, 3)) + _DONE]) as (url, calls):
        sampler = DeploymentSampler(inference_url=url, model="synthetic", api_key="unused")
        sidecar = TITOSidecar.from_deployment_sampler(
            sampler,
            renderer=FakeRenderer(),
            max_context_tokens=4096,
            max_output_tokens=128,
            failure_trace_config=TITOFailureTraceConfig(root_dir=tmp_path, min_free_bytes=0),
        )
        await sidecar.start()
        try:
            endpoint = await sidecar.create_trajectory_async()
            headers = {"authorization": "Bearer " + endpoint.api_key}
            request = {"messages": [{"role": "user", "content": "synthetic"}], "stream": stream}
            async with httpx.AsyncClient(trust_env=False) as client:
                response = await client.post(
                    endpoint.openai_base_url + "/chat/completions", headers=headers, json=request
                )
                error = (
                    next(
                        json.loads(line[6:])["error"]
                        for line in response.text.splitlines()
                        if line.startswith("data: {") and '"error"' in line
                    )
                    if stream
                    else response.json()["error"]
                )
                local_decode = fault != _ERROR
                assert response.status_code == (200 if stream else (422 if local_decode else 502))
                assert error["code"] == ("tito_sdk_sampling_parse_error" if local_decode else "tito_server_stream_error")
                assert error["origin"] == ("sdk_parser" if local_decode else "server")
                assert error["wire_status"] == 200
                assert error["should_retry"] is False
                assert error["discard_trajectory"] is local_decode
                assert error["request_id"] == "synthetic-response-id"
                assert error["upstream_response_id"] == "synthetic-completion-id"
                request["stream"] = False
                healthy = await client.post(
                    endpoint.openai_base_url + "/chat/completions", headers=headers, json=request
                )
                assert healthy.status_code == (422 if local_decode else 200)
            artifact = await sidecar.finish_trajectory(endpoint.trajectory_id)
            turns = [turn for segment in artifact.segments for turn in segment.turns]
            assert len(turns) == (0 if local_decode else 1)
            if not local_decode:
                assert turns[0].exact_completion_ids == (198, 3)
                assert [call.outcome for call in artifact.calls] == ["failed", "succeeded"]
            assert len(calls) == (1 if local_decode else 2)
        finally:
            await sidecar.close()
            sampler.close()


@pytest.mark.parametrize("primary_status", [None, 503])
async def test_transient_error_retries_fresh_tokens_once(monkeypatch: Any, primary_status: int | None) -> None:
    transient = _event({"error": {"status_code": primary_status, "status": 503, "code": "unavailable"}})
    async with _upstream([_completion(tokens=(197, 3)) + transient + _DONE, _completion(tokens=(198, 3)) + _DONE]) as (
        url,
        calls,
    ):
        sampler = DeploymentSampler(inference_url=url, model="synthetic", api_key="unused")
        sampler._RETRY_MAX_ATTEMPTS = 2

        async def no_backoff(*args: Any, **kwargs: Any) -> float:
            return 0.0

        monkeypatch.setattr(sampler, "_backoff_after_transient", no_backoff)
        try:
            result = await sampler.sample_with_prompt_tokens_result([1], logprobs=True)
            assert result.completions[0].full_tokens == [1, 198, 3]
            assert result.completions[0].sampling_logprobs == [-0.2, -0.2]
            assert result.attempts == 2
            assert [attempt.outcome for attempt in result.server_attempts] == ["retryable_error", "succeeded"]
            assert len(calls) == 2
        finally:
            sampler.close()


async def test_disconnect_after_headers_retains_wire_identity() -> None:
    async with _upstream([_completion(None)], disconnect=True) as (url, calls):
        sampler = DeploymentSampler(inference_url=url, model="synthetic", api_key="unused")
        sampler._RETRY_MAX_ATTEMPTS = 1
        try:
            with pytest.raises(SamplingRequestError) as failure:
                await sampler.sample_with_prompt_tokens_result([1])
            assert failure.value.final_error_kind == "connection"
            assert failure.value.final_status is None
            assert failure.value.wire_status == 200
            assert failure.value.request_id == "synthetic-response-id"
            assert len(calls) == 1
        finally:
            sampler.close()


@pytest.mark.parametrize(
    "status,attempts,max_attempts", [(400, 1, 1), (400, 1, 2), (200, 1, 2), (None, 1, 2), (503, 2, 2)]
)
async def test_stream_failure_retry_policy_is_bounded(
    status: int | None, attempts: int, max_attempts: int, monkeypatch: Any
) -> None:
    error = _event({"error": {"status_code": status, "code": "synthetic_failure", "type": "server_error"}})
    async with _upstream([_completion() + error + _DONE]) as (url, calls):
        sampler = DeploymentSampler(inference_url=url, model="synthetic", api_key="unused")
        sampler._RETRY_MAX_ATTEMPTS = max_attempts

        async def no_backoff(*args: Any, **kwargs: Any) -> float:
            return 0.0

        monkeypatch.setattr(sampler, "_backoff_after_transient", no_backoff)
        try:
            with pytest.raises(SamplingRequestError) as failure:
                await sampler.sample_with_prompt_tokens_result([1])
            assert len(calls) == failure.value.attempts == attempts
            assert failure.value.retry_budget_exhausted == (attempts == 2)
            assert failure.value.final_status == (status if status in (400, 503) else None)
            assert failure.value.wire_status == 200
            assert failure.value.upstream_error_code == "synthetic_failure"
            assert all(attempt.status_code == 200 for attempt in failure.value.server_attempts)
        finally:
            sampler.close()


@pytest.mark.parametrize("finish", ["stop", "length"])
async def test_valid_finish_usage_keepalives_and_post_done_boundary(finish: str) -> None:
    wire = (
        b": heartbeat\r\n\r\nevent: ping\r\ndata: alive\r\n\r\n"
        + _completion(finish)
        + _event({"choices": [], "usage": {"completion_tokens": 2}, "perf_metrics": {}})
        + _DONE
        + _ERROR
    )
    async with _upstream([wire]) as (url, calls):
        sampler = DeploymentSampler(inference_url=url, model="synthetic", api_key="unused")
        try:
            result = await sampler.sample_with_prompt_tokens_result([1])
            assert result.completions[0].finish_reason == finish
            assert len(calls) == 1
        finally:
            sampler.close()


async def test_error_words_inside_generated_text_are_not_an_error_envelope() -> None:
    chunk = json.loads(_completion().decode().removeprefix("data: ").strip())
    chunk["choices"][0]["text"] = 'Discuss {"error": "ordinary text"} and event: error'
    async with _upstream([_event(chunk) + _DONE]) as (url, calls):
        sampler = DeploymentSampler(inference_url=url, model="synthetic", api_key="unused")
        try:
            result = await sampler.sample_with_prompt_tokens_result([1])
            assert result.completions[0].text == chunk["choices"][0]["text"]
            assert len(calls) == 1
        finally:
            sampler.close()


async def test_fragmented_decoder_preserves_utf8_crlf_and_multiline_data() -> None:
    wire = ': keepalive\r\nevent: message\r\ndata: {"text":\r\ndata: "你好"}\r\n\r\n'.encode()

    class FragmentedResponse:
        async def aiter_bytes(self) -> AsyncIterator[bytes]:
            for byte in wire:
                yield bytes([byte])

    events = [event async for event in _SSEDecoder().aiter_events(FragmentedResponse())]
    assert len(events) == 1
    assert events[0].event == "message"
    assert json.loads(events[0].data) == {"text": "你好"}


@pytest.mark.parametrize("stream", [False, True])
async def test_openai_client_receives_stream_failure_without_a_completion(stream: bool) -> None:
    async with _upstream([_completion() + _ERROR + _DONE]) as (url, calls):
        sampler = DeploymentSampler(inference_url=url, model="synthetic", api_key="unused")
        sidecar = TITOSidecar.from_deployment_sampler(
            sampler,
            renderer=FakeRenderer(),
            max_context_tokens=4096,
            max_output_tokens=128,
        )
        await sidecar.start()
        try:
            endpoint = sidecar.create_trajectory()
            async with AsyncOpenAI(
                base_url=endpoint.openai_base_url, api_key=endpoint.api_key, max_retries=0
            ) as client:
                with pytest.raises(APIError) as failure:
                    response = await client.chat.completions.create(
                        model="policy",
                        messages=[{"role": "user", "content": "synthetic"}],
                        stream=stream,
                    )
                    if stream:
                        async for _chunk in response:
                            pytest.fail("an upstream failure must not deliver an assistant completion")
                body = failure.value.body
                details = body.get("error", body)
                assert details["code"] == "tito_server_stream_error"
                assert details["wire_status"] == 200
                assert len(calls) == 1
            artifact = await sidecar.finish_trajectory(endpoint.trajectory_id)
            assert not [turn for segment in artifact.segments for turn in segment.turns]
        finally:
            await sidecar.close()
            sampler.close()


async def test_cancellation_during_response_read_is_not_retried(monkeypatch: Any) -> None:
    entered = asyncio.Event()
    cancelled = asyncio.Event()

    class BlockingStream(httpx.AsyncByteStream):
        async def __aiter__(self) -> AsyncIterator[bytes]:
            entered.set()
            await cancelled.wait()
            yield _completion() + _DONE

    def handle(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, stream=BlockingStream(), headers={"x-request-id": "reading"})

    sampler = DeploymentSampler(inference_url="http://synthetic.invalid", model="synthetic", api_key="unused")
    async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as client:
        monkeypatch.setattr(sampler, "_get_async_client", lambda: client)
        releases: list[Any] = []
        monkeypatch.setattr(sampler, "_release_concurrency", lambda *args: releases.append(args))
        task = asyncio.create_task(sampler.sample_with_prompt_tokens_result([1]))
        await entered.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError) as failure:
            await task
        assert len(failure.value.server_attempts) == 1
        assert failure.value.server_attempts[0].outcome == "cancelled"
        assert len(releases) == 1
    sampler.close()


@pytest.mark.parametrize("status", [429, 503, None])
async def test_semantic_stream_status_controls_admission_without_rewriting_wire_status(status: int | None) -> None:
    controller = AdaptiveConcurrencyController(initial_window=8, min_window=1, adjustment_interval=1)
    error = _event({"error": {"status_code": None, "status": status}})
    async with _upstream([_completion() + error + _DONE]) as (url, calls):
        sampler = DeploymentSampler(inference_url=url, model="synthetic", api_key="unused", concurrency_controller=controller)
        sampler._RETRY_MAX_ATTEMPTS = 1
        try:
            with pytest.raises(SamplingRequestError) as failure:
                await sampler.sample_with_prompt_tokens_result([1])
            assert failure.value.final_status == status
            assert failure.value.wire_status == 200
            assert failure.value.server_attempts[0].status_code == 200
            assert sampler.drain_metrics()[0].http_status_code == 200
            assert controller.window_size < 8 if status is not None else controller.window_size == 8
            assert len(calls) == 1
        finally:
            sampler.close()


async def test_truncated_stream_metrics_keep_response_identity() -> None:
    async with _upstream([_completion(None)]) as (url, calls):
        sampler = DeploymentSampler(inference_url=url, model="synthetic", api_key="unused")
        sampler._RETRY_MAX_ATTEMPTS = 1
        try:
            with pytest.raises(SamplingRequestError):
                await sampler.sample_with_prompt_tokens_result([1])
            metrics = sampler.drain_metrics()[0]
            assert metrics.http_status_code == 200
            assert metrics.response_request_id == "synthetic-response-id"
            assert len(calls) == 1
        finally:
            sampler.close()


async def test_failed_custom_sampler_finish_keeps_wire_status_only() -> None:
    engine = _engine(FakeSampler(finishes=["error"]))
    trajectory_id = engine.create_trajectory()
    with pytest.raises(TITOError) as failure:
        await engine.complete(trajectory_id, _first_request())
    assert failure.value.code == "tito_sdk_sampling_parse_error"
    assert failure.value.origin == "sdk_parser"
    assert failure.value.discard_trajectory is True
    assert failure.value.context["wire_status"] == 200
    assert failure.value.context.get("upstream_status") is None
    await engine.close()


@pytest.mark.parametrize("request_id", ["fw_request-1", "sk-request-2", "bearer-request", "opaque/id with spaces"])
def test_request_identity_preserves_opaque_request_ids(request_id: str) -> None:
    assert extract_request_id({"x-request-id": request_id}) == request_id


def test_request_identity_bounds_and_escapes_without_dropping_it() -> None:
    assert extract_request_id({"x-request-id": "x" * 257}) == "x" * 256
    assert extract_request_id({"x-request-id": "bad\nheader"}) == r"bad\x0aheader"


@pytest.mark.parametrize("header", ["x-request-id", "X-Request-Id", "X-REQUEST-ID"])
def test_header_metrics_preserve_case_insensitive_safe_identity(header: str) -> None:
    assert ServerMetrics.from_headers({header: "safe-correlation-id"}).response_request_id == "safe-correlation-id"
    assert ServerMetrics.from_headers({header: "fw_request-1"}).response_request_id == "fw_request-1"


async def test_null_error_member_does_not_reject_a_valid_completion() -> None:
    payload = json.loads(_completion().decode().split("data: ")[1])
    payload["error"] = None
    async with _upstream([_event(payload) + _DONE]) as (url, calls):
        sampler = DeploymentSampler(inference_url=url, model="synthetic", api_key="unused")
        try:
            result = await sampler.sample_with_prompt_tokens_result([1])
            assert result.completions[0].finish_reason == "stop"
            assert len(calls) == 1
        finally:
            sampler.close()


async def test_transport_failure_after_done_remains_fail_closed() -> None:
    async with _upstream([_completion() + _DONE], disconnect=True) as (url, calls):
        sampler = DeploymentSampler(inference_url=url, model="synthetic", api_key="unused")
        sampler._RETRY_MAX_ATTEMPTS = 1
        try:
            with pytest.raises(SamplingRequestError):
                await sampler.sample_with_prompt_tokens_result([1])
            assert len(calls) == 1
        finally:
            sampler.close()


async def test_read_failure_trace_does_not_serialize_authenticated_request(tmp_path: Path) -> None:
    secret = "synthetic-api-key-not-for-logging"
    async with _upstream([_completion(None)], disconnect=True) as (url, calls):
        sampler = DeploymentSampler(inference_url=url, model="synthetic", api_key=secret)
        sampler._RETRY_MAX_ATTEMPTS = 1
        engine = _engine(
            sampler,
            failure_recorder=_FailureTraceRecorder(TITOFailureTraceConfig(root_dir=tmp_path, min_free_bytes=0)),
        )
        trajectory_id = engine.create_trajectory()
        try:
            with pytest.raises(TITOError) as failure:
                await engine.complete(trajectory_id, _first_request())
            trace_path = Path(failure.value.context["trace_path"])
            assert trace_path.is_file()
            assert secret not in trace_path.read_text()
            assert secret not in repr(failure.value.as_error_record())
            assert len(calls) == 1
        finally:
            await engine.close()
            sampler.close()
