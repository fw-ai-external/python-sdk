"""Tests for structured sampling observability in DeploymentSampler.

Covers the single-owner retry budget, Retry-After honoring, stable logical
request ids, and the structured terminal error (attempt history + context).
Payload-free by construction: no prompt/token/key content may appear in any
recorded attempt or exception.
"""

from __future__ import annotations

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


def _http_error(status: int, headers: dict | None = None) -> httpx.HTTPStatusError:
    req = httpx.Request("POST", _URL)
    resp = httpx.Response(status, headers=headers or {}, request=req)
    return httpx.HTTPStatusError(f"HTTP {status}", request=req, response=resp)


_SUCCESS = (
    {"choices": [{"text": "hi", "finish_reason": "stop", "raw_output": {"completion_token_ids": [40, 50]}}]},
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
        with pytest.raises(httpx.HTTPStatusError):
            asyncio.run(sampler.sample_with_prompt_tokens([1, 2, 3]))
        assert len(calls) == 1  # no retry

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


class TestContextAndRedaction:
    def test_context_carried_into_error(self, no_sleep, no_jitter):
        sampler = _make_sampler(request_context={"session": "sess-1", "run": "run-1", "checkpoint": "ckpt-3"})
        _install_stream(sampler, [_http_error(503)])

        with pytest.raises(SamplingRequestError) as excinfo:
            asyncio.run(sampler.sample_with_prompt_tokens([1, 2, 3], sampling_context={"step": 2, "group": 7}))

        err = excinfo.value
        assert err.context == {"session": "sess-1", "run": "run-1", "checkpoint": "ckpt-3", "step": 2, "group": 7}
        assert err.model == "m" and err.logical_request_id

    def test_error_record_has_no_secrets_or_prompt(self, no_sleep, no_jitter):
        sampler = _make_sampler()
        _install_stream(sampler, [_http_error(503)])
        with pytest.raises(SamplingRequestError) as excinfo:
            asyncio.run(sampler.sample_with_prompt_tokens([111, 222, 333]))
        err = excinfo.value
        blob = repr(err.as_error_record()) + str(err)
        assert "secret-key" not in blob  # api key never leaks
        assert "111" not in blob and "222" not in blob  # prompt tokens never leak


def _sse_success_bytes() -> bytes:
    chunk = (
        '{"choices":[{"text":"hi","finish_reason":"stop","raw_output":{"completion_token_ids":[40,50]}}]}'
    )
    return f"data: {chunk}\n\ndata: [DONE]\n\n".encode("utf-8")


class TestTransportLevel:
    def test_x_request_id_header_sent(self):
        seen: dict = {}

        def _handler(request: httpx.Request) -> httpx.Response:
            seen["x-request-id"] = request.headers.get("x-request-id")
            return httpx.Response(200, content=_sse_success_bytes())

        sampler = _make_sampler()
        sampler._async_client = httpx.AsyncClient(transport=httpx.MockTransport(_handler))
        result, _ = asyncio.run(
            sampler.async_completions_stream(prompt=[1, 2, 3], raw_output=True, logical_request_id="lr-xyz")
        )
        assert result["choices"][0]["raw_output"]["completion_token_ids"] == [40, 50]
        assert seen["x-request-id"] == "lr-xyz"
        sampler.close()

    def test_no_layer1_status_retry_single_post(self):
        posts = {"n": 0}

        def _handler(request: httpx.Request) -> httpx.Response:
            posts["n"] += 1
            return httpx.Response(503, json={"error": {"message": "overloaded"}})

        sampler = _make_sampler()
        sampler._async_client = httpx.AsyncClient(transport=httpx.MockTransport(_handler))
        with pytest.raises(httpx.HTTPStatusError):
            asyncio.run(
                sampler.async_completions_stream(prompt=[1, 2, 3], raw_output=True, logical_request_id="lr-1")
            )
        # errors.py opt-out means the transport is hit exactly once per stream call.
        assert posts["n"] == 1
        sampler.close()
