"""Tests for fireworks.training.sdk.trainer — payload serialization and state machine logic."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from fireworks.training.sdk.trainer import (
    TrainerJobConfig,
    TrainerJobManager,
    TrainerServiceEndpoint,
)


@pytest.fixture
def mgr():
    return TrainerJobManager(
        api_key="test-key",
        account_id="test-account",
        base_url="https://api.example.com",
        additional_headers={"X-Custom": "val"},
    )


@pytest.fixture
def basic_config():
    return TrainerJobConfig(
        base_model="accounts/test/models/qwen3-1p7b",
        node_count=2,
        region="US_OHIO_1",
        lora_rank=0,
        max_context_length=4096,
        learning_rate=1e-5,
        skip_validations=True,
        hot_load_deployment_id="my-deploy",
    )


class TestCreate:
    @patch("fireworks.training.sdk.trainer.request_with_retries")
    def test_payload_construction(self, mock_req, mgr, basic_config):
        resp = MagicMock()
        resp.ok = True
        resp.status_code = 200
        resp.json.return_value = {"name": "accounts/test/rlorTrainerJobs/job-1"}
        mock_req.return_value = resp

        result = mgr._create(basic_config)

        call_kwargs = mock_req.call_args
        url = call_kwargs[0][1]
        payload = call_kwargs[1]["json"]

        assert "deploymentId=my-deploy" in url
        assert "skipValidations=true" in url
        assert payload["serviceMode"] is True
        assert payload["nodeCount"] == 2
        assert payload["trainingConfig"]["baseModel"] == "accounts/test/models/qwen3-1p7b"
        assert payload["trainingConfig"]["region"] == "US_OHIO_1"
        assert payload["hotLoadDeploymentId"] == "my-deploy"

    @patch("fireworks.training.sdk.trainer.request_with_retries")
    def test_extra_args_flattened(self, mock_req, mgr):
        config = TrainerJobConfig(
            base_model="accounts/test/models/m",
            extra_args=["--pp 8", "--ep=4", "--flag"],
        )
        resp = MagicMock()
        resp.ok = True
        resp.status_code = 200
        resp.json.return_value = {"name": "j"}
        mock_req.return_value = resp

        mgr._create(config)
        payload = mock_req.call_args[1]["json"]
        assert payload["trainingConfig"]["extraArgs"] == ["--pp", "8", "--ep=4", "--flag"]


class TestPollUntilReady:
    @patch.object(TrainerJobManager, "_check_healthz", return_value=True)
    @patch.object(TrainerJobManager, "get")
    def test_running_with_endpoint(self, mock_get, mock_healthz, mgr):
        mock_get.return_value = {
            "state": "JOB_STATE_RUNNING",
            "directRouteHandle": "https://trainer.internal:8080",
        }
        result = mgr._poll_until_ready("job-1", "accounts/test/rlorTrainerJobs/job-1", timeout_s=10)
        assert isinstance(result, TrainerServiceEndpoint)
        assert result.job_id == "job-1"
        assert result.base_url == "https://trainer.internal:8080"

    @patch.object(TrainerJobManager, "get")
    def test_failed_raises_runtime_error(self, mock_get, mgr):
        mock_get.return_value = {
            "state": "JOB_STATE_FAILED",
            "status": {"message": "GPU OOM"},
        }
        with pytest.raises(RuntimeError, match="failed"):
            mgr._poll_until_ready("job-1", "name", timeout_s=10)

    @patch("fireworks.training.sdk.trainer.time.sleep")
    @patch("fireworks.training.sdk.trainer.time.time")
    @patch.object(TrainerJobManager, "get")
    def test_timeout_raises(self, mock_get, mock_time, mock_sleep, mgr):
        # Use a call counter instead of a fixed list: return 0 for the first
        # several calls, then jump past the timeout.  This avoids StopIteration
        # from the logging module's internal time.time() calls consuming values.
        call_count = 0

        def fake_time():
            nonlocal call_count
            call_count += 1
            return 0.0 if call_count <= 6 else 100.0

        mock_time.side_effect = fake_time
        mock_get.return_value = {"state": "JOB_STATE_CREATING"}
        with pytest.raises(TimeoutError, match="not become ready"):
            mgr._poll_until_ready("job-1", "name", timeout_s=5)


class TestReconnectAndWait:
    @patch.object(TrainerJobManager, "resume_and_wait")
    @patch.object(TrainerJobManager, "get")
    def test_failed_triggers_resume(self, mock_get, mock_resume, mgr):
        mock_get.return_value = {"state": "JOB_STATE_FAILED"}
        ep = TrainerServiceEndpoint("n", "j", "https://u")
        mock_resume.return_value = ep
        result = mgr.reconnect_and_wait("j")
        assert result is ep

    @patch("fireworks.training.sdk.trainer.time.sleep")
    @patch("fireworks.training.sdk.trainer.time.time")
    @patch.object(TrainerJobManager, "get")
    def test_stuck_state_raises(self, mock_get, mock_time, mock_sleep, mgr):
        call_count = 0

        def fake_time():
            nonlocal call_count
            call_count += 1
            return 0.0 if call_count <= 4 else 200.0

        mock_time.side_effect = fake_time
        mock_get.return_value = {"state": "JOB_STATE_CREATING"}
        with pytest.raises(RuntimeError, match="stuck"):
            mgr.reconnect_and_wait("j", max_wait_for_resumable_s=5)
