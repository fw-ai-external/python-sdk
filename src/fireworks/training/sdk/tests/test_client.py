"""Tests for fireworks.training.sdk.client — session ID, snapshot names, checkpoint resolution."""

from __future__ import annotations

import logging
from unittest.mock import MagicMock, patch

import pytest
from tinker import types

from fireworks.training.sdk.client import (
    FiretitanTrainingClient,
    generate_session_id,
    qualify_snapshot_name,
)

# ---------------------------------------------------------------------------
# generate_session_id
# ---------------------------------------------------------------------------


class TestGenerateSessionId:
    def test_length(self):
        sid = generate_session_id()
        assert len(sid) == 8

    def test_hex_chars(self):
        sid = generate_session_id()
        int(sid, 16)  # raises ValueError if not hex

    def test_unique_across_calls(self):
        ids = {generate_session_id() for _ in range(100)}
        assert len(ids) == 100


# ---------------------------------------------------------------------------
# qualify_snapshot_name
# ---------------------------------------------------------------------------


class TestQualifySnapshotName:
    def test_basic(self):
        assert qualify_snapshot_name("a1b2c3d4", "step-0-base") == "step-0-base-a1b2c3d4"

    def test_separator_is_dash(self):
        result = qualify_snapshot_name("deadbeef", "ckpt")
        assert "/" not in result
        assert result == "ckpt-deadbeef"


# ---------------------------------------------------------------------------
# FiretitanTrainingClient — checkpoint name reuse detection
# ---------------------------------------------------------------------------


class TestWarnIfNameReused:
    def _make_client(self):
        client = FiretitanTrainingClient.__new__(FiretitanTrainingClient)
        client._saved_sampler_names = set()
        client._saved_state_names = set()
        client.session_id = "test1234"
        return client

    def test_first_use_no_warning(self, caplog):
        client = self._make_client()
        with caplog.at_level(logging.WARNING):
            client._warn_if_name_reused("step-0", client._saved_sampler_names, "Sampler")
        assert "already used" not in caplog.text

    def test_duplicate_warns(self, caplog):
        client = self._make_client()
        client._saved_sampler_names.add("step-0")
        with caplog.at_level(logging.WARNING):
            client._warn_if_name_reused("step-0", client._saved_sampler_names, "Sampler")
        assert "already used" in caplog.text


# ---------------------------------------------------------------------------
# resolve_checkpoint_path
# ---------------------------------------------------------------------------


class TestResolveCheckpointPath:
    def _make_client(self):
        client = FiretitanTrainingClient.__new__(FiretitanTrainingClient)
        client._saved_sampler_names = set()
        client._saved_state_names = set()
        client.session_id = "test1234"
        return client

    def test_gs_path_returned_as_is(self):
        client = self._make_client()
        assert client.resolve_checkpoint_path("gs://bucket/path") == "gs://bucket/path"

    def test_absolute_path_returned_as_is(self):
        client = self._make_client()
        assert client.resolve_checkpoint_path("/tmp/checkpoint") == "/tmp/checkpoint"

    def test_relative_name_returned_as_is(self):
        client = self._make_client()
        result = client.resolve_checkpoint_path("step-2")
        assert result == "step-2"

    def test_source_job_id_returns_opaque_ref(self):
        client = self._make_client()
        result = client.resolve_checkpoint_path("step-2", source_job_id="old-job")
        assert result == "cross_job://old-job/step-2"


# ---------------------------------------------------------------------------
# FiretitanTrainingClient.save_state — timeout compatibility
# ---------------------------------------------------------------------------


class TestSaveState:
    def _make_client(self):
        client = FiretitanTrainingClient.__new__(FiretitanTrainingClient)
        client._saved_sampler_names = set()
        client._saved_state_names = set()
        client.session_id = "test1234"
        return client

    @patch("tinker.lib.public_interfaces.training_client.TrainingClient.save_state")
    def test_timeout_waits_for_future(self, mock_save_state):
        client = self._make_client()
        future = MagicMock()
        mock_save_state.return_value = future

        result = client.save_state("step-1", timeout=30)

        assert result is future
        mock_save_state.assert_called_once_with("step-1", ttl_seconds=None)
        future.result.assert_called_once_with(timeout=30)

    @patch("tinker.lib.public_interfaces.training_client.TrainingClient.save_state")
    def test_without_timeout_returns_future_immediately(self, mock_save_state):
        client = self._make_client()
        future = MagicMock()
        mock_save_state.return_value = future

        result = client.save_state("step-1")

        assert result is future
        mock_save_state.assert_called_once_with("step-1", ttl_seconds=None)
        future.result.assert_not_called()


class TestForwardBackward:
    def _make_client(self):
        client = FiretitanTrainingClient.__new__(FiretitanTrainingClient)
        client._saved_sampler_names = set()
        client._saved_state_names = set()
        client.session_id = "test1234"
        return client

    @patch("tinker.lib.public_interfaces.training_client.TrainingClient.forward_backward")
    def test_cross_entropy_adds_response_tokens_from_weights(self, mock_forward_backward):
        client = self._make_client()
        future = MagicMock()
        future.result.return_value = types.ForwardBackwardOutput(
            loss_fn_output_type="cross_entropy",
            loss_fn_outputs=[],
            metrics={"loss:sum": 3.0},
        )
        mock_forward_backward.return_value = future
        datum = MagicMock()
        datum.loss_fn_inputs = {
            "weights": types.TensorData(data=[0.0, 1.0, 1.0, 0.0], dtype="float32", shape=[4]),
            "target_tokens": types.TensorData(data=[10, 11, 12, 13], dtype="int64", shape=[4]),
        }

        result = client.forward_backward([datum], "cross_entropy").result()

        assert result.metrics["response_tokens"] == 2.0
        mock_forward_backward.assert_called_once_with([datum], "cross_entropy", None)

    @patch("tinker.lib.public_interfaces.training_client.TrainingClient.forward_backward")
    def test_cross_entropy_falls_back_to_target_token_length(self, mock_forward_backward):
        client = self._make_client()
        future = MagicMock()
        future.result.return_value = types.ForwardBackwardOutput(
            loss_fn_output_type="cross_entropy",
            loss_fn_outputs=[],
            metrics={"loss:sum": 1.0},
        )
        mock_forward_backward.return_value = future
        datum = MagicMock()
        datum.loss_fn_inputs = {
            "target_tokens": types.TensorData(data=[10, 11, 12], dtype="int64", shape=[3]),
        }

        result = client.forward_backward([datum], "cross_entropy").result()

        assert result.metrics["response_tokens"] == 3.0

    @patch("tinker.lib.public_interfaces.training_client.TrainingClient.forward_backward")
    def test_existing_response_tokens_metric_is_preserved(self, mock_forward_backward):
        client = self._make_client()
        future = MagicMock()
        future.result.return_value = types.ForwardBackwardOutput(
            loss_fn_output_type="cross_entropy",
            loss_fn_outputs=[],
            metrics={"loss:sum": 1.0, "response_tokens": 7.0},
        )
        mock_forward_backward.return_value = future
        datum = MagicMock()
        datum.loss_fn_inputs = {}

        result = client.forward_backward([datum], "cross_entropy").result()

        assert result.metrics["response_tokens"] == 7.0


# ---------------------------------------------------------------------------
# FiretitanServiceClient.create_training_client — duplicate detection
# ---------------------------------------------------------------------------


class TestCreateTrainingClientDuplicate:
    def test_duplicate_config_raises(self):
        from fireworks.training.sdk.client import FiretitanServiceClient

        svc = FiretitanServiceClient.__new__(FiretitanServiceClient)
        svc._created_training_configs = {("model-a", 0)}

        with pytest.raises(ValueError, match="already exists"):
            svc.create_training_client("model-a", lora_rank=0)

    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    @pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
    def test_different_lora_rank_ok(self):
        from fireworks.training.sdk.client import FiretitanServiceClient

        svc = FiretitanServiceClient.__new__(FiretitanServiceClient)
        svc._created_training_configs = {("model-a", 0)}
        svc.holder = MagicMock()
        svc.holder.get_session_id.return_value = 1
        svc.holder.get_training_client_id.return_value = 1
        svc.holder.run_coroutine_threadsafe.return_value.result.return_value = "model-id"

        # Should not raise — different lora_rank is a different config
        try:
            svc.create_training_client("model-a", lora_rank=32)
        except ValueError:
            pytest.fail("Should not raise for different lora_rank")
