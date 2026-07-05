"""Patch tinker's ForwardBackwardInput loss_fn Literal for Fireworks built-ins.

Tinker's published ``ForwardBackwardInput.loss_fn`` Literal can lag behind the
set of built-in loss functions supported by Fireworks trainers. When that
happens, valid Fireworks loss names fail client-side validation before the
request is even sent.

This patch extends the Literal at import time so Fireworks-specific built-ins
remain usable until upstream tinker adds them natively.
"""

from __future__ import annotations

import logging
from typing import Literal, get_args

from fireworks.training.sdk.patches._model_utils import rebuild_model

logger = logging.getLogger(__name__)

_SENTINEL = "_builtin_loss_fn_patch_applied"
_FIREWORKS_BUILTIN_LOSS_FNS = ("dapo", "gspo")


def _apply_builtin_loss_fn_patch() -> None:
    import tinker.types as tinker_types
    import tinker.types.loss_fn_type as loss_fn_type_module
    import tinker.types.forward_backward_input as forward_backward_input_module
    import tinker.types._pydantic_types.forward_backward_input as pydantic_forward_backward_input_module
    from tinker.types.forward_backward_input import ForwardBackwardInput
    from tinker.types.forward_backward_request import ForwardBackwardRequest
    from tinker.types._pydantic_types.forward_request import ForwardRequest as PydanticForwardRequest
    from tinker.types._pydantic_types.forward_backward_input import (
        ForwardBackwardInput as PydanticForwardBackwardInput,
    )
    from tinker.types._pydantic_types.forward_backward_request import (
        ForwardBackwardRequest as PydanticForwardBackwardRequest,
    )

    if getattr(PydanticForwardBackwardInput, _SENTINEL, False):
        return

    loss_fn_field = PydanticForwardBackwardInput.model_fields.get("loss_fn")
    if loss_fn_field is None:
        logger.warning("Builtin loss patch skipped: Pydantic ForwardBackwardInput.loss_fn field not found")
        return

    existing_loss_fns = tuple(get_args(loss_fn_field.annotation))
    if not existing_loss_fns:
        logger.warning("Builtin loss patch skipped: unexpected Pydantic ForwardBackwardInput.loss_fn annotation")
        return

    missing_loss_fns = tuple(loss_fn for loss_fn in _FIREWORKS_BUILTIN_LOSS_FNS if loss_fn not in existing_loss_fns)
    if not missing_loss_fns:
        setattr(PydanticForwardBackwardInput, _SENTINEL, True)
        return

    patched_loss_fn = Literal.__getitem__(existing_loss_fns + missing_loss_fns)
    PydanticForwardBackwardInput.model_fields["loss_fn"].annotation = patched_loss_fn
    ForwardBackwardInput.__annotations__["loss_fn"] = patched_loss_fn
    loss_fn_type_module.LossFnType = patched_loss_fn
    forward_backward_input_module.LossFnType = patched_loss_fn
    pydantic_forward_backward_input_module.LossFnType = patched_loss_fn
    tinker_types.LossFnType = patched_loss_fn
    rebuild_model(PydanticForwardBackwardInput)
    rebuild_model(PydanticForwardBackwardRequest)
    rebuild_model(PydanticForwardRequest)
    rebuild_model(ForwardBackwardInput)
    rebuild_model(ForwardBackwardRequest)

    setattr(PydanticForwardBackwardInput, _SENTINEL, True)
    logger.info(
        "Builtin loss patch applied: added %s to ForwardBackwardInput.loss_fn",
        ", ".join(missing_loss_fns),
    )


_apply_builtin_loss_fn_patch()
