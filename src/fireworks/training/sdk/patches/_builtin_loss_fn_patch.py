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

logger = logging.getLogger(__name__)

_SENTINEL = "_builtin_loss_fn_patch_applied"
_FIREWORKS_BUILTIN_LOSS_FNS = ("dapo", "gspo")


def _apply_builtin_loss_fn_patch() -> None:
    from tinker.types.forward_backward_input import ForwardBackwardInput
    from tinker.types.forward_backward_request import ForwardBackwardRequest

    if getattr(ForwardBackwardInput, _SENTINEL, False):
        return

    loss_fn_field = ForwardBackwardInput.model_fields.get("loss_fn")
    if loss_fn_field is None:
        logger.warning("Builtin loss patch skipped: ForwardBackwardInput.loss_fn field not found")
        return

    existing_loss_fns = tuple(get_args(loss_fn_field.annotation))
    if not existing_loss_fns:
        logger.warning("Builtin loss patch skipped: unexpected ForwardBackwardInput.loss_fn annotation")
        return

    missing_loss_fns = tuple(
        loss_fn for loss_fn in _FIREWORKS_BUILTIN_LOSS_FNS if loss_fn not in existing_loss_fns
    )
    if not missing_loss_fns:
        setattr(ForwardBackwardInput, _SENTINEL, True)
        return

    patched_loss_fn = Literal.__getitem__(existing_loss_fns + missing_loss_fns)
    ForwardBackwardInput.model_fields["loss_fn"].annotation = patched_loss_fn
    ForwardBackwardInput.__annotations__["loss_fn"] = patched_loss_fn
    ForwardBackwardInput.model_rebuild(force=True)
    ForwardBackwardRequest.model_rebuild(force=True)

    setattr(ForwardBackwardInput, _SENTINEL, True)
    logger.info(
        "Builtin loss patch applied: added %s to ForwardBackwardInput.loss_fn",
        ", ".join(missing_loss_fns),
    )


_apply_builtin_loss_fn_patch()
