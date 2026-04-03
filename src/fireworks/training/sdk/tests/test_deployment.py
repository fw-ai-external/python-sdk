"""Tests for fireworks.training.sdk.deployment — DeploymentManager + DeploymentSampler."""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

import pytest

from fireworks.training.sdk.deployment import (
    ServerMetrics,
    DeploymentConfig,
    DeploymentManager,
    DeploymentSampler,
    AdaptiveConcurrencyController,
)
from fireworks.training.sdk._rest_client import _should_verify_ssl


@pytest.fixture
def mgr():
    manager = DeploymentManager(
        api_key="test-key",
        base_url="https://api.example.com",
        inference_url="https://inference.example.com",
        hotload_api_url="https://hotload.example.com",
        additional_headers={"X-Secret": "s"},
    )
    manager._account_id = "test-acct"
    yield manager
    manager.close()


@pytest.fixture
def deploy_config():
    return DeploymentConfig(
        deployment_id="dep-1",
        base_model="accounts/test/models/qwen3-1p7b",
        region="US_OHIO_1",
    )


def _make_mock_tokenizer(return_ids=None):
    tok = MagicMock()
    tok.apply_chat_template.return_value = return_ids or [1, 2, 3]
    return tok


def _make_sampler(**kwargs):
    defaults = dict(
        inference_url="https://api.example.com",
        model="m",
        api_key="key",
        tokenizer=_make_mock_tokenizer(),
    )
    defaults.update(kwargs)
    return DeploymentSampler(**defaults)


def _mock_async_completions_stream(sampler, return_value):
    """Patch async_completions_stream to return a value without hitting the network."""
    async def _fake(*args, **kwargs):
        return return_value, ServerMetrics()
    sampler.async_completions_stream = _fake


# ---------------------------------------------------------------------------
# _should_verify_ssl
# ---------------------------------------------------------------------------


class TestShouldVerifySsl:
    def test_https_domain(self):
        assert _should_verify_ssl("https://api.fireworks.ai") is True

    def test_http_no_verify(self):
        assert _should_verify_ssl("http://203.0.113.10:8083") is False

    def test_https_ip_no_verify(self):
        assert _should_verify_ssl("https://203.0.113.10:8083") is False

    def test_https_localhost(self):
        assert _should_verify_ssl("https://127.0.0.1:8080") is False

    def test_https_real_domain(self):
        assert _should_verify_ssl("https://example.com") is True


# ---------------------------------------------------------------------------
# _parse_deployment_info
# ---------------------------------------------------------------------------


class TestParseDeploymentInfo:
    def test_all_fields_present(self, mgr):
        data = {
            "name": "accounts/a/deployments/d",
            "state": "READY",
            "deploymentShape": "accounts/a/deploymentShapes/s/versions/v",
        }
        info = mgr._parse_deployment_info("d", data)
        assert info.deployment_id == "d"
        assert info.state == "READY"
        assert info.deployment_shape_version == "accounts/a/deploymentShapes/s/versions/v"

    def test_missing_shape(self, mgr):
        data = {"name": "accounts/a/deployments/d", "state": "CREATING"}
        info = mgr._parse_deployment_info("d", data)
        assert info.deployment_shape_version is None


# ---------------------------------------------------------------------------
# Deployment creation
# ---------------------------------------------------------------------------


class TestCreateDeployment:
    def test_create_posts_correct_path(self, mgr, deploy_config):
        resp = MagicMock()
        resp.status_code = 200
        resp.is_success = True
        resp.json.return_value = {
            "name": "accounts/test-acct/deployments/dep-1",
            "state": "CREATING",
        }
        mgr._post = MagicMock(return_value=resp)
        mgr._create_deployment(deploy_config)
        path = mgr._post.call_args[0][0]
        assert "/deployments" in path

    def test_create_omits_placement_when_region_unset(self, mgr):
        resp = MagicMock()
        resp.status_code = 200
        resp.is_success = True
        resp.json.return_value = {
            "name": "accounts/test-acct/deployments/dep-1",
            "state": "CREATING",
        }
        mgr._post = MagicMock(return_value=resp)

        mgr._create_deployment(
            DeploymentConfig(
                deployment_id="dep-1",
                base_model="accounts/test/models/qwen3-1p7b",
            )
        )

        body = mgr._post.call_args[1]["json"]
        assert "placement" not in body

    def test_409_is_not_raised(self, mgr, deploy_config):
        resp = MagicMock()
        resp.status_code = 409
        resp.is_success = False
        resp.json.return_value = {"error": "already exists"}
        mgr._post = MagicMock(return_value=resp)
        mgr._create_deployment(deploy_config)


# ---------------------------------------------------------------------------
# Hotload
# ---------------------------------------------------------------------------


class TestHotload:
    @staticmethod
    def _response(status_code: int, payload: dict | None = None, text: str = ""):
        resp = MagicMock()
        resp.status_code = status_code
        resp.is_success = 200 <= status_code < 300
        resp.json.return_value = payload or {}
        resp.text = text
        return resp

    def test_hotload_sends_identity(self, mgr):
        resp = MagicMock()
        resp.status_code = 200
        resp.is_success = True
        resp.json.return_value = {}
        mgr._sync_request = MagicMock(return_value=resp)

        mgr.hotload("dep-1", "accounts/test/models/m", "snap-123")
        call_kwargs = mgr._sync_request.call_args[1]
        assert call_kwargs["json"]["identity"] == "snap-123"

    def test_hotload_headers_include_additional_headers(self, mgr):
        headers = mgr._hotload_headers("dep-1", "accounts/test/models/m")
        assert headers.get("X-Secret") == "s"
        assert "Authorization" in headers
        assert "fireworks-model" in headers

    def test_hotload_incremental_metadata(self, mgr):
        resp = MagicMock()
        resp.status_code = 200
        resp.is_success = True
        resp.json.return_value = {}
        mgr._sync_request = MagicMock(return_value=resp)

        mgr.hotload(
            "dep-1", "accounts/test/models/m", "snap-2",
            incremental_snapshot_metadata={"previous_snapshot_identity": "snap-1"},
        )
        payload = mgr._sync_request.call_args[1]["json"]
        assert payload["incremental_snapshot_metadata"]["previous_snapshot_identity"] == "snap-1"

    def test_hotload_retries_without_reset_prompt_cache_when_rejected(self, mgr):
        unsupported = self._response(
            400,
            {"error": {"message": "Extra inputs are not permitted, field: 'reset_prompt_cache', value: True"}},
            text="Extra inputs are not permitted, field: 'reset_prompt_cache', value: True",
        )
        success = self._response(200, {})
        mgr._sync_request = MagicMock(side_effect=[unsupported, success, success])

        mgr.hotload("dep-1", "accounts/test/models/m", "snap-123")
        mgr.hotload("dep-1", "accounts/test/models/m", "snap-456")

        first_payload = mgr._sync_request.call_args_list[0].kwargs["json"]
        retry_payload = mgr._sync_request.call_args_list[1].kwargs["json"]
        second_call_payload = mgr._sync_request.call_args_list[2].kwargs["json"]

        assert first_payload["reset_prompt_cache"] is True
        assert "reset_prompt_cache" not in retry_payload
        assert "reset_prompt_cache" not in second_call_payload
        assert mgr._hotload_reset_prompt_cache_supported is False


# ---------------------------------------------------------------------------
# wait_for_hotload
# ---------------------------------------------------------------------------


class TestWaitForHotload:
    def test_immediate_success(self, mgr):
        mgr.hotload_check_status = MagicMock(return_value={
            "replicas": [{
                "identity": "snap-1",
                "stage": "idle",
                "ready": True,
            }]
        })
        result = mgr.wait_for_hotload("dep-1", "m", "snap-1", timeout_seconds=5, poll_interval=0)
        assert result is True

    def test_timeout_returns_false(self, mgr):
        mgr.hotload_check_status = MagicMock(return_value={
            "replicas": [{
                "identity": None,
                "stage": "downloading",
                "ready": False,
            }]
        })
        result = mgr.wait_for_hotload("dep-1", "m", "snap-x", timeout_seconds=0.01, poll_interval=0.005)
        assert result is False


# ---------------------------------------------------------------------------
# _extract_logprobs
# ---------------------------------------------------------------------------


class TestExtractLogprobs:
    def test_modern_structured_format(self):
        choice = {"logprobs": {"content": [{"logprob": -0.5}, {"logprob": -1.2}]}}
        lps = DeploymentSampler._extract_logprobs(choice)
        assert lps == [-0.5, -1.2]

    def test_none_if_absent(self):
        assert DeploymentSampler._extract_logprobs({}) is None
        assert DeploymentSampler._extract_logprobs({"logprobs": None}) is None
        assert DeploymentSampler._extract_logprobs({"logprobs": {}}) is None

    def test_empty_content(self):
        assert DeploymentSampler._extract_logprobs({"logprobs": {"content": []}}) is None



# ---------------------------------------------------------------------------
# DeploymentManager.warmup — token-in warmup payload
# ---------------------------------------------------------------------------


class TestWarmup:
    def test_uses_token_prompt(self, mgr):
        resp = MagicMock()
        resp.status_code = 200
        mgr._sync_request = MagicMock(return_value=resp)

        assert mgr.warmup("accounts/test/deployments/dep-1", max_retries=1) is True
        payload = mgr._sync_request.call_args[1]["json"]
        assert isinstance(payload["prompt"], list)
        assert all(isinstance(tok, int) for tok in payload["prompt"])

    def test_warmup_headers_include_additional(self, mgr):
        resp = MagicMock()
        resp.status_code = 200
        mgr._sync_request = MagicMock(return_value=resp)

        mgr.warmup("accounts/test/deployments/dep-1", max_retries=1)
        headers = mgr._sync_request.call_args[1]["headers"]
        assert headers.get("X-Secret") == "s"


# ---------------------------------------------------------------------------
# DeploymentSampler.sample_with_tokens — client-side tokenization
# ---------------------------------------------------------------------------


class TestSampleWithTokens:
    def test_basic_sample(self):
        prompt_ids = [1, 100, 200]
        completion_ids = [400, 500]

        sampler = _make_sampler(tokenizer=_make_mock_tokenizer(prompt_ids))
        _mock_async_completions_stream(sampler, {
            "choices": [{
                "text": "hello world",
                "finish_reason": "stop",
                "raw_output": {"completion_token_ids": completion_ids},
            }]
        })

        results = asyncio.run(sampler.sample_with_tokens(
            messages=[{"role": "user", "content": "hi"}],
        ))

        assert len(results) == 1
        c = results[0]
        assert c.text == "hello world"
        assert c.full_tokens == prompt_ids + completion_ids
        assert c.prompt_len == len(prompt_ids)
        assert c.completion_len == len(completion_ids)
        assert c.finish_reason == "stop"
        sampler.close()

    def test_tokenizer_called_with_messages(self):
        tok = _make_mock_tokenizer([1, 2, 3])
        sampler = _make_sampler(tokenizer=tok)
        _mock_async_completions_stream(sampler, {
            "choices": [{
                "text": "ok", "finish_reason": "stop",
                "raw_output": {"completion_token_ids": [99]},
            }]
        })

        messages = [{"role": "user", "content": "test"}]
        asyncio.run(sampler.sample_with_tokens(messages=messages))
        tok.apply_chat_template.assert_called_once_with(
            messages, tokenize=True, add_generation_prompt=True, return_dict=False,
        )
        sampler.close()

    def test_missing_completion_token_ids_raises(self):
        sampler = _make_sampler(tokenizer=_make_mock_tokenizer([1, 2, 3]))
        _mock_async_completions_stream(sampler, {
            "choices": [{"text": "ok", "finish_reason": "stop", "raw_output": {}}]
        })

        with pytest.raises(RuntimeError, match="missing completion_token_ids"):
            asyncio.run(sampler.sample_with_tokens(
                messages=[{"role": "user", "content": "hi"}],
            ))
        sampler.close()

    def test_echo_strips_verified_prefix(self):
        prompt_ids = [1, 100, 200]
        echoed_completion_ids = [1, 100, 200, 400, 500]

        sampler = _make_sampler(tokenizer=_make_mock_tokenizer(prompt_ids))
        _mock_async_completions_stream(sampler, {
            "choices": [{
                "text": "gen", "finish_reason": "stop",
                "raw_output": {"completion_token_ids": echoed_completion_ids},
            }]
        })

        results = asyncio.run(sampler.sample_with_tokens(
            messages=[{"role": "user", "content": "hi"}], echo=True,
        ))

        assert len(results) == 1
        c = results[0]
        assert c.full_tokens == prompt_ids + [400, 500]
        assert c.completion_len == 2
        assert c.logprobs_echoed is False
        sampler.close()

    def test_echo_logprobs_aligned(self):
        prompt_ids = [1, 100, 200]
        echoed_ids = [1, 100, 200, 400, 500]

        sampler = _make_sampler(tokenizer=_make_mock_tokenizer(prompt_ids))
        _mock_async_completions_stream(sampler, {
            "choices": [{
                "text": "gen", "finish_reason": "stop",
                "raw_output": {"completion_token_ids": echoed_ids},
                "logprobs": {"content": [
                    {"logprob": 0.0},
                    {"logprob": -0.1},
                    {"logprob": -0.2},
                    {"logprob": -0.3},
                    {"logprob": -0.4},
                ]},
            }]
        })

        results = asyncio.run(sampler.sample_with_tokens(
            messages=[{"role": "user", "content": "hi"}],
            echo=True, logprobs=True,
        ))

        c = results[0]
        assert c.logprobs_echoed is True
        assert c.inference_logprobs == [-0.1, -0.2, -0.3, -0.4]
        sampler.close()

    def test_max_seq_len_pre_filter(self):
        sampler = _make_sampler(tokenizer=_make_mock_tokenizer([1, 2, 3, 4, 5]))
        _mock_async_completions_stream(sampler, {"choices": []})

        results = asyncio.run(sampler.sample_with_tokens(
            messages=[{"role": "user", "content": "hi"}], max_seq_len=5,
        ))
        assert results == []
        sampler.close()

    def test_max_seq_len_post_filter(self):
        prompt_ids = [1, 2]
        long_completion = list(range(100, 200))

        sampler = _make_sampler(tokenizer=_make_mock_tokenizer(prompt_ids))
        _mock_async_completions_stream(sampler, {
            "choices": [{
                "text": "long", "finish_reason": "length",
                "raw_output": {"completion_token_ids": long_completion},
            }]
        })

        results = asyncio.run(sampler.sample_with_tokens(
            messages=[{"role": "user", "content": "hi"}], max_seq_len=50,
        ))
        assert len(results) == 0
        sampler.close()

    def test_logprobs_extracted(self):
        sampler = _make_sampler(tokenizer=_make_mock_tokenizer([1, 2]))
        _mock_async_completions_stream(sampler, {
            "choices": [{
                "text": "hi", "finish_reason": "stop",
                "raw_output": {"completion_token_ids": [99]},
                "logprobs": {"content": [{"logprob": -1.5}]},
            }]
        })

        results = asyncio.run(sampler.sample_with_tokens(
            messages=[{"role": "user", "content": "x"}], logprobs=True,
        ))
        assert results[0].inference_logprobs == [-1.5]
        sampler.close()

    def test_routing_matrices_extracted(self):
        sampler = _make_sampler(tokenizer=_make_mock_tokenizer([1, 2]))
        _mock_async_completions_stream(sampler, {
            "choices": [{
                "text": "hi", "finish_reason": "stop",
                "raw_output": {"completion_token_ids": [99]},
                "logprobs": {"content": [{"logprob": -0.5, "routing_matrix": "AQID"}]},
            }]
        })

        results = asyncio.run(sampler.sample_with_tokens(
            messages=[{"role": "user", "content": "x"}],
            include_routing_matrix=True,
        ))
        assert results[0].routing_matrices == ["AQID"]
        sampler.close()


# ---------------------------------------------------------------------------
# Default parameter values
# ---------------------------------------------------------------------------


class TestDefaultValues:
    def test_default_temperature_is_1(self):
        import inspect
        sig = inspect.signature(DeploymentSampler.async_completions_stream)
        assert sig.parameters["temperature"].default == 1.0
        sig2 = inspect.signature(DeploymentSampler.sample_with_tokens)
        assert sig2.parameters["temperature"].default == 1.0


# ---------------------------------------------------------------------------
# Deployment CRUD — REST method wrappers
# ---------------------------------------------------------------------------


class TestDeploymentCrud:
    def test_get_deployment_calls_rest_get(self, mgr):
        resp = MagicMock()
        resp.status_code = 200
        resp.is_success = True
        resp.json.return_value = {"name": "n", "state": "READY"}
        mgr._get = MagicMock(return_value=resp)

        result = mgr._get_deployment("dep-1")
        path = mgr._get.call_args[0][0]
        assert "/deployments/dep-1" in path
        assert result is not None

    def test_get_deployment_returns_none_on_404(self, mgr):
        resp = MagicMock()
        resp.status_code = 404
        mgr._get = MagicMock(return_value=resp)

        result = mgr._get_deployment("dep-1")
        assert result is None

    def test_scale_to_zero_calls_rest_patch(self, mgr):
        resp = MagicMock()
        resp.is_success = True
        mgr._patch = MagicMock(return_value=resp)

        mgr.scale_to_zero("dep-1")
        path = mgr._patch.call_args[0][0]
        assert "/deployments/dep-1" in path
        body = mgr._patch.call_args[1]["json"]
        assert body["maxReplicaCount"] == 0
        assert body["minReplicaCount"] == 0


# ---------------------------------------------------------------------------
# ServerMetrics
# ---------------------------------------------------------------------------


class TestServerMetrics:
    def test_from_headers_full(self):
        headers = {
            "num-concurrent-requests": "12",
            "prefill-queue-duration": "0.250",
            "generation-queue-duration": "1.100",
            "server-time-to-first-token": "0.350",
            "cached-prompt-tokens": "128",
            "prompt-tokens": "256",
            "server-processing-time": "2.500",
        }
        m = ServerMetrics.from_headers(headers, client_ttft=0.4)
        assert m.num_concurrent_requests == 12
        assert m.prefill_queue_duration == pytest.approx(0.25)
        assert m.generation_queue_duration == pytest.approx(1.1)
        assert m.server_ttft == pytest.approx(0.35)
        assert m.cached_prompt_tokens == 128
        assert m.prompt_tokens == 256
        assert m.server_processing_time == pytest.approx(2.5)
        assert m.client_ttft == pytest.approx(0.4)

    def test_from_headers_empty(self):
        m = ServerMetrics.from_headers({})
        assert m.num_concurrent_requests is None
        assert m.prefill_queue_duration is None
        assert m.client_ttft is None

    def test_from_headers_invalid_values(self):
        headers = {"num-concurrent-requests": "bad", "prefill-queue-duration": "bad"}
        m = ServerMetrics.from_headers(headers)
        assert m.num_concurrent_requests is None
        assert m.prefill_queue_duration is None


# ---------------------------------------------------------------------------
# AdaptiveConcurrencyController
# ---------------------------------------------------------------------------


class TestAdaptiveConcurrencyController:
    def test_initial_window(self):
        ctrl = AdaptiveConcurrencyController(initial_window=16)
        assert ctrl.window_size == 16

    def test_acquire_release_basic(self):
        ctrl = AdaptiveConcurrencyController(initial_window=2)

        async def _test():
            await ctrl.acquire()
            await ctrl.acquire()
            assert ctrl._semaphore._value == 0
            ctrl.release()
            ctrl.release()
            assert ctrl._semaphore._value == 2

        asyncio.run(_test())

    def test_release_collects_but_does_not_adjust(self):
        """release() collects metrics but does NOT change the window."""
        ctrl = AdaptiveConcurrencyController(initial_window=10, ema_alpha=1.0)
        ctrl.release(ServerMetrics(prefill_queue_duration=5.0))
        assert ctrl.window_size == 10  # unchanged until step_completed()

    def test_step_completed_decrease_on_high_pq(self):
        ctrl = AdaptiveConcurrencyController(
            initial_window=10, prefill_queue_target=0.5,
            multiplicative_decrease=0.5, ema_alpha=1.0,
        )
        # Simulate a step with high prefill queue.
        for _ in range(8):
            ctrl.release(ServerMetrics(prefill_queue_duration=2.0))
        summary = ctrl.step_completed()
        assert ctrl.window_size < 10
        assert summary["avg_pq"] == pytest.approx(2.0)

    def test_step_completed_increase_on_low_pq(self):
        ctrl = AdaptiveConcurrencyController(
            initial_window=4, prefill_queue_target=1.0,
            additive_increase=2.0, ema_alpha=1.0,
        )
        for _ in range(8):
            ctrl.release(ServerMetrics(prefill_queue_duration=0.1))
        ctrl.step_completed()
        assert ctrl._window > 4.0

    def test_no_change_without_metrics(self):
        ctrl = AdaptiveConcurrencyController(initial_window=8)
        ctrl.release(None)
        ctrl.step_completed()
        assert ctrl.window_size == 8
        assert ctrl.ema_prefill_queue is None

    def test_ema_smoothing_across_steps(self):
        ctrl = AdaptiveConcurrencyController(initial_window=10, ema_alpha=0.5, prefill_queue_target=1.0)
        # Step 1: avg_pq = 0.4
        ctrl.release(ServerMetrics(prefill_queue_duration=0.4))
        ctrl.step_completed()
        assert ctrl.ema_prefill_queue == pytest.approx(0.4)
        # Step 2: avg_pq = 0.8
        ctrl.release(ServerMetrics(prefill_queue_duration=0.8))
        ctrl.step_completed()
        assert ctrl.ema_prefill_queue == pytest.approx(0.5 * 0.8 + 0.5 * 0.4)

    def test_repeated_congestion_floors_at_min(self):
        ctrl = AdaptiveConcurrencyController(
            initial_window=16, min_window=2, prefill_queue_target=0.1,
            multiplicative_decrease=0.5, ema_alpha=1.0,
        )
        for _ in range(20):
            ctrl.release(ServerMetrics(prefill_queue_duration=5.0))
            ctrl.step_completed()
        assert ctrl.window_size == 2

    def test_repeated_good_metrics_caps_at_max(self):
        ctrl = AdaptiveConcurrencyController(
            initial_window=4, max_window=16, prefill_queue_target=1.0,
            additive_increase=5.0, ema_alpha=1.0,
        )
        for _ in range(100):
            ctrl.release(ServerMetrics(prefill_queue_duration=0.01))
            ctrl.step_completed()
        assert ctrl.window_size == 16

    def test_step_completed_resets_accumulators(self):
        ctrl = AdaptiveConcurrencyController(initial_window=8)
        ctrl.release(ServerMetrics(prefill_queue_duration=0.3, cached_prompt_tokens=10, prompt_tokens=100))
        ctrl.release(ServerMetrics(prefill_queue_duration=0.5, cached_prompt_tokens=20, prompt_tokens=100))
        summary = ctrl.step_completed()
        assert summary["requests"] == 2
        assert summary["avg_pq"] == pytest.approx(0.4)
        assert summary["cache_hit_rate"] == pytest.approx(30 / 200)
        # After step_completed, accumulators are reset.
        summary2 = ctrl.step_completed()
        assert summary2["requests"] == 0
        assert "avg_pq" not in summary2


# ---------------------------------------------------------------------------
# Streaming completions
# ---------------------------------------------------------------------------


class TestStreamingCompletions:
    def test_streaming_with_adaptive_controller(self):
        import json as _json
        prompt_ids = [1, 2, 3]
        completion_ids = [400, 500]
        ctrl = AdaptiveConcurrencyController(initial_window=8, ema_alpha=1.0)
        sampler = _make_sampler(tokenizer=_make_mock_tokenizer(prompt_ids), concurrency_controller=ctrl)

        chunk_data = {
            "choices": [{
                "text": "hello",
                "raw_output": {"completion_token_ids": completion_ids},
                "finish_reason": "stop",
            }],
            "perf_metrics": {"prefill-queue-duration": "0.1"},
        }
        # SSE wire format: "data: {json}\n\n" per event
        raw_bytes = (
            f"data: {_json.dumps(chunk_data)}\n\n"
            f"data: [DONE]\n\n"
        ).encode()

        async def mock_post(*args, **kwargs):
            resp = MagicMock()
            resp.status_code = 200
            resp.raise_for_status = MagicMock()
            resp.headers = {}

            async def aiter_bytes():
                yield raw_bytes
            resp.aiter_bytes = aiter_bytes
            return resp

        sampler._get_async_client = MagicMock()
        sampler._get_async_client.return_value.post = mock_post

        results = asyncio.run(sampler.sample_with_tokens(
            messages=[{"role": "user", "content": "hi"}],
        ))
        assert len(results) == 1
        assert results[0].full_tokens == prompt_ids + completion_ids
        # Metrics collected but window not adjusted yet.
        assert ctrl.ema_prefill_queue is None
        # Trigger step-level adjustment.
        summary = ctrl.step_completed()
        assert ctrl.ema_prefill_queue == pytest.approx(0.1)
        assert summary["avg_pq"] == pytest.approx(0.1)
        sampler.close()
