"""Tests for fireworks.training.sdk.client — session ID, snapshot names, checkpoint resolution."""

from __future__ import annotations

import asyncio
import logging
from unittest.mock import MagicMock, patch

import torch
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
        assert (
            qualify_snapshot_name("a1b2c3d4", "step-0-base") == "step-0-base-a1b2c3d4"
        )

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
            client._warn_if_name_reused(
                "step-0", client._saved_sampler_names, "Sampler"
            )
        assert "already used" not in caplog.text

    def test_duplicate_warns(self, caplog):
        client = self._make_client()
        client._saved_sampler_names.add("step-0")
        with caplog.at_level(logging.WARNING):
            client._warn_if_name_reused(
                "step-0", client._saved_sampler_names, "Sampler"
            )
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

    @patch(
        "tinker.lib.public_interfaces.training_client.TrainingClient.forward_backward"
    )
    def test_cross_entropy_adds_response_tokens_from_weights(
        self, mock_forward_backward
    ):
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
            "weights": types.TensorData(
                data=[0.0, 1.0, 1.0, 0.0], dtype="float32", shape=[4]
            ),
            "target_tokens": types.TensorData(
                data=[10, 11, 12, 13], dtype="int64", shape=[4]
            ),
        }

        result = client.forward_backward([datum], "cross_entropy").result()

        assert result.metrics["response_tokens"] == 2.0
        mock_forward_backward.assert_called_once_with([datum], "cross_entropy", None)

    @patch(
        "tinker.lib.public_interfaces.training_client.TrainingClient.forward_backward"
    )
    def test_cross_entropy_falls_back_to_target_token_length(
        self, mock_forward_backward
    ):
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
            "target_tokens": types.TensorData(
                data=[10, 11, 12], dtype="int64", shape=[3]
            ),
        }

        result = client.forward_backward([datum], "cross_entropy").result()

        assert result.metrics["response_tokens"] == 3.0

    @patch(
        "tinker.lib.public_interfaces.training_client.TrainingClient.forward_backward"
    )
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


class TestForwardBackwardCustomEmbedding:
    def _make_client(self):
        client = FiretitanTrainingClient.__new__(FiretitanTrainingClient)
        client._saved_sampler_names = set()
        client._saved_state_names = set()
        client.session_id = "test1234"
        return client

    @patch(
        "tinker.lib.public_interfaces.training_client.TrainingClient.forward_backward_custom"
    )
    def test_logprob_output_delegates_to_upstream_tinker(
        self, mock_forward_backward_custom
    ):
        client = self._make_client()
        future = MagicMock()
        mock_forward_backward_custom.return_value = future

        result = client.forward_backward_custom([], MagicMock())

        assert result is future
        mock_forward_backward_custom.assert_called_once()

    def test_embedding_output_calls_loss_and_sends_embedding_grads(self, monkeypatch):
        client = self._make_client()
        datum = types.Datum(
            model_input=types.ModelInput.from_ints([1, 2]),
            loss_fn_inputs={},
        )
        forward_output = types.ForwardBackwardOutput(
            loss_fn_output_type="forward",
            loss_fn_outputs=[
                {
                    "embedding": types.TensorData(
                        data=[1.0, 2.0],
                        dtype="float32",
                        shape=[2],
                    )
                }
            ],
            metrics={},
        )
        backward_output = types.ForwardBackwardOutput(
            loss_fn_output_type="cross_entropy",
            loss_fn_outputs=[],
            metrics={"loss:sum": 0.0},
        )
        captured = {}

        class _ImmediateFuture:
            def __init__(self, value):
                self._value = value

            async def result_async(self, timeout=None):
                return self._value

            def result(self, timeout=None):
                return self._value

        async def fake_forward(data, pooling):
            captured["forward_pooling"] = pooling
            return _ImmediateFuture(forward_output)

        async def fake_backward(data, pooling):
            captured["backward_pooling"] = pooling
            captured["backward_data"] = data
            return _ImmediateFuture(backward_output)

        monkeypatch.setattr(client, "_forward_embedding_async", fake_forward)
        monkeypatch.setattr(client, "_forward_backward_embedding_async", fake_backward)

        def loss_fn(data, embeddings):
            assert data == [datum]
            return (embeddings[0] * torch.tensor([3.0, -1.0])).sum(), {"custom": 2.0}

        future = asyncio.run(
            client.forward_backward_custom_async(
                [datum],
                loss_fn,
                output="embedding",
                pooling="last",
            )
        )
        result = future.result()

        assert result.metrics["custom"] == 2.0
        assert captured["forward_pooling"] == "last"
        assert captured["backward_pooling"] == "last"
        grad_data = captured["backward_data"][0].loss_fn_inputs["embedding_grads"]
        assert grad_data.data == [3.0, -1.0]
        assert grad_data.shape == [2]

    def test_embedding_output_pools_sequence_hidden_states(self, monkeypatch):
        client = self._make_client()
        datum = types.Datum(
            model_input=types.ModelInput.from_ints([1, 2]),
            loss_fn_inputs={},
        )
        forward_output = types.ForwardBackwardOutput(
            loss_fn_output_type="forward",
            loss_fn_outputs=[
                {
                    "embedding": types.TensorData(
                        data=[1.0, 2.0, 3.0, 4.0, 100.0, 200.0],
                        dtype="float32",
                        shape=[3, 2],
                    )
                }
            ],
            metrics={},
        )
        backward_output = types.ForwardBackwardOutput(
            loss_fn_output_type="cross_entropy",
            loss_fn_outputs=[],
            metrics={"loss:sum": 0.0},
        )
        captured = {}

        class _ImmediateFuture:
            def __init__(self, value):
                self._value = value

            async def result_async(self, timeout=None):
                return self._value

            def result(self, timeout=None):
                return self._value

        async def fake_forward(data, pooling):
            return _ImmediateFuture(forward_output)

        async def fake_backward(data, pooling):
            captured["backward_data"] = data
            return _ImmediateFuture(backward_output)

        monkeypatch.setattr(client, "_forward_embedding_async", fake_forward)
        monkeypatch.setattr(client, "_forward_backward_embedding_async", fake_backward)

        def loss_fn(data, embeddings):
            assert embeddings[0].tolist() == [3.0, 4.0]
            return (embeddings[0] * torch.tensor([5.0, -2.0])).sum(), {}

        future = asyncio.run(
            client.forward_backward_custom_async(
                [datum],
                loss_fn,
                output="embedding",
                pooling="last",
            )
        )
        future.result()

        grad_data = captured["backward_data"][0].loss_fn_inputs["embedding_grads"]
        assert grad_data.data == [5.0, -2.0]
        assert grad_data.shape == [2]

    def test_embedding_output_pools_shaped_sequence_hidden_states(self, monkeypatch):
        client = self._make_client()
        datum = types.Datum(
            model_input=types.ModelInput.from_ints([1, 2]),
            loss_fn_inputs={},
        )
        forward_output = types.ForwardBackwardOutput(
            loss_fn_output_type="forward",
            loss_fn_outputs=[
                {
                    "embedding": types.TensorData(
                        data=[1.0, 2.0, 3.0, 4.0, 100.0, 200.0],
                        dtype="float32",
                        shape=[3, 2],
                    )
                }
            ],
            metrics={},
        )
        backward_output = types.ForwardBackwardOutput(
            loss_fn_output_type="cross_entropy",
            loss_fn_outputs=[],
            metrics={"loss:sum": 0.0},
        )
        captured = {}

        class _ImmediateFuture:
            def __init__(self, value):
                self._value = value

            async def result_async(self, timeout=None):
                return self._value

            def result(self, timeout=None):
                return self._value

        async def fake_forward(data, pooling):
            return _ImmediateFuture(forward_output)

        async def fake_backward(data, pooling):
            captured["backward_data"] = data
            return _ImmediateFuture(backward_output)

        monkeypatch.setattr(client, "_forward_embedding_async", fake_forward)
        monkeypatch.setattr(client, "_forward_backward_embedding_async", fake_backward)

        def loss_fn(data, embeddings):
            assert embeddings[0].tolist() == [3.0, 4.0]
            return (embeddings[0] * torch.tensor([7.0, -3.0])).sum(), {}

        future = asyncio.run(
            client.forward_backward_custom_async(
                [datum],
                loss_fn,
                output="embedding",
                pooling="last",
            )
        )
        future.result()

        grad_data = captured["backward_data"][0].loss_fn_inputs["embedding_grads"]
        assert grad_data.data == [7.0, -3.0]
        assert grad_data.shape == [2]


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
        svc.holder.run_coroutine_threadsafe.return_value.result.return_value = (
            "model-id"
        )

        # Should not raise — different lora_rank is a different config
        try:
            svc.create_training_client("model-a", lora_rank=32)
        except ValueError:
            pytest.fail("Should not raise for different lora_rank")


# ---------------------------------------------------------------------------
# FiretitanTrainingClient.load_adapter
# ---------------------------------------------------------------------------


class TestLoadAdapter:
    def _make_client(self):
        client = FiretitanTrainingClient.__new__(FiretitanTrainingClient)
        client._saved_sampler_names = set()
        client._saved_state_names = set()
        client.session_id = "test1234"
        client.holder = MagicMock()
        return client

    def test_empty_path_raises_valueerror(self):
        client = self._make_client()
        with pytest.raises(ValueError, match="adapter_path must be a non-empty string"):
            client.load_adapter("")

    def test_whitespace_only_path_raises_valueerror(self):
        client = self._make_client()
        with pytest.raises(ValueError, match="adapter_path must be a non-empty string"):
            client.load_adapter("   ")

    def test_non_empty_path_schedules_coroutine(self):
        """Valid path should dispatch to holder.run_coroutine_threadsafe with an
        async coroutine that will POST to /api/v1/load_adapter when awaited.

        We don't actually run the coroutine (would require a full async stack);
        we just verify the dispatch happened and the coroutine was constructed.
        """
        client = self._make_client()
        with patch.object(client, "_get_request_id", return_value=42):
            client.load_adapter("gs://bucket/adapter-dir")

        client.holder.run_coroutine_threadsafe.assert_called_once()
        coro_arg = client.holder.run_coroutine_threadsafe.call_args.args[0]
        assert hasattr(coro_arg, "__await__")
        # Close to avoid RuntimeWarning about un-awaited coroutine
        coro_arg.close()
