"""Negotiate through real Tinker session/model/F/B HTTP resource calls."""

import json
import asyncio
from types import SimpleNamespace
from unittest.mock import Mock

import httpx
import pytest

from fireworks.training.sdk import types
from fireworks.training.sdk.client import FiretitanServiceClient
from fireworks.training.sdk.trainer import TrainerServiceEndpoint
from fireworks.training.sdk.decision import DecisionCalibration, SamplerCheckpointMetadata
from fireworks.training.sdk._core._base_client import AsyncHttpxClientWrapper

pytestmark = pytest.mark.filterwarnings(
    "ignore:The .*construct.* method is deprecated:pydantic.warnings.PydanticDeprecatedSince20"
)


@pytest.fixture
def connect(monkeypatch):
    # Keep background telemetry out of the deterministic HTTP transcript.
    monkeypatch.setattr(
        "fireworks.training.sdk._core.lib.internal_client_holder.init_telemetry", lambda *_, **__: None
    )
    monkeypatch.setattr(FiretitanServiceClient, "_resolved_account_id", lambda _: "test")
    resources = []

    def create(route, capabilities, *, weight_sync_status=200):
        prefix = "/training/v1/serverless" if route == "serverless" else "/training/v1/rlorTrainerJobs/test/trainer"
        calls = []
        pending = {}
        models = iter(capabilities)

        def receive(request):
            assert request.url.path.startswith(prefix + "/api/v1/")
            operation = request.url.path.rsplit("/", 1)[-1]
            body = json.loads(request.content) if request.content else {}
            calls.append((operation, body))
            if operation == "create_session":
                # Even a global advertisement cannot enable an older selected trainer.
                return httpx.Response(200, json={"session_id": "ts-test", "comms": "v2"})
            if operation == "create_model":
                index = len(pending)
                request_id = f"run-{index}:fut:create"
                model_id = (
                    f"base-{index}"
                    if body.get("base_only")
                    else f"run-{index}:train:0" if route == "serverless" else f"model-{index}"
                )
                pending[request_id] = {"type": "create_model", "model_id": model_id, **next(models)}
                return httpx.Response(200, json={"request_id": request_id})
            if operation == "forward_backward":
                request_id = f"run-{len(pending)}:fut:fb"
                pending[request_id] = {
                    "loss_fn_output_type": "cross_entropy",
                    "loss_fn_outputs": [{"logprobs": {"data": [-1.0, -2.0], "dtype": "float32"}}],
                    "metrics": {"loss:sum": 3.0},
                }
                return httpx.Response(200, json={"request_id": request_id})
            if operation == "retrieve_future":
                return httpx.Response(200, json=pending[body["request_id"]])
            if operation in ("weight_sync", "save_weights_for_sampler"):
                if operation == "weight_sync" and weight_sync_status != 200:
                    return httpx.Response(weight_sync_status, json={"detail": "weight_sync unavailable"})
                request_id = f"sync-{len(pending)}"
                pending[request_id] = (
                    {"version": "rdma-version", "optimizer_version": 1, "metrics": {}}
                    if operation == "weight_sync"
                    else {"path": body["path"]}
                )
                return httpx.Response(200, json={"request_id": request_id})
            if operation == "unload_model":
                request_id = "unload-test"
                pending[request_id] = {"model_id": body["model_id"], "type": "unload_model"}
                return httpx.Response(200, json={"request_id": request_id})
            if operation == "optim_step":
                request_id = f"optim-{len(pending)}"
                pending[request_id] = {"metrics": {}}
                return httpx.Response(200, json={"request_id": request_id})
            if operation == "weights_info":
                assert route == "serverless", "Dedicated trainers do not serve weights_info"
                return httpx.Response(200, json={"base_model": "test/model", "is_lora": True, "lora_rank": 8})
            if operation == "load_weights":
                request_id = f"run-{len(pending)}:fut:load"
                pending[request_id] = {"type": "load_weights", "path": body["path"]}
                return httpx.Response(200, json={"request_id": request_id})
            if operation == "telemetry":
                return httpx.Response(200, json={"status": "accepted"})
            if operation == "session_heartbeat":
                return httpx.Response(200, json={})
            raise AssertionError(f"Unexpected request: {operation}")

        http_client = AsyncHttpxClientWrapper(transport=httpx.MockTransport(receive))
        service = FiretitanServiceClient(
            api_key="fw-test",
            base_url="https://training.invalid" + prefix,
            http_client=http_client,
            _client_config={"use_pyqwest_transport": False, "parallel_fwdbwd_chunks": True},
            max_retries=0,
        )
        resources.append((service, http_client))
        return service, calls

    yield create
    for service, http_client in resources:
        service.holder.close()
        service.holder.run_coroutine_threadsafe(http_client.aclose()).result(timeout=5)


@pytest.mark.parametrize("route", ["dedicated", "serverless"])
@pytest.mark.parametrize(
    "capability,enabled",
    [
        ({"comms": "v2"}, True),
        ({}, False),
        ({"comms": "v1"}, False),
        ({"comms": "v3"}, False),
        ({"comms": None}, False),
        ({"comms": True}, False),
        ({"comms": {"v2": True}}, False),
    ],
)
def test_negotiation_controls_first_fb_request(connect, route, capability, enabled):
    service, calls = connect(route, [capability])
    client = service.create_training_client("test/model", lora_rank=8 if route == "serverless" else 0)
    assert client.comms == ("v2" if enabled else "v1")
    datum = types.Datum(
        model_input=types.ModelInput.from_ints([1, 2]),
        loss_fn_inputs={
            "target_tokens": types.TensorData(data=[2, 3], dtype="int64"),
            "weights": types.TensorData(data=[1.0, 1.0], dtype="float32"),
        },
    )
    result = client.forward_backward([datum], loss_fn="cross_entropy").result(timeout=5)
    assert result.loss_fn_outputs[0]["logprobs"].data == [-1.0, -2.0]
    training_calls = [(op, body) for op, body in calls if op not in ("telemetry", "session_heartbeat")]
    assert [op for op, _ in training_calls] == [
        "create_session",
        "create_model",
        "retrieve_future",
        "forward_backward",
        "retrieve_future",
    ]
    body = training_calls[3][1]
    assert body.get("comms", "v1") == ("v2" if enabled else "v1")
    assert "experimental" not in body and "streaming" not in body
    if not enabled:
        assert "comms" not in body


@pytest.mark.parametrize("route", ["dedicated", "serverless"])
def test_async_and_reference_models_negotiate_independently(connect, route):
    service, _ = connect(route, [{"comms": "v2"}, {}, {"comms": "v2"}])
    policy = asyncio.run(service.create_lora_training_client_async("test/model", rank=8))
    reference = policy.create_base_training_client("test/model")
    second_reference = service.create_base_training_client("test/model")
    assert policy.comms == "v2"
    assert reference.comms == "v1"
    assert second_reference.comms == "v2"


def test_capability_is_not_shared_between_services(connect):
    new_service, _ = connect("serverless", [{"comms": "v2"}])
    old_service, _ = connect("dedicated", [{}])
    new_client = new_service.create_lora_training_client("test/model", rank=8)
    old_client = old_service.create_training_client("test/model")
    assert new_client.comms == "v2"
    assert old_client.comms == "v1"


@pytest.mark.parametrize("capability,enabled", [({"comms": "v2"}, True), ({}, False)])
@pytest.mark.parametrize(
    "setup_kwargs",
    [{}, {"extra_args": ["--test-flag"], "weight_sync_transport": "RDMA"}],
)
def test_lazy_managed_service_negotiates_after_provisioning(connect, monkeypatch, capability, enabled, setup_kwargs):
    from fireworks.training.sdk import managed

    monkeypatch.setattr(managed, "_build_resource_managers", lambda **_: (object(), object()))
    endpoint = TrainerServiceEndpoint(
        job_name="accounts/test/rlorTrainerJobs/trainer",
        job_id="trainer",
        base_url="https://training.invalid/training/v1/rlorTrainerJobs/test/trainer",
    )
    monkeypatch.setattr(
        managed, "_start_or_reuse_trainer", lambda *_, **__: SimpleNamespace(created=False, job=endpoint)
    )
    monkeypatch.setattr(managed, "_wait_for_started_trainer", lambda *_, **__: endpoint)
    monkeypatch.setattr(managed, "_attach_managed_deployment", lambda *_, **__: (None, None, False, False))
    connections = []

    def connect_ready_trainer(*, base_url, api_key):
        assert base_url == endpoint.base_url and api_key == "fw-test"
        service, calls = connect("dedicated", [capability])
        connections.append(calls)
        return service

    monkeypatch.setattr(managed, "FiretitanServiceClient", connect_ready_trainer)
    service = FiretitanServiceClient.from_firetitan_config(api_key="fw-test", base_model="test/model", **setup_kwargs)
    assert connections == []
    client = service.create_training_client()
    assert client.comms == ("v2" if enabled else "v1")
    assert not client.supports_rdma_weight_sync
    assert len(connections) == 1


@pytest.mark.parametrize("with_optimizer", [False, True])
@pytest.mark.parametrize("use_async", [False, True])
def test_serverless_resume_negotiates_with_new_trainer(connect, with_optimizer, use_async):
    service, calls = connect("serverless", [{"comms": "v2"}])
    method = "create_training_client_from_state"
    if with_optimizer:
        method += "_with_optimizer"
    if use_async:
        method += "_async"
    result = getattr(service, method)("test/run-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/checkpoint")
    client = asyncio.run(result) if use_async else result
    assert client.comms == "v2"
    operations = [op for op, _ in calls if op not in ("telemetry", "session_heartbeat")]
    assert operations == [
        "create_session",
        "weights_info",
        "create_model",
        "retrieve_future",
        "load_weights",
        "retrieve_future",
    ]


def test_old_response_model_accepts_new_capability():
    response = types.CreateModelResponse.model_validate(
        {"model_id": "test", "comms": "v2", "supports_rdma_weight_sync": True}
    )
    assert response.model_id == "test"
    assert not hasattr(response, "comms")
    assert not hasattr(response, "supports_rdma_weight_sync")


def test_capability_does_not_weaken_model_validation(connect):
    service, _ = connect("serverless", [{"model_id": None, "comms": "v2"}])
    with pytest.raises(ValueError, match="model_id"):
        service.create_lora_training_client("test/model", rank=8)


@pytest.mark.parametrize(
    "probe_status,message,restored_binding",
    [
        (200, "", False),
        (400, "Extra inputs are not permitted, field: 'routing_matrix_format', value: 'parquet_v1'", False),
        (400, "Extra inputs are not permitted, field: 'routing_matrix_format'", False),
        (400, "temperature must be between 0 and 2", False),
        (400, "R3 shared storage domain mismatch", False),
        (429, "rate limit", False),
        (500, "internal error", False),
        (200, "", True),
        (400, "Extra inputs are not permitted, field: 'routing_matrix_format', value: 'parquet_v1'", True),
        (400, "Extra inputs are not permitted, field: 'routing_matrix_format'", True),
    ],
)
def test_r3_probe_is_lazy_shared_and_only_unknown_format_falls_back(
    monkeypatch, probe_status, message, restored_binding
):
    from fireworks.training.sdk.sampling import DeploymentSampler

    calls = []
    error = {"error": {"code": "invalid_request_error", "message": message}}
    fallback = probe_status == 400 and message.startswith("Extra inputs are not permitted,")

    async def receive(request):
        body = json.loads(request.content)
        calls.append(body)
        assert request.url.path == "/inference/v1/completions"
        if body.get("stream") is False:
            await asyncio.sleep(0.01)  # All concurrent callers must share this probe.
            assert body["max_tokens"] == 0 and body["echo"] is True
            assert body["logprobs"] is True and "use_new_logprobs" not in body
            assert request.headers["x-fireworks-r3-store-id"] == "nfs-test"
            return httpx.Response(probe_status, json=_r3_probe_result() if probe_status == 200 else error)
        assert body.get("routing_matrix_format") == ("parquet_v1" if probe_status == 200 else None)
        assert bool(body.get("include_routing_matrix")) == (probe_status != 200)
        return httpx.Response(200, text='data: {"choices":[{"text":"ok","finish_reason":"stop"}]}\n\ndata: [DONE]\n\n')

    def unexpected_probe(request):
        raise AssertionError(f"Binding must not call {request.url}")

    monkeypatch.setattr(
        "fireworks.training.sdk._rest_client._make_sync_client",
        lambda _verify: httpx.Client(transport=httpx.MockTransport(unexpected_probe)),
    )
    sampler = DeploymentSampler("https://inference.invalid", "test/model", "fw-test")
    if restored_binding:
        # A sidecar restores the trainer's store before the parent's first R3 request.
        sampler.r3_store_id = "nfs-test"
    else:
        sampler.negotiate_routing_matrix_format("parquet_v1", "nfs-test")
    assert calls == []
    sampler._async_client = httpx.AsyncClient(transport=httpx.MockTransport(receive))

    async def run():
        results = await asyncio.gather(
            *(sampler.async_completions_stream([1, 2], include_routing_matrix=True) for _ in range(256)),
            return_exceptions=True,
        )
        assert len([body for body in calls if body.get("stream") is False]) == 1
        if probe_status == 200 or fallback:
            assert all(not isinstance(result, BaseException) for result in results)
            assert len(calls) == 257
        else:
            assert all(isinstance(result, httpx.HTTPStatusError) for result in results)
            assert len(calls) == 1
        await sampler._async_client.aclose()

    try:
        asyncio.run(run())
    finally:
        sampler.close()


def _r3_probe_result():
    return {
        "choices": [
            {
                "routing_matrix_format": "parquet_v1",
                "r3_store_id": "nfs-test",
                "routing_references": {
                    "length": 2,
                    "files": [
                        {
                            "store_id": "nfs-test",
                            "file_id": "00000000-0000-0000-0000-000000000001",
                            "format": "parquet_v1",
                            "row_count": 2,
                        }
                    ],
                    "spans": [{"input_token_start": 0, "count": 2, "file_index": 0, "file_row_start": 0}],
                },
            }
        ]
    }


@pytest.mark.parametrize(
    "status,message,replay,expects_guidance",
    [
        (400, "Extra inputs are not permitted, field: 'top_sampling_format', value: 'parquet_v1'", True, True),
        (
            400,
            "2 request validation errors: Extra inputs are not permitted, field: 'top_sampling_logprobs', "
            "value: 20000; Extra inputs are not permitted, field: 'top_sampling_format', value: 'parquet_v1'",
            True,
            True,
        ),
        (400, "R3 shared storage domain mismatch", True, False),
        (400, "Extra inputs are not permitted, field: 'other_option', value: 1", True, False),
        (
            429,
            "Extra inputs are not permitted, field: 'top_sampling_format', value: 'parquet_v1'",
            True,
            False,
        ),
        (
            400,
            "Extra inputs are not permitted, field: 'top_sampling_format', value: 'parquet_v1'",
            False,
            False,
        ),
    ],
)
def test_old_serving_sampling_support_error_is_actionable_without_fallback(status, message, replay, expects_guidance):
    from fireworks.training.sdk.sampling import DeploymentSampler

    calls = []

    async def receive(request):
        calls.append(json.loads(request.content))
        return httpx.Response(
            status,
            json={"error": {"code": "invalid_request_error", "message": message}},
            headers={"x-request-id": "unsupported-serving-probe"},
        )

    sampler = DeploymentSampler("https://inference.invalid", "test/model", "fw-test")
    sampler.r3_store_id = "nfs-test"
    sampler._async_client = httpx.AsyncClient(transport=httpx.MockTransport(receive))
    kwargs = {"top_sampling_logprobs": 20000, "top_sampling_format": "parquet_v1"} if replay else {}

    async def run():
        with pytest.raises(httpx.HTTPStatusError) as caught:
            if status == 400:
                await sampler.sample_with_prompt_tokens_result([1, 2], logprobs=True, **kwargs)
            else:
                await sampler.async_completions_stream([1, 2], logprobs=True, **kwargs)
        assert ("use a serving image" in str(caught.value)) == expects_guidance
        assert caught.value.response.status_code == status
        assert caught.value.response.json()["error"]["message"] == message
        if status == 400:
            assert caught.value.attempts == 1
            assert caught.value.server_attempts[0].status_code == 400
            assert caught.value.server_attempts[0].response_request_id == "unsupported-serving-probe"
        assert len(calls) == 1
        assert (calls[0].get("top_sampling_format") == "parquet_v1") == replay
        await sampler._async_client.aclose()

    try:
        asyncio.run(run())
    finally:
        sampler.close()


def test_old_replica_after_successful_probe_retries_inline_once():
    from fireworks.training.sdk.sampling import DeploymentSampler

    calls = []

    async def receive(request):
        body = json.loads(request.content)
        calls.append(body)
        if not body["stream"]:
            return httpx.Response(200, json=_r3_probe_result())
        if "routing_matrix_format" in body:
            return httpx.Response(
                400,
                json={
                    "error": {
                        "code": "invalid_request_error",
                        "message": "Extra inputs are not permitted, field: 'routing_matrix_format', value: 'parquet_v1'",
                    }
                },
            )
        assert body["include_routing_matrix"] is True
        assert "x-fireworks-r3-store-id" not in request.headers
        return httpx.Response(200, text='data: {"choices":[{"finish_reason":"stop"}]}\n\ndata: [DONE]\n\n')

    sampler = DeploymentSampler("https://inference.invalid", "test/model", "fw-test")
    sampler.negotiate_routing_matrix_format("parquet_v1", "nfs-test")
    sampler._async_client = httpx.AsyncClient(transport=httpx.MockTransport(receive))

    async def run():
        for _ in range(2):
            await sampler.async_completions_stream([1, 2], include_routing_matrix=True)
        assert len(calls) == 4  # One probe, one rejected request, two inline requests.
        assert sampler.routing_matrix_format == "base64_inline"
        await sampler._async_client.aclose()

    try:
        asyncio.run(run())
    finally:
        sampler.close()


@pytest.mark.parametrize("comms", ["v1", "v2"])
@pytest.mark.parametrize(
    "inference_new",
    [False, True],
)
@pytest.mark.parametrize("route", ["dedicated", "serverless"])
@pytest.mark.parametrize("use_async", [False, True])
def test_sampler_binding_is_independent_for_reused_deployment(
    connect, monkeypatch, comms, inference_new, route, use_async
):
    from fireworks.training.sdk.sampling import DeploymentSampler

    service, _ = connect(route, [{"comms": comms, "routing_matrix_format": "parquet_v1", "r3_store_id": "nfs-test"}])
    training = service.create_training_client("test/model", lora_rank=8 if route == "serverless" else 0)

    async def receive(request):
        assert request.url.path.endswith("/inference/v1/completions")
        if json.loads(request.content).get("stream") is False:
            return (
                httpx.Response(200, json=_r3_probe_result())
                if inference_new
                else httpx.Response(
                    400,
                    json={
                        "error": {
                            "code": "invalid_request_error",
                            "message": "Extra inputs are not permitted, field: 'routing_matrix_format', value: 'parquet_v1'",
                        }
                    },
                )
            )
        return httpx.Response(200, text='data: {"choices":[{"finish_reason":"stop"}]}\n\ndata: [DONE]\n\n')

    monkeypatch.setattr(
        "fireworks.training.sdk._rest_client._make_async_client",
        lambda _verify: httpx.AsyncClient(transport=httpx.MockTransport(receive)),
    )
    backend = DeploymentSampler("https://inference.invalid", "test/model", "fw-test")
    first = (
        asyncio.run(service.create_sampling_client_async(deployment_sampler=backend, training_client=training))
        if use_async
        else service.create_sampling_client(deployment_sampler=backend, training_client=training)
    )
    old = SimpleNamespace(comms="v2", routing_matrix_format="base64_inline", r3_store_id=None)
    second = service.create_sampling_client(deployment_sampler=backend, training_client=old)
    assert first.deployment_sampler.routing_matrix_format == "base64_inline"
    asyncio.run(first.deployment_sampler.async_completions_stream([1, 2], include_routing_matrix=True))
    enabled = inference_new
    assert first.deployment_sampler.r3_store_id == "nfs-test"
    assert second.deployment_sampler.r3_store_id is None
    assert first.deployment_sampler.routing_matrix_format == ("parquet_v1" if enabled else "base64_inline")
    assert second.deployment_sampler.routing_matrix_format == "base64_inline"
    assert backend.r3_store_id is None
    backend.close()
    second.close()
    assert not first.deployment_sampler._sync_client.is_closed
    asyncio.run(first.deployment_sampler.async_completions_stream([1, 2], include_routing_matrix=True))
    assert first.deployment_sampler.routing_matrix_format == ("parquet_v1" if enabled else "base64_inline")
    first.close()


@pytest.mark.parametrize("route", ["dedicated", "serverless"])
@pytest.mark.parametrize(
    "capability,expected",
    [
        ({"supports_router_replay": True}, True),
        ({"supports_router_replay": False}, False),
        ({}, None),  # older trainer: field absent -> unknown
        ({"supports_router_replay": None}, None),
        ({"supports_router_replay": "yes"}, None),  # malformed -> unknown, not truthy
        ({"supports_router_replay": 1}, None),
    ],
)
def test_router_replay_capability_reaches_training_client(connect, route, capability, expected):
    # The trainer-authoritative R3 on/off signal flows from the create_model
    # response to the training client so callers never need GET model.
    service, _ = connect(route, [capability])
    client = service.create_training_client("test/model", lora_rank=8 if route == "serverless" else 0)
    assert client.supports_router_replay is expected


def test_router_replay_capability_is_independent_of_routing_matrix_format(connect):
    # parquet_v1 is the R3 wire format and is advertised for dense models too;
    # it must never be read as "this model supports Router Replay".
    service, _ = connect(
        "serverless",
        [{"routing_matrix_format": "parquet_v1", "r3_store_id": "nfs-test", "supports_router_replay": False}],
    )
    client = service.create_training_client("test/model", lora_rank=8)
    assert client.routing_matrix_format == "parquet_v1"
    assert client.supports_router_replay is False


def test_old_response_model_accepts_router_replay_capability():
    response = types.CreateModelResponse.model_validate({"model_id": "test", "supports_router_replay": True})
    assert response.model_id == "test"


@pytest.mark.parametrize("lora_rank", [0, 8], ids=["full", "lora"])
@pytest.mark.parametrize("trainer_support", [False, True], ids=["old-trainer", "new-trainer"])
@pytest.mark.parametrize("inference_support", [False, True], ids=["old-inference", "new-inference"])
def test_weight_sync_transport_matrix(connect, lora_rank, trainer_support, inference_support):
    from fireworks.training.sdk.managed import _TinkerSamplerBackend

    # Missing fields reproduce the response of old images, rather than requiring
    # those images to learn how to advertise a negative capability.
    capability = {"supports_rdma_weight_sync": True} if trainer_support else {}
    service, calls = connect("dedicated", [capability])
    client = service.create_training_client("test/model", lora_rank=lora_rank)
    manager = Mock(
        account_id="test",
        api_key="fw-test",
        inference_url="https://inference.invalid",
        hotload_api_url="https://inference.invalid",
    )
    manager._hotload_headers.return_value = {}
    replica = {"supports_rdma_weight_sync": True} if inference_support else {}
    manager.hotload_check_status.return_value = {"replicas": [replica]}
    manager.hotload_and_wait.return_value = True
    if (lora_rank == 0 and trainer_support != inference_support) or (lora_rank != 0 and trainer_support):
        with pytest.raises(RuntimeError, match="FILE fallback is not allowed"):
            client._attach_sampler_backend(
                _TinkerSamplerBackend(manager, "rollout", "test/model", lora_rank=lora_rank)
            )
        assert not any(op in ("weight_sync", "save_weights_for_sampler") for op, _ in calls)
        manager.hotload_and_wait.assert_not_called()
        return
    client._attach_sampler_backend(_TinkerSamplerBackend(manager, "rollout", "test/model", lora_rank=lora_rank))

    expected_rdma = lora_rank == 0 and trainer_support and inference_support
    assert client.supports_rdma_weight_sync is expected_rdma
    result = client.weight_sync().result(timeout=5)
    submitted = [op for op, _ in calls if op in ("weight_sync", "save_weights_for_sampler")]
    assert submitted == (["weight_sync"] if expected_rdma else ["save_weights_for_sampler"])
    assert manager.hotload_and_wait.call_count == (0 if expected_rdma else 1)
    assert (result.optimizer_version is not None) is expected_rdma
    assert manager.hotload_check_status.call_count == (2 if lora_rank == 0 else 0)


def _weight_sync_client(connect, *, weight_sync_status=200, rdma=True):
    from fireworks.training.sdk.managed import _TinkerSamplerBackend

    service, calls = connect("dedicated", [{"supports_rdma_weight_sync": rdma}], weight_sync_status=weight_sync_status)
    client = service.create_training_client("test/model")
    manager = Mock(account_id="test", hotload_api_url="https://inference.invalid")
    manager._hotload_headers.return_value = {}
    manager.hotload_check_status.return_value = {"replicas": [{"supports_rdma_weight_sync": rdma}]}
    manager.hotload_and_wait.return_value = True
    client._attach_sampler_backend(_TinkerSamplerBackend(manager, "rollout", "test/model"))
    return client, manager, calls


@pytest.mark.parametrize("replicas", [[], [{}], [{"supports_rdma_weight_sync": True}, {}]])
@pytest.mark.parametrize("use_async", [False, True])
def test_weight_sync_rejects_capability_mismatch_before_file(connect, replicas, use_async):
    client, manager, calls = _weight_sync_client(connect)
    assert client.weight_sync().result(timeout=5).optimizer_version is not None
    calls.clear()
    manager.hotload_check_status.return_value = {"replicas": replicas}
    future = asyncio.run(client.weight_sync_async()) if use_async else client.weight_sync()
    optimizer = client.optim_step(types.AdamParams())
    with pytest.raises(RuntimeError, match="FILE fallback is not allowed"):
        future.result(timeout=5)
    optimizer.result(timeout=5)
    assert not any(op in ("weight_sync", "save_weights_for_sampler") for op, _ in calls)
    manager.hotload_and_wait.assert_not_called()
    manager.hotload_check_status.return_value = {"replicas": [{"supports_rdma_weight_sync": True}]}
    assert client.weight_sync().result(timeout=5).optimizer_version is not None


def test_prior_rdma_selection_never_downgrades_to_file(connect):
    client, manager, calls = _weight_sync_client(connect)
    assert client.weight_sync().result(timeout=5).optimizer_version is not None
    client._trainer_supports_rdma_weight_sync = False
    manager.hotload_check_status.return_value = {"replicas": [{}]}
    with pytest.raises(RuntimeError, match="FILE fallback is not allowed"):
        client.weight_sync().result(timeout=5)
    assert [op for op, _ in calls if op in ("weight_sync", "save_weights_for_sampler")] == ["weight_sync"]
    manager.hotload_and_wait.assert_not_called()


@pytest.mark.parametrize("blocked_stage", ["status", "hotload"])
@pytest.mark.parametrize("use_async", [False, True])
def test_file_fallback_future_covers_probe_hotload_and_preserves_training_order(connect, blocked_stage, use_async):
    from threading import Event

    client, manager, calls = _weight_sync_client(connect, rdma=False)
    entered, release = Event(), Event()

    def blocked(*args, **kwargs):
        entered.set()
        assert release.wait(timeout=5)
        return {"replicas": [{}]} if blocked_stage == "status" else True

    manager.hotload_check_status.return_value = {"replicas": [{}]}
    getattr(manager, "hotload_check_status" if blocked_stage == "status" else "hotload_and_wait").side_effect = blocked
    future = asyncio.run(client.weight_sync_async()) if use_async else client.weight_sync()
    try:
        assert entered.wait(timeout=3)
        with pytest.raises(TimeoutError):
            future.result(timeout=0.01)
        optimizer = client.optim_step(types.AdamParams())
        assert not any(op == "optim_step" for op, _ in calls)
    finally:
        release.set()
    assert future.result(timeout=5).optimizer_version is None
    optimizer.result(timeout=5)
    operations = [(op, body) for op, body in calls if op in ("save_weights_for_sampler", "optim_step")]
    assert [op for op, _ in operations] == ["save_weights_for_sampler", "optim_step"]
    assert operations[1][1]["seq_id"] == operations[0][1]["seq_id"] + 1


@pytest.mark.parametrize("status", [404, 405])
def test_missing_trainer_weight_sync_route_errors_without_file(connect, status):
    client, manager, calls = _weight_sync_client(connect, weight_sync_status=status)
    for _ in range(2):
        with pytest.raises(RuntimeError, match="trainer RDMA API is unavailable"):
            client.weight_sync().result(timeout=5)
    assert [op for op, _ in calls if op in ("weight_sync", "save_weights_for_sampler")] == [
        "weight_sync",
        "weight_sync",
    ]
    manager.hotload_and_wait.assert_not_called()


@pytest.mark.parametrize("use_async", [False, True])
def test_rdma_allows_later_training_submission_before_publication_completes(connect, monkeypatch, use_async):
    from threading import Event

    from fireworks.training.sdk import client as client_module

    client, manager, calls = _weight_sync_client(connect)
    entered, release = Event(), Event()
    api_future = client_module._APIFuture

    async def pending_publication(*args, **kwargs):
        if kwargs["request_type"] == "WeightSync":
            entered.set()
            assert await asyncio.to_thread(release.wait, 5)
        return await api_future(*args, **kwargs)

    monkeypatch.setattr(client_module, "_APIFuture", pending_publication)
    publication = asyncio.run(client.weight_sync_async()) if use_async else client.weight_sync()
    try:
        assert entered.wait(timeout=3)
        client.optim_step(types.AdamParams()).result(timeout=3)
        with pytest.raises(TimeoutError):
            publication.result(timeout=0.01)
        operations = [(op, body) for op, body in calls if op in ("weight_sync", "optim_step")]
        assert [op for op, _ in operations] == ["weight_sync", "optim_step"]
        assert operations[1][1]["seq_id"] == operations[0][1]["seq_id"] + 1
    finally:
        release.set()
    assert publication.result(timeout=5).optimizer_version == 1
    manager.hotload_and_wait.assert_not_called()


def test_accepted_rdma_failure_does_not_trigger_file_retry(connect, monkeypatch):
    client, manager, calls = _weight_sync_client(connect)

    async def failed_future(*args, **kwargs):
        raise ValueError("accepted publication failed")

    monkeypatch.setattr("fireworks.training.sdk.client._APIFuture", failed_future)
    with pytest.raises(ValueError, match="accepted publication failed"):
        client.weight_sync().result(timeout=5)
    assert [op for op, _ in calls if op in ("weight_sync", "save_weights_for_sampler")] == ["weight_sync"]
    manager.hotload_and_wait.assert_not_called()


def test_failed_capability_refresh_does_not_block_later_operations(connect):
    client, manager, calls = _weight_sync_client(connect)
    manager.hotload_check_status.side_effect = httpx.ConnectError("status unavailable")
    sync = client.weight_sync()
    optimizer = client.optim_step(types.AdamParams())
    with pytest.raises(httpx.ConnectError, match="status unavailable"):
        sync.result(timeout=5)
    optimizer.result(timeout=5)
    assert not any(op in ("weight_sync", "save_weights_for_sampler") for op, _ in calls)
    manager.hotload_and_wait.assert_not_called()


def test_rdma_keeps_explicit_checkpoint_exports_available(connect):
    client, manager, calls = _weight_sync_client(connect)
    for name, checkpoint_type in (("base", "base"), ("delta", "delta")):
        assert client.save_weights_for_sampler(name, checkpoint_type=checkpoint_type).result(timeout=5).path
    assert [op for op, _ in calls if op == "weight_sync"] == []
    manager.hotload_and_wait.assert_not_called()


@pytest.mark.parametrize("value", [None, False, "true", 1, "rdma_v2", {}, []])
def test_unknown_rdma_advertisements_keep_file_transport(connect, value):
    service, _ = connect("dedicated", [{"supports_rdma_weight_sync": value}])
    client = service.create_training_client("test/model")
    assert client._trainer_supports_rdma_weight_sync is False


@pytest.mark.parametrize(
    "replicas",
    [[], [{}], [{"supports_rdma_weight_sync": "true"}], [{"supports_rdma_weight_sync": True}, {}]],
)
def test_every_inference_replica_must_advertise_rdma(connect, replicas):
    from fireworks.training.sdk.managed import _TinkerSamplerBackend

    service, _ = connect("dedicated", [{"supports_rdma_weight_sync": True}])
    client = service.create_training_client("test/model")
    manager = Mock()
    manager.hotload_check_status.return_value = {"replicas": replicas}
    with pytest.raises(RuntimeError, match="FILE fallback is not allowed"):
        client._attach_sampler_backend(_TinkerSamplerBackend(manager, "rollout", "test/model"))
    assert client.supports_rdma_weight_sync is False


@pytest.mark.parametrize("trainer_support", [False, True])
def test_mixed_rollout_capabilities_reject_for_either_trainer_capability(connect, trainer_support):
    from fireworks.training.sdk.managed import _TinkerSamplerBackend

    service, calls = connect("dedicated", [{"supports_rdma_weight_sync": trainer_support}])
    client = service.create_training_client("test/model")
    manager = Mock()
    manager.hotload_check_status.return_value = {
        "replicas": [{"supports_rdma_weight_sync": True}, {"supports_rdma_weight_sync": False}]
    }
    with pytest.raises(RuntimeError, match="FILE fallback is not allowed"):
        client._attach_sampler_backend(_TinkerSamplerBackend(manager, "rollout", "test/model"))
    assert not any(op in ("weight_sync", "save_weights_for_sampler") for op, _ in calls)
    manager.hotload_and_wait.assert_not_called()


@pytest.mark.parametrize("regions", [["US_MINNESOTA_1"], ["US_MINNESOTA_1", "US_OHIO_1"]])
def test_shard_fanout_rejects_enabled_rdma(connect, regions):
    from fireworks.training.sdk.managed import _TinkerSamplerBackend

    service, calls = connect("dedicated", [{"supports_rdma_weight_sync": True}])
    client = service.create_training_client("test/model")
    manager = Mock()
    manager.hotload_and_wait.return_value = True
    # Shape of aggregateHotLoadStatus's real gateway response. A single
    # responding shard also needs FILE; other shard responses may be missing.
    manager.hotload_check_status.return_value = {
        "replicas": [{"region": region, "supports_rdma_weight_sync": True} for region in regions],
        "replica_distribution": {region: 1 for region in regions},
    }
    with pytest.raises(RuntimeError, match="FILE fallback is not allowed"):
        client._attach_sampler_backend(_TinkerSamplerBackend(manager, "rollout", "test/model"))
    assert not any(op in ("weight_sync", "save_weights_for_sampler") for op, _ in calls)
    manager.hotload_and_wait.assert_not_called()


def test_rdma_negotiation_does_not_hide_status_failures(connect):
    from fireworks.training.sdk.managed import _TinkerSamplerBackend

    service, _ = connect("dedicated", [{"supports_rdma_weight_sync": True}])
    client = service.create_training_client("test/model")
    manager = Mock()
    manager.hotload_check_status.side_effect = httpx.ConnectError("unavailable")
    with pytest.raises(httpx.ConnectError):
        client._attach_sampler_backend(_TinkerSamplerBackend(manager, "rollout", "test/model"))


@pytest.mark.parametrize(
    "trainer_enabled,rollout_enabled", [(True, True), (True, False), (False, True), (False, False)]
)
@pytest.mark.parametrize("supported", [False, True])
def test_configured_rdma_flags_are_enforced_even_before_first_sync(
    connect, trainer_enabled, rollout_enabled, supported
):
    from fireworks.training.sdk.managed import _TinkerSamplerBackend

    service, calls = connect(
        "dedicated",
        [
            {
                "rdma_weight_sync_enabled": trainer_enabled,
                "supports_rdma_weight_sync": supported,
            }
        ],
    )
    client = service.create_training_client("test/model")
    assert client._trainer_rdma_weight_sync_enabled is trainer_enabled
    manager = Mock(account_id="test", hotload_api_url="https://inference.invalid")
    manager._hotload_headers.return_value = {}
    manager.hotload_check_status.return_value = {
        "replicas": [
            {
                "rdma_weight_sync_enabled": rollout_enabled,
                "supports_rdma_weight_sync": supported,
            }
        ]
    }
    backend = _TinkerSamplerBackend(manager, "rollout", "test/model")
    if trainer_enabled and rollout_enabled and supported:
        client._attach_sampler_backend(backend)
        assert client.weight_sync().result(timeout=5).optimizer_version is not None
    elif not trainer_enabled and not rollout_enabled and not supported:
        manager.hotload_and_wait.return_value = True
        client._attach_sampler_backend(backend)
        assert client.weight_sync().result(timeout=5).optimizer_version is None
        manager.hotload_and_wait.assert_called_once()
        return
    else:
        with pytest.raises(RuntimeError, match="FILE fallback is not allowed"):
            client._attach_sampler_backend(backend)
        assert not any(op in ("weight_sync", "save_weights_for_sampler") for op, _ in calls)
    manager.hotload_and_wait.assert_not_called()


def test_decision_calibration_rides_on_sampler_save_only(connect):
    calibration = DecisionCalibration(temperature={"choice": 1.3, "noul": 1.1}, fit_rows={"choice": 400})
    service, calls = connect("serverless", [{}])
    client = service.create_lora_training_client("test/model", rank=8)
    client.save_weights_for_sampler_ext("final", metadata=SamplerCheckpointMetadata(decision_calibration=calibration))
    bodies = dict(calls)
    assert "decision" not in bodies["create_model"]
    assert bodies["save_weights_for_sampler"]["metadata"] == {
        "decision_calibration": calibration.model_dump(mode="json")
    }


def test_public_close_stops_session_heartbeat(connect):
    service, _ = connect("dedicated", [{}])
    holder = service.holder
    task = holder._session_heartbeat_task
    assert task is not None and not task.done()
    service.close()
    service.close()
    holder.run_coroutine_threadsafe(asyncio.sleep(0)).result(timeout=5)
    assert holder._closed
    assert task.done()


def test_public_close_flushes_queued_telemetry(connect, monkeypatch):
    from fireworks.training.sdk._core.lib.telemetry import Telemetry

    monkeypatch.setattr("fireworks.training.sdk._core.lib.telemetry.FLUSH_INTERVAL", 3600)
    service, calls = connect("dedicated", [{}])
    holder = service.holder
    telemetry = holder._telemetry = Telemetry(holder, "ts-test")
    holder.run_coroutine_threadsafe(asyncio.sleep(0)).result(timeout=5)
    telemetry.log("queued-before-close", {"count": 1})
    service.close()
    events = [event for operation, body in calls if operation == "telemetry" for event in body["events"]]
    assert any(event.get("event_name") == "queued-before-close" for event in events)
    assert telemetry._flush_counter == telemetry._push_counter


def test_public_close_on_holder_loop_does_not_wait_for_itself(connect):
    from fireworks.training.sdk._core.lib.telemetry import Telemetry

    service, _ = connect("dedicated", [{}])
    holder = service.holder
    telemetry = holder._telemetry = Telemetry(holder, "ts-test")
    wait = Mock(wraps=telemetry._wait_until_drained_sync)
    telemetry._wait_until_drained_sync = wait

    async def close():
        service.close()
        assert telemetry._task is not None
        await asyncio.wait_for(asyncio.gather(telemetry._task, return_exceptions=True), timeout=1)

    holder.run_coroutine_threadsafe(close()).result(timeout=2)
    wait.assert_not_called()
    assert telemetry._task.done()


def test_public_unload_model_keeps_native_request_and_future_contract(connect):
    service, calls = connect("dedicated", [{}])
    client = service.create_training_client("test/model", lora_rank=8)
    response = client.unload_model().result(timeout=5)
    assert response.model_id == client._guaranteed_model_id()
    assert ("unload_model", {"model_id": response.model_id, "type": "unload_model"}) in calls


@pytest.mark.parametrize("with_optimizer", [False, True])
@pytest.mark.parametrize("use_async", [False, True])
def test_direct_dedicated_resume_requires_explicit_configuration(connect, with_optimizer, use_async):
    service, calls = connect("dedicated", [])
    before = list(calls)
    method = "create_training_client_from_state"
    if with_optimizer:
        method += "_with_optimizer"
    if use_async:
        method += "_async"
    with pytest.raises(NotImplementedError, match="serverless"):
        result = getattr(service, method)("test/run-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/checkpoint")
        if use_async:
            asyncio.run(result)
    assert calls == before


@pytest.mark.parametrize("route", ["dedicated", "serverless"])
@pytest.mark.parametrize("ttl", [0, 60])
@pytest.mark.parametrize(
    "method",
    [
        "save_state",
        "save_state_async",
        "save_weights_for_sampler",
        "save_weights_for_sampler_async",
        "save_weights_for_sampler_ext",
    ],
)
def test_unsupported_checkpoint_ttl_does_not_submit_or_consume_sequence(connect, route, ttl, method):
    service, calls = connect(route, [{}])
    client = service.create_lora_training_client("test/model", rank=8)
    before = list(calls)
    with pytest.raises(NotImplementedError, match="ttl_seconds"):
        result = getattr(client, method)("checkpoint", ttl_seconds=ttl)
        if method.endswith("_async"):
            asyncio.run(result)
    assert calls == before
    client.optim_step(types.AdamParams()).result(timeout=5)
    body = next(body for operation, body in calls if operation == "optim_step")
    assert body["seq_id"] == 1


def test_tinker_project_environment_is_not_applied(connect, monkeypatch):
    monkeypatch.setenv("TINKER_PROJECT_ID", "foreign-project")
    _, calls = connect("serverless", [])
    body = next(body for operation, body in calls if operation == "create_session")
    assert body.get("project_id") is None


@pytest.mark.parametrize("managed", [False, True])
def test_project_assignment_is_rejected_before_session_creation(monkeypatch, managed):
    def unexpected_session(*args, **kwargs):
        raise AssertionError("Unsupported project assignment must not create a session")

    monkeypatch.setattr(
        "fireworks.training.sdk._core.lib.public_interfaces.service_client.InternalClientHolder", unexpected_session
    )
    with pytest.raises(NotImplementedError, match="project assignment"):
        if managed:
            FiretitanServiceClient.from_firetitan_config(
                api_key="fw-test", base_model="test/model", project_id="unsupported-project"
            )
        else:
            FiretitanServiceClient(api_key="fw-test", project_id="unsupported-project")
