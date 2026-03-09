"""Tests for fireworks.training.sdk.trainer — payload serialization and state machine logic."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from fireworks.training.sdk.trainer import (
    TrainerJobConfig,
    TrainerJobManager,
    TrainingShapeProfile,
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
    def test_validated_shape_omits_all_infra_fields(self, mock_req, mgr):
        """Validated-shape path sends only algorithm fields; all shape-derived
        infra fields are omitted so the backend populates them from the shape."""
        config = TrainerJobConfig(
            base_model="accounts/test/models/m",
            training_shape_ref="accounts/test-account/trainingShapes/ts-test/versions/shape-v1",
            accelerator_type="NVIDIA_H100_80GB",
            accelerator_count=8,
            custom_image_tag="0.33.0",
            node_count=4,
            max_context_length=8192,
            region="US_OHIO_1",
            extra_args=["--flag"],
        )
        resp = MagicMock()
        resp.ok = True
        resp.status_code = 200
        resp.json.return_value = {"name": "j"}
        mock_req.return_value = resp

        mgr._create(config)

        url = mock_req.call_args[0][1]
        payload = mock_req.call_args[1]["json"]
        assert "trainingShape=" in url
        assert "accounts%2Ftest-account%2FtrainingShapes%2Fts-test%2Fversions%2Fshape-v1" in url
        tc = payload["trainingConfig"]
        assert "acceleratorType" not in tc
        assert "acceleratorCount" not in tc
        assert "customImageTag" not in tc
        assert "maxContextLength" not in tc
        assert "nodeCount" not in payload
        assert tc["region"] == "US_OHIO_1"
        assert tc["extraArgs"] == ["--flag"]

    @patch("fireworks.training.sdk.trainer.request_with_retries")
    def test_skip_validations_sends_all_fields(self, mock_req, mgr):
        """Skip-validation path sends all fields including shape-derived ones."""
        config = TrainerJobConfig(
            base_model="accounts/test/models/m",
            training_shape_ref="accounts/test-account/trainingShapes/ts-test/versions/shape-v1",
            skip_validations=True,
            accelerator_type="NVIDIA_H100_80GB",
            accelerator_count=8,
            custom_image_tag="0.33.0",
            node_count=4,
            max_context_length=8192,
            region="US_OHIO_1",
        )
        resp = MagicMock()
        resp.ok = True
        resp.status_code = 200
        resp.json.return_value = {"name": "j"}
        mock_req.return_value = resp

        mgr._create(config)

        url = mock_req.call_args[0][1]
        payload = mock_req.call_args[1]["json"]
        assert "trainingShape=" in url
        assert "skipValidations=true" in url
        tc = payload["trainingConfig"]
        assert tc["acceleratorType"] == "NVIDIA_H100_80GB"
        assert tc["acceleratorCount"] == 8
        assert tc["customImageTag"] == "0.33.0"
        assert tc["maxContextLength"] == 8192
        assert payload["nodeCount"] == 4
        assert tc["region"] == "US_OHIO_1"

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
        assert payload["trainingConfig"]["extraArgs"] == [
            "--pp",
            "8",
            "--ep=4",
            "--flag",
        ]


class TestPollUntilReady:
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


class TestResolveTrainingProfile:
    def test_parses_sharding(self):
        """resolve_training_profile parses the latest shape-version snapshot."""
        mgr = TrainerJobManager(api_key="k", account_id="a", base_url="https://x")
        with patch("fireworks.training.sdk.trainer.request_with_retries") as mock_req:
            resp = MagicMock()
            resp.ok = True
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
            mock_req.return_value = resp
            profile = mgr.resolve_training_profile("ts-test")
            called_url = mock_req.call_args[0][1]
            assert called_url.endswith("/trainingShapes/ts-test/versions?filter=latest_validated%3Dtrue&pageSize=1")
            assert profile.pipeline_parallelism == 4
            assert profile.max_supported_context_length == 8192
            assert profile.training_shape_version == ("accounts/a/trainingShapes/ts-test/versions/ver-123")
            assert profile.training_shape == "accounts/a/trainingShapes/ts-test"


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
    def test_strips_version_suffix(self):
        profile = _make_profile(
            deployment_shape_version="accounts/fw/deploymentShapes/ds-x/versions/1",
        )
        assert profile.deployment_shape == "accounts/fw/deploymentShapes/ds-x"

    def test_empty_returns_none(self):
        profile = _make_profile(deployment_shape_version="")
        assert profile.deployment_shape is None

    def test_no_version_suffix_unchanged(self):
        profile = _make_profile(deployment_shape_version="accounts/fw/deploymentShapes/ds-x")
        assert profile.deployment_shape == "accounts/fw/deploymentShapes/ds-x"


# ---------------------------------------------------------------------------
# TrainerJobConfig.apply_shape
# ---------------------------------------------------------------------------


class TestApplyShape:
    def test_shape_values_applied(self):
        """Shape values populate the config."""
        config = TrainerJobConfig(
            base_model="accounts/test/models/m",
        )
        profile = _make_profile()
        config.apply_shape(profile)

        assert config.accelerator_type == "NVIDIA_H100_80GB"
        assert config.accelerator_count == 8
        assert config.custom_image_tag == "0.33.0"
        assert config.node_count == 2
        assert config.max_context_length == 8192

    def test_shape_wins_without_skip_validations_for_copied_fields(self):
        """Without skip_validations, shape wins for copied launch fields."""
        config = TrainerJobConfig(
            base_model="accounts/test/models/m",
            accelerator_type="NVIDIA_A100_80GB",
            accelerator_count=4,
            max_context_length=4096,
        )
        profile = _make_profile()
        config.apply_shape(profile)

        assert config.accelerator_type == "NVIDIA_H100_80GB"
        assert config.accelerator_count == 8
        assert config.node_count == 2
        assert config.max_context_length == 8192

    def test_skip_validations_keeps_user_overrides(self):
        """With skip_validations, user values override copied shape fields."""
        config = TrainerJobConfig(
            base_model="accounts/test/models/m",
            skip_validations=True,
            accelerator_type="NVIDIA_A100_80GB",
            accelerator_count=4,
            max_context_length=4096,
        )
        profile = _make_profile()
        config.apply_shape(profile)

        assert config.accelerator_type == "NVIDIA_A100_80GB"
        assert config.accelerator_count == 4
        assert config.max_context_length == 4096
        assert config.custom_image_tag == "0.33.0"
        assert config.node_count == 2

    def test_skip_validations_fills_none_fields(self):
        """With skip_validations, shape fills fields the user left as None."""
        config = TrainerJobConfig(
            base_model="accounts/test/models/m",
            skip_validations=True,
        )
        profile = _make_profile()
        config.apply_shape(profile)

        assert config.accelerator_type == "NVIDIA_H100_80GB"
        assert config.accelerator_count == 8
        assert config.custom_image_tag == "0.33.0"
        assert config.max_context_length == 8192

    def test_skip_validations_can_partially_override_accelerators(self):
        """Skip-validation launches can override part of the accelerator tuple."""
        config = TrainerJobConfig(
            base_model="accounts/test/models/m",
            skip_validations=True,
            accelerator_type="MY_ACCEL",
        )
        profile = _make_profile()
        config.apply_shape(profile)

        assert config.accelerator_type == "MY_ACCEL"
        assert config.accelerator_count == 8
