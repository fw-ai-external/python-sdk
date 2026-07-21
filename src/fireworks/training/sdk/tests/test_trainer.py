"""Tests for fireworks.training.sdk.trainer — payload serialization and state machine logic."""

from __future__ import annotations

import uuid
import logging
from datetime import timedelta
from urllib.parse import parse_qs, urlparse
from unittest.mock import MagicMock, patch

import httpx
import pytest

from fireworks.training.sdk.trainer import (
    TrainerJobConfig,
    CreatedTrainerJob,
    TrainerJobManager,
    TrainerServiceEndpoint,
)
from fireworks.training.sdk._constants import DEFAULT_TRAINER_PENDING_TIMEOUT_S
from fireworks.training.sdk.fireworks_client import TrainingShapeProfile


def _query_params(path: str) -> dict[str, list[str]]:
    return parse_qs(urlparse(path).query)


@pytest.fixture
def mgr():
    manager = TrainerJobManager(
        api_key="test-key",
        base_url="https://api.example.com",
        additional_headers={"X-Custom": "val"},
    )
    manager._account_id = "test-account"
    yield manager
    manager.close()


@pytest.fixture
def basic_config():
    """Manual-path config: no training_shape_ref, all infra fields set."""
    return TrainerJobConfig(
        base_model="accounts/test/models/qwen3-1p7b",
        node_count=2,
        region="US_OHIO_1",
        lora_rank=0,
        max_context_length=4096,
        learning_rate=1e-5,
        hot_load_deployment_id="my-deploy",
    )


class TestCreate:
    def test_public_create_returns_job_identity(self, mgr, basic_config):
        resp = MagicMock()
        resp.is_success = True
        resp.status_code = 200
        resp.json.return_value = {"name": "accounts/test/rlorTrainerJobs/job-1"}
        mgr._post = MagicMock(return_value=resp)

        result = mgr.create(basic_config)

        assert result == CreatedTrainerJob(
            job_name="accounts/test/rlorTrainerJobs/job-1",
            job_id="job-1",
        )

    def test_payload_construction(self, mgr, basic_config):
        resp = MagicMock()
        resp.is_success = True
        resp.status_code = 200
        resp.json.return_value = {"name": "accounts/test/rlorTrainerJobs/job-1"}
        mgr._post = MagicMock(return_value=resp)

        result = mgr._create(basic_config)

        path = mgr._post.call_args[0][0]
        payload = mgr._post.call_args[1]["json"]

        assert "deploymentId=my-deploy" in path
        assert "skipValidations=true" in path
        assert payload["serviceMode"] is True
        assert payload["nodeCount"] == 2
        assert payload["trainingConfig"]["baseModel"] == "accounts/test/models/qwen3-1p7b"
        assert payload["trainingConfig"]["region"] == "US_OHIO_1"
        assert payload["hotLoadDeploymentId"] == "my-deploy"

    def test_auto_requested_job_id_query_param_when_unset(self, mgr, basic_config):
        resp = MagicMock()
        resp.is_success = True
        resp.status_code = 200
        resp.json.return_value = {"name": "accounts/test/rlorTrainerJobs/job-1"}
        mgr._post = MagicMock(return_value=resp)

        with patch(
            "fireworks.training.sdk.trainer.uuid.uuid4",
            return_value=uuid.UUID("12345678-1234-5678-1234-567812345678"),
        ):
            mgr._create(basic_config)

        path = mgr._post.call_args[0][0]
        assert basic_config.requested_job_id == "training-api-service-12345678"
        assert _query_params(path)["rlorTrainerJobId"] == [basic_config.requested_job_id]

    def test_auto_requested_job_id_reused_for_same_config(self, mgr, basic_config):
        first = MagicMock()
        first.is_success = True
        first.status_code = 200
        first.json.return_value = {"name": "accounts/test/rlorTrainerJobs/job-1"}
        second = MagicMock()
        second.is_success = True
        second.status_code = 200
        second.json.return_value = {"name": "accounts/test/rlorTrainerJobs/job-1"}
        mgr._post = MagicMock(side_effect=[first, second])

        with patch(
            "fireworks.training.sdk.trainer.uuid.uuid4",
            side_effect=[
                uuid.UUID("12345678-1234-5678-1234-567812345678"),
                uuid.UUID("87654321-4321-8765-4321-876543218765"),
            ],
        ):
            mgr._create(basic_config)
            mgr._create(basic_config)

        paths = [call.args[0] for call in mgr._post.call_args_list]
        assert [_query_params(path)["rlorTrainerJobId"][0] for path in paths] == [
            "training-api-service-12345678",
            "training-api-service-12345678",
        ]

    def test_requested_job_id_query_param(self, mgr, basic_config):
        resp = MagicMock()
        resp.is_success = True
        resp.status_code = 200
        resp.json.return_value = {"name": "accounts/test/rlorTrainerJobs/sft-job-1"}
        mgr._post = MagicMock(return_value=resp)

        config = TrainerJobConfig(
            base_model=basic_config.base_model,
            requested_job_id="sft-job-1",
        )
        mgr._create(config)

        path = mgr._post.call_args[0][0]
        assert "rlorTrainerJobId=sft-job-1" in path

    def test_create_409_returns_existing_requested_job(self, mgr, basic_config):
        resp = MagicMock()
        resp.is_success = False
        resp.status_code = 409
        resp.json.return_value = {"error": "already exists"}
        resp.raise_for_status = MagicMock()
        mgr._post = MagicMock(return_value=resp)
        existing = {"name": "accounts/test/rlorTrainerJobs/sft-job-1"}
        mgr.try_get = MagicMock(return_value=existing)

        config = TrainerJobConfig(
            base_model=basic_config.base_model,
            requested_job_id="sft-job-1",
        )
        result = mgr._create(config)

        assert result is existing
        mgr.try_get.assert_called_once_with("sft-job-1")
        resp.raise_for_status.assert_not_called()

    @pytest.mark.parametrize(
        "state",
        ["JOB_STATE_DELETED", "JOB_STATE_ARCHIVED"],
    )
    def test_create_409_rejects_tombstone_existing_job(self, mgr, basic_config, state):
        resp = MagicMock()
        resp.is_success = False
        resp.status_code = 409
        resp.json.return_value = {"error": "already exists"}
        resp.raise_for_status = MagicMock()
        mgr._post = MagicMock(return_value=resp)
        mgr.try_get = MagicMock(
            return_value={
                "name": "accounts/test/rlorTrainerJobs/sft-job-1",
                "state": state,
                "status": {"message": "Archived. Resources released; no further billing."},
            }
        )

        config = TrainerJobConfig(
            base_model=basic_config.base_model,
            requested_job_id="sft-job-1",
        )
        with pytest.raises(RuntimeError, match="archived and cannot be recreated"):
            mgr._create(config)

        mgr.try_get.assert_called_once_with("sft-job-1")
        resp.raise_for_status.assert_not_called()

    def test_create_retry_reuses_auto_job_id_after_conflict(
        self, mgr, basic_config, monkeypatch
    ):
        """E2E-style retry stack test: same SDK call, same generated job ID."""
        generated_job_id = "training-api-service-12345678"
        requests: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            if (
                request.method == "POST"
                and request.url.path == "/v1/accounts/test-account/rlorTrainerJobs"
            ):
                post_count = sum(req.method == "POST" for req in requests)
                if post_count == 1:
                    return httpx.Response(
                        503,
                        json={"error": {"message": "transient"}},
                        request=request,
                    )
                return httpx.Response(
                    409,
                    json={"error": {"message": "rlor trainer job ID already exists"}},
                    request=request,
                )
            if (
                request.method == "GET"
                and request.url.path
                == f"/v1/accounts/test-account/rlorTrainerJobs/{generated_job_id}"
            ):
                return httpx.Response(
                    200,
                    json={
                        "name": (
                            "accounts/test-account/rlorTrainerJobs/"
                            f"{generated_job_id}"
                        )
                    },
                    request=request,
                )
            return httpx.Response(404, json={"error": "not found"}, request=request)

        monkeypatch.setattr(
            "fireworks.training.sdk.errors._backoff_delay",
            lambda *_args, **_kwargs: 0.0,
        )
        monkeypatch.setattr(
            "fireworks.training.sdk.errors.time.sleep", lambda _delay: None
        )
        mgr._sync_client.close()
        mgr._sync_client = httpx.Client(transport=httpx.MockTransport(handler))

        with patch(
            "fireworks.training.sdk.trainer.uuid.uuid4",
            return_value=uuid.UUID("12345678-1234-5678-1234-567812345678"),
        ):
            result = mgr.create(basic_config)

        post_requests = [req for req in requests if req.method == "POST"]
        get_requests = [req for req in requests if req.method == "GET"]
        post_job_ids = [
            _query_params(str(req.url))["rlorTrainerJobId"][0] for req in post_requests
        ]

        assert result == CreatedTrainerJob(
            job_name=f"accounts/test-account/rlorTrainerJobs/{generated_job_id}",
            job_id=generated_job_id,
        )
        assert basic_config.requested_job_id == generated_job_id
        assert post_job_ids == [generated_job_id, generated_job_id]
        assert [req.url.path for req in get_requests] == [
            f"/v1/accounts/test-account/rlorTrainerJobs/{generated_job_id}"
        ]

    def test_shape_path_omits_infra_fields(self, mgr):
        """Shape path sends only algorithm fields; infra fields are omitted."""
        config = TrainerJobConfig(
            base_model="accounts/test/models/m",
            training_shape_ref="accounts/test-account/trainingShapes/ts-test/versions/shape-v1",
            region="US_OHIO_1",
            custom_image_tag="0.33.0",
            extra_args=["--flag"],
        )
        resp = MagicMock()
        resp.is_success = True
        resp.status_code = 200
        resp.json.return_value = {"name": "j"}
        mgr._post = MagicMock(return_value=resp)

        mgr._create(config)

        path = mgr._post.call_args[0][0]
        payload = mgr._post.call_args[1]["json"]
        assert "trainingShape=" in path
        assert "skipValidations" not in path
        tc = payload["trainingConfig"]
        assert "acceleratorType" not in tc
        assert "acceleratorCount" not in tc
        assert tc["customImageTag"] == "0.33.0"
        assert "maxContextLength" not in tc
        assert "nodeCount" not in payload
        assert tc["region"] == "US_OHIO_1"
        assert tc["extraArgs"] == ["--flag"]

    def test_auto_shape_path_omits_manual_infra_but_sends_selector_inputs(self, mgr):
        config = TrainerJobConfig(
            base_model="accounts/test/models/m",
            auto_select_training_shape=True,
            max_context_length=8192,
            region="US_OHIO_1",
            custom_image_tag="0.33.0",
            forward_only=True,
        )
        resp = MagicMock()
        resp.is_success = True
        resp.status_code = 200
        resp.json.return_value = {"name": "j"}
        mgr._post = MagicMock(return_value=resp)

        mgr._create(config)

        path = mgr._post.call_args[0][0]
        payload = mgr._post.call_args[1]["json"]
        assert "skipValidations" not in path
        assert "trainingShape" not in path
        tc = payload["trainingConfig"]
        assert tc["maxContextLength"] == 8192
        assert tc["region"] == "US_OHIO_1"
        assert tc["customImageTag"] == "0.33.0"
        assert "acceleratorType" not in tc
        assert "acceleratorCount" not in tc
        assert "nodeCount" not in payload
        assert payload["forwardOnly"] is True

    def test_auto_shape_path_with_extra_args_omits_skip_validations(self, mgr):
        # Regression: managed jobs whose extra_args were populated by the
        # control plane (e.g. the warm-start --lora-target-modules shim) must
        # stay on the auto-shape path and not send skipValidations=true, which
        # the server rejects with 400 for non-superuser (customer) keys.
        config = TrainerJobConfig(
            base_model="accounts/test/models/m",
            auto_select_training_shape=True,
            max_context_length=8192,
            region="US_OHIO_1",
            extra_args=["--lora-target-modules", "q_proj,k_proj"],
        )
        resp = MagicMock()
        resp.is_success = True
        resp.status_code = 200
        resp.json.return_value = {"name": "j"}
        mgr._post = MagicMock(return_value=resp)

        mgr._create(config)

        path = mgr._post.call_args[0][0]
        payload = mgr._post.call_args[1]["json"]
        assert "skipValidations" not in path
        assert "trainingShape" not in path
        assert payload["trainingConfig"]["extraArgs"] == [
            "--lora-target-modules",
            "q_proj,k_proj",
        ]

    def test_manual_path_sends_all_fields(self, mgr):
        """Manual path sends all infra fields and skipValidations=true."""
        config = TrainerJobConfig(
            base_model="accounts/test/models/m",
            accelerator_type="NVIDIA_H100_80GB",
            accelerator_count=8,
            custom_image_tag="0.33.0",
            node_count=4,
            max_context_length=8192,
            region="US_OHIO_1",
            preemptible=True,
        )
        resp = MagicMock()
        resp.is_success = True
        resp.status_code = 200
        resp.json.return_value = {"name": "j"}
        mgr._post = MagicMock(return_value=resp)

        mgr._create(config)

        path = mgr._post.call_args[0][0]
        payload = mgr._post.call_args[1]["json"]
        assert "skipValidations=true" in path
        assert "trainingShape" not in path
        tc = payload["trainingConfig"]
        assert tc["acceleratorType"] == "NVIDIA_H100_80GB"
        assert tc["acceleratorCount"] == 8
        assert tc["customImageTag"] == "0.33.0"
        assert tc["maxContextLength"] == 8192
        assert payload["nodeCount"] == 4
        assert tc["region"] == "US_OHIO_1"
        assert payload["preemptible"] is True

    def test_trainer_replica_count_sent_on_shape_path(self, mgr):
        """trainer_replica_count is a run-level HSDP knob: it rides the shape
        path (which otherwise omits infra fields) as top-level trainerReplicaCount."""
        config = TrainerJobConfig(
            base_model="accounts/test/models/m",
            training_shape_ref="accounts/test-account/trainingShapes/ts-test/versions/shape-v1",
            trainer_replica_count=3,
        )
        config.validate()  # must not reject the run-level knob on the shape path
        resp = MagicMock()
        resp.is_success = True
        resp.status_code = 200
        resp.json.return_value = {"name": "j"}
        mgr._post = MagicMock(return_value=resp)

        mgr._create(config)

        payload = mgr._post.call_args[1]["json"]
        assert payload["trainerReplicaCount"] == 3
        # Still on the shape path -> infra fields stay shape-owned.
        assert "nodeCount" not in payload

    def test_trainer_replica_count_omitted_when_unset(self, mgr, basic_config):
        """No HSDP override -> the field is absent so the backend default applies."""
        resp = MagicMock()
        resp.is_success = True
        resp.status_code = 200
        resp.json.return_value = {"name": "accounts/test/rlorTrainerJobs/job-1"}
        mgr._post = MagicMock(return_value=resp)

        mgr._create(basic_config)

        payload = mgr._post.call_args[1]["json"]
        assert "trainerReplicaCount" not in payload

    def test_inactivity_cleanup_fields(self, mgr):
        config = TrainerJobConfig(
            base_model="accounts/test/models/m",
            training_shape_ref="accounts/test-account/trainingShapes/ts-test/versions/shape-v1",
            inactivity_timeout=timedelta(minutes=30),
            disable_inactivity_cleanup=True,
        )
        resp = MagicMock()
        resp.is_success = True
        resp.status_code = 200
        resp.json.return_value = {"name": "j"}
        mgr._post = MagicMock(return_value=resp)

        mgr._create(config)

        payload = mgr._post.call_args[1]["json"]
        assert payload["inactivityTimeout"] == "1800s"
        assert payload["disableInactivityCleanup"] is True

    def test_inactivity_timeout_accepts_proto_duration_string(self, mgr):
        config = TrainerJobConfig(
            base_model="accounts/test/models/m",
            inactivity_timeout="7200s",
        )
        resp = MagicMock()
        resp.is_success = True
        resp.status_code = 200
        resp.json.return_value = {"name": "j"}
        mgr._post = MagicMock(return_value=resp)

        mgr._create(config)

        payload = mgr._post.call_args[1]["json"]
        assert payload["inactivityTimeout"] == "7200s"

    def test_extra_args_flattened(self, mgr):
        config = TrainerJobConfig(
            base_model="accounts/test/models/m",
            extra_args=["--pp 8", "--ep=4", "--flag"],
        )
        resp = MagicMock()
        resp.is_success = True
        resp.status_code = 200
        resp.json.return_value = {"name": "j"}
        mgr._post = MagicMock(return_value=resp)

        mgr._create(config)
        payload = mgr._post.call_args[1]["json"]
        assert payload["trainingConfig"]["extraArgs"] == [
            "--pp",
            "8",
            "--ep=4",
            "--flag",
        ]

    def test_display_name_too_long_rejected_locally(self, mgr):
        config = TrainerJobConfig(
            base_model="accounts/test/models/m",
            display_name="x" * 64,
        )
        mgr._post = MagicMock()

        with pytest.raises(ValueError, match="display_name must be fewer than 64 characters"):
            mgr._create(config)

        mgr._post.assert_not_called()

    def test_create_error_logs_backend_message(self, mgr, caplog):
        config = TrainerJobConfig(
            base_model="accounts/test/models/m",
            display_name="valid-name",
        )
        resp = httpx.Response(
            400,
            json={"message": "invalid resource: display_name must be fewer than 64 characters"},
            request=httpx.Request(
                "POST",
                "https://api.example.com/v1/accounts/test-account/rlorTrainerJobs",
                headers={
                    "Authorization": "Bearer secret-token",
                    "X-Api-Key": "secret-api-key",
                },
                json={"displayName": "valid-name"},
            ),
        )
        mgr._post = MagicMock(return_value=resp)

        with caplog.at_level(logging.WARNING, logger="fireworks.training.sdk.trainer"):
            with pytest.raises(RuntimeError) as exc_info:
                mgr._create(config)

        # The raised error (not just the log) now carries the backend message,
        # so it reaches the customer instead of httpx's bare status line.
        err_text = str(exc_info.value)
        assert "RLOR job creation failed (HTTP 400)" in err_text
        assert "invalid resource: display_name must be fewer than 64 characters" in err_text
        # Secrets from the request must not leak into the raised message.
        assert "Authorization" not in err_text
        assert "secret-token" not in err_text
        assert "secret-api-key" not in err_text

        log_text = caplog.text
        assert "RLOR job creation failed (HTTP 400)" in log_text
        assert "invalid resource: display_name must be fewer than 64 characters" in log_text
        assert "displayName" not in log_text
        assert "Authorization" not in log_text
        assert "X-Api-Key" not in log_text
        assert "secret-token" not in log_text
        assert "secret-api-key" not in log_text
        mgr._post.assert_called_once()

    def test_create_tier_gate_raises_actionable_message(self, mgr):
        """A B200/B300 tier gate (HTTP 403) surfaces the actionable backend
        message in the raised error rather than a bare '403 Forbidden' line."""
        config = TrainerJobConfig(
            base_model="accounts/test/models/m",
            display_name="valid-name",
        )
        body_message = (
            "B200/B300 training requires a Tier 2 account or higher. "
            "Add $50 in credits to unlock training quota automatically."
        )
        resp = httpx.Response(
            403,
            json={"message": body_message},
            request=httpx.Request(
                "POST",
                "https://api.example.com/v1/accounts/test-account/rlorTrainerJobs",
            ),
        )
        mgr._post = MagicMock(return_value=resp)

        with pytest.raises(RuntimeError) as exc_info:
            mgr._create(config)

        err_text = str(exc_info.value)
        assert "RLOR job creation failed (HTTP 403)" in err_text
        assert body_message in err_text


class TestPollUntilReady:
    @patch.object(TrainerJobManager, "_poll_until_ready")
    def test_wait_for_ready_uses_explicit_job_name(self, mock_poll, mgr):
        ep = TrainerServiceEndpoint("accounts/test/rlorTrainerJobs/job-1", "job-1", "https://u")
        mock_poll.return_value = ep

        result = mgr.wait_for_ready(
            "job-1",
            job_name="accounts/test/rlorTrainerJobs/job-1",
            timeout_s=10,
        )

        assert result is ep
        mock_poll.assert_called_once_with(
            "job-1",
            "accounts/test/rlorTrainerJobs/job-1",
            5.0,
            10,
            DEFAULT_TRAINER_PENDING_TIMEOUT_S,
        )

    @patch.object(TrainerJobManager, "_check_healthz", return_value=True)
    @patch.object(TrainerJobManager, "get")
    def test_running_uses_gateway_endpoint(self, mock_get, mock_healthz, mgr):
        mock_get.return_value = {
            "state": "JOB_STATE_RUNNING",
            "directRouteHandle": "https://trainer.internal:8080",
            "trainingConfig": {
                "maxContextLength": 32768,
            },
        }
        result = mgr._poll_until_ready("job-1", "accounts/test/rlorTrainerJobs/job-1", timeout_s=10)
        assert isinstance(result, TrainerServiceEndpoint)
        assert result.job_id == "job-1"
        assert result.base_url == "https://api.example.com/training/v1/rlorTrainerJobs/test-account/job-1"
        assert result.max_context_length == 32768

    @patch.object(TrainerJobManager, "get")
    def test_failed_raises_runtime_error(self, mock_get, mgr):
        mock_get.return_value = {
            "state": "JOB_STATE_FAILED",
            "status": {"message": "GPU OOM"},
        }
        with pytest.raises(RuntimeError, match="failed"):
            mgr._poll_until_ready("job-1", "name", timeout_s=10)

    @pytest.mark.parametrize(
        "state",
        ["JOB_STATE_DELETED", "JOB_STATE_ARCHIVED"],
    )
    @patch.object(TrainerJobManager, "get")
    def test_tombstone_raises_runtime_error(self, mock_get, mgr, state):
        mock_get.return_value = {
            "state": state,
            "status": {"message": "Archived. Resources released; no further billing."},
        }
        with pytest.raises(RuntimeError, match="archived and cannot be recreated"):
            mgr._poll_until_ready("job-1", "name", timeout_s=10)

    @patch("fireworks.training.sdk.trainer.time.sleep")
    @patch("fireworks.training.sdk.trainer.time.time")
    @patch.object(TrainerJobManager, "get")
    def test_timeout_raises(self, mock_get, mock_time, mock_sleep, mgr):
        mock_time.side_effect = [0.0, 0.0, 6.0]
        mock_get.return_value = {"state": "JOB_STATE_CREATING"}
        with pytest.raises(TimeoutError, match="not become ready"):
            mgr._poll_until_ready("job-1", "name", timeout_s=5)

    @patch("fireworks.training.sdk.trainer.time.sleep")
    @patch("fireworks.training.sdk.trainer.time.time")
    @patch.object(TrainerJobManager, "get")
    def test_pending_uses_separate_capacity_timeout(self, mock_get, mock_time, mock_sleep, mgr):
        mock_time.side_effect = [0.0, 0.0, 6.0]
        mock_get.return_value = {"state": "JOB_STATE_PENDING"}

        with pytest.raises(TimeoutError, match="pending for capacity"):
            mgr._poll_until_ready(
                "job-1",
                "name",
                timeout_s=1,
                pending_timeout_s=5,
            )

    @patch("fireworks.training.sdk.trainer.time.sleep")
    @patch("fireworks.training.sdk.trainer.time.time")
    @patch.object(TrainerJobManager, "_check_healthz", return_value=True)
    @patch.object(TrainerJobManager, "get")
    def test_readiness_clock_starts_after_pending(
        self,
        mock_get,
        mock_healthz,
        mock_time,
        mock_sleep,
        mgr,
    ):
        mock_get.side_effect = [
            {"state": "JOB_STATE_PENDING"},
            {"state": "JOB_STATE_CREATING"},
            {"state": "JOB_STATE_RUNNING"},
        ]
        mock_time.side_effect = [0.0, 9.0, 9.0, 13.0]

        result = mgr._poll_until_ready(
            "job-1",
            "name",
            timeout_s=5,
            pending_timeout_s=10,
        )

        assert result.job_id == "job-1"
        assert mgr.boot_time_s == 13.0

    @patch("fireworks.training.sdk.trainer.time.sleep")
    @patch.object(TrainerJobManager, "_check_healthz", return_value=True)
    @patch.object(TrainerJobManager, "get")
    def test_deduplicates_identical_poll_logs(self, mock_get, mock_healthz, mock_sleep, mgr, caplog):
        mock_get.side_effect = [
            {"state": "JOB_STATE_CREATING", "status": {"message": "Waiting for capacity"}},
            {"state": "JOB_STATE_CREATING", "status": {"message": "Waiting for capacity"}},
            {"state": "JOB_STATE_RUNNING"},
        ]

        with caplog.at_level("INFO"):
            mgr._poll_until_ready("job-1", "name", timeout_s=10)

        creating_logs = [
            record.message
            for record in caplog.records
            if "JOB_STATE_CREATING" in record.message
        ]
        assert len(creating_logs) == 1
        assert "Waiting for capacity" in creating_logs[0]


class TestCreateAndWait:
    @patch.object(TrainerJobManager, "wait_for_ready")
    @patch.object(TrainerJobManager, "create")
    def test_delegates_to_create_then_wait(self, mock_create, mock_wait_for_ready, mgr, basic_config):
        created = CreatedTrainerJob(
            job_name="accounts/test/rlorTrainerJobs/job-1",
            job_id="job-1",
        )
        ep = TrainerServiceEndpoint(created.job_name, created.job_id, "https://u")
        mock_create.return_value = created
        mock_wait_for_ready.return_value = ep

        result = mgr.create_and_wait(basic_config, poll_interval_s=7.0, timeout_s=11.0)

        assert result is ep
        mock_create.assert_called_once_with(basic_config)
        mock_wait_for_ready.assert_called_once_with(
            "job-1",
            job_name="accounts/test/rlorTrainerJobs/job-1",
            poll_interval_s=7.0,
            timeout_s=11.0,
            pending_timeout_s=DEFAULT_TRAINER_PENDING_TIMEOUT_S,
        )


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


class TestResolveTrainingProfile:
    def test_parses_sharding(self):
        """resolve_training_profile parses the latest shape-version snapshot."""
        mgr = TrainerJobManager(api_key="k", base_url="https://x")
        mgr._account_id = "a"
        resp = MagicMock()
        resp.is_success = True
        resp.json.return_value = {
            "trainingShapeVersions": [
                {
                    "name": "accounts/a/trainingShapes/ts-test/versions/ver-123",
                    "snapshot": {
                        "name": "accounts/a/trainingShapes/ts-test",
                        "trainerImageTag": "0.33.0",
                        "maxSupportedContextLength": 8192,
                        "nodeCount": 2,
                        "deploymentShapeVersion": "dsv",
                        "deploymentImageTag": "img",
                        "acceleratorType": "NVIDIA_H100_80GB",
                        "acceleratorCount": 8,
                        "baseModelWeightPrecision": "bfloat16",
                        "trainerMode": "LORA_TRAINER",
                        "trainerShardingScheme": {
                            "tensorParallelism": 1,
                            "pipelineParallelism": 4,
                            "contextParallelism": 1,
                            "expertParallelism": 1,
                        },
                    },
                },
            ],
        }
        mgr._get = MagicMock(return_value=resp)
        profile = mgr.resolve_training_profile("accounts/a/trainingShapes/ts-test")
        path = mgr._get.call_args[0][0]
        assert "/trainingShapes/ts-test/versions" in path
        assert profile.pipeline_parallelism == 4
        assert profile.max_supported_context_length == 8192
        assert profile.training_shape_version == ("accounts/a/trainingShapes/ts-test/versions/ver-123")
        assert profile.training_shape == "accounts/a/trainingShapes/ts-test"
        assert profile.trainer_mode == "LORA_TRAINER"
        assert profile.supports_lora is True
        mgr.close()

    def test_rejects_bare_shape_id(self):
        mgr = TrainerJobManager(api_key="k", base_url="https://x")
        mgr._account_id = "a"
        with pytest.raises(ValueError, match="not a valid training shape resource name"):
            mgr.resolve_training_profile("ts-test")
        mgr.close()

    def test_respects_fully_qualified_training_shape_name(self):
        mgr = TrainerJobManager(api_key="k", base_url="https://x")
        mgr._account_id = "a"
        resp = MagicMock()
        resp.ok = True
        resp.json.return_value = {
            "trainingShapeVersions": [
                {"name": "accounts/fireworks/trainingShapes/ts-test/versions/ver-123"}
            ]
        }
        mgr._get = MagicMock(return_value=resp)

        mgr.resolve_training_profile("accounts/fireworks/trainingShapes/ts-test")

        path = mgr._get.call_args[0][0]
        assert path.startswith("/v1/accounts/fireworks/trainingShapes/ts-test/versions?")
        mgr.close()

    def test_401_reports_training_scoped_key_requirement(self):
        mgr = TrainerJobManager(api_key="k", base_url="https://x")
        mgr._account_id = "a"
        resp = MagicMock()
        resp.is_success = False
        resp.status_code = 401
        resp.json.return_value = {"error": {"message": "unauthorized"}}
        mgr._get = MagicMock(return_value=resp)

        with pytest.raises(RuntimeError, match="training-scoped Fireworks API key"):
            mgr.resolve_training_profile("accounts/a/trainingShapes/ts-test")

        mgr.close()


class TestListCheckpoints:
    def _mgr(self):
        mgr = TrainerJobManager(api_key="k", base_url="https://x")
        mgr._account_id = "a"
        return mgr

    def _resp(self, body, status=200):
        resp = MagicMock()
        resp.is_success = 200 <= status < 300
        resp.status_code = status
        resp.json.return_value = body
        return resp

    def test_single_page(self):
        mgr = self._mgr()
        mgr._get = MagicMock(
            return_value=self._resp(
                {
                    "checkpoints": [
                        {
                            "name": "accounts/a/rlorTrainerJobs/j/checkpoints/step-1",
                            "createTime": "2026-04-16T10:00:00Z",
                            "checkpointType": "INFERENCE_BASE",
                            "promotable": True,
                        },
                    ],
                },
            )
        )

        rows = mgr.list_checkpoints("j")

        assert len(rows) == 1
        assert rows[0]["checkpointType"] == "INFERENCE_BASE"
        assert rows[0]["promotable"] is True
        path = mgr._get.call_args[0][0]
        assert path.startswith("/v1/accounts/a/rlorTrainerJobs/j/checkpoints?")
        assert "pageSize=200" in path
        assert "pageToken" not in path
        mgr.close()

    def test_auto_paginates(self):
        mgr = self._mgr()
        responses = [
            self._resp(
                {
                    "checkpoints": [{"name": "c/1", "promotable": True}],
                    "nextPageToken": "tok-2",
                },
            ),
            self._resp(
                {
                    "checkpoints": [{"name": "c/2", "promotable": False}],
                    "nextPageToken": "",
                },
            ),
        ]
        mgr._get = MagicMock(side_effect=responses)

        rows = mgr.list_checkpoints("j", page_size=1)

        assert [r["name"] for r in rows] == ["c/1", "c/2"]
        assert mgr._get.call_count == 2
        second_path = mgr._get.call_args_list[1][0][0]
        assert "pageToken=tok-2" in second_path
        assert "pageSize=1" in second_path
        mgr.close()

    def test_handles_empty_response(self):
        mgr = self._mgr()
        mgr._get = MagicMock(return_value=self._resp({}))

        rows = mgr.list_checkpoints("j")

        assert rows == []
        mgr.close()

    def test_404_surfaces_job_not_found(self):
        mgr = self._mgr()
        mgr._get = MagicMock(
            return_value=self._resp(
                {"message": "RlorTrainerJob ... not found", "code": 5},
                status=404,
            )
        )

        with pytest.raises(RuntimeError, match="was not found in this account"):
            mgr.list_checkpoints("bogus")
        mgr.close()

    def test_403_surfaces_permission_denied(self):
        mgr = self._mgr()
        mgr._get = MagicMock(
            return_value=self._resp({"message": "", "code": 7}, status=403)
        )

        with pytest.raises(RuntimeError, match="does not have access"):
            mgr.list_checkpoints("j")
        mgr.close()

    def test_alternate_response_key(self):
        """Some gateway versions return `rlorTrainerJobCheckpoints` instead of `checkpoints`."""
        mgr = self._mgr()
        mgr._get = MagicMock(
            return_value=self._resp(
                {"rlorTrainerJobCheckpoints": [{"name": "c/1", "promotable": True}]},
            )
        )

        rows = mgr.list_checkpoints("j")

        assert [r["name"] for r in rows] == ["c/1"]
        mgr.close()


# ---------------------------------------------------------------------------
# TrainingShapeProfile.training_shape / deployment_shape
# ---------------------------------------------------------------------------


def _make_profile(**overrides) -> TrainingShapeProfile:
    defaults = dict(
        training_shape_version="accounts/fw/trainingShapes/ts-x/versions/1",
        trainer_image_tag="0.33.0",
        max_supported_context_length=8192,
        node_count=2,
        deployment_shape_version="accounts/fw/deploymentShapes/ds-x/versions/1",
        deployment_image_tag="img",
        accelerator_type="NVIDIA_H100_80GB",
        accelerator_count=8,
        base_model_weight_precision="bfloat16",
        pipeline_parallelism=1,
        trainer_mode="POLICY_TRAINER",
    )
    defaults.update(overrides)
    return TrainingShapeProfile(**defaults)


class TestTrainingShapeProperty:
    def test_strips_version_suffix(self):
        profile = _make_profile(
            training_shape_version="accounts/fw/trainingShapes/ts-x/versions/1",
        )
        assert profile.training_shape == "accounts/fw/trainingShapes/ts-x"

    def test_empty_returns_none(self):
        profile = _make_profile(training_shape_version="")
        assert profile.training_shape is None

    def test_no_version_suffix_unchanged(self):
        profile = _make_profile(
            training_shape_version="accounts/fw/trainingShapes/ts-x",
        )
        assert profile.training_shape == "accounts/fw/trainingShapes/ts-x"


# ---------------------------------------------------------------------------
# TrainingShapeProfile.deployment_shape
# ---------------------------------------------------------------------------


class TestDeploymentShapeProperty:
    def test_returns_versioned_path(self):
        profile = _make_profile(
            deployment_shape_version="accounts/fw/deploymentShapes/ds-x/versions/1",
        )
        assert profile.deployment_shape == "accounts/fw/deploymentShapes/ds-x/versions/1"

    def test_empty_returns_none(self):
        profile = _make_profile(deployment_shape_version="")
        assert profile.deployment_shape is None

    def test_no_version_suffix_unchanged(self):
        profile = _make_profile(deployment_shape_version="accounts/fw/deploymentShapes/ds-x")
        assert profile.deployment_shape == "accounts/fw/deploymentShapes/ds-x"


class TestSupportsLoraProperty:
    def test_true_for_lora_trainer_mode(self):
        profile = _make_profile(trainer_mode="LORA_TRAINER")
        assert profile.supports_lora is True

    def test_false_for_non_lora_trainer_mode(self):
        profile = _make_profile(trainer_mode="POLICY_TRAINER")
        assert profile.supports_lora is False


# ---------------------------------------------------------------------------
# TrainerJobConfig.validate
# ---------------------------------------------------------------------------


class TestValidate:
    def test_shape_path_passes_without_infra(self):
        config = TrainerJobConfig(
            base_model="accounts/test/models/m",
            training_shape_ref="accounts/fw/trainingShapes/ts-x/versions/1",
        )
        config.validate()

    def test_shape_path_rejects_accelerator_type(self):
        config = TrainerJobConfig(
            base_model="accounts/test/models/m",
            training_shape_ref="accounts/fw/trainingShapes/ts-x/versions/1",
            accelerator_type="NVIDIA_H100_80GB",
        )
        with pytest.raises(ValueError, match="accelerator_type"):
            config.validate()

    def test_shape_path_rejects_accelerator_count(self):
        config = TrainerJobConfig(
            base_model="accounts/test/models/m",
            training_shape_ref="accounts/fw/trainingShapes/ts-x/versions/1",
            accelerator_count=8,
        )
        with pytest.raises(ValueError, match="accelerator_count"):
            config.validate()

    def test_shape_path_accepts_custom_image_tag_selector(self):
        config = TrainerJobConfig(
            base_model="accounts/test/models/m",
            training_shape_ref="accounts/fw/trainingShapes/ts-x/versions/1",
            custom_image_tag="0.33.0",
        )
        config.validate()

    def test_shape_path_rejects_node_count(self):
        config = TrainerJobConfig(
            base_model="accounts/test/models/m",
            training_shape_ref="accounts/fw/trainingShapes/ts-x/versions/1",
            node_count=4,
        )
        with pytest.raises(ValueError, match="node_count"):
            config.validate()

    def test_shape_path_reports_all_violations(self):
        config = TrainerJobConfig(
            base_model="accounts/test/models/m",
            training_shape_ref="accounts/fw/trainingShapes/ts-x/versions/1",
            accelerator_type="NVIDIA_H100_80GB",
            custom_image_tag="0.33.0",
            node_count=4,
        )
        with pytest.raises(ValueError, match="accelerator_type") as exc_info:
            config.validate()
        assert "node_count" in str(exc_info.value)

    def test_auto_shape_path_rejects_infra_fields(self):
        config = TrainerJobConfig(
            base_model="accounts/test/models/m",
            auto_select_training_shape=True,
            accelerator_count=8,
            node_count=4,
            custom_image_tag="0.33.0",
        )
        with pytest.raises(ValueError, match="accelerator_count") as exc_info:
            config.validate()
        assert "node_count" in str(exc_info.value)
        assert "custom_image_tag" not in str(exc_info.value)

    def test_auto_shape_path_rejects_explicit_shape_ref(self):
        config = TrainerJobConfig(
            base_model="accounts/test/models/m",
            training_shape_ref="accounts/fw/trainingShapes/ts-x/versions/1",
            auto_select_training_shape=True,
        )
        with pytest.raises(ValueError, match="cannot both be set"):
            config.validate()

    def test_manual_path_passes_with_all_infra(self):
        config = TrainerJobConfig(
            base_model="accounts/test/models/m",
            accelerator_type="NVIDIA_H100_80GB",
            accelerator_count=8,
            custom_image_tag="0.33.0",
            node_count=4,
        )
        config.validate()

    def test_manual_path_passes_minimal(self):
        config = TrainerJobConfig(base_model="accounts/test/models/m")
        config.validate()

    def test_rejects_empty_base_model(self):
        config = TrainerJobConfig(base_model="")
        with pytest.raises(ValueError, match="base_model"):
            config.validate()

    def test_unset_gradient_accumulation_steps_is_silent(self, caplog):
        config = TrainerJobConfig(base_model="accounts/test/models/m")
        with caplog.at_level(logging.WARNING, logger="fireworks.training.sdk.trainer"):
            config.validate()
        assert not any("gradient_accumulation_steps" in rec.message for rec in caplog.records)

    def test_rejects_gradient_accumulation_steps_above_one(self):
        config = TrainerJobConfig(
            base_model="accounts/test/models/m",
            gradient_accumulation_steps=4,
        )
        with pytest.raises(ValueError):
            config.validate()

    def test_explicit_one_gradient_accumulation_steps_warns(self, caplog):
        config = TrainerJobConfig(
            base_model="accounts/test/models/m",
            gradient_accumulation_steps=1,
        )
        with caplog.at_level(logging.WARNING, logger="fireworks.training.sdk.trainer"):
            config.validate()
        assert any(
            "gradient_accumulation_steps=1 is deprecated" in rec.message
            for rec in caplog.records
        )

    def test_rejects_negative_inactivity_timeout(self):
        config = TrainerJobConfig(
            base_model="accounts/test/models/m",
            inactivity_timeout=timedelta(seconds=-1),
        )
        with pytest.raises(ValueError, match="inactivity_timeout"):
            config.validate()

    def test_rejects_invalid_inactivity_timeout_string(self):
        config = TrainerJobConfig(
            base_model="accounts/test/models/m",
            inactivity_timeout="30m",
        )
        with pytest.raises(ValueError, match="protobuf JSON duration"):
            config.validate()


# ---------------------------------------------------------------------------
# _check_healthz — uses persistent session
# ---------------------------------------------------------------------------


class TestHealthz:
    def test_uses_sync_client(self, mgr):
        resp = MagicMock()
        resp.status_code = 200
        mgr._sync_client.get = MagicMock(return_value=resp)

        base_url = "https://api.example.com/training/v1/rlorTrainerJobs/test-account/job-1"
        result = mgr._check_healthz(base_url)
        assert result is True
        url = mgr._sync_client.get.call_args[0][0]
        assert "/api/v1/healthz" in url


# ---------------------------------------------------------------------------
# get — REST GET wrapper
# ---------------------------------------------------------------------------


class TestGet:
    def test_calls_rest_get(self, mgr):
        resp = MagicMock()
        resp.is_success = True
        resp.json.return_value = {"state": "JOB_STATE_RUNNING"}
        mgr._get = MagicMock(return_value=resp)

        result = mgr.get("job-1")
        path = mgr._get.call_args[0][0]
        assert "/rlorTrainerJobs/job-1" in path
        assert result["state"] == "JOB_STATE_RUNNING"
