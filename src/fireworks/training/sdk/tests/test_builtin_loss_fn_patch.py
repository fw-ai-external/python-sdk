"""Tests for Fireworks built-in loss function compatibility patches."""

from __future__ import annotations

from typing import get_args

from tinker.lib._pydantic_conv import to_pydantic_input
from tinker.types.forward_backward_input import ForwardBackwardInput
from tinker.types._pydantic_types.forward_backward_input import (
    ForwardBackwardInput as PydanticForwardBackwardInput,
)

import fireworks.training.sdk.patches  # noqa: F401  (applies builtin loss patch)


def _loss_fn_args() -> tuple[str, ...]:
    return tuple(get_args(PydanticForwardBackwardInput.model_fields["loss_fn"].annotation))


class TestBuiltinLossFnPatch:
    def test_annotation_includes_fireworks_builtin_loss_functions(self):
        loss_fns = _loss_fn_args()
        assert "dapo" in loss_fns
        assert "gspo" in loss_fns

    def test_gspo_validates(self):
        request = PydanticForwardBackwardInput(data=[], loss_fn="gspo")
        assert request.loss_fn == "gspo"

    def test_dapo_validates(self):
        request = PydanticForwardBackwardInput(data=[], loss_fn="dapo")
        assert request.loss_fn == "dapo"

    def test_dataclass_to_pydantic_conversion_preserves_fireworks_builtin_loss(self):
        request = ForwardBackwardInput(data=[], loss_fn="gspo")

        pydantic_request = to_pydantic_input(request)

        assert pydantic_request.loss_fn == "gspo"
