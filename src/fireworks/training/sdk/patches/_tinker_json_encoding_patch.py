"""Encode numeric training JSON efficiently without changing Tinker's pools.

Fireworks training requests through Tinker's default HTTPX wrapper use the
optimized encoder. Other requests keep HTTPX's encoder. Its configured transport,
timeouts and separate connection pools remain intact; caller-supplied clients
keep their own encoding. Remove this patch when Tinker supplies a native hook.
"""

from __future__ import annotations

from typing import Any

import httpx
import numpy as np
import orjson
from tinker._base_client import AsyncHttpxClientWrapper

from fireworks.training.sdk._comms import get_comms


def _float32_training_json(payload: Any) -> Any:
    """Keep declared float32 tensors at float32 precision in ordinary JSON.

    TensorData stores float32, but its list export widens each value to a Python
    float. Encoding that widened value produces unnecessary double-precision
    decimals. Only shorten exact, finite float32 values; leave malformed data,
    other fields and the original request objects untouched. Float32 extrema
    retain their expanded representation because older trainers validate the
    parsed decimal against the exact float32 maximum before materialization.
    """
    if not isinstance(payload, dict):
        return payload
    result = payload
    for key in ("forward_input", "forward_backward_input"):
        inputs = payload.get(key)
        if not isinstance(inputs, dict) or not isinstance(inputs.get("data"), list):
            continue
        datums = list(inputs["data"])
        changed = False
        for index, datum in enumerate(datums):
            if not isinstance(datum, dict) or not isinstance(datum.get("loss_fn_inputs"), dict):
                continue
            tensors = dict(datum["loss_fn_inputs"])
            for name, tensor in tensors.items():
                if not isinstance(tensor, dict) or tensor.get("dtype") != "float32":
                    continue
                values = tensor.get("data")
                if not isinstance(values, list) or len(values) < 256:
                    continue
                try:
                    wide = np.asarray(values)
                    if wide.ndim != 1 or wide.dtype.kind != "f" or not np.isfinite(wide).all():
                        continue
                    with np.errstate(over="ignore", invalid="ignore"):
                        narrow = wide.astype(np.float32)
                    if not np.array_equal(wide, narrow) or np.max(np.abs(narrow)) >= np.finfo(np.float32).max:
                        continue
                except (TypeError, ValueError, OverflowError):
                    continue
                encoded = orjson.dumps(narrow, option=orjson.OPT_SERIALIZE_NUMPY)
                tensors[name] = {**tensor, "data": orjson.Fragment(encoded)}
                datums[index] = {**datum, "loss_fn_inputs": tensors}
                changed = True
        if changed:
            result = {**result, key: {**inputs, "data": datums}}
    return result


def _apply_patch() -> None:
    if getattr(AsyncHttpxClientWrapper, "_fireworks_fast_json", False):
        return
    original = AsyncHttpxClientWrapper.build_request

    def build_request(self, method: str, url: httpx.URL | str, *, json: Any = None, **kwargs):
        if (
            get_comms() == "v2"
            and json is not None
            and httpx.URL(url).path.endswith(("/api/v1/forward", "/api/v1/forward_backward"))
            and all(kwargs.get(field) is None for field in ("content", "data", "files"))
        ):
            try:
                body = orjson.dumps(_float32_training_json(json))
            except TypeError:
                body = None
            # orjson maps NaN/Inf to null; defer to HTTPX's strict encoder for
            # those inputs, existing nulls and unsupported/arbitrary-size ints.
            if (
                body is not None
                and body != b"null"
                and not any(marker in body for marker in (b":null", b",null", b"[null"))
            ):
                headers = httpx.Headers(kwargs.pop("headers", None))
                headers.setdefault("Content-Type", "application/json")
                kwargs["content"] = body
                return original(self, method, url, headers=headers, **kwargs)
        return original(self, method, url, json=json, **kwargs)

    AsyncHttpxClientWrapper.build_request = build_request
    AsyncHttpxClientWrapper._fireworks_fast_json = True


_apply_patch()
