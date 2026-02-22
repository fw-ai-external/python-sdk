"""Tests for fireworks.training.sdk.deployment — DeploymentManager + DeploymentSampler."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from fireworks.training.sdk.deployment import (
    DeploymentConfig,
    DeploymentManager,
    DeploymentSampler,
)


@pytest.fixture
def mgr():
    return DeploymentManager(
        api_key="test-key",
        account_id="test-acct",
        base_url="https://api.example.com",
        inference_url="https://inference.example.com",
        hotload_api_url="https://hotload.example.com",
        additional_headers={"X-Secret": "s"},
    )


@pytest.fixture
def deploy_config():
    return DeploymentConfig(
        deployment_id="dep-1",
        base_model="accounts/test/models/qwen3-1p7b",
        region="US_OHIO_1",
    )


# ---------------------------------------------------------------------------
# _should_verify_ssl
# ---------------------------------------------------------------------------


class TestShouldVerifySsl:
    def test_https_domain(self):
        assert DeploymentManager._should_verify_ssl("https://api.fireworks.ai") is True

    def test_http_no_verify(self):
        assert DeploymentManager._should_verify_ssl("http://203.0.113.10:8083") is False

    def test_https_ip_no_verify(self):
        assert DeploymentManager._should_verify_ssl("https://203.0.113.10:8083") is False

    def test_https_localhost(self):
        assert DeploymentManager._should_verify_ssl("https://127.0.0.1:8080") is False

    def test_https_real_domain(self):
        assert DeploymentManager._should_verify_ssl("https://example.com") is True


# ---------------------------------------------------------------------------
# _parse_deployment_info
# ---------------------------------------------------------------------------


class TestParseDeploymentInfo:
    def test_all_fields_present(self, mgr):
        data = {
            "name": "accounts/test-acct/deployments/dep-1",
            "state": "READY",
            "hotLoadBucketUrl": "gs://bucket/path",
        }
        info = mgr._parse_deployment_info("dep-1", data)
        assert info.deployment_id == "dep-1"
        assert info.state == "READY"
        assert info.hot_load_bucket_url == "gs://bucket/path"
        assert info.inference_model == "accounts/test-acct/deployments/dep-1"

    def test_missing_hot_load_bucket(self, mgr):
        data = {"name": "n", "state": "READY"}
        info = mgr._parse_deployment_info("dep-1", data)
        assert info.hot_load_bucket_url is None


# ---------------------------------------------------------------------------
# hotload — header construction
# ---------------------------------------------------------------------------


class TestHotload:
    @patch("fireworks.training.sdk.deployment.request_with_retries")
    def test_hotload_headers_and_payload(self, mock_req, mgr):
        resp = MagicMock()
        resp.ok = True
        resp.json.return_value = {"status": "ok"}
        mock_req.return_value = resp

        mgr.hotload("dep-1", "accounts/test/models/m", "snap-1")

        call_args = mock_req.call_args
        headers = call_args[1]["headers"]
        assert headers["fireworks-model"] == "accounts/test/models/m"
        assert headers["fireworks-deployment"] == "accounts/test-acct/deployments/dep-1"
        assert headers["Authorization"] == "Bearer test-key"

        payload = call_args[1]["json"]
        assert payload["identity"] == "snap-1"

    @patch("fireworks.training.sdk.deployment.request_with_retries")
    def test_hotload_with_incremental_metadata(self, mock_req, mgr):
        resp = MagicMock()
        resp.ok = True
        resp.json.return_value = {}
        mock_req.return_value = resp

        meta = {"previous_snapshot_identity": "snap-0", "compression_format": "arc_v2"}
        mgr.hotload("dep-1", "accounts/test/models/m", "snap-1", incremental_snapshot_metadata=meta)

        payload = mock_req.call_args[1]["json"]
        assert payload["incremental_snapshot_metadata"] == meta


# ---------------------------------------------------------------------------
# wait_for_hotload
# ---------------------------------------------------------------------------


class TestWaitForHotload:
    @patch.object(DeploymentManager, "hotload_check_status")
    def test_replicas_format_ready(self, mock_status, mgr):
        mock_status.return_value = {
            "replicas": [
                {
                    "current_snapshot_identity": "snap-1",
                    "readiness": True,
                    "loading_state": {"stage": "done"},
                }
            ]
        }
        assert mgr.wait_for_hotload("dep-1", "m", "snap-1", timeout_seconds=5) is True

    @patch.object(DeploymentManager, "hotload_check_status")
    def test_missing_replicas_key_raises_runtime_error(self, mock_status, mgr):
        mock_status.return_value = {
            "identity": "snap-1",
            "state": "READY",
            "readiness": True,
        }
        with pytest.raises(RuntimeError, match="Expected 'replicas' list"):
            mgr.wait_for_hotload("dep-1", "m", "snap-1", timeout_seconds=5)

    @patch.object(DeploymentManager, "hotload_check_status")
    def test_identity_mismatch_waits(self, mock_status, mgr):
        mock_status.return_value = {
            "replicas": [
                {
                    "current_snapshot_identity": "snap-0",
                    "readiness": True,
                    "loading_state": {"stage": "done"},
                }
            ]
        }
        assert mgr.wait_for_hotload("dep-1", "m", "snap-1", timeout_seconds=0) is False

    @patch.object(DeploymentManager, "hotload_check_status")
    def test_error_stage_returns_false(self, mock_status, mgr):
        mock_status.return_value = {
            "replicas": [
                {
                    "current_snapshot_identity": None,
                    "readiness": False,
                    "loading_state": {"stage": "error"},
                }
            ]
        }
        assert mgr.wait_for_hotload("dep-1", "m", "snap-1", timeout_seconds=5) is False

    @patch.object(DeploymentManager, "hotload_check_status")
    def test_unrecognized_format_raises_runtime_error(self, mock_status, mgr):
        mock_status.return_value = {"unknown_key": "value"}
        with pytest.raises(RuntimeError, match="Unrecognized hotload status response format"):
            mgr.wait_for_hotload("dep-1", "m", "snap-1", timeout_seconds=5)


# ---------------------------------------------------------------------------
# DeploymentSampler._extract_logprobs
# ---------------------------------------------------------------------------


class TestExtractLogprobs:
    def test_structured_format(self):
        choice = {
            "logprobs": {
                "content": [
                    {"logprob": -0.5, "token": "hello"},
                    {"logprob": -1.2, "token": "world"},
                ]
            }
        }
        result = DeploymentSampler._extract_logprobs(choice)
        assert result == [-0.5, -1.2]

    def test_structured_takes_priority(self):
        choice = {
            "logprobs": {
                "content": [{"logprob": -0.5}],
                "token_logprobs": [-0.9],
            }
        }
        result = DeploymentSampler._extract_logprobs(choice)
        assert result == [-0.5]

    def test_missing_logprobs(self):
        assert DeploymentSampler._extract_logprobs({}) is None

    def test_empty_content_returns_none(self):
        assert DeploymentSampler._extract_logprobs({"logprobs": {"content": []}}) is None

    def test_missing_logprob_field_defaults_zero(self):
        choice = {"logprobs": {"content": [{"token": "hi"}]}}
        result = DeploymentSampler._extract_logprobs(choice)
        assert result == [0.0]


# ---------------------------------------------------------------------------
# Mock tokenizer for DeploymentSampler tests
# ---------------------------------------------------------------------------


def _make_mock_tokenizer(prompt_ids=None):
    """Create a mock tokenizer that returns fixed token IDs."""
    tok = MagicMock()
    tok.apply_chat_template.return_value = prompt_ids or [1, 100, 200, 300]
    return tok


# ---------------------------------------------------------------------------
# DeploymentSampler.completions — mock HTTP
# ---------------------------------------------------------------------------


class TestCompletions:
    @patch("fireworks.training.sdk.deployment.time.sleep")
    @patch("fireworks.training.sdk.deployment.request_with_retries")
    def test_425_retry(self, mock_req, mock_sleep):
        resp_425 = MagicMock()
        resp_425.status_code = 425
        resp_425.ok = False

        resp_ok = MagicMock()
        resp_ok.status_code = 200
        resp_ok.ok = True
        resp_ok.json.return_value = {"choices": []}
        mock_req.side_effect = [resp_425, resp_ok]

        sampler = DeploymentSampler(
            inference_url="https://api.example.com",
            model="m",
            api_key="key",
            tokenizer=_make_mock_tokenizer(),
        )
        result = sampler.completions(
            prompt=[1, 2, 3],
            hotload_retry_interval=0.01,
        )
        assert mock_req.call_count == 2

    @patch("fireworks.training.sdk.deployment.request_with_retries")
    def test_sends_token_ids_as_prompt(self, mock_req):
        resp_ok = MagicMock()
        resp_ok.status_code = 200
        resp_ok.ok = True
        resp_ok.json.return_value = {"choices": []}
        mock_req.return_value = resp_ok

        sampler = DeploymentSampler(
            inference_url="https://api.example.com",
            model="m",
            api_key="key",
            tokenizer=_make_mock_tokenizer(),
        )
        sampler.completions(prompt=[10, 20, 30])

        payload = mock_req.call_args[1]["json"]
        assert payload["prompt"] == [10, 20, 30]
        assert "messages" not in payload
        assert "/v1/completions" in mock_req.call_args[0][1]


# ---------------------------------------------------------------------------
# DeploymentManager.warmup — token-in warmup payload
# ---------------------------------------------------------------------------


class TestWarmup:
    @patch("fireworks.training.sdk.deployment.requests.post")
    def test_uses_token_prompt(self, mock_post, mgr):
        resp = MagicMock()
        resp.status_code = 200
        mock_post.return_value = resp

        assert mgr.warmup("accounts/test/deployments/dep-1", max_retries=1) is True
        payload = mock_post.call_args[1]["json"]
        assert isinstance(payload["prompt"], list)
        assert all(isinstance(tok, int) for tok in payload["prompt"])


# ---------------------------------------------------------------------------
# DeploymentSampler.sample_with_tokens — client-side tokenization
# ---------------------------------------------------------------------------


class TestSampleWithTokens:
    @patch("fireworks.training.sdk.deployment.request_with_retries")
    def test_basic_sample(self, mock_req):
        prompt_ids = [1, 100, 200]
        completion_ids = [400, 500]

        resp = MagicMock()
        resp.status_code = 200
        resp.ok = True
        resp.json.return_value = {
            "choices": [
                {
                    "text": "hello world",
                    "finish_reason": "stop",
                    "raw_output": {"completion_token_ids": completion_ids},
                }
            ]
        }
        mock_req.return_value = resp

        sampler = DeploymentSampler(
            inference_url="https://api.example.com",
            model="m",
            api_key="key",
            tokenizer=_make_mock_tokenizer(prompt_ids),
        )
        results = sampler.sample_with_tokens(
            messages=[{"role": "user", "content": "hi"}],
        )

        assert len(results) == 1
        c = results[0]
        assert c.text == "hello world"
        assert c.full_tokens == prompt_ids + completion_ids
        assert c.prompt_len == len(prompt_ids)
        assert c.completion_len == len(completion_ids)
        assert c.finish_reason == "stop"

    @patch("fireworks.training.sdk.deployment.request_with_retries")
    def test_tokenizer_called_with_messages(self, mock_req):
        tok = _make_mock_tokenizer([1, 2, 3])

        resp = MagicMock()
        resp.status_code = 200
        resp.ok = True
        resp.json.return_value = {
            "choices": [
                {
                    "text": "ok",
                    "finish_reason": "stop",
                    "raw_output": {"completion_token_ids": [99]},
                }
            ]
        }
        mock_req.return_value = resp

        sampler = DeploymentSampler(
            inference_url="https://api.example.com",
            model="m",
            api_key="key",
            tokenizer=tok,
        )
        messages = [{"role": "user", "content": "test"}]
        sampler.sample_with_tokens(messages=messages)

        tok.apply_chat_template.assert_called_once_with(
            messages, tokenize=True, add_generation_prompt=True,
        )

    @patch("fireworks.training.sdk.deployment.request_with_retries")
    def test_missing_completion_token_ids_raises(self, mock_req):
        resp = MagicMock()
        resp.status_code = 200
        resp.ok = True
        resp.json.return_value = {
            "choices": [
                {
                    "text": "ok",
                    "finish_reason": "stop",
                    "raw_output": {},
                }
            ]
        }
        mock_req.return_value = resp

        sampler = DeploymentSampler(
            inference_url="https://api.example.com",
            model="m",
            api_key="key",
            tokenizer=_make_mock_tokenizer([1, 2, 3]),
        )
        with pytest.raises(RuntimeError, match="missing completion_token_ids"):
            sampler.sample_with_tokens(messages=[{"role": "user", "content": "hi"}])

    @patch("fireworks.training.sdk.deployment.request_with_retries")
    def test_echo_strips_verified_prefix(self, mock_req):
        prompt_ids = [1, 100, 200]
        echoed_completion_ids = [1, 100, 200, 400, 500]

        resp = MagicMock()
        resp.status_code = 200
        resp.ok = True
        resp.json.return_value = {
            "choices": [
                {
                    "text": "gen",
                    "finish_reason": "stop",
                    "raw_output": {"completion_token_ids": echoed_completion_ids},
                }
            ]
        }
        mock_req.return_value = resp

        sampler = DeploymentSampler(
            inference_url="https://api.example.com",
            model="m",
            api_key="key",
            tokenizer=_make_mock_tokenizer(prompt_ids),
        )
        results = sampler.sample_with_tokens(
            messages=[{"role": "user", "content": "hi"}],
            echo=True,
        )

        c = results[0]
        assert c.full_tokens == prompt_ids + [400, 500]
        assert c.completion_len == 2

    @patch("fireworks.training.sdk.deployment.request_with_retries")
    def test_echo_no_strip_when_prefix_mismatch(self, mock_req):
        """echo=True should fail if completion_token_ids lack prompt prefix."""
        prompt_ids = [1, 100, 200]
        completion_ids = [999, 400, 500, 600, 700]

        resp = MagicMock()
        resp.status_code = 200
        resp.ok = True
        resp.json.return_value = {
            "choices": [
                {
                    "text": "gen",
                    "finish_reason": "stop",
                    "raw_output": {"completion_token_ids": completion_ids},
                }
            ]
        }
        mock_req.return_value = resp

        sampler = DeploymentSampler(
            inference_url="https://api.example.com",
            model="m",
            api_key="key",
            tokenizer=_make_mock_tokenizer(prompt_ids),
        )
        with pytest.raises(RuntimeError, match="Echo response format mismatch"):
            sampler.sample_with_tokens(
                messages=[{"role": "user", "content": "hi"}],
                echo=True,
            )
