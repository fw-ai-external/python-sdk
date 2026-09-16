"""The fast default-client encoder preserves HTTPX's JSON/error contract."""

import json
import math

import httpx
import numpy as np
import pytest
from tinker import TensorData
from tinker._base_client import AsyncHttpxClientWrapper

from fireworks.training.sdk._comms import comms_context
from fireworks.training.sdk.patches import _tinker_json_encoding_patch  # noqa: F401


@pytest.fixture(autouse=True)
def _v2_encoder():
    with comms_context("v2"):
        yield


@pytest.mark.parametrize(
    "value",
    [
        {"data": [1, 0.1, -0.0, 2**60 + 1], "s": "测试"},
        {"data": [None, 2**80]},
    ],
)
def test_numeric_json_retains_values_and_request_options(value):
    client = AsyncHttpxClientWrapper()
    request = client.build_request(
        "POST",
        "https://example.com/api/v1/forward_backward",
        json=value,
        content=None,
        data=None,
        files=None,
        headers={"X-Test": "kept"},
        extensions={"caller": True},
    )
    assert json.loads(request.content) == value
    assert request.headers["content-type"] == "application/json"
    assert int(request.headers["content-length"]) == len(request.content)
    assert request.headers["x-test"] == "kept"
    assert request.extensions["caller"] is True
    if value["data"] == [1, 0.1, -0.0, 2**60 + 1]:
        assert math.copysign(1, json.loads(request.content)["data"][2]) == -1


@pytest.mark.parametrize("operation, comms", [("forward", "v1"), ("forward_backward", "v1"), ("other", "v2")])
def test_default_and_unrelated_requests_keep_httpx_bytes(operation, comms):
    tensor = TensorData(data=[1e-6] * 512, dtype="float32")
    input_key = "forward_backward_input" if operation == "forward_backward" else "forward_input"
    body = {input_key: {"data": [{"loss_fn_inputs": {
        "weights": {"data": tensor.data, "dtype": "float32"},
    }}]}, "model_id": "model", "seq_id": 1}
    url = f"https://example.com/api/v1/{operation}"
    with comms_context(comms):
        actual = AsyncHttpxClientWrapper().build_request("POST", url, json=body)
    expected = httpx.AsyncClient().build_request("POST", url, json=body)
    assert actual.content == expected.content


@pytest.mark.parametrize("operation", ["forward", "forward_backward"])
def test_declared_float32_tensors_roundtrip_bits_without_widened_json(operation):
    rng = np.random.default_rng(20260908)
    bits = rng.integers(0, 2**32, 8192, dtype=np.uint32)
    values = bits.view(np.float32)
    values = values[np.isfinite(values)]
    values = np.concatenate([values, np.array([0, 0x80000000, 1, 0x80000001], dtype=np.uint32).view(np.float32)])
    tensor = TensorData(data=values, dtype="float32", shape=[len(values)])
    dense = tensor.data
    weights = TensorData(data=[1e-6] * 4096, dtype="float32")
    inputs = {
        "data": [
            {
                "loss_fn_inputs": {
                    "grads": {"data": dense, "dtype": "float32", "shape": tensor.shape},
                    "weights": {"data": weights.data, "dtype": "float32"},
                    "target_tokens": {"data": [2**63 - 1], "dtype": "int64"},
                }
            }
        ],
        "loss_fn_config": {"coefficient": 0.12345678901234567},
    }
    body = {f"{operation}_input": inputs}
    request = AsyncHttpxClientWrapper().build_request("POST", f"https://example.com/api/v1/{operation}", json=body)
    decoded = json.loads(request.content)[f"{operation}_input"]
    tensors = decoded["data"][0]["loss_fn_inputs"]
    restored = TensorData(data=tensors["grads"]["data"], dtype="float32").to_numpy()
    assert np.array_equal(restored.view(np.uint32), values.view(np.uint32))
    assert np.array_equal(np.asarray(tensors["weights"]["data"], dtype=np.float32), weights.to_numpy())
    assert len(json.dumps(tensors["weights"]["data"])) < len(json.dumps(weights.data)) / 2
    assert tensors["target_tokens"]["data"] == [2**63 - 1]
    assert decoded["loss_fn_config"] == inputs["loss_fn_config"]
    assert inputs["data"][0]["loss_fn_inputs"]["grads"]["data"] is dense
    assert np.array_equal(np.asarray(dense, dtype=np.float32).view(np.uint32), values.view(np.uint32))


@pytest.mark.parametrize("value", [float(np.finfo(np.float32).max), -float(np.finfo(np.float32).max), 0.1])
def test_float32_extrema_and_noncanonical_values_keep_exact_json(value):
    tensor = {"data": [value] * 256, "dtype": "float32"}
    body = {"forward_input": {"data": [{"loss_fn_inputs": {"weights": tensor}}]}}
    request = AsyncHttpxClientWrapper().build_request("POST", "https://example.com/api/v1/forward", json=body)
    assert json.loads(request.content) == body


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
@pytest.mark.parametrize("size", [1, 256])
def test_nonfinite_rejected_before_and_after_float32_optimization_threshold(value, size):
    body = {"forward_input": {"data": [{"loss_fn_inputs": {"weights": {"data": [value] * size, "dtype": "float32"}}}]}}
    with pytest.raises(ValueError):
        AsyncHttpxClientWrapper().build_request("POST", "https://example.com/api/v1/forward", json=body)
