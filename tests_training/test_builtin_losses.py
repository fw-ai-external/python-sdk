"""Native built-in loss validation and JSON conversion."""

from __future__ import annotations

from typing import get_args

from fireworks.training.sdk._core.lib._pydantic_conv import to_pydantic_input
from fireworks.training.sdk.types.forward_backward_input import ForwardBackwardInput
from fireworks.training.sdk.types._pydantic_types.forward_backward_input import (
    ForwardBackwardInput as PydanticForwardBackwardInput,
)


def _loss_fn_args() -> tuple[str, ...]:
    return tuple(get_args(PydanticForwardBackwardInput.model_fields["loss_fn"].annotation))


class TestBuiltinLossFunctions:
    def test_annotation_includes_fireworks_builtin_loss_functions(self):
        loss_fns = _loss_fn_args()
        assert "dapo" in loss_fns
        assert "gspo" in loss_fns
        assert "dppo" in loss_fns

    def test_gspo_validates(self):
        request = PydanticForwardBackwardInput(data=[], loss_fn="gspo")
        assert request.loss_fn == "gspo"

    def test_dppo_validates(self):
        request = PydanticForwardBackwardInput(data=[], loss_fn="dppo")
        assert request.loss_fn == "dppo"

    def test_dapo_validates(self):
        request = PydanticForwardBackwardInput(data=[], loss_fn="dapo")
        assert request.loss_fn == "dapo"

    def test_dataclass_to_pydantic_conversion_preserves_fireworks_builtin_loss(self):
        request = ForwardBackwardInput(data=[], loss_fn="gspo")

        pydantic_request = to_pydantic_input(request)

        assert pydantic_request.loss_fn == "gspo"
