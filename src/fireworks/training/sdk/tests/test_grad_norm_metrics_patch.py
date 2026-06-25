from __future__ import annotations

import pytest
from tinker import types

import fireworks.training.sdk.patches  # noqa: F401


def _optim_step_body(adam_params: types.AdamParams) -> dict:
    request = types.OptimStepRequest(
        adam_params=adam_params,
        model_id="model",
        seq_id=1,
    )
    return request.model_dump(exclude_unset=False, exclude_none=True, mode="json")


def test_adam_params_default_omits_grad_norm_metrics_mode() -> None:
    params = types.AdamParams()

    assert params.emit_grad_norm_metrics is None
    assert "emit_grad_norm_metrics" not in _optim_step_body(params)["adam_params"]


@pytest.mark.parametrize("value", [False, True, "off", "basic", "detailed"])
def test_adam_params_serializes_explicit_grad_norm_metrics_mode(value: bool | str) -> None:
    params = types.AdamParams(emit_grad_norm_metrics=value)

    assert _optim_step_body(params)["adam_params"]["emit_grad_norm_metrics"] == value


def test_adam_params_rejects_unknown_grad_norm_metrics_mode() -> None:
    with pytest.raises(ValueError, match="emit_grad_norm_metrics"):
        types.AdamParams(emit_grad_norm_metrics="global")
