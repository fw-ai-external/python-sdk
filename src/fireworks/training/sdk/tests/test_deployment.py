"""Tests for fireworks.training.sdk.deployment — DeploymentManager + DeploymentSampler."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import requests

from fireworks.training.sdk.deployment import (
    DeploymentConfig,
    DeploymentInfo,
    DeploymentManager,
    DeploymentSampler,
    SampledCompletion,
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
        assert DeploymentManager._should_verify_ssl("http://136.117.233.238:8083") is False

    def test_https_ip_no_verify(self):
        assert DeploymentManager._should_verify_ssl("https://136.117.233.238:8083") is False

    def test_https_localhost(self):
        assert DeploymentManager._should_verify_ssl("https://127.0.0.1:8080") is False

    def test_https_real_domain(self):
        assert DeploymentManager._should_verify_ssl("https://dev.api.fireworks.ai") is True


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
    def test_legacy_format_ready(self, mock_status, mgr):
        mock_status.return_value = {
            "identity": "snap-1",
            "state": "READY",
            "readiness": True,
        }
        assert mgr.wait_for_hotload("dep-1", "m", "snap-1", timeout_seconds=5) is True

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
# DeploymentSampler._extract_structured_logprobs
# ---------------------------------------------------------------------------


class TestExtractStructuredLogprobs:
    def test_standard_format(self):
        choice = {
            "logprobs": {
                "content": [
                    {"logprob": -0.5, "token": "hello"},
                    {"logprob": -1.2, "token": "world"},
                ]
            }
        }
        result = DeploymentSampler._extract_structured_logprobs(choice)
        assert result == [-0.5, -1.2]

    def test_missing_logprobs(self):
        assert DeploymentSampler._extract_structured_logprobs({}) is None

    def test_empty_content(self):
        assert DeploymentSampler._extract_structured_logprobs({"logprobs": {"content": []}}) is None

    def test_missing_logprob_field_defaults_zero(self):
        choice = {"logprobs": {"content": [{"token": "hi"}]}}
        result = DeploymentSampler._extract_structured_logprobs(choice)
        assert result == [0.0]


# ---------------------------------------------------------------------------
# DeploymentSampler._strip_echo_prefix
# ---------------------------------------------------------------------------


class TestStripEchoPrefix:
    def test_echo_detected_and_stripped(self):
        prompt = [1, 2, 3]
        completion = [1, 2, 3, 4, 5]
        result, stripped = DeploymentSampler._strip_echo_prefix(prompt, completion)
        assert result == [4, 5]
        assert stripped is True

    def test_no_echo(self):
        prompt = [1, 2, 3]
        completion = [4, 5]
        result, stripped = DeploymentSampler._strip_echo_prefix(prompt, completion)
        assert result == [4, 5]
        assert stripped is False

    def test_empty_prompt(self):
        result, stripped = DeploymentSampler._strip_echo_prefix([], [4, 5])
        assert result == [4, 5]
        assert stripped is False


# ---------------------------------------------------------------------------
# DeploymentSampler.chat_completions — mock HTTP
# ---------------------------------------------------------------------------


class TestChatCompletions:
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
        )
        result = sampler.chat_completions(
            messages=[{"role": "user", "content": "hi"}],
            hotload_retry_interval=0.01,
        )
        assert mock_req.call_count == 2
