"""Negotiate through real Tinker session/model/F/B HTTP resource calls."""

import json
import asyncio
from types import SimpleNamespace

import httpx
import pytest
from tinker import types
from tinker._base_client import AsyncHttpxClientWrapper

from fireworks.training.sdk.client import FiretitanServiceClient
from fireworks.training.sdk.trainer import TrainerServiceEndpoint

pytestmark = pytest.mark.filterwarnings(
    "ignore:The .*construct.* method is deprecated:pydantic.warnings.PydanticDeprecatedSince20"
)


@pytest.fixture
def connect(monkeypatch):
    # Keep background telemetry out of the deterministic HTTP transcript.
    monkeypatch.setattr("tinker.lib.internal_client_holder.init_telemetry", lambda *_, **__: None)
    monkeypatch.setattr(FiretitanServiceClient, "_resolved_account_id", lambda _: "test")
    resources = []

    def create(route, capabilities):
        prefix = (
            "/training/v1/serverless"
            if route == "serverless"
            else "/training/v1/rlorTrainerJobs/test/trainer"
        )
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
                model_id = f"base-{index}" if body.get("base_only") else f"run-{index}:train:0"
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
            if operation == "weights_info":
                return httpx.Response(200, json={"base_model": "test/model", "is_lora": True, "lora_rank": 8})
            if operation == "load_weights":
                request_id = f"run-{len(pending)}:fut:load"
                pending[request_id] = {"type": "load_weights", "path": body["path"]}
                return httpx.Response(200, json={"request_id": request_id})
            if operation in ("session_heartbeat", "telemetry"):
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
def test_lazy_managed_service_negotiates_after_provisioning(connect, monkeypatch, capability, enabled):
    from fireworks.training.sdk import managed

    monkeypatch.setattr(managed, "_build_resource_managers", lambda **_: (object(), object()))
    endpoint = TrainerServiceEndpoint(
        job_name="accounts/test/rlorTrainerJobs/trainer",
        job_id="trainer",
        base_url="https://training.invalid/training/v1/rlorTrainerJobs/test/trainer",
    )
    monkeypatch.setattr(managed, "_start_or_reuse_trainer", lambda *_, **__: SimpleNamespace(created=False, job=endpoint))
    monkeypatch.setattr(managed, "_wait_for_started_trainer", lambda *_, **__: endpoint)
    monkeypatch.setattr(managed, "_attach_managed_deployment", lambda *_, **__: (None, None, False, False))
    connections = []

    def connect_ready_trainer(*, base_url, api_key):
        assert base_url == endpoint.base_url and api_key == "fw-test"
        service, calls = connect("dedicated", [capability])
        connections.append(calls)
        return service

    monkeypatch.setattr(managed, "FiretitanServiceClient", connect_ready_trainer)
    service = FiretitanServiceClient.from_firetitan_config(api_key="fw-test", base_model="test/model")
    assert connections == []
    client = service.create_training_client()
    assert client.comms == ("v2" if enabled else "v1")
    assert len(connections) == 1


@pytest.mark.parametrize("route", ["dedicated", "serverless"])
@pytest.mark.parametrize("with_optimizer", [False, True])
@pytest.mark.parametrize("use_async", [False, True])
def test_resume_negotiates_with_new_trainer(connect, route, with_optimizer, use_async):
    service, calls = connect(route, [{"comms": "v2"}])
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
    response = types.CreateModelResponse.model_validate({"model_id": "test", "comms": "v2"})
    assert response.model_id == "test"
    assert not hasattr(response, "comms")


def test_capability_does_not_weaken_model_validation(connect):
    service, _ = connect("serverless", [{"model_id": None, "comms": "v2"}])
    with pytest.raises(ValueError, match="model_id"):
        service.create_lora_training_client("test/model", rank=8)


@pytest.mark.parametrize(
    "probe_status,message,restored_binding",
    [
        (200, "", False),
        (400, "Extra inputs are not permitted, field: 'routing_matrix_format', value: 'parquet_v1'", False),
        (400, "temperature must be between 0 and 2", False),
        (400, "R3 shared storage domain mismatch", False),
        (429, "rate limit", False),
        (500, "internal error", False),
        (200, "", True),
        (400, "Extra inputs are not permitted, field: 'routing_matrix_format', value: 'parquet_v1'", True),
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
