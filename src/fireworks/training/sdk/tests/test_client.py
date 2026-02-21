"""Tests for fireworks.training.sdk.client — session ID, snapshot names, checkpoint resolution."""

from __future__ import annotations

import logging
from unittest.mock import MagicMock

import pytest

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
# FiretitanServiceClient.create_training_client — duplicate detection
# ---------------------------------------------------------------------------


class TestCreateTrainingClientDuplicate:
    def test_duplicate_config_raises(self):
        from fireworks.training.sdk.client import FiretitanServiceClient

        svc = FiretitanServiceClient.__new__(FiretitanServiceClient)
        svc._created_training_configs = {("model-a", 0)}

        with pytest.raises(ValueError, match="already exists"):
            svc.create_training_client("model-a", lora_rank=0)

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
