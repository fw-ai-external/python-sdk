"""Tests for fireworks.training.sdk.client — session ID, snapshot names, checkpoint resolution."""

from __future__ import annotations

import asyncio
import logging
import warnings
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import httpx
import torch
import pytest
from tinker import types

from fireworks.training.sdk.client import (
    FIRETITAN_TINKER_CLIENT_CONFIG,
    SAMPLING_CLIENT_FROM_TRAINER_MESSAGE,
    SaveSamplerResult,
    GradNormMetricsMode,
    FiretitanServiceClient,
    FiretitanTrainingClient,
    generate_session_id,
    _run_id_from_model_id,
    qualify_snapshot_name,
    _LazyManagedRestClient,
    _is_serverless_session_id,
    _BaseOnlyCreateModelRequest,
    _FireworksApiKeyAuthProvider,
    _check_cos_similarity_matrix_single_chunk,
)
from fireworks.training.sdk.managed import (
    _ManagedTinkerConfig,
    _TinkerSamplerBackend,
    _create_or_reattach_deployment,
)
from fireworks.training.sdk._constants import CLEANUP_DEPLOYMENT_ON_CLOSE_SCALE_TO_ZERO
from fireworks.training.sdk.deployment import DeploymentConfig

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
        client.holder = SimpleNamespace(
            _client_config=SimpleNamespace(
                parallel_fwdbwd_chunks=False,
                proto_write_fwdbwd=False,
                proto_compress_fwdbwd=False,
            )
        )
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
        mock_save_state.assert_called_once_with("step-1", ttl_seconds=None, overwrite=False)
        future.result.assert_called_once_with(timeout=30)

    @patch("tinker.lib.public_interfaces.training_client.TrainingClient.save_state")
    def test_without_timeout_returns_future_immediately(self, mock_save_state):
        client = self._make_client()
        future = MagicMock()
        mock_save_state.return_value = future

        result = client.save_state("step-1")

        assert result is future
        mock_save_state.assert_called_once_with("step-1", ttl_seconds=None, overwrite=False)
        future.result.assert_not_called()

    @patch("tinker.lib.public_interfaces.training_client.TrainingClient.save_state")
    def test_overwrite_true_raises_not_implemented(self, mock_save_state):
        client = self._make_client()

        with pytest.raises(NotImplementedError, match="overwrite=True"):
            client.save_state("step-1", overwrite=True)

        mock_save_state.assert_not_called()

    @patch("tinker.lib.public_interfaces.training_client.TrainingClient.save_state")
    def test_save_state_async_rejects_overwrite_true(self, mock_save_state):
        client = self._make_client()

        with pytest.raises(NotImplementedError, match="overwrite=True"):
            asyncio.run(client.save_state_async("step-1", overwrite=True))

        mock_save_state.assert_not_called()


class TestLoadStateCompatibility:
    def _make_client(self):
        client = FiretitanTrainingClient.__new__(FiretitanTrainingClient)
        return client

    @patch("tinker.lib.public_interfaces.training_client.TrainingClient.load_state")
    def test_load_state_passes_through_without_access_token(self, mock_load_state):
        client = self._make_client()
        future = MagicMock()
        mock_load_state.return_value = future

        result = client.load_state("tinker://run/weights/step-1")

        assert result is future
        mock_load_state.assert_called_once_with("tinker://run/weights/step-1", weights_access_token=None)

    @patch("tinker.lib.public_interfaces.training_client.TrainingClient.load_state")
    def test_load_state_rejects_access_token(self, mock_load_state):
        client = self._make_client()

        with pytest.raises(NotImplementedError, match="weights_access_token"):
            client.load_state("tinker://run/weights/step-1", weights_access_token="token")

        mock_load_state.assert_not_called()

    @patch("tinker.lib.public_interfaces.training_client.TrainingClient.load_state_with_optimizer")
    def test_load_state_with_optimizer_rejects_access_token(self, mock_load_state):
        client = self._make_client()

        with pytest.raises(NotImplementedError, match="weights_access_token"):
            client.load_state_with_optimizer("tinker://run/weights/step-1", weights_access_token="token")

        mock_load_state.assert_not_called()


class TestForwardBackward:
    def _make_client(self):
        client = FiretitanTrainingClient.__new__(FiretitanTrainingClient)
        client._saved_sampler_names = set()
        client._saved_state_names = set()
        client.session_id = "test1234"
        client.holder = SimpleNamespace(
            _client_config=SimpleNamespace(
                parallel_fwdbwd_chunks=False,
                proto_write_fwdbwd=False,
                proto_compress_fwdbwd=False,
            )
        )
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
    def test_proto_forward_backward_is_rejected(self, mock_forward_backward):
        client = self._make_client()
        client.holder._client_config.proto_write_fwdbwd = True

        with pytest.raises(NotImplementedError, match="proto forward_backward"):
            client.forward_backward([MagicMock()], "cross_entropy")

        mock_forward_backward.assert_not_called()

    @patch("tinker.lib.public_interfaces.training_client.TrainingClient.forward_backward")
    def test_parallel_forward_backward_is_preserved_for_firetitan(self, mock_forward_backward):
        client = self._make_client()
        client.holder._client_config.parallel_fwdbwd_chunks = True
        future = MagicMock()
        mock_forward_backward.return_value = future

        result = client.forward_backward([MagicMock()], "supervised")

        assert result is future
        assert client.holder._client_config.parallel_fwdbwd_chunks is True


class TestParallelChunkSubmission:
    class _ClientContext:
        def __init__(self, training):
            self._training = training

        def __enter__(self):
            return SimpleNamespace(training=self._training)

        def __exit__(self, exc_type, exc, tb):
            return False

    class _ImmediateThreadFuture:
        def __init__(self, coro):
            self._value = asyncio.run(coro)

        def result(self, timeout=None):
            return self._value

        async def result_async(self, timeout=None):
            return self._value

        def __await__(self):
            return self.result_async().__await__()

    class _FakeAPIFuture:
        def __init__(self, _model_cls, _holder, untyped_future, **_kwargs):
            self._value = untyped_future

        def result(self, timeout=None):
            return self._value

        async def result_async(self, timeout=None):
            return self._value

        def __await__(self):
            return self.result_async().__await__()

    class _FakeCombinedAPIFuture:
        def __init__(self, futures, _transform, _holder):
            self._futures = futures

        def result(self, timeout=None):
            return asyncio.run(self.result_async(timeout))

        async def result_async(self, timeout=None):
            return [await future.result_async(timeout) for future in self._futures]

        def __await__(self):
            return self.result_async().__await__()

    def _datum(self, token: int = 1) -> types.Datum:
        return types.Datum(
            model_input=types.ModelInput.from_ints([token, token + 1]),
            loss_fn_inputs={"target_tokens": types.TensorData(data=[token + 1], dtype="int64", shape=[1])},
        )

    def _make_client(self, *, parallel: bool, send_order: list[int]):
        client = _bare_training_client()
        client.model_id = "model"
        client._queue_state_logger = None
        client._turn_counter = 0
        client._turn_waiters = {}
        chunks = [[self._datum(1)], [self._datum(10)], [self._datum(20)]]
        client._chunked_requests = MagicMock(return_value=[(0, chunks[0]), (1, chunks[1]), (2, chunks[2])])

        class _Training:
            async def forward(self, *, request):
                send_order.append(request.seq_id)
                await asyncio.sleep(0)
                return request.seq_id

        async def execute_with_retries(send, *args):
            return await send(*args)

        holder = MagicMock()
        holder._client_config = SimpleNamespace(
            parallel_fwdbwd_chunks=parallel,
            proto_write_fwdbwd=False,
            proto_compress_fwdbwd=False,
            fwd_via_fwdbwd=False,
        )
        holder.aclient.return_value = self._ClientContext(_Training())
        holder.execute_with_retries.side_effect = execute_with_retries
        holder.run_coroutine_threadsafe.side_effect = self._ImmediateThreadFuture
        client.holder = holder
        return client

    def test_forward_parallel_chunks_send_rest_before_first(self):
        send_order: list[int] = []
        client = self._make_client(parallel=True, send_order=send_order)

        with (
            patch("fireworks.training.sdk.client._APIFuture", self._FakeAPIFuture),
            patch("fireworks.training.sdk.client._CombinedAPIFuture", self._FakeCombinedAPIFuture),
        ):
            result = client.forward([self._datum()], "cross_entropy").result()

        assert send_order == [2, 3, 1]
        assert result == [1, 2, 3]

    def test_forward_respects_serial_chunk_flag(self):
        send_order: list[int] = []
        client = self._make_client(parallel=False, send_order=send_order)

        with (
            patch("fireworks.training.sdk.client._APIFuture", self._FakeAPIFuture),
            patch("fireworks.training.sdk.client._CombinedAPIFuture", self._FakeCombinedAPIFuture),
        ):
            result = client.forward([self._datum()], "cross_entropy").result()

        assert send_order == [1, 2, 3]
        assert result == [1, 2, 3]

    def test_embedding_custom_forward_uses_parallel_chunks(self):
        send_order: list[int] = []
        client = self._make_client(parallel=True, send_order=[])
        client._build_embedding_requests = MagicMock(
            return_value=[
                (0, [self._datum(1)]),
                (1, [self._datum(10)]),
                (2, [self._datum(20)]),
            ]
        )

        async def send_embedding(request_id, _chunk, pooling, output):
            assert pooling == "last"
            assert output == "embedding"
            send_order.append(request_id + 1)
            await asyncio.sleep(0)
            return request_id + 1

        client._send_single_forward_embedding_request = send_embedding

        with (
            patch("fireworks.training.sdk.client._APIFuture", self._FakeAPIFuture),
            patch("fireworks.training.sdk.client._CombinedAPIFuture", self._FakeCombinedAPIFuture),
        ):
            future = asyncio.run(
                client._forward_embedding_async(
                    [self._datum()],
                    "last",
                    output="embedding",
                )
            )
            result = asyncio.run(future.result_async())

        assert send_order == [2, 3, 1]
        assert result == [1, 2, 3]

    def test_embedding_custom_backward_uses_parallel_chunks(self):
        send_order: list[int] = []
        client = self._make_client(parallel=True, send_order=[])
        client._build_embedding_requests = MagicMock(
            return_value=[
                (0, [self._datum(1)]),
                (1, [self._datum(10)]),
                (2, [self._datum(20)]),
            ]
        )

        async def send_embedding_backward(request_id, _chunk, pooling, output):
            assert pooling == "mean"
            assert output == "embedding"
            send_order.append(request_id + 1)
            await asyncio.sleep(0)
            return request_id + 1

        client._send_single_forward_backward_embedding_request = send_embedding_backward

        with (
            patch("fireworks.training.sdk.client._APIFuture", self._FakeAPIFuture),
            patch("fireworks.training.sdk.client._CombinedAPIFuture", self._FakeCombinedAPIFuture),
        ):
            future = asyncio.run(
                client._forward_backward_embedding_async(
                    [self._datum()],
                    "mean",
                    output="embedding",
                )
            )
            result = asyncio.run(future.result_async())

        assert send_order == [2, 3, 1]
        assert result == [1, 2, 3]


class TestOptimStep:
    class _NoopTurn:
        async def __aenter__(self):
            return None

        async def __aexit__(self, exc_type, exc, tb):
            return False

    class _ImmediateThreadFuture:
        def __init__(self, coro):
            self._coro = coro

        def result(self):
            return asyncio.run(self._coro)

    class _ClientContext:
        def __init__(self, training):
            self._training = training

        def __enter__(self):
            return SimpleNamespace(training=self._training)

        def __exit__(self, exc_type, exc, tb):
            return False

    class _FakeAPIFuture:
        def __init__(self, *args, **kwargs):
            pass

        def __await__(self):
            async def _result():
                return "api-future"

            return _result().__await__()

    def _make_client(self, captured: dict):
        client = FiretitanTrainingClient.__new__(FiretitanTrainingClient)
        client._get_request_id = MagicMock(return_value=41)
        client._guaranteed_model_id = MagicMock(return_value="model")
        client._queue_state_logger = None
        client._take_turn = MagicMock(return_value=self._NoopTurn())

        async def optim_step(*, request, extra_body):
            captured["request"] = request
            captured["extra_body"] = extra_body
            return "raw-future"

        async def execute_with_retries(send):
            return await send()

        holder = MagicMock()
        holder.aclient.return_value = self._ClientContext(SimpleNamespace(optim_step=optim_step))
        holder.execute_with_retries.side_effect = execute_with_retries
        holder.run_coroutine_threadsafe.side_effect = self._ImmediateThreadFuture
        client.holder = holder
        return client

    def test_default_omits_grad_norm_metrics_mode(self):
        captured = {}
        client = self._make_client(captured)

        with patch("fireworks.training.sdk.client._APIFuture", self._FakeAPIFuture):
            result = client.optim_step(types.AdamParams()).result()

        assert result == "api-future"
        body = captured["request"].model_dump(
            exclude_unset=False,
            exclude_none=True,
            mode="json",
        )
        assert "emit_grad_norm_metrics" not in body["adam_params"]
        assert captured["extra_body"] == {}

    def test_call_time_grad_norm_metrics_mode_overrides_adam_params(self):
        captured = {}
        client = self._make_client(captured)
        adam_params = types.AdamParams(emit_grad_norm_metrics=False)

        with patch("fireworks.training.sdk.client._APIFuture", self._FakeAPIFuture):
            result = client.optim_step(
                adam_params,
                emit_grad_norm_metrics=GradNormMetricsMode.DETAILED,
            ).result()

        assert result == "api-future"
        assert captured["request"].adam_params.emit_grad_norm_metrics == "detailed"

    def test_invalid_grad_norm_metrics_mode_raises_before_dispatch(self):
        captured = {}
        client = self._make_client(captured)

        with pytest.raises(ValueError, match="emit_grad_norm_metrics"):
            client.optim_step(types.AdamParams(), emit_grad_norm_metrics="global")

        client.holder.run_coroutine_threadsafe.assert_not_called()


class _FakeInferenceDeploymentManager:
    account_id = "acct"
    api_key = "fw-key"
    inference_url = "https://inference.test"

    def __init__(self, existing=None, wait_error=None, scale_error=None, delete_error=None):
        self.existing = existing
        self.wait_error = wait_error
        self.scale_error = scale_error
        self.delete_error = delete_error
        self.created_config = None
        self.waited = []
        self.scaled_to_zero = []
        self.deleted = []

    def get(self, deployment_id):
        self.get_id = deployment_id
        return self.existing

    def create_or_get(self, config):
        self.created_config = config
        return SimpleNamespace(
            deployment_id=config.deployment_id,
            state="CREATING",
            inference_model=None,
        )

    def wait_for_ready(self, deployment_id, timeout_s):
        self.waited.append((deployment_id, timeout_s))
        if self.wait_error is not None:
            raise self.wait_error
        return SimpleNamespace(
            deployment_id=deployment_id,
            state="READY",
            inference_model=f"accounts/acct/deployments/{deployment_id}",
        )

    def scale_to_zero(self, deployment_id):
        self.scaled_to_zero.append(deployment_id)
        if self.scale_error is not None:
            raise self.scale_error

    def delete(self, deployment_id):
        self.deleted.append(deployment_id)
        if self.delete_error is not None:
            raise self.delete_error


class TestFiretitanServiceClientManagedCompat:
    def _make_service(self):
        svc = FiretitanServiceClient.__new__(FiretitanServiceClient)
        svc._managed_config = None
        svc._managed_handle = None
        svc._sampler_backend = None
        svc._reference_handle = None
        svc._default_user_metadata = None
        svc.create_training_client = MagicMock(return_value="training-client")
        return svc

    def _make_managed_service(self, deploy_mgr, *, region="US_OHIO_1"):
        svc = FiretitanServiceClient.__new__(FiretitanServiceClient)
        svc._managed_config = SimpleNamespace(
            base_model="accounts/acct/models/base",
            deployment_shape=None,
            region=region,
        )
        svc._managed_handle = SimpleNamespace(
            deployment_manager=deploy_mgr,
            deployment_shape="accounts/acct/deploymentShapes/student/versions/v1",
            close=MagicMock(),
        )
        svc._fireworks_api_key = "fw-key"
        svc._managed_base_url = "https://api.fireworks.ai"
        svc._managed_inference_url = None
        svc._managed_hotload_api_url = None
        svc._managed_additional_headers = None
        svc._managed_verify_ssl = None
        svc._owned_reference_handles = []
        svc._owned_inference_deployments = []
        svc._reference_handle = None
        return svc

    def test_reference_auto_full_param_uses_base_client(self):
        svc = self._make_service()
        svc.create_base_training_client = MagicMock(return_value="base-client")

        result = svc.create_reference_client("accounts/acct/models/base", lora_rank=0)

        assert result == "base-client"
        svc.create_base_training_client.assert_called_once()

    def test_create_inference_deployment_sampler_reuses_managed_region_and_shape(self):
        deploy_mgr = _FakeInferenceDeploymentManager()
        svc = self._make_managed_service(deploy_mgr)

        result = svc.create_inference_deployment_sampler(
            DeploymentConfig(
                deployment_id="teacher-unit",
                base_model="accounts/acct/models/base",
                min_replica_count=2,
                max_replica_count=2,
                hot_load_bucket_type=None,
                enable_hot_load=False,
            ),
            timeout_s=123,
            cleanup_on_close=CLEANUP_DEPLOYMENT_ON_CLOSE_SCALE_TO_ZERO,
            tokenizer="tokenizer",
        )

        assert deploy_mgr.created_config is not None
        assert deploy_mgr.created_config.deployment_id == "teacher-unit"
        assert deploy_mgr.created_config.base_model == "accounts/acct/models/base"
        assert deploy_mgr.created_config.deployment_shape == "accounts/acct/deploymentShapes/student/versions/v1"
        assert deploy_mgr.created_config.region == "US_OHIO_1"
        assert deploy_mgr.created_config.enable_hot_load is False
        assert deploy_mgr.created_config.hot_load_bucket_type is None
        assert deploy_mgr.created_config.min_replica_count == 2
        assert deploy_mgr.created_config.max_replica_count == 2
        assert deploy_mgr.waited == [("teacher-unit", 123)]
        assert result.model == "accounts/acct/deployments/teacher-unit"
        assert result.base_url == "https://inference.test"
        assert result.tokenizer == "tokenizer"

        svc.close()

        assert deploy_mgr.scaled_to_zero == ["teacher-unit"]
        assert deploy_mgr.deleted == []
        svc._managed_handle.close.assert_called_once()

    def test_create_inference_deployment_sampler_reuses_existing_without_cleanup(self):
        existing = SimpleNamespace(
            deployment_id="teacher-existing",
            state="READY",
            inference_model="accounts/acct/deployments/teacher-existing",
        )
        deploy_mgr = _FakeInferenceDeploymentManager(existing=existing)
        svc = self._make_managed_service(deploy_mgr)

        result = svc.create_inference_deployment_sampler(
            DeploymentConfig(
                deployment_id="teacher-existing",
                base_model="accounts/acct/models/base",
            ),
            cleanup_on_close=CLEANUP_DEPLOYMENT_ON_CLOSE_SCALE_TO_ZERO,
        )

        assert deploy_mgr.created_config is None
        assert result.model == "accounts/acct/deployments/teacher-existing"
        svc.close()
        assert deploy_mgr.scaled_to_zero == []

    def test_create_inference_deployment_sampler_tracks_cleanup_before_ready(self):
        deploy_mgr = _FakeInferenceDeploymentManager(wait_error=TimeoutError("not ready"))
        svc = self._make_managed_service(deploy_mgr)

        with pytest.raises(TimeoutError, match="not ready"):
            svc.create_inference_deployment_sampler(
                DeploymentConfig(
                    deployment_id="teacher-timeout",
                    base_model="accounts/acct/models/base",
                ),
                cleanup_on_close=CLEANUP_DEPLOYMENT_ON_CLOSE_SCALE_TO_ZERO,
            )

        svc.close()

        assert deploy_mgr.scaled_to_zero == ["teacher-timeout"]

    def test_close_still_closes_managed_handle_when_inference_cleanup_fails(self):
        deploy_mgr = _FakeInferenceDeploymentManager(scale_error=RuntimeError("cleanup failed"))
        svc = self._make_managed_service(deploy_mgr)
        svc._owned_inference_deployments = [(deploy_mgr, "teacher-unit", CLEANUP_DEPLOYMENT_ON_CLOSE_SCALE_TO_ZERO)]

        with pytest.raises(RuntimeError, match="cleanup failed"):
            svc.close()

        assert deploy_mgr.scaled_to_zero == ["teacher-unit"]
        assert svc._owned_inference_deployments == []
        svc._managed_handle.close.assert_called_once()

    def test_create_inference_deployment_sampler_rejects_region_conflict(self):
        svc = self._make_managed_service(_FakeInferenceDeploymentManager(), region="US_OHIO_1")

        with pytest.raises(ValueError, match="region conflicts"):
            svc.create_inference_deployment_sampler(
                DeploymentConfig(
                    deployment_id="teacher-unit",
                    base_model="accounts/acct/models/base",
                    region="US_VIRGINIA_1",
                )
            )

    def test_create_inference_deployment_sampler_rejects_terminal_existing_deployment(self):
        deploy_mgr = _FakeInferenceDeploymentManager(
            existing=SimpleNamespace(deployment_id="teacher-failed", state="FAILED")
        )
        svc = self._make_managed_service(deploy_mgr)

        with pytest.raises(RuntimeError, match="terminal state"):
            svc.create_inference_deployment_sampler(
                DeploymentConfig(
                    deployment_id="teacher-failed",
                    base_model="accounts/acct/models/base",
                )
            )

    def test_reference_auto_lora_uses_base_client(self):
        svc = self._make_service()
        svc.create_base_training_client = MagicMock(return_value="base-client")

        result = svc.create_reference_client(
            "accounts/acct/models/base",
            lora_rank=16,
            user_metadata={"purpose": "reference"},
        )

        assert result == "base-client"
        svc.create_base_training_client.assert_called_once_with(
            "accounts/acct/models/base",
            user_metadata={"purpose": "reference"},
        )

    def test_base_only_request_marks_flag_as_explicitly_set(self):
        request = _BaseOnlyCreateModelRequest(
            session_id="session-1",
            model_seq_id=1,
            base_model="accounts/acct/models/base",
            base_only=True,
        )

        assert request.base_only is True
        assert request.model_dump(exclude_unset=True)["base_only"] is True

    def test_from_firetitan_config_accepts_aliases(self):
        svc = FiretitanServiceClient.from_firetitan_config(
            api_key="fw-key",
            base_url=None,
            model_name="accounts/acct/models/base",
            training_shape="accounts/acct/trainingShapes/shape",
        )

        assert svc._managed_config.base_model == "accounts/acct/models/base"
        assert svc._managed_config.training_shape_id == "accounts/acct/trainingShapes/shape"

    def test_from_firetitan_config_normalizes_blank_optional_reference_fields(self):
        svc = FiretitanServiceClient.from_firetitan_config(
            api_key="fw-key",
            base_url=None,
            base_model="accounts/acct/models/base",
            training_shape_id="accounts/acct/trainingShapes/shape",
            reference_training_shape_id="",
            reference_trainer_job_id="",
        )

        assert svc._managed_config.reference_training_shape_id is None
        assert svc._managed_config.reference_trainer_job_id is None

    def test_from_firetitan_config_defaults_speculative_decoding_enabled(self):
        svc = FiretitanServiceClient.from_firetitan_config(
            api_key="fw-key",
            base_url=None,
            base_model="accounts/acct/models/base",
            training_shape_id="accounts/acct/trainingShapes/shape",
        )

        assert svc._managed_config.disable_speculative_decoding is False

    def test_from_firetitan_config_rejects_conflicting_aliases(self):
        with pytest.raises(ValueError, match="Pass only one alias"):
            FiretitanServiceClient.from_firetitan_config(
                api_key="fw-key",
                base_url=None,
                model_name="accounts/acct/models/base",
                training_shape="shape-a",
                training_shape_ref="shape-b",
            )

    def test_fireworks_key_service_client_uses_local_client_config(self):
        from tinker.lib import internal_client_holder as holder_module

        original_auth_provider = getattr(holder_module, "ApiKeyAuthProvider", None)
        with patch(
            "tinker.lib.public_interfaces.service_client.ServiceClient.__init__",
            return_value=None,
        ) as init:
            FiretitanServiceClient(base_url="https://trainer.test", api_key="fw-key")

        init.assert_called_once()
        assert init.call_args.kwargs["api_key"] == "fw-key"
        assert init.call_args.kwargs["_client_config"] == FIRETITAN_TINKER_CLIENT_CONFIG
        assert init.call_args.kwargs["default_headers"]["X-API-Key"] == "fw-key"
        assert "Authorization" not in init.call_args.kwargs["default_headers"]
        assert getattr(holder_module, "ApiKeyAuthProvider", None) is original_auth_provider

    def test_fireworks_key_auth_provider_sends_control_plane_api_key_header(self):
        async def apply_auth() -> httpx.Request:
            provider = _FireworksApiKeyAuthProvider("fw-key")
            request = httpx.Request("GET", "https://trainer.test/api/v1/healthz")
            async for authed_request in provider.async_auth_flow(request):
                return authed_request
            raise AssertionError("auth flow did not yield a request")

        request = asyncio.run(apply_auth())

        assert request.headers["X-API-Key"] == "fw-key"
        assert "X-TINKER-API" not in request.headers
        assert "Authorization" not in request.headers

    def test_create_training_client_from_state_rejects_access_token(self):
        svc = self._make_service()

        with pytest.raises(NotImplementedError, match="weights_access_token"):
            svc.create_training_client_from_state("tinker://run/weights/step-1", weights_access_token="token")

    def test_create_training_client_from_state_with_optimizer_rejects_access_token(self):
        svc = self._make_service()

        with pytest.raises(NotImplementedError, match="weights_access_token"):
            svc.create_training_client_from_state_with_optimizer(
                "tinker://run/weights/step-1",
                weights_access_token="token",
            )

    def test_create_training_client_from_state_with_optimizer_is_thin_wrapper(self):
        svc = self._make_service()
        svc._managed_config = SimpleNamespace(
            base_model="accounts/acct/models/base",
            lora_rank=8,
            seed=123,
            train_unembed=True,
            train_mlp=True,
            train_attn=True,
        )
        training_client = MagicMock()
        training_client.load_state_with_optimizer.return_value.result.return_value = None
        svc.create_lora_training_client = MagicMock(return_value=training_client)

        result = svc.create_training_client_from_state_with_optimizer(
            "tinker://run/weights/step-1",
            user_metadata={"owner": "test"},
        )

        assert result is training_client
        svc.create_lora_training_client.assert_called_once_with(
            base_model="accounts/acct/models/base",
            rank=8,
            seed=123,
            train_unembed=True,
            train_mlp=True,
            train_attn=True,
            user_metadata={"owner": "test"},
        )
        training_client.load_state_with_optimizer.assert_called_once_with("tinker://run/weights/step-1")

    def test_from_firetitan_config_deprecates_accelerator_fields(self):
        with pytest.warns(DeprecationWarning) as record:
            svc = FiretitanServiceClient.from_firetitan_config(
                api_key="fw-key",
                base_url=None,
                base_model="accounts/acct/models/base",
                training_shape_id="accounts/acct/trainingShapes/shape",
                accelerator_type="NVIDIA_H200",
                accelerator_count=8,
                node_count=1,
                replica_count=2,
                trainer_replica_count=3,
            )

        messages = " ".join(str(w.message) for w in record)
        assert "accelerator_type" in messages
        assert "accelerator_count" in messages
        assert "node_count" in messages
        # Accelerator fields are dropped (owned by the training shape). The two
        # scaling knobs survive and map to different resources: replica_count
        # scales the deployment, trainer_replica_count scales the trainer.
        assert svc._managed_config.accelerator_type is None
        assert svc._managed_config.accelerator_count is None
        assert svc._managed_config.node_count is None
        assert svc._managed_config.replica_count == 2
        assert svc._managed_config.trainer_replica_count == 3

    def test_create_lora_training_client_lazy_provisions_managed_infra(self):
        handle = SimpleNamespace(training_client="training", sampler_backend=object())
        svc = FiretitanServiceClient.from_firetitan_config(
            api_key="fw-key",
            base_model="accounts/acct/models/base",
            lora_rank=4,
            user_metadata={"recipe": "sdft"},
        )

        with patch(
            "fireworks.training.sdk.managed._create_managed_tinker_client",
            return_value=handle,
        ) as create:
            result = svc.create_lora_training_client(
                "accounts/acct/models/base",
                rank=4,
            )

        assert result == "training"
        assert create.call_args.kwargs["user_metadata"] == {"recipe": "sdft"}
        assert svc._sampler_backend is handle.sampler_backend

    def test_managed_max_context_length_surfaces_shape_resolved_value(self):
        # The recipe leaves context length unset; it is resolved from the
        # training shape during provisioning and only the handle carries the
        # resolved value. The property must prefer the handle (not the config,
        # which still reads None) so recipes don't raise a spurious ValueError.
        svc = FiretitanServiceClient.from_firetitan_config(
            api_key="fw-key",
            base_url=None,
            base_model="accounts/acct/models/base",
            training_shape_id="accounts/acct/trainingShapes/shape",
        )
        assert svc._managed_config.max_context_length is None

        handle = SimpleNamespace(
            training_client="training",
            sampler_backend=None,
            training_profile=SimpleNamespace(
                accelerator_type="NVIDIA_H100_80GB",
                accelerator_count=8,
            ),
            max_context_length=8192,
        )
        with patch(
            "fireworks.training.sdk.managed._create_managed_tinker_client",
            return_value=handle,
        ):
            svc.create_training_client("accounts/acct/models/base")

        assert svc.managed_max_context_length == 8192
        assert svc.managed_training_profile is handle.training_profile
        assert svc.managed_accelerator_type == "NVIDIA_H100_80GB"
        assert svc.managed_accelerator_count == 8

    def test_required_service_properties_return_resolved_metadata(self):
        handle = SimpleNamespace(
            training_client="training",
            sampler_backend=None,
            trainer_endpoint=SimpleNamespace(job_id="trainer-1"),
            deployment=SimpleNamespace(deployment_id="deployment-1"),
            max_context_length=32768,
            deployment_shape="accounts/acct/deploymentShapes/ds/versions/v1",
            training_profile=SimpleNamespace(
                accelerator_type="NVIDIA_H100_80GB",
                accelerator_count=8,
            ),
        )
        svc = FiretitanServiceClient.from_firetitan_config(
            api_key="fw-key",
            base_url=None,
            base_model="accounts/acct/models/base",
            training_shape_id="accounts/acct/trainingShapes/shape",
        )

        with patch(
            "fireworks.training.sdk.managed._create_managed_tinker_client",
            return_value=handle,
        ):
            assert svc.create_training_client("accounts/acct/models/base") == "training"

        assert svc.trainer_job_id == "trainer-1"
        assert svc.deployment_id == "deployment-1"
        assert svc.max_context_length == 32768
        assert svc.deployment_shape == "accounts/acct/deploymentShapes/ds/versions/v1"
        assert svc.accelerator_type == "NVIDIA_H100_80GB"
        assert svc.accelerator_count == 8
        assert svc.training_profile is handle.training_profile

    def test_reference_client_job_id_uses_policy_trainer_for_shared_reference(self):
        svc = FiretitanServiceClient.__new__(FiretitanServiceClient)
        svc._owned_reference_handles = []
        svc._reference_handle = None
        svc._managed_handle = SimpleNamespace(
            trainer_endpoint=SimpleNamespace(job_id="trainer-1"),
        )

        assert svc.reference_client_job_id == "trainer-1"
        assert svc.reference_trainer_job_id is None

    def test_reference_client_job_id_uses_separate_reference_trainer(self):
        svc = FiretitanServiceClient.__new__(FiretitanServiceClient)
        svc._owned_reference_handles = []
        svc._reference_handle = SimpleNamespace(trainer_endpoint=SimpleNamespace(job_id="ref-trainer-1"))
        svc._managed_handle = SimpleNamespace(
            trainer_endpoint=SimpleNamespace(job_id="trainer-1"),
        )

        assert svc.reference_client_job_id == "ref-trainer-1"
        assert svc.reference_trainer_job_id == "ref-trainer-1"

    def test_create_reference_client_uses_preprovisioned_reference_handle(self):
        reference_handle = SimpleNamespace(
            training_client="reference-training",
            trainer_endpoint=SimpleNamespace(job_id="ref-trainer-1"),
        )
        svc = FiretitanServiceClient.__new__(FiretitanServiceClient)
        svc._managed_config = SimpleNamespace(
            base_model="accounts/acct/models/base",
            lora_rank=0,
            reference_training_shape_id="ref-shape",
            reference_trainer_job_id=None,
        )
        svc._default_user_metadata = None
        svc._reference_handle = None
        svc._owned_reference_handles = []
        svc._ensure_managed_handle = MagicMock(return_value=SimpleNamespace(reference_handle=reference_handle))
        svc._provision_reference_handle = MagicMock()

        result = svc.create_reference_client("accounts/acct/models/base", lora_rank=0)

        assert result == "reference-training"
        assert svc._reference_handle is reference_handle
        svc._provision_reference_handle.assert_not_called()

    def test_required_service_properties_raise_when_metadata_missing(self):
        handle = SimpleNamespace(
            training_client="training",
            sampler_backend=None,
            trainer_endpoint=SimpleNamespace(job_id="trainer-1"),
            deployment=SimpleNamespace(deployment_id="deployment-1"),
            max_context_length=None,
        )
        svc = FiretitanServiceClient.from_firetitan_config(
            api_key="fw-key",
            base_url=None,
            base_model="accounts/acct/models/base",
            training_shape_id="accounts/acct/trainingShapes/shape",
        )

        with patch(
            "fireworks.training.sdk.managed._create_managed_tinker_client",
            return_value=handle,
        ):
            svc.create_training_client("accounts/acct/models/base")

        with pytest.raises(RuntimeError, match="max context length"):
            _ = svc.max_context_length

    def test_deprecated_accelerator_kwargs_are_not_reported_without_profile(self):
        with pytest.warns(DeprecationWarning):
            svc = FiretitanServiceClient.from_firetitan_config(
                api_key="fw-key",
                base_model="accounts/acct/models/base",
                accelerator_type="NVIDIA_B200",
                accelerator_count=16,
            )

        assert svc.managed_training_profile is None
        assert svc.managed_accelerator_type is None
        assert svc.managed_accelerator_count is None

    def test_create_training_client_deprecation_warns_on_base_model_override(self):
        # base_model/lora_rank are single-sourced from the service config; a
        # divergent create_training_client value is deprecated + ignored.
        svc = FiretitanServiceClient.from_firetitan_config(
            api_key="fw-key",
            base_url=None,
            base_model="accounts/acct/models/base",
            lora_rank=8,
        )
        handle = SimpleNamespace(training_client="tc", sampler_backend=None)
        with patch("fireworks.training.sdk.managed._create_managed_tinker_client", return_value=handle):
            with pytest.warns(DeprecationWarning, match="base_model.*deprecated and ignored"):
                svc.create_training_client("accounts/acct/models/OTHER", lora_rank=8)

    def test_create_training_client_no_deprecation_when_matching(self):
        svc = FiretitanServiceClient.from_firetitan_config(
            api_key="fw-key",
            base_url=None,
            base_model="accounts/acct/models/base",
            lora_rank=8,
        )
        handle = SimpleNamespace(training_client="tc", sampler_backend=None)
        with patch("fireworks.training.sdk.managed._create_managed_tinker_client", return_value=handle):
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                svc.create_training_client("accounts/acct/models/base", lora_rank=8)
        assert not any("override is deprecated" in str(w.message) for w in caught)

    def test_deprecated_override_does_not_poison_managed_handle_cache(self):
        # An ignored deprecated base_model on the first call must not make a
        # later canonical call look like a different training configuration.
        # The managed handle is keyed off the immutable service config, so the
        # first call provisions once and the canonical follow-up reuses it
        # rather than raising "different training configuration".
        svc = FiretitanServiceClient.from_firetitan_config(
            api_key="fw-key",
            base_url=None,
            base_model="accounts/acct/models/base",
            lora_rank=8,
        )
        handle = SimpleNamespace(training_client="tc", sampler_backend=None)
        with patch("fireworks.training.sdk.managed._create_managed_tinker_client", return_value=handle) as create:
            with pytest.warns(DeprecationWarning, match="base_model.*deprecated and ignored"):
                first = svc.create_training_client("accounts/acct/models/OTHER", lora_rank=8)
            # The canonical follow-up reuses the same handle (no raise).
            second = svc.create_training_client("accounts/acct/models/base", lora_rank=8)

        assert first == "tc"
        assert second == "tc"
        create.assert_called_once()
        # Provisioning used the immutable config, never the divergent override.
        assert create.call_args.kwargs["config"].base_model == "accounts/acct/models/base"

    def test_managed_deployment_id_prefers_provisioned_handle(self):
        svc = FiretitanServiceClient.from_firetitan_config(
            api_key="fw-key",
            base_url=None,
            base_model="accounts/acct/models/base",
            deployment_id="requested-deployment",
        )
        assert svc.managed_deployment_id == "requested-deployment"

        svc._managed_handle = SimpleNamespace(
            deployment=SimpleNamespace(deployment_id="resolved-deployment"),
        )
        assert svc.managed_deployment_id == "resolved-deployment"

    def test_from_firetitan_config_accepts_managed_by(self):
        svc = FiretitanServiceClient.from_firetitan_config(
            api_key="fw-key",
            base_url=None,
            base_model="accounts/acct/models/base",
            managed_by="parent-job",
        )

        assert svc._managed_config.managed_by == "parent-job"

    def test_existing_managed_deployment_is_reattached_with_patch(self):
        deploy_mgr = MagicMock()
        existing = SimpleNamespace(
            state="READY",
            deployment_id="dep-1",
            hot_load_trainer_job="accounts/acct/rlorTrainerJobs/old-job",
            deployment_shape_version=None,
        )
        deploy_mgr.get.return_value = existing
        deploy_mgr.reattach_trainer.return_value = SimpleNamespace(
            state="READY",
            deployment_id="dep-1",
            hot_load_trainer_job="accounts/acct/rlorTrainerJobs/job-1",
        )
        config = _ManagedTinkerConfig(
            base_model="accounts/acct/models/base",
            deployment_id="dep-1",
            reattach_settle_timeout_s=5,
            reattach_poll_interval_s=0.01,
        )

        deployment = _create_or_reattach_deployment(
            deploy_mgr,
            config,
            trainer_job_name="accounts/acct/rlorTrainerJobs/job-1",
            deployment_shape=None,
        )

        assert deployment.deployment_id == "dep-1"
        deploy_mgr.reattach_trainer.assert_called_once_with(
            existing,
            base_model="accounts/acct/models/base",
            trainer_job_name="accounts/acct/rlorTrainerJobs/job-1",
            timeout_s=5,
            poll_interval_s=0.01,
        )
        deploy_mgr.wait_for_ready.assert_not_called()

    def test_existing_managed_deployment_already_attached_is_reused(self):
        deploy_mgr = MagicMock()
        existing = SimpleNamespace(
            state="READY",
            deployment_id="dep-1",
            hot_load_trainer_job="accounts/acct/rlorTrainerJobs/job-1",
            deployment_shape_version=None,
        )
        deploy_mgr.get.return_value = existing
        deploy_mgr.reattach_trainer.return_value = existing
        config = _ManagedTinkerConfig(
            base_model="accounts/acct/models/base",
            deployment_id="dep-1",
        )

        deployment = _create_or_reattach_deployment(
            deploy_mgr,
            config,
            trainer_job_name="accounts/acct/rlorTrainerJobs/job-1",
            deployment_shape=None,
        )

        assert deployment is existing
        deploy_mgr.reattach_trainer.assert_called_once_with(
            existing,
            base_model="accounts/acct/models/base",
            trainer_job_name="accounts/acct/rlorTrainerJobs/job-1",
            timeout_s=config.reattach_settle_timeout_s,
            poll_interval_s=config.reattach_poll_interval_s,
        )

    def test_generated_managed_deployment_id_does_not_reattach(self):
        deploy_mgr = MagicMock()
        deploy_mgr.create_or_get.return_value = SimpleNamespace(
            state="READY",
            deployment_id="generated-dep",
        )
        config = _ManagedTinkerConfig(
            base_model="accounts/acct/models/base",
        )

        deployment = _create_or_reattach_deployment(
            deploy_mgr,
            config,
            trainer_job_name="accounts/acct/rlorTrainerJobs/job-1",
            deployment_shape="accounts/acct/deploymentShapes/ds/versions/1",
        )

        assert deployment.deployment_id == "generated-dep"
        deploy_mgr.get.assert_not_called()
        deploy_mgr.update.assert_not_called()

    def test_list_and_promote_checkpoints_delegate_to_managed_trainer_manager(self):
        # The cookbook's TrainingCheckpoints treats the service as its
        # control-plane checkpoint client. These must delegate to the managed
        # TrainerJobManager (TrainerJobManager had them; ServiceClient does not).
        manager = MagicMock()
        manager.list_checkpoints.return_value = [{"name": "cp", "promotable": True}]
        manager.promote_checkpoint.return_value = {"model": "accounts/acct/models/out"}

        svc = FiretitanServiceClient.__new__(FiretitanServiceClient)
        svc._managed_handle = SimpleNamespace(trainer_manager=manager)

        rows = svc.list_checkpoints("job-1")
        assert rows == [{"name": "cp", "promotable": True}]
        manager.list_checkpoints.assert_called_once_with("job-1", page_size=200)

        result = svc.promote_checkpoint(
            name="accounts/acct/rlorTrainerJobs/job-1/checkpoints/cp",
            output_model_id="out",
            base_model="accounts/acct/models/base",
        )
        assert result == {"model": "accounts/acct/models/out"}
        manager.promote_checkpoint.assert_called_once_with(
            name="accounts/acct/rlorTrainerJobs/job-1/checkpoints/cp",
            output_model_id="out",
            base_model="accounts/acct/models/base",
        )

    def test_checkpoint_ops_without_trainer_raise_runtime_error(self):
        # No provisioned handle -> a clear error, not the AttributeError that
        # _latest_resumable would silently swallow into a spurious fresh start.
        svc = FiretitanServiceClient.__new__(FiretitanServiceClient)
        svc._managed_handle = None
        with pytest.raises(RuntimeError, match="require a provisioned trainer"):
            svc.list_checkpoints("job-1")
        with pytest.raises(RuntimeError, match="require a provisioned trainer"):
            svc.promote_checkpoint(name="x")

    def test_create_sampling_client_requires_managed_sampler_state(self):
        svc = FiretitanServiceClient.__new__(FiretitanServiceClient)
        svc._sampler_backend = None
        svc._managed_config = None

        with pytest.raises(NotImplementedError, match="SDK-managed sampler state"):
            svc.create_sampling_client(base_model="accounts/acct/models/base")

    def test_create_sampling_client_hotloads_sdk_managed_snapshot(self):
        svc = FiretitanServiceClient.__new__(FiretitanServiceClient)
        svc._managed_config = None
        sampler_backend = MagicMock()
        sampler_backend.hotload_saved_snapshot.return_value = True
        sampler_backend.get_sampling_client.return_value = "sampling-client"
        svc._sampler_backend = sampler_backend

        result = svc.create_sampling_client(model_path="snapshot-1")

        assert result == "sampling-client"
        sampler_backend.hotload_saved_snapshot.assert_called_once_with("snapshot-1")

    def test_create_sampling_client_uses_serverless_completions_route(self):
        svc = FiretitanServiceClient.__new__(FiretitanServiceClient)
        svc._sampler_backend = None
        svc._managed_config = None
        svc._managed_base_url = "https://dev.api.fireworks.ai/training/v1/serverless"
        svc._fireworks_api_key = "fw_test"
        svc._cp_account_id = "pyroworks-dev"
        svc.holder = SimpleNamespace(get_session_id=lambda: "ts-abc123")

        sampler = svc.create_sampling_client(model_path="pyroworks-dev/run-1/step-1")

        assert sampler.deployment_sampler.base_url == "https://dev.api.fireworks.ai/training/v1/serverless"
        assert (
            sampler.deployment_sampler.model
            == "accounts/pyroworks-dev/trainingSessions/ts-abc123/checkpoints/pyroworks-dev/run-1/step-1"
        )
        assert sampler.deployment_sampler.api_key == "fw_test"
        sampler.close()

    def test_create_sampling_client_rejects_non_serverless_base_url(self):
        svc = FiretitanServiceClient.__new__(FiretitanServiceClient)
        svc._sampler_backend = None
        svc._managed_config = None
        svc._managed_base_url = "https://dev.api.fireworks.ai/training/v1"
        svc._fireworks_api_key = "fw_test"
        svc._cp_account_id = "pyroworks-dev"
        svc.holder = SimpleNamespace(get_session_id=lambda: "ts-abc123")

        with pytest.raises(ValueError, match="/training/v1/serverless"):
            svc.create_sampling_client(model_path="pyroworks-dev/run-1/step-1")

    def test_hotload_sampler_snapshot_returns_none(self):
        svc = FiretitanServiceClient.__new__(FiretitanServiceClient)
        svc._managed_config = None
        sampler_backend = MagicMock()
        sampler_backend.hotload_saved_snapshot.return_value = True
        svc._sampler_backend = sampler_backend

        result = svc.hotload_sampler_snapshot("snapshot-1")

        assert result is None
        sampler_backend.hotload_saved_snapshot.assert_called_once_with("snapshot-1")

    def test_requires_initial_sampler_sync_until_hotload(self):
        svc = FiretitanServiceClient.__new__(FiretitanServiceClient)
        svc._managed_config = None
        svc._managed_handle = SimpleNamespace(requires_initial_sampler_sync=True)
        sampler_backend = MagicMock()
        sampler_backend.hotload_saved_snapshot.return_value = True
        svc._sampler_backend = sampler_backend

        assert svc.requires_initial_sampler_sync() is True

        svc.hotload_sampler_snapshot("step-11-session")

        assert svc.requires_initial_sampler_sync() is False
        assert svc._managed_handle.requires_initial_sampler_sync is False

    def test_requires_initial_sampler_sync_noops_without_handle(self):
        svc = FiretitanServiceClient.__new__(FiretitanServiceClient)
        svc._managed_handle = None

        assert svc.requires_initial_sampler_sync() is False


class TestLazyManagedRestClient:
    def _make_rest_client(self):
        managed_config = SimpleNamespace(
            base_model="accounts/acct/models/base",
            trainer_job_id=None,
            lora_rank=8,
            train_unembed=True,
            train_mlp=True,
            train_attn=True,
        )
        return _LazyManagedRestClient(managed_config)

    def test_get_audit_log_raises_not_implemented(self):
        rest_client = self._make_rest_client()

        with pytest.raises(NotImplementedError, match="get_audit_log"):
            rest_client.get_audit_log().result()

    def test_assign_session_project_raises_not_implemented(self):
        rest_client = self._make_rest_client()

        with pytest.raises(NotImplementedError, match="assign_session_project"):
            rest_client.assign_session_project("session-1", "project-1").result()

    def test_get_audit_log_async_raises_not_implemented(self):
        rest_client = self._make_rest_client()

        with pytest.raises(NotImplementedError, match="get_audit_log_async"):
            asyncio.run(rest_client.get_audit_log_async())

    def test_assign_session_project_async_raises_not_implemented(self):
        rest_client = self._make_rest_client()

        with pytest.raises(NotImplementedError, match="assign_session_project_async"):
            asyncio.run(rest_client.assign_session_project_async("session-1", "project-1"))


def _bare_training_client():
    """A FiretitanTrainingClient with __init__ bypassed for unit testing."""
    client = FiretitanTrainingClient.__new__(FiretitanTrainingClient)
    client._sampler_backend = None
    client._tokenizer_model = None
    client._lora_rank = 0
    client._sampler_checkpoint_saved = False
    client._first_sampler_checkpoint_type = "base"
    return client


class TestSaveWeightsAndGetSamplingClientUnsupported:
    """The Tinker combined save+sample idiom has no FireTitan equivalent.

    Fireworks samples from a separate hot-load deployment, so the inherited
    tinker implementation (ephemeral in-service sampling session) cannot work.
    All three entry points must raise NotImplementedError with the two-step
    idiom rather than the opaque inherited AssertionError.
    """

    def test_sync_raises_with_idiom(self):
        client = _bare_training_client()
        with pytest.raises(NotImplementedError) as exc:
            client.save_weights_and_get_sampling_client("step-1")
        assert "save_weights_for_sampler" in str(exc.value)
        assert "create_sampling_client" in str(exc.value)
        assert str(exc.value) == SAMPLING_CLIENT_FROM_TRAINER_MESSAGE

    def test_submit_raises(self):
        client = _bare_training_client()
        with pytest.raises(NotImplementedError):
            client.save_weights_and_get_sampling_client_submit()

    def test_async_raises(self):
        client = _bare_training_client()
        with pytest.raises(NotImplementedError):
            asyncio.run(client.save_weights_and_get_sampling_client_async("step-1"))


class TestGetTokenizer:
    def test_loads_from_managed_tokenizer_model_without_rpc(self):
        client = _bare_training_client()
        client._tokenizer_model = "Qwen/Qwen3-1.7B"
        with patch("transformers.AutoTokenizer.from_pretrained", return_value="tok") as load:
            result = client.get_tokenizer()
        assert result == "tok"
        load.assert_called_once_with("Qwen/Qwen3-1.7B")

    def test_raises_when_no_tokenizer_model(self):
        client = _bare_training_client()
        client._tokenizer_model = None
        with pytest.raises(ValueError, match="tokenizer_model"):
            client.get_tokenizer()


class TestTrainingClientSamplingHelpers:
    def _make_client(self):
        client = FiretitanTrainingClient.__new__(FiretitanTrainingClient)
        client._sampler_backend = None
        client._lora_rank = 0
        client._sampler_checkpoint_saved = False
        client._first_sampler_checkpoint_type = "base"
        return client

    def test_sampler_checkpoint_type_defaults_base_then_delta_for_full_param(self):
        client = self._make_client()

        assert client._next_sampler_checkpoint_type() == "base"
        client._sampler_checkpoint_saved = True
        assert client._next_sampler_checkpoint_type() == "delta"

    def test_sampler_checkpoint_type_defaults_base_for_lora(self):
        client = self._make_client()
        client._lora_rank = 8
        client._sampler_checkpoint_saved = True

        assert client._next_sampler_checkpoint_type() == "base"

    def test_sampler_checkpoint_type_accepts_explicit_override(self):
        client = self._make_client()

        assert client._next_sampler_checkpoint_type("delta") == "delta"
        assert client._next_sampler_checkpoint_type("base") == "base"

    def test_sampler_checkpoint_type_rejects_unknown_value(self):
        client = self._make_client()

        with pytest.raises(ValueError, match="checkpoint_type"):
            client._next_sampler_checkpoint_type("full")

    def test_save_weights_for_sampler_passes_checkpoint_override(self):
        client = self._make_client()
        with patch.object(
            client,
            "save_weights_for_sampler_ext",
            return_value=SaveSamplerResult(path="raw/path", snapshot_name="step-1-test1234"),
        ) as save_ext:
            future = client.save_weights_for_sampler("step-1", checkpoint_type="base", ttl_seconds=60)

        assert future.result().path == "raw/path"
        save_ext.assert_called_once_with("step-1", checkpoint_type="base", ttl_seconds=60)

    def test_save_weights_for_sampler_records_public_path_and_snapshot_alias(self):
        client = self._make_client()
        client.session_id = "test1234"
        client._saved_sampler_names = set()
        sampler_backend = MagicMock()
        client._attach_sampler_backend(sampler_backend)
        client._get_request_id = MagicMock(return_value=41)

        public_path = "run-abc:train:0/step-1-test1234"

        def run_coroutine_threadsafe(coro):
            coro.close()
            future = MagicMock()
            future.result.return_value = public_path
            return future

        client.holder = SimpleNamespace(run_coroutine_threadsafe=MagicMock(side_effect=run_coroutine_threadsafe))

        result = client.save_weights_for_sampler_ext("step-1", checkpoint_type="delta")

        assert result == SaveSamplerResult(path=public_path, snapshot_name="step-1-test1234")
        calls = sampler_backend.remember_saved_snapshot.call_args_list
        assert [call.args[0] for call in calls] == [public_path, "step-1-test1234"]
        assert [call.kwargs for call in calls] == [
            {"checkpoint_type": "delta"},
            {"checkpoint_type": "delta"},
        ]

    def test_attach_sampler_backend_returns_self(self):
        client = self._make_client()
        sampler_backend = object()

        assert client._attach_sampler_backend(sampler_backend) is client
        assert client._sampler_backend is sampler_backend

    def test_create_sampling_client_hotloads_saved_sampler_path(self):
        client = self._make_client()
        sampler_backend = MagicMock()
        sampler_backend.hotload_saved_snapshot.return_value = True
        sampler_backend.get_sampling_client.return_value = "sampling-client"
        client._attach_sampler_backend(sampler_backend)

        result = client.create_sampling_client("sampler-path")

        assert result == "sampling-client"
        sampler_backend.hotload_saved_snapshot.assert_called_once_with("sampler-path")

    def test_tinker_sampler_backend_hotloads_snapshot_identity(self):
        deploy_mgr = MagicMock()
        deploy_mgr.account_id = "acct"
        deploy_mgr.api_key = "fw-key"
        deploy_mgr.inference_url = "https://inference.test"
        deploy_mgr.hotload_and_wait.return_value = True

        sampler_backend = _TinkerSamplerBackend(
            deploy_mgr=deploy_mgr,
            deployment_id="dep-1",
            base_model="accounts/acct/models/base",
            hotload_timeout_s=123,
        )

        assert sampler_backend.hotload_saved_snapshot("sampler-path") is True
        deploy_mgr.hotload_and_wait.assert_called_once_with(
            deployment_id="dep-1",
            base_model="accounts/acct/models/base",
            snapshot_identity="sampler-path",
            incremental_snapshot_metadata=None,
            reset_prompt_cache=True,
            timeout_seconds=123,
            path=None,
        )
        deploy_mgr.get.assert_not_called()

    def test_tinker_sampler_backend_full_param_delta_chain(self):
        """Full-param: first save is base (FULL hotload), later deltas carry
        incremental metadata referencing the previously loaded snapshot."""
        deploy_mgr = MagicMock()
        deploy_mgr.account_id = "acct"
        deploy_mgr.get.return_value = SimpleNamespace(hot_load_bucket_url="gs://bucket/prefix")
        deploy_mgr.hotload_and_wait.return_value = True

        sampler_backend = _TinkerSamplerBackend(
            deploy_mgr=deploy_mgr,
            deployment_id="dep-1",
            base_model="accounts/acct/models/base",
            lora_rank=0,
        )

        # Step 1: base checkpoint -> FULL hotload (no incremental metadata).
        sampler_backend.remember_saved_snapshot("snap-base", checkpoint_type="base")
        assert sampler_backend.hotload_saved_snapshot("snap-base") is True
        assert deploy_mgr.hotload_and_wait.call_args.kwargs["incremental_snapshot_metadata"] is None

        # Step 2: delta checkpoint -> incremental metadata pins the prior snapshot.
        sampler_backend.remember_saved_snapshot("snap-delta", checkpoint_type="delta")
        assert sampler_backend.hotload_saved_snapshot("snap-delta") is True
        meta = deploy_mgr.hotload_and_wait.call_args.kwargs["incremental_snapshot_metadata"]
        assert meta == {
            "previous_snapshot_identity": "snap-base",
            "compression_format": "arc_v2",
            "checksum_format": "alder32",
        }

    def test_tinker_sampler_backend_lora_never_sends_incremental(self):
        """LoRA always hotloads a full adapter, even when typed 'delta'."""
        deploy_mgr = MagicMock()
        deploy_mgr.account_id = "acct"
        deploy_mgr.get.return_value = SimpleNamespace(hot_load_bucket_url="gs://bucket/prefix")
        deploy_mgr.hotload_and_wait.return_value = True

        sampler_backend = _TinkerSamplerBackend(
            deploy_mgr=deploy_mgr,
            deployment_id="dep-1",
            base_model="accounts/acct/models/base",
            lora_rank=8,
        )

        sampler_backend.remember_saved_snapshot("snap-a", checkpoint_type="base")
        assert sampler_backend.hotload_saved_snapshot("snap-a") is True
        sampler_backend.remember_saved_snapshot("snap-b", checkpoint_type="delta")
        assert sampler_backend.hotload_saved_snapshot("snap-b") is True
        assert deploy_mgr.hotload_and_wait.call_args.kwargs["incremental_snapshot_metadata"] is None

    def test_tinker_sampler_backend_reset_snapshot_chain_forces_full_hotload(self):
        deploy_mgr = MagicMock()
        deploy_mgr.account_id = "acct"
        deploy_mgr.hotload_and_wait.return_value = True

        sampler_backend = _TinkerSamplerBackend(
            deploy_mgr=deploy_mgr,
            deployment_id="dep-1",
            base_model="accounts/acct/models/base",
            lora_rank=0,
        )

        sampler_backend.remember_saved_snapshot("snap-base", checkpoint_type="base")
        assert sampler_backend.hotload_saved_snapshot("snap-base") is True
        sampler_backend.remember_saved_snapshot("snap-delta", checkpoint_type="delta")
        assert sampler_backend.hotload_saved_snapshot("snap-delta") is True
        assert deploy_mgr.hotload_and_wait.call_args.kwargs["incremental_snapshot_metadata"] is not None

        sampler_backend.reset_snapshot_chain()
        sampler_backend.remember_saved_snapshot("snap-after-reattach", checkpoint_type="delta")
        assert sampler_backend.hotload_saved_snapshot("snap-after-reattach") is True

        assert deploy_mgr.hotload_and_wait.call_args.kwargs["incremental_snapshot_metadata"] is None

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


class TestForwardBackwardCustomEmbedding:
    def _make_client(self):
        client = FiretitanTrainingClient.__new__(FiretitanTrainingClient)
        client._saved_sampler_names = set()
        client._saved_state_names = set()
        client.session_id = "test1234"
        return client

    @patch("tinker.lib.public_interfaces.training_client.TrainingClient.forward_backward_custom")
    def test_logprob_output_delegates_to_upstream_tinker(self, mock_forward_backward_custom):
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

        async def fake_forward(data, pooling, output="embedding"):
            captured["forward_pooling"] = pooling
            captured["forward_output_mode"] = output
            return _ImmediateFuture(forward_output)

        async def fake_backward(data, pooling, output="embedding"):
            captured["backward_pooling"] = pooling
            captured["backward_output_mode"] = output
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

        async def fake_forward(data, pooling, output="embedding"):
            return _ImmediateFuture(forward_output)

        async def fake_backward(data, pooling, output="embedding"):
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

        async def fake_forward(data, pooling, output="embedding"):
            return _ImmediateFuture(forward_output)

        async def fake_backward(data, pooling, output="embedding"):
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
        svc._managed_config = None
        svc._default_user_metadata = None
        # _created_training_configs is keyed by _TrainingKey
        # (base_model, lora_rank, seed, train_mlp, train_attn, train_unembed, lora_alpha);
        # a namedtuple compares equal to the plain tuple with the same fields.
        svc._created_training_configs = {("model-a", 0, None, True, True, True, None)}

        with pytest.raises(ValueError, match="already exists"):
            svc.create_training_client("model-a", lora_rank=0)

    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    @pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
    def test_different_lora_rank_ok(self):
        from fireworks.training.sdk.client import FiretitanServiceClient

        svc = FiretitanServiceClient.__new__(FiretitanServiceClient)
        svc._managed_config = None
        svc._default_user_metadata = None
        svc._created_training_configs = {("model-a", 0, None, True, True, True, None)}
        svc.holder = MagicMock()
        svc.holder.get_session_id.return_value = 1
        svc.holder.get_training_client_id.return_value = 1

        class FakeFuture:
            def result(self):
                return "model-id"

        def run_coroutine_threadsafe(coro):
            coro.close()
            return FakeFuture()

        svc.holder.run_coroutine_threadsafe.side_effect = run_coroutine_threadsafe

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
        coro_arg.close()


# ---------------------------------------------------------------------------
# cos_similarity_matrix single-chunk guard
# ---------------------------------------------------------------------------


class TestCheckCosSimilarityMatrixSingleChunk:
    """``output='cos_similarity_matrix'`` is fundamentally a single-HTTP-request
    operation: the trainer builds ``S = Z @ Z.T`` over the request-local batch,
    so any SDK-level chunking would silently drop every cross-chunk similarity
    pair. The guard surfaces that as a loud, actionable error instead.

    These tests pin the contract of the stateless helper so it can be reasoned
    about in isolation from a real ``FiretitanTrainingClient``.
    """

    def test_single_chunk_is_allowed(self):
        # one chunk = one HTTP request = trainer sees the entire batch → safe
        _check_cos_similarity_matrix_single_chunk(
            [["d0", "d1", "d2"]],
            output="cos_similarity_matrix",
        )

    def test_empty_chunks_list_is_allowed(self):
        # degenerate case (no data at all) — len > 1 is the only failure mode
        _check_cos_similarity_matrix_single_chunk([], output="cos_similarity_matrix")

    def test_two_chunks_raises_with_remediation_hint(self):
        chunks = [["d0", "d1"], ["d2", "d3", "d4"]]
        with pytest.raises(ValueError) as exc_info:
            _check_cos_similarity_matrix_single_chunk(
                chunks,
                output="cos_similarity_matrix",
            )
        msg = str(exc_info.value)
        # mentions the offending mode and the actual split sizes
        assert "cos_similarity_matrix" in msg
        assert "[2, 3]" in msg
        assert "2 chunks" in msg or "split into 2" in msg
        # points users at the two viable alternatives
        assert "contrastive_loss" in msg
        assert "embedding" in msg
        # cites the cap constants so the user knows what 'too big' means
        assert "MAX_CHUNK_LEN=1024" in msg
        assert "MAX_CHUNK_BYTES_COUNT=5_000_000" in msg

    def test_many_chunks_reports_total_size_correctly(self):
        chunks = [list(range(1024))] * 5 + [list(range(7))]
        with pytest.raises(ValueError) as exc_info:
            _check_cos_similarity_matrix_single_chunk(
                chunks,
                output="cos_similarity_matrix",
            )
        # sum of chunk sizes is reported as the offending len(data)
        assert "len(data)=5127" in str(exc_info.value)


# ---------------------------------------------------------------------------
# _build_embedding_requests dispatch
# ---------------------------------------------------------------------------


class TestBuildEmbeddingRequestsDispatch:
    """``_build_embedding_requests`` is the single SDK chokepoint that decides
    between the chunked path (``embedding``) and the forced single-request path
    (``cos_similarity_matrix``). Test the dispatch is correct for both, without
    needing a real trainer connection.
    """

    def _make_client(self):
        client = FiretitanTrainingClient.__new__(FiretitanTrainingClient)
        client.session_id = "test1234"
        client.holder = MagicMock()
        return client

    def test_embedding_mode_goes_through_chunked_path(self):
        client = self._make_client()
        # mark the two delegates so we can tell which path was taken
        client._chunked_requests = MagicMock(return_value=[(1, ["d0"]), (2, ["d1"])])
        client._chunked_requests_generator = MagicMock(
            side_effect=AssertionError("embedding mode must NOT call _chunked_requests_generator directly")
        )
        client._get_request_id = MagicMock(return_value=99)

        out = client._build_embedding_requests(["d0", "d1"], "embedding")

        assert out == [(1, ["d0"]), (2, ["d1"])]
        client._chunked_requests.assert_called_once_with(["d0", "d1"])
        client._get_request_id.assert_not_called()

    def test_cos_similarity_matrix_mode_forces_single_request(self):
        client = self._make_client()
        # natural chunking would still produce 1 chunk for small data
        client._chunked_requests_generator = MagicMock(return_value=iter([["d0", "d1"]]))
        client._chunked_requests = MagicMock(
            side_effect=AssertionError("cos_similarity_matrix mode must NOT call _chunked_requests")
        )
        client._get_request_id = MagicMock(return_value=77)

        out = client._build_embedding_requests(["d0", "d1"], "cos_similarity_matrix")

        # exactly one request, carrying the full data (not the chunker's split)
        assert out == [(77, ["d0", "d1"])]
        client._get_request_id.assert_called_once()

    def test_cos_similarity_matrix_mode_raises_when_would_chunk(self):
        client = self._make_client()
        # simulate natural chunking that would split data into 2 chunks
        client._chunked_requests_generator = MagicMock(return_value=iter([["d0", "d1"], ["d2"]]))
        client._get_request_id = MagicMock()

        with pytest.raises(ValueError, match="cos_similarity_matrix"):
            client._build_embedding_requests(
                ["d0", "d1", "d2"],
                "cos_similarity_matrix",
            )
        # never reached request-id allocation
        client._get_request_id.assert_not_called()


# ---------------------------------------------------------------------------
# Serverless identity surfacing: session on the service, run on the client
# ---------------------------------------------------------------------------


class TestServerlessSessionId:
    def test_ts_prefixed_is_serverless(self):
        assert _is_serverless_session_id("ts-0123456789abcdef")

    def test_non_ts_is_not_serverless(self):
        # The legacy tinker short id and the run id are not CP session ids.
        assert not _is_serverless_session_id("0400ab94")
        assert not _is_serverless_session_id("run-deadbeef:train:0")

    def test_none_and_empty_are_not_serverless(self):
        assert not _is_serverless_session_id(None)
        assert not _is_serverless_session_id("")


class TestRunIdFromModelId:
    def test_parses_run_scoped_model_id(self):
        assert _run_id_from_model_id("run-ceb524:train:0") == "run-ceb524"
        assert _run_id_from_model_id("run-abc:train:5") == "run-abc"

    def test_none_for_non_run_scoped(self):
        assert _run_id_from_model_id("base-xyz") is None  # base-only reference
        assert _run_id_from_model_id("ts-abc") is None
        assert _run_id_from_model_id("model-without-suffix") is None

    def test_none_for_non_str(self):
        assert _run_id_from_model_id(None) is None


def _service(account_id: str | None = "pyroworks-dev", session_id: str = "ts-abc123"):
    # Bypass __init__: exercise the serverless identity surface. We pre-cache the
    # resolved account so the name builders don't do a real whoami in the test;
    # account resolution itself is covered separately.
    svc = FiretitanServiceClient.__new__(FiretitanServiceClient)
    svc.holder = SimpleNamespace(get_session_id=lambda: session_id)
    svc._cp_account_id = account_id
    return svc


class TestServiceTrainingSession:
    """The session is owned by the service (one session : many runs)."""

    def test_session_id_and_name(self):
        svc = _service()
        assert svc.training_session_id == "ts-abc123"
        assert svc.training_session_name == "accounts/pyroworks-dev/trainingSessions/ts-abc123"

    def test_none_for_non_serverless_session(self):
        svc = _service(session_id="0400ab94")
        assert svc.training_session_id is None
        assert svc.training_session_name is None


class TestServerlessRunName:
    """The run is owned by each training client; the service builds its name."""

    def test_builds_full_run_resource_name(self):
        svc = _service()
        assert svc._serverless_run_name("run-ceb524:train:0") == "accounts/pyroworks-dev/trainingRuns/run-ceb524"

    def test_none_for_base_only_model(self):
        svc = _service()
        assert svc._serverless_run_name("base-xyz") is None


class TestAccountResolutionBestEffort:
    """The ids are the durable handles; names degrade to None when the account
    can't be resolved — they never fail the caller."""

    def test_no_api_key_degrades_to_none(self):
        svc = FiretitanServiceClient.__new__(FiretitanServiceClient)
        svc.holder = SimpleNamespace(get_session_id=lambda: "ts-abc123")
        svc._fireworks_api_key = None  # nothing to resolve the account with
        assert svc._resolved_account_id() is None
        assert svc.training_session_id == "ts-abc123"  # id still surfaced
        assert svc.training_session_name is None  # name degrades, no crash
        assert svc._serverless_run_name("run-x:train:0") is None

    def test_account_cached(self):
        svc = _service()  # pre-cached account
        assert svc._resolved_account_id() == "pyroworks-dev"
        assert svc._resolved_account_id() == "pyroworks-dev"

    def test_no_in_progress_none_published(self):
        # Regression: the cache must never hold a transient None *during*
        # resolution. A concurrent reader must see "unset" (and resolve too) or
        # the final value — never a premature None baked into a mid-flight client.
        svc = FiretitanServiceClient.__new__(FiretitanServiceClient)
        svc._fireworks_api_key = "fw_x"
        seen = {}

        class _FakeFireworksClient:
            def __init__(self, **kwargs):
                pass

            @property
            def account_id(self):
                # at the moment of the whoami the cache must still be unset
                seen["mid"] = getattr(svc, "_cp_account_id", "unset")
                return "pyroworks-dev"

        with patch("fireworks.training.sdk.fireworks_client.FireworksClient", _FakeFireworksClient):
            assert svc._resolved_account_id() == "pyroworks-dev"
        assert seen["mid"] == "unset"  # no premature None observed mid-resolution
