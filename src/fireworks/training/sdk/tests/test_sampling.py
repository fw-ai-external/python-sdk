"""Tests for structured sampling observability in DeploymentSampler.

Covers the single-owner retry budget, Retry-After honoring, stable logical
request ids, and the structured terminal error (attempt history + context).
Payload-free by construction: no prompt/token/key content may appear in any
recorded attempt or exception.
"""

from __future__ import annotations

import uuid
import asyncio

import httpx
import pytest

from fireworks.training.sdk.sampling import (
    ServerMetrics,
    DeploymentSampler,
    SamplingRequestError,
    DeploymentSamplerTimeoutError,
)

# NOTE: conftest.py's autouse fixture disables errors.py layer-1 backoff
# (_backoff_delay -> None) for every module except test_errors. The sampler's
# own retry loop (_do_one_completion) does not use that helper, so the tests
# below still exercise real per-completion retries. Layer-1 retry opt-out and
# Retry-After parsing live in test_errors.py (the exempt module).

_URL = "https://api.example.com/inference/v1/completions"


def _make_sampler(**kwargs):
    defaults = dict(inference_url="https://api.example.com", model="m", api_key="secret-key", tokenizer=None)
    defaults.update(kwargs)
    return DeploymentSampler(**defaults)


def _http_error(
    status: int,
    headers: dict | None = None,
    *,
    body: dict | None = None,
    url: str = _URL,
) -> httpx.HTTPStatusError:
    req = httpx.Request("POST", url)
    response_kwargs = {"json": body} if body is not None else {}
    resp = httpx.Response(
        status,
        headers=headers or {},
        request=req,
        **response_kwargs,
    )
    return httpx.HTTPStatusError(f"HTTP {status}", request=req, response=resp)


_SUCCESS = (
    {
        "id": "cmpl-upstream-test",
        "choices": [{"text": "hi", "finish_reason": "stop", "raw_output": {"completion_token_ids": [40, 50]}}],
    },
    ServerMetrics(),
)


def _install_stream(sampler, effects):
    """Replace async_completions_stream with a scripted sequence of effects.

    Each effect is an Exception (raised) or a (result, metrics) tuple; the last
    effect repeats once exhausted. Returns the list of per-call kwargs so tests
    can assert what the retry loop passed down (e.g. the stable request id).
    """
    calls: list[dict] = []

    async def _fake(*args, **kwargs):
        calls.append(kwargs)
        effect = effects[min(len(calls) - 1, len(effects) - 1)]
        if isinstance(effect, BaseException):
            raise effect
        return effect

    sampler.async_completions_stream = _fake
    return calls


class _CountingController:
    def __init__(self) -> None:
        self.acquired = 0
        self.released = 0
        self.released_metrics: list[ServerMetrics | None] = []
        self.exhausted_metrics: list[ServerMetrics | None] = []

    @property
    def window_size(self) -> int:
        return 1

    async def acquire(self) -> None:
        self.acquired += 1

    def release(self, metrics: ServerMetrics | None = None) -> None:
        self.released += 1
        self.released_metrics.append(metrics)

    def note_retry_exhausted(self, metrics: ServerMetrics | None) -> None:
        self.exhausted_metrics.append(metrics)

    def step_completed(self) -> dict[str, float]:
        return {"window": 1.0}


@pytest.fixture
def no_sleep(monkeypatch):
    """Patch backoff sleeps to no-ops and record requested durations."""
    slept: list[float] = []

    async def _fake_sleep(seconds):
        slept.append(seconds)

    monkeypatch.setattr(asyncio, "sleep", _fake_sleep)
    return slept


@pytest.fixture
def no_jitter(monkeypatch):
    """Make jitter deterministic: factor 0.5 (random() -> 0.0)."""
    import random as _random

    monkeypatch.setattr(_random, "random", lambda: 0.0)


class TestSamplingRetryLoop:
    def test_success_after_retry(self, no_sleep, no_jitter):
        sampler = _make_sampler()
        calls = _install_stream(sampler, [_http_error(429, {"retry-after": "2"}), _SUCCESS])

        results = asyncio.run(sampler.sample_with_prompt_tokens([1, 2, 3]))

        assert len(results) == 1
        assert len(calls) == 2  # one retry, then success (no exception)
        # Retry-After (2.0) dominates the jittered base backoff (1.0).
        assert no_sleep and no_sleep[0] == 2.0

    def test_persistent_503_raises_structured(self, no_sleep, no_jitter):
        sampler = _make_sampler()
        calls = _install_stream(sampler, [_http_error(503, {"x-request-id": "gw-x"})])

        with pytest.raises(SamplingRequestError) as excinfo:
            asyncio.run(sampler.sample_with_prompt_tokens([1, 2, 3]))

        err = excinfo.value
        assert len(calls) == DeploymentSampler._RETRY_MAX_ATTEMPTS
        assert err.attempts == DeploymentSampler._RETRY_MAX_ATTEMPTS
        assert err.final_status == 503 and err.final_error_kind == "http_status"
        assert err.model == "m"
        assert err.request_id == "gw-x"  # server id of the last attempt, for log search
        assert not isinstance(err, DeploymentSamplerTimeoutError)
        assert len(err.server_attempts) == DeploymentSampler._RETRY_MAX_ATTEMPTS
        assert all(attempt.response_request_id == "gw-x" for attempt in err.server_attempts)

    def test_transport_failures_retain_attempt_metrics(self, no_sleep, no_jitter):
        sampler = _make_sampler()
        request = httpx.Request("POST", _URL)
        _install_stream(
            sampler,
            [httpx.ConnectError("connection refused", request=request)],
        )

        with pytest.raises(SamplingRequestError) as excinfo:
            asyncio.run(sampler.sample_with_prompt_tokens([1, 2, 3]))

        assert len(excinfo.value.server_attempts) == DeploymentSampler._RETRY_MAX_ATTEMPTS
        assert all(
            attempt.server_metrics is not None and attempt.server_metrics.transport_error
            for attempt in excinfo.value.server_attempts
        )

    def test_retry_exhaustion_reports_final_released_metrics(self, no_sleep, no_jitter):
        controller = _CountingController()
        sampler = _make_sampler(concurrency_controller=controller)
        _install_stream(sampler, [_http_error(503)])

        with pytest.raises(SamplingRequestError):
            asyncio.run(sampler.sample_with_prompt_tokens([1, 2, 3]))

        assert len(controller.exhausted_metrics) == 1
        final_metrics = controller.exhausted_metrics[0]
        assert final_metrics is controller.released_metrics[-1]
        assert final_metrics is not None
        assert final_metrics.http_status_code == 503
        assert final_metrics.retry_attempt == DeploymentSampler._RETRY_MAX_ATTEMPTS

    def test_final_serverless_gateway_error_attaches_private_context(self, no_sleep, no_jitter):
        serverless_url = "https://api.example.com/training/v1/serverless/inference/v1/completions"
        sampler = _make_sampler(inference_url="https://api.example.com/training/v1/serverless")
        gateway_body = {
            "error": {
                "code": "Future_Code/V2",
                "type": "Future.Type/V3",
                "message": "mutable diagnostic",
            }
        }
        _install_stream(
            sampler,
            [
                httpx.ConnectError("first attempt"),
                _http_error(
                    503,
                    {"x-request-id": "gw-final"},
                    body=gateway_body,
                    url=serverless_url,
                ),
            ],
        )

        with pytest.raises(SamplingRequestError) as excinfo:
            asyncio.run(sampler.sample_with_prompt_tokens([1, 2, 3]))

        err = excinfo.value
        assert err.attempts == DeploymentSampler._RETRY_MAX_ATTEMPTS
        assert err.final_status == 503
        assert err.request_id == "gw-final"
        source = err._fireworks_training_error_source
        assert source.source == "serverless_gateway"
        assert source.code == "Future_Code/V2"
        assert source.type == "Future.Type/V3"
        assert "Future_Code/V2" not in str(err)
        assert "Future_Code/V2" not in repr(err.as_error_record())

    def test_final_connection_error_does_not_inherit_stale_gateway_context(self, no_sleep, no_jitter):
        sampler = _make_sampler(inference_url="https://api.example.com/training/v1/serverless")
        structured = _http_error(
            503,
            body={
                "error": {
                    "code": "SERVICE_UNAVAILABLE",
                    "type": "error",
                    "message": "earlier response",
                }
            },
            url="https://api.example.com/training/v1/serverless/inference/v1/completions",
        )
        _install_stream(
            sampler,
            [structured, httpx.ConnectError("final connection failure")],
        )

        with pytest.raises(SamplingRequestError) as excinfo:
            asyncio.run(sampler.sample_with_prompt_tokens([1, 2, 3]))

        assert excinfo.value.final_error_kind == "connection"
        assert not hasattr(excinfo.value, "_fireworks_training_error_source")

    def test_missing_request_id_header(self, no_sleep, no_jitter):
        sampler = _make_sampler()
        _install_stream(sampler, [_http_error(503)])
        with pytest.raises(SamplingRequestError) as excinfo:
            asyncio.run(sampler.sample_with_prompt_tokens([1, 2, 3]))
        assert excinfo.value.request_id is None  # no crash

    def test_500_is_retried_then_succeeds(self, no_sleep, no_jitter):
        sampler = _make_sampler()
        calls = _install_stream(sampler, [_http_error(500), _http_error(500), _SUCCESS])
        results = asyncio.run(sampler.sample_with_prompt_tokens([1, 2, 3]))
        assert len(results) == 1 and len(calls) == 3

    def test_connection_error_retried(self, no_sleep, no_jitter):
        sampler = _make_sampler()
        _install_stream(sampler, [httpx.ConnectError("reset")])
        with pytest.raises(SamplingRequestError) as excinfo:
            asyncio.run(sampler.sample_with_prompt_tokens([1, 2, 3]))
        assert excinfo.value.final_error_kind == "connection"

    def test_non_retryable_400_fails_fast(self, no_sleep, no_jitter):
        sampler = _make_sampler()
        calls = _install_stream(sampler, [_http_error(400)])
        with pytest.raises(httpx.HTTPStatusError) as excinfo:
            asyncio.run(sampler.sample_with_prompt_tokens([1, 2, 3]))
        assert len(calls) == 1  # no retry
        assert not hasattr(excinfo.value, "_fireworks_training_error_source")

    def test_non_retryable_serverless_gateway_error_keeps_type_and_context(self):
        serverless_url = "https://api.example.com/training/v1/serverless/inference/v1/completions"
        sampler = _make_sampler(inference_url="https://api.example.com/training/v1/serverless")
        original = _http_error(
            400,
            body={
                "error": {
                    "code": "BAD_REQUEST",
                    "type": "error",
                    "message": "mutable diagnostic",
                }
            },
            url=serverless_url,
        )
        original_args = original.args
        calls = _install_stream(sampler, [original])

        with pytest.raises(httpx.HTTPStatusError) as excinfo:
            asyncio.run(sampler.sample_with_prompt_tokens([1, 2, 3]))

        assert excinfo.value is original
        assert excinfo.value.args == original_args
        assert len(calls) == 1
        source = excinfo.value._fireworks_training_error_source
        assert (source.source, source.code, source.type) == (
            "serverless_gateway",
            "BAD_REQUEST",
            "error",
        )

    def test_persistent_504_raises_timeout_subclass(self, no_sleep, no_jitter):
        sampler = _make_sampler()
        _install_stream(sampler, [_http_error(504)])
        with pytest.raises(DeploymentSamplerTimeoutError) as excinfo:
            asyncio.run(sampler.sample_with_prompt_tokens([1, 2, 3]))
        assert isinstance(excinfo.value, SamplingRequestError)
        assert excinfo.value.final_error_kind == "timeout"

    def test_stable_logical_id_across_attempts(self, no_sleep, no_jitter):
        sampler = _make_sampler()
        calls = _install_stream(sampler, [_http_error(503)])
        with pytest.raises(SamplingRequestError) as excinfo:
            asyncio.run(sampler.sample_with_prompt_tokens([1, 2, 3]))
        sent_ids = {c["logical_request_id"] for c in calls}
        assert len(sent_ids) == 1  # identical across every attempt
        assert excinfo.value.logical_request_id == sent_ids.pop()

    def test_cancelled_stream_releases_concurrency_slot(self):
        controller = _CountingController()
        sampler = _make_sampler(concurrency_controller=controller)
        stream_started = asyncio.Event()
        never_finishes = asyncio.Event()

        async def _blocked_stream(*_args, **_kwargs):
            stream_started.set()
            await never_finishes.wait()
            return _SUCCESS

        sampler.async_completions_stream = _blocked_stream

        async def _cancel_live_request():
            task = asyncio.create_task(sampler.sample_with_prompt_tokens([1, 2, 3]))
            await stream_started.wait()
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task

        asyncio.run(_cancel_live_request())
        assert controller.acquired == 1
        assert controller.released == 1

    def test_unclassified_stream_error_releases_concurrency_slot(self):
        controller = _CountingController()
        sampler = _make_sampler(concurrency_controller=controller)
        _install_stream(sampler, [ValueError("contract failure")])

        with pytest.raises(ValueError, match="contract failure"):
            asyncio.run(sampler.sample_with_prompt_tokens([1, 2, 3]))

        assert controller.acquired == 1
        assert controller.released == 1

    def test_retry_releases_each_acquired_slot_once(self, no_sleep, no_jitter):
        controller = _CountingController()
        sampler = _make_sampler(concurrency_controller=controller)
        _install_stream(
            sampler,
            [
                _http_error(
                    429,
                    {"prefill-queue-duration": "0.250", "num-concurrent-requests": "12"},
                ),
                _SUCCESS,
            ],
        )

        results = asyncio.run(sampler.sample_with_prompt_tokens([1, 2, 3]))

        assert len(results) == 1
        assert controller.acquired == 2
        assert controller.released == 2
        first_metrics = controller.released_metrics[0]
        assert first_metrics is not None
        assert first_metrics.http_status_code == 429
        assert first_metrics.retry_attempt == 1
        assert first_metrics.prefill_queue_duration == pytest.approx(0.25)
        assert first_metrics.num_concurrent_requests == 12


class TestContextAndRedaction:
    def test_context_carried_into_error(self, no_sleep, no_jitter):
        sampler = _make_sampler(request_context={"session": "sess-1", "run": "run-1", "checkpoint": "ckpt-3"})
        _install_stream(sampler, [_http_error(503)])

        with pytest.raises(SamplingRequestError) as excinfo:
            asyncio.run(sampler.sample_with_prompt_tokens([1, 2, 3], sampling_context={"step": 2, "group": 7}))

        err = excinfo.value
        assert err.context == {"session": "sess-1", "run": "run-1", "checkpoint": "ckpt-3", "step": 2, "group": 7}
        assert err.model == "m" and err.logical_request_id

    def test_error_record_has_no_secrets_or_prompt(self, no_sleep, no_jitter, monkeypatch):
        monkeypatch.setattr(
            uuid,
            "uuid4",
            lambda: uuid.UUID("01234567-89ab-cdef-0123-456789abcdef"),
        )
        sampler = _make_sampler()
        _install_stream(sampler, [_http_error(503)])
        with pytest.raises(SamplingRequestError) as excinfo:
            asyncio.run(sampler.sample_with_prompt_tokens([111, 222, 333]))
        err = excinfo.value
        blob = repr(err.as_error_record()) + str(err)
        assert "secret-key" not in blob  # api key never leaks
        assert "111" not in blob and "222" not in blob  # prompt tokens never leak


def _sse_success_bytes() -> bytes:
    chunk = '{"id":"cmpl-upstream-test","choices":[{"text":"hi","finish_reason":"stop","raw_output":{"completion_token_ids":[40,50]}}]}'
    return f"data: {chunk}\n\ndata: [DONE]\n\n".encode("utf-8")


class TestTransportLevel:
    def test_x_request_id_header_sent(self):
        seen: dict = {}

        def _handler(request: httpx.Request) -> httpx.Response:
            seen["x-request-id"] = request.headers.get("x-request-id")
            return httpx.Response(
                200,
                content=_sse_success_bytes(),
                headers={
                    "x-request-id": "lr-xyz-cmpl-server",
                    "fireworks-backend-host": "serving-pod-1",
                    "fireworks-deployment": "accounts/a/deployments/d",
                    "fireworks-pod-template-hash": "abc123",
                },
            )

        sampler = _make_sampler()
        sampler._async_client = httpx.AsyncClient(transport=httpx.MockTransport(_handler))
        result, metrics = asyncio.run(
            sampler.async_completions_stream(prompt=[1, 2, 3], raw_output=True, logical_request_id="lr-xyz")
        )
        assert result["choices"][0]["raw_output"]["completion_token_ids"] == [40, 50]
        assert result["id"] == "cmpl-upstream-test"
        assert seen["x-request-id"] == "lr-xyz"
        assert metrics.response_request_id == "lr-xyz-cmpl-server"
        assert metrics.backend_host == "serving-pod-1"
        assert metrics.deployment == "accounts/a/deployments/d"
        assert metrics.pod_template_hash == "abc123"
        sampler.close()

    def test_no_layer1_status_retry_single_post(self):
        posts = {"n": 0}

        def _handler(request: httpx.Request) -> httpx.Response:
            posts["n"] += 1
            return httpx.Response(503, json={"error": {"message": "overloaded"}})

        sampler = _make_sampler()
        sampler._async_client = httpx.AsyncClient(transport=httpx.MockTransport(_handler))
        with pytest.raises(httpx.HTTPStatusError):
            asyncio.run(sampler.async_completions_stream(prompt=[1, 2, 3], raw_output=True, logical_request_id="lr-1"))
        # errors.py opt-out means the transport is hit exactly once per stream call.
        assert posts["n"] == 1
        sampler.close()

    def test_typed_prompt_cache_key_and_header_snapshot(self):
        seen: dict = {}

        def _handler(request: httpx.Request) -> httpx.Response:
            seen["body"] = __import__("json").loads(request.content)
            seen["custom"] = request.headers.get("x-custom")
            return httpx.Response(200, content=_sse_success_bytes())

        source = {"X-Custom": "mutable"}
        sampler = _make_sampler(additional_headers=source)
        sampler._async_client = httpx.AsyncClient(transport=httpx.MockTransport(_handler))
        snapshot = {"x-custom": "frozen"}
        result, _ = asyncio.run(
            sampler.async_completions_stream(
                prompt=[1, 2, 3],
                raw_output=True,
                prompt_cache_key="affinity-1",
                additional_headers_snapshot=snapshot,
            )
        )
        assert result["choices"]
        assert seen["body"]["prompt_cache_key"] == "affinity-1"
        assert seen["custom"] == "frozen"
        sampler.close()

    def test_header_snapshot_keeps_auth_and_sdk_session_headers_request_local(self, monkeypatch):
        seen: list[dict[str, str]] = []

        def _handler(request: httpx.Request) -> httpx.Response:
            seen.append(dict(request.headers))
            return httpx.Response(200, content=_sse_success_bytes())

        source = {"X-Fireworks-Gateway-Secret": "fixed", "X-Custom": "original"}
        sampler = _make_sampler(additional_headers=source)
        sampler._async_client = httpx.AsyncClient(transport=httpx.MockTransport(_handler))
        snapshot = dict(source)
        first_session = str(uuid.uuid4())
        second_session = str(uuid.uuid4())
        monkeypatch.setenv("FIREWORKS_SESSION_ID", first_session)
        asyncio.run(
            sampler.async_completions_stream(
                prompt=[1, 2, 3],
                raw_output=True,
                additional_headers_snapshot=snapshot,
            )
        )

        sampler.api_key = "rotated-key"
        sampler.additional_headers = {"X-Custom": "replaced"}
        source["X-Custom"] = "mutated"
        monkeypatch.setenv("FIREWORKS_SESSION_ID", second_session)
        asyncio.run(
            sampler.async_completions_stream(
                prompt=[1, 2, 3],
                raw_output=True,
                additional_headers_snapshot=snapshot,
            )
        )

        assert seen[0]["authorization"] == "Bearer secret-key"
        assert seen[1]["authorization"] == "Bearer rotated-key"
        assert seen[0]["x-api-key"] == "secret-key"
        assert seen[1]["x-api-key"] == "rotated-key"
        assert seen[0]["x-fireworks-session-id"] == first_session
        assert seen[1]["x-fireworks-session-id"] == second_session
        assert [headers["x-fireworks-gateway-secret"] for headers in seen] == [
            "fixed",
            "fixed",
        ]
        assert [headers["x-custom"] for headers in seen] == ["original", "original"]
        sampler.close()

    def test_request_result_owns_attempt_and_metrics(self, no_sleep, no_jitter):
        sampler = _make_sampler()
        calls = _install_stream(
            sampler,
            [
                _http_error(429, {"x-request-id": "retry-attempt-1"}),
                (
                    _SUCCESS[0],
                    ServerMetrics(
                        prompt_tokens=3,
                        cached_prompt_tokens=2,
                        response_request_id="success-attempt-2",
                    ),
                ),
            ],
        )

        result = asyncio.run(
            sampler.sample_with_prompt_tokens_result([1, 2, 3], logical_request_id="gateway-logical-id")
        )
        assert len(calls) == 2
        assert result.attempts == 2
        assert result.logical_request_id == "gateway-logical-id"
        assert result.upstream_response_id == "cmpl-upstream-test"
        assert {call["logical_request_id"] for call in calls} == {"gateway-logical-id"}
        assert result.server_metrics.cached_prompt_tokens == 2
        assert len(result.completions) == 1
        assert [attempt.outcome for attempt in result.server_attempts] == [
            "retryable_error",
            "succeeded",
        ]
        assert [attempt.response_request_id for attempt in result.server_attempts] == [
            "retry-attempt-1",
            "success-attempt-2",
        ]
        assert result.server_attempts[1].upstream_response_id == "cmpl-upstream-test"


class TestServerMetricsNormalization:
    def test_prefixed_headers_and_unprefixed_perf_metrics_match(self):
        values = {
            "prompt-tokens": "12",
            "cached-prompt-tokens": "9",
            "server-processing-time": "1.25",
            "tokenizer-queue-duration": "0.1",
            "tokenizer-duration": "0.2",
            "prefill-queue-duration": "0.3",
            "prefill-duration": "0.4",
            "generation-queue-duration": "0.5",
            "generation-duration": "0.6",
        }
        unprefixed = ServerMetrics.from_headers(values)
        prefixed = ServerMetrics.from_headers({f"fireworks-{key}": value for key, value in values.items()})
        assert unprefixed == prefixed
        assert prefixed.prompt_tokens == 12
        assert prefixed.generation_duration == 0.6

    def test_header_only_correlation_fields_survive_perf_metric_merge(self):
        response_headers = {
            "x-request-id": "request-cmpl-1",
            "fireworks-backend-host": "pod-1",
            "fireworks-deployment": "accounts/a/deployments/d",
            "fireworks-pod-template-hash": "hash-1",
        }
        perf_metrics = {"prompt-tokens": "12", "cached-prompt-tokens": "9"}
        metrics = ServerMetrics.from_headers({**response_headers, **perf_metrics})
        assert metrics.response_request_id == "request-cmpl-1"
        assert metrics.backend_host == "pod-1"
        assert metrics.deployment == "accounts/a/deployments/d"
        assert metrics.pod_template_hash == "hash-1"
        assert metrics.cached_prompt_tokens == 9

    def test_numeric_zero_perf_metrics_are_not_dropped(self):
        metrics = ServerMetrics.from_headers(
            {
                "cached-prompt-tokens": 0,
                "prefill-queue-duration": 0.0,
            }
        )
        assert metrics.cached_prompt_tokens == 0
        assert metrics.prefill_queue_duration == 0.0
