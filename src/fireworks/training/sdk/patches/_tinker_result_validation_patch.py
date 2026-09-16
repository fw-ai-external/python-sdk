"""Bound numeric-union work when an comms v2 F/B future decodes results.

Default Fireworks and native Tinker futures keep their original schema.
The public result type, field validation and future timeout/budget handling
remain Tinker's; only failed numeric-union branches stop at their first error.
"""

from typing import Any, Dict, List
from contextvars import ContextVar

from tinker import types
from tinker.lib import _pydantic_conv, api_future_impl
from tinker.types._pydantic_types.forward_backward_output import ForwardBackwardOutput

from ._tinker_tensor_validation_patch import CommsV2TensorData

_result_comms: ContextVar[str] = ContextVar("fireworks_result_comms", default="v1")


class _CommsV2ForwardBackwardOutput(ForwardBackwardOutput):
    loss_fn_outputs: List[Dict[str, CommsV2TensorData]]


class CommsV2APIFuture(api_future_impl._APIFuture):
    async def _handle_outcome(self, *args: Any, **kwargs: Any) -> Any:
        token = _result_comms.set("v2")
        try:
            return await super()._handle_outcome(*args, **kwargs)
        finally:
            _result_comms.reset(token)


def _apply_result_validation_patch() -> None:
    original = api_future_impl.deserialize_json_response
    if getattr(original, "_fireworks_comms_v2_result", False):
        return

    def deserialize(result_dict, model_cls):
        if _result_comms.get() != "v2" or model_cls is not types.ForwardBackwardOutput:
            return original(result_dict, model_cls)
        validated = _CommsV2ForwardBackwardOutput.model_validate(result_dict)
        return _pydantic_conv._convert_forward_backward_output(validated)

    deserialize._fireworks_comms_v2_result = True
    api_future_impl.deserialize_json_response = deserialize


_apply_result_validation_patch()
