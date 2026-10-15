"""Float32 JSON encoding for the negotiated v2 transport."""

from typing import Any

import numpy as np
import orjson


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
