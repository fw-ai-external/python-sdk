"""Tests for fireworks.training.sdk.trainer — payload serialization and state machine logic."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from fireworks.training.sdk.trainer import (
    TrainerJobConfig,
    CreatedTrainerJob,
    TrainerJobManager,
    TrainerServiceEndpoint,
)
from fireworks.training.sdk.fireworks_client import TrainingShapeProfile


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

    def test_shape_path_omits_infra_fields(self, mgr):
        """Shape path sends only algorithm fields; infra fields are omitted."""
        config = TrainerJobConfig(
            base_model="accounts/test/models/m",
            training_shape_ref="accounts/test-account/trainingShapes/ts-test/versions/shape-v1",
            region="US_OHIO_1",
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
        assert "customImageTag" not in tc
        assert "maxContextLength" not in tc
        assert "nodeCount" not in payload
        assert tc["region"] == "US_OHIO_1"
        assert tc["extraArgs"] == ["--flag"]

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
        )

    @patch.object(TrainerJobManager, "_check_healthz", return_value=True)
    @patch.object(TrainerJobManager, "get")
    def test_running_uses_gateway_endpoint(self, mock_get, mock_healthz, mgr):
        mock_get.return_value = {
            "state": "JOB_STATE_RUNNING",
            "directRouteHandle": "https://trainer.internal:8080",
        }
        result = mgr._poll_until_ready("job-1", "accounts/test/rlorTrainerJobs/job-1", timeout_s=10)
        assert isinstance(result, TrainerServiceEndpoint)
        assert result.job_id == "job-1"
        assert result.base_url == "https://api.example.com/training/v1/rlorTrainerJobs/test-account/job-1"

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
        call_count = 0

        def fake_time():
            nonlocal call_count
            call_count += 1
            return 0.0 if call_count <= 6 else 100.0

        mock_time.side_effect = fake_time
        mock_get.return_value = {"state": "JOB_STATE_CREATING"}
        with pytest.raises(TimeoutError, match="not become ready"):
            mgr._poll_until_ready("job-1", "name", timeout_s=5)

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

    def test_shape_path_rejects_custom_image_tag(self):
        config = TrainerJobConfig(
            base_model="accounts/test/models/m",
            training_shape_ref="accounts/fw/trainingShapes/ts-x/versions/1",
            custom_image_tag="0.33.0",
        )
        with pytest.raises(ValueError, match="custom_image_tag"):
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
        assert "custom_image_tag" in str(exc_info.value)
        assert "node_count" in str(exc_info.value)

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
