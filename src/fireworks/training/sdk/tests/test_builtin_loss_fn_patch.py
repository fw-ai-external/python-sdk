"""Tests for Fireworks built-in loss function compatibility patches."""

from __future__ import annotations

from typing import get_args

from tinker.types.forward_backward_input import ForwardBackwardInput


class TestBuiltinLossFnPatch:
    def test_annotation_includes_fireworks_builtin_loss_functions(self):
        loss_fns = get_args(ForwardBackwardInput.model_fields["loss_fn"].annotation)
        assert "dapo" in loss_fns
        assert "gspo" in loss_fns

    def test_gspo_validates(self):
        request = ForwardBackwardInput(data=[], loss_fn="gspo")
        assert request.loss_fn == "gspo"

    def test_dapo_validates(self):
        request = ForwardBackwardInput(data=[], loss_fn="dapo")
        assert request.loss_fn == "dapo"
