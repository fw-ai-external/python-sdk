"""Preserve heterogeneous ``loss_fn_config`` values in Tinker's wire models.

Tinker types ``loss_fn_config`` as ``Dict[str, float]``, but Fireworks built-in
losses also take string target-policy support choices and boolean objective modifiers.
Preserve their values for backend validation instead of coercing them to floats.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from fireworks.training.sdk.patches._model_utils import rebuild_model

_LOSS_FN_CONFIG = Optional[Dict[str, Any]]


def _apply_loss_fn_config_patch() -> None:
    from tinker.types.forward_backward_input import ForwardBackwardInput
    from tinker.types.forward_backward_request import ForwardBackwardRequest
    from tinker.types._pydantic_types.forward_request import ForwardRequest as PydanticForwardRequest
    from tinker.types._pydantic_types.forward_backward_input import (
        ForwardBackwardInput as PydanticForwardBackwardInput,
    )
    from tinker.types._pydantic_types.forward_backward_request import (
        ForwardBackwardRequest as PydanticForwardBackwardRequest,
    )

    PydanticForwardBackwardInput.model_fields["loss_fn_config"].annotation = _LOSS_FN_CONFIG
    ForwardBackwardInput.__annotations__["loss_fn_config"] = _LOSS_FN_CONFIG
    for model in (
        PydanticForwardBackwardInput,
        PydanticForwardBackwardRequest,
        PydanticForwardRequest,
        ForwardBackwardInput,
        ForwardBackwardRequest,
    ):
        rebuild_model(model)


_apply_loss_fn_config_patch()
