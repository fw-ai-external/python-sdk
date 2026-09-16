"""Exercise the actual resource conversion and HTTP wire format for every send path."""

import json
from types import SimpleNamespace
from contextlib import nullcontext

import httpx
import pytest
from tinker import types
from tinker._client import AsyncTinker
from tinker._base_client import AsyncHttpxClientWrapper
from tinker.types.client_config_response import ClientConfigResponse

from fireworks.training.sdk._comms import get_comms
from fireworks.training.sdk.client import FiretitanServiceClient, FiretitanTrainingClient

# Tinker's response decoder still calls Pydantic's deprecated construct().
pytestmark = pytest.mark.filterwarnings(
    "ignore:The .*construct.* method is deprecated:pydantic.warnings.PydanticDeprecatedSince20"
)


def test_managed_service_leaves_negotiation_to_each_model(monkeypatch):
    service = FiretitanServiceClient.from_firetitan_config(
        api_key="fw-test", base_model="accounts/test/models/base",
    )
    assert not hasattr(service, "holder")
    received = []

    def provision(**kwargs):
        received.append(kwargs)
        return SimpleNamespace(sampler_backend=None, reference_handle=None)

    monkeypatch.setattr("fireworks.training.sdk.managed._create_managed_tinker_client", provision)
    service._ensure_managed_handle()
    assert "comms" not in received[0]
    assert not hasattr(received[0]["config"], "comms")


@pytest.mark.parametrize("value", [True, "v3", None])
def test_training_client_rejects_unknown_comms(value):
    with pytest.raises(ValueError, match="comms must be"):
        FiretitanTrainingClient(None, 0, "model", comms=value)


@pytest.mark.asyncio
@pytest.mark.parametrize("operation", ["forward", "backward", "embedding_forward", "embedding_backward", "contrastive"])
@pytest.mark.parametrize("comms", ["v1", "v2"])
async def test_sdk_marks_only_comms_training_requests(operation, comms, monkeypatch):
    bodies = []

    def receive(request):
        bodies.append(json.loads(request.content))
        if len(bodies) == 1:
            return httpx.Response(503, headers={"retry-after-ms": "1"}, json={"error": "retry"})
        return httpx.Response(200, json={"request_id": "future"})

    async def execute(send, *args):
        return await send(*args)

    async with AsyncTinker(
        api_key="tml-test",
        base_url="https://trainer.invalid",
        max_retries=1,
        http_client=AsyncHttpxClientWrapper(transport=httpx.MockTransport(receive)),
        _client_config=ClientConfigResponse(proto_write_fwdbwd=False, use_pyqwest_transport=False),
    ) as resource:
        holder = SimpleNamespace(aclient=lambda _: nullcontext(resource), execute_with_retries=execute)
        client = FiretitanTrainingClient(holder, 0, "model", comms=comms)
        monkeypatch.setattr("fireworks.training.sdk.client._APIFuture", lambda _cls, _holder, value, **_: value)
        monkeypatch.setattr("fireworks.training.sdk.client.CommsV2APIFuture", lambda _cls, _holder, value, **_: value)
        datum = types.Datum(
            model_input=types.ModelInput.from_ints([1, 2]),
            loss_fn_inputs={"weights": types.TensorData(data=[0.25, -0.0], dtype="float32", shape=[2])},
        )
        if operation == "forward":
            await client._send_single_forward_request(0, [datum], "cross_entropy", None)
        elif operation == "backward":
            await client._send_single_forward_backward_request(0, [datum], "cross_entropy", None)
        elif operation == "embedding_forward":
            await client._send_single_forward_embedding_request(0, [datum], "last", "embedding")
        elif operation == "embedding_backward":
            await client._send_single_forward_backward_embedding_request(0, [datum], "last", "embedding")
        else:
            await client.forward_backward_contrastive_async([datum, datum], num_queries=1, temperature=0.05)

        assert len(bodies) == 2
        assert all(body == bodies[0] for body in bodies)
        body = bodies[0]
        if comms == "v2":
            assert body["comms"] == "v2"
        else:
            assert "comms" not in body
        assert body["model_id"] == "model" and body["seq_id"] == 1
        inputs = body.get("forward_input", body.get("forward_backward_input"))
        assert inputs["data"][0]["model_input"]["chunks"][0]["tokens"] == [1, 2]
        assert inputs["data"][0]["loss_fn_inputs"]["weights"] == {
            "data": [0.25, -0.0],
            "dtype": "float32",
            "shape": [2],
        }
        if operation.startswith("embedding"):
            assert inputs["loss_fn_config"] == {"output": "embedding", "pooling": "last"}
        elif operation == "contrastive":
            assert inputs["loss_fn_config"]["output"] == "contrastive_loss"
            assert inputs["loss_fn_config"]["num_queries"] == 1
        assert get_comms() == "v1"

        # An unrelated native client sharing this resource keeps its original wire contract.
        await resource.training.forward(
            request=types.ForwardRequest(
                model_id="native",
                seq_id=1,
                forward_input=types.ForwardBackwardInput(data=[datum], loss_fn="cross_entropy"),
            )
        )
        assert "comms" not in bodies[-1]
