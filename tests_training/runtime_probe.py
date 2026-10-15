"""Run against either source checkout; no GPU or external service required."""

import json
import time
import asyncio
import inspect
import argparse
import cProfile
import importlib
import statistics
from types import SimpleNamespace
from typing import Any
from pathlib import Path
from contextlib import AsyncExitStack
from unittest.mock import patch

import httpx
import numpy as np

from fireworks.training.sdk import client as sdk_client
from fireworks.training.sdk._comms import comms_context

runtime = sdk_client.ServiceClient.__module__.split(".lib.public_interfaces")[0]
base = importlib.import_module(runtime + "._base_client")
futures = importlib.import_module(runtime + ".lib.api_future_impl")
holder_module = importlib.import_module(runtime + ".lib.internal_client_holder")
types = sdk_client.types


def shape(cls: type) -> dict[str, Any]:
    methods = {}
    for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
        if name.startswith("_"):
            continue
        sig = inspect.signature(method)
        methods[name] = {
            "async": inspect.iscoroutinefunction(method),
            "params": [[p.name, str(p.kind), str(p.default)] for p in sig.parameters.values()],
        }
    return methods


def wire_probe(route: str, comms: str) -> list[dict[str, Any]]:
    prefix = "/training/v1/serverless" if route == "serverless" else "/training/v1/rlorTrainerJobs/test/trainer"
    calls = []
    pending = {}

    def receive(request: httpx.Request) -> httpx.Response:
        op = request.url.path.rsplit("/", 1)[-1]
        body = json.loads(request.content) if request.content else {}
        calls.append(
            {
                "operation": op,
                "body": body,
                "content_type": request.headers.get("content-type"),
                "accept": request.headers.get("accept"),
            }
        )
        if op == "create_session":
            return httpx.Response(200, json={"session_id": "ts-fixed"})
        if op == "retrieve_future":
            return httpx.Response(200, json=pending[body["request_id"]])
        result_id = "result-" + str(len(pending))
        if op == "create_model":
            result = {"model_id": "run-fixed:train:0" if route == "serverless" else "model-fixed", "comms": comms}
        elif op in ("forward", "forward_backward"):
            result = {
                "loss_fn_output_type": "ppo",
                "loss_fn_outputs": [{"logprobs": {"data": [-1.25, -0.0], "dtype": "float32"}}],
                "metrics": {"loss:sum": 1.25},
            }
        elif op == "optim_step":
            result = {"metrics": {"step_id:last": 1.0}}
        elif op == "save_weights":
            result = {"path": body["path"]}
        elif op == "load_weights":
            result = {"type": "load_weights", "path": body["path"]}
        elif op == "save_weights_for_sampler":
            result = {"path": body["path"]}
        elif op in ("session_heartbeat", "telemetry"):
            return httpx.Response(200, json={})
        else:
            raise AssertionError(op)
        pending[result_id] = result
        return httpx.Response(200, json={"request_id": result_id})

    http_client = base.AsyncHttpxClientWrapper(transport=httpx.MockTransport(receive))
    with patch.object(holder_module, "init_telemetry", return_value=None):
        service = sdk_client.FiretitanServiceClient(
            api_key="fw-test",
            base_url="https://trainer.invalid" + prefix,
            http_client=http_client,
            _client_config={"use_pyqwest_transport": False, "parallel_fwdbwd_chunks": True},
            max_retries=0,
        )
    service._resolved_account_id = lambda: "test"
    try:
        client = service.create_training_client(base_model="test/model", lora_rank=8, seed=42)
        client.session_id = "deadbeef"
        datum = types.Datum(
            model_input=types.ModelInput.from_ints([1, 2], routing_matrices=["", "matrix"]),
            loss_fn_inputs={
                "target_tokens": np.array([2, 3], dtype=np.int64),
                "weights": np.array([0.25, -0.0], dtype=np.float32),
                "logprobs": np.array([-1.25, -2.5], dtype=np.float32),
                "advantages": np.array([0.5, 1.0], dtype=np.float32),
            },
        )
        config = {"clip_eps": 0.2, "target_logprob_support": "full_vocabulary", "use_unbiased_estimator": True}
        client.forward([datum], "ppo", config).result(timeout=5)
        client.forward_backward([datum], "ppo", config).result(timeout=5)
        client.optim_step(types.AdamParams(learning_rate=1e-5, emit_grad_norm_metrics="detailed")).result(timeout=5)
        client.save_state("state", timeout=5).result(timeout=5)
        client.load_state("state").result(timeout=5)
        client.save_weights_for_sampler_ext("sampler", checkpoint_type="base")
    finally:
        service.holder.close()
        service.holder.run_coroutine_threadsafe(http_client.aclose()).result(timeout=5)
    return [call for call in calls if call["operation"] not in ("session_heartbeat", "telemetry")]


def codec_probe(output: Path) -> dict[str, Any]:
    rng = np.random.default_rng(42)
    inputs = []
    for _ in range(16):
        inputs.append(
            types.Datum(
                model_input=types.ModelInput.from_ints(rng.integers(0, 32000, size=8192).tolist()),
                loss_fn_inputs={
                    "target_tokens": rng.integers(0, 32000, size=8192, dtype=np.int64),
                    "logprobs": rng.normal(size=8192).astype(np.float32),
                    "advantages": rng.normal(size=8192).astype(np.float32),
                    "weights": np.ones(8192, dtype=np.float32),
                },
            )
        )
    request = types.ForwardBackwardInput(data=inputs, loss_fn="ppo")
    wrapper = base.AsyncHttpxClientWrapper()
    raw = {
        "loss_fn_output_type": "ppo",
        "loss_fn_outputs": [
            {"logprobs": {"data": inputs[0].loss_fn_inputs["logprobs"].data, "dtype": "float32"}} for _ in range(16)
        ],
        "metrics": {"loss:sum": 1.0},
    }

    async def decode() -> Any:
        future = object.__new__(sdk_client.CommsV2APIFuture)
        future.model_cls = types.ForwardBackwardOutput
        future.untyped_future = SimpleNamespace(request_id="codec")
        future.get_telemetry = lambda: None
        async with AsyncExitStack() as stack:
            return await future._handle_outcome(
                futures._SuccessJson(result_dict=raw), futures._LoopState(), stack, 1, 0.0
            )

    samples = []
    trace = []
    profile = cProfile.Profile()
    for iteration in range(12):
        timings = []
        with comms_context("v2"):
            start = time.perf_counter_ns()
            converted = sdk_client._serialize_input_for_extra_body(request)
            mid = time.perf_counter_ns()
            body = wrapper.build_request(
                "POST",
                "https://trainer.invalid/api/v1/forward_backward",
                json={"forward_backward_input": converted, "model_id": "model", "seq_id": 1},
            ).content
            encoded = time.perf_counter_ns()
            result = asyncio.run(decode())
            end = time.perf_counter_ns()
        timings = [(mid - start) / 1e6, (encoded - mid) / 1e6, (end - encoded) / 1e6]
        if iteration >= 3:
            samples.append(timings)
        if iteration == 11:
            trace = [
                {"name": name, "ph": "X", "pid": 1, "tid": 1, "ts": (s - start) / 1000, "dur": (e - s) / 1000}
                for name, s, e in [
                    ("validate + dictionary", start, mid),
                    ("JSON encode", mid, encoded),
                    ("result validation + arrays", encoded, end),
                ]
            ]
        assert (
            result.loss_fn_outputs[0]["logprobs"].to_numpy().tobytes()
            == inputs[0].loss_fn_inputs["logprobs"].to_numpy().tobytes()
        )
    with comms_context("v2"):
        profile.enable()
        converted = sdk_client._serialize_input_for_extra_body(request)
        wrapper.build_request(
            "POST", "https://trainer.invalid/api/v1/forward_backward", json={"forward_backward_input": converted}
        )
        asyncio.run(decode())
        profile.disable()
    profile.dump_stats(str(output.with_suffix(".pstats")))
    asyncio.run(wrapper.aclose())
    return {
        "workload": "16 x 8192, PPO tensors, CPU only",
        "warmups": 3,
        "runs": 9,
        "median_ms": [statistics.median(s[i] for s in samples) for i in range(3)],
        "payload_bytes": len(body),
        "traceEvents": trace,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)

    report = {
        "source": str(Path(sdk_client.__file__)),
        "api": {
            cls.__name__: shape(cls)
            for cls in [
                sdk_client.FiretitanServiceClient,
                sdk_client.FiretitanTrainingClient,
                sdk_client.FiretitanSamplingClient,
            ]
        },
        "wire": {
            route + "-" + comms: wire_probe(route, comms)
            for route in ("dedicated", "serverless")
            for comms in ("v1", "v2")
        },
        "codec": codec_probe(output),
    }
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(
        json.dumps(
            {
                "output": str(output),
                "median_ms": report["codec"]["median_ms"],
                "payload_bytes": report["codec"]["payload_bytes"],
            }
        )
    )
