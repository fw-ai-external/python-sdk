"""Response validation selected by the future's negotiated JSON version."""

from typing import Any

from fireworks.training.sdk import types
from fireworks.training.sdk._core.lib._pydantic_conv import CommsV2TensorData, _convert_forward_backward_output
from fireworks.training.sdk._core.lib.api_future_impl import _APIFuture
from fireworks.training.sdk.types._pydantic_types.forward_backward_output import ForwardBackwardOutput


class _CommsV2ForwardBackwardOutput(ForwardBackwardOutput):
    loss_fn_outputs: list[dict[str, CommsV2TensorData]]


class CommsV2APIFuture(_APIFuture):
    def _deserialize_json_response(self, result_dict: dict[str, Any], model_cls: type) -> Any:
        if model_cls is types.ForwardBackwardOutput:
            return _convert_forward_backward_output(_CommsV2ForwardBackwardOutput.model_validate(result_dict))
        return super()._deserialize_json_response(result_dict, model_cls)
