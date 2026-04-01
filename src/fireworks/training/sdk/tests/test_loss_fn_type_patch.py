"""Tests for the LossFnType patch that adds missing builtin loss names."""

from typing import get_args


class TestLossFnTypePatch:
    """Verify that the LossFnType patch adds server-supported loss names."""

    def test_gspo_in_loss_fn_type(self):
        """'gspo' should be in the patched LossFnType."""
        import tinker.types.loss_fn_type as mod

        allowed = get_args(mod.LossFnType)
        assert "gspo" in allowed, f"gspo not in LossFnType: {allowed}"

    def test_dapo_in_loss_fn_type(self):
        """'dapo' should be in the patched LossFnType."""
        import tinker.types.loss_fn_type as mod

        allowed = get_args(mod.LossFnType)
        assert "dapo" in allowed, f"dapo not in LossFnType: {allowed}"

    def test_kl_distillation_in_loss_fn_type(self):
        """'kl_distillation' should be in the patched LossFnType."""
        import tinker.types.loss_fn_type as mod

        allowed = get_args(mod.LossFnType)
        assert "kl_distillation" in allowed, f"kl_distillation not in LossFnType: {allowed}"

    def test_original_types_still_present(self):
        """Original loss types should still be valid."""
        import tinker.types.loss_fn_type as mod

        allowed = get_args(mod.LossFnType)
        for expected in ("cross_entropy", "importance_sampling", "ppo", "cispo", "dro"):
            assert expected in allowed, f"{expected} not in LossFnType: {allowed}"

    def test_forward_backward_input_accepts_gspo(self):
        """ForwardBackwardInput should validate with loss_fn='gspo'."""
        from tinker.types.datum import Datum
        from tinker.types.model_input import ModelInput
        from tinker.types.forward_backward_input import ForwardBackwardInput
        from tinker.types.tensor_data import TensorData

        mi = ModelInput.from_ints([1, 2, 3])
        loss_fn_inputs = {"weights": TensorData(data=[1.0, 1.0, 1.0], dtype="float32")}
        datum = Datum(model_input=mi, loss_fn_inputs=loss_fn_inputs)
        fbi = ForwardBackwardInput(data=[datum], loss_fn="gspo")
        assert fbi.loss_fn == "gspo"

    def test_forward_backward_input_accepts_dapo(self):
        """ForwardBackwardInput should validate with loss_fn='dapo'."""
        from tinker.types.datum import Datum
        from tinker.types.model_input import ModelInput
        from tinker.types.forward_backward_input import ForwardBackwardInput
        from tinker.types.tensor_data import TensorData

        mi = ModelInput.from_ints([1, 2, 3])
        loss_fn_inputs = {"weights": TensorData(data=[1.0, 1.0, 1.0], dtype="float32")}
        datum = Datum(model_input=mi, loss_fn_inputs=loss_fn_inputs)
        fbi = ForwardBackwardInput(data=[datum], loss_fn="dapo")
        assert fbi.loss_fn == "dapo"

    def test_idempotent_double_apply(self):
        """Calling the patch function twice should not break anything."""
        from fireworks.training.sdk.patches._loss_fn_type_patch import (
            _apply_loss_fn_type_patch,
        )

        _apply_loss_fn_type_patch()  # second call

        import tinker.types.loss_fn_type as mod

        allowed = get_args(mod.LossFnType)
        assert "gspo" in allowed
        assert "cross_entropy" in allowed
