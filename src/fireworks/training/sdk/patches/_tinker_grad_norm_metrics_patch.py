"""Patch tinker's AdamParams for FireTitan grad-norm metric controls.

Tinker's generated ``AdamParams`` does not yet expose FireTitan's
``emit_grad_norm_metrics`` option. Add it client-side so callers can opt in to
trainer-side grad-norm telemetry without waiting for a regenerated tinker SDK.

Safe to import multiple times -- patches are applied only once.
Remove this file when tinker adds native ``emit_grad_norm_metrics`` support.
"""

from __future__ import annotations

import logging
from typing import Union, Literal, Optional

from pydantic.fields import FieldInfo

from fireworks.training.sdk.patches._model_utils import rebuild_model

logger = logging.getLogger(__name__)

GradNormMetricsMode = Optional[Union[Literal["off", "basic", "detailed"], bool]]


def _apply_grad_norm_metrics_patch() -> None:
    from tinker import types

    AdamParams = types.AdamParams
    if "emit_grad_norm_metrics" in AdamParams.model_fields:
        return

    AdamParams.model_fields["emit_grad_norm_metrics"] = FieldInfo(
        default=None,
        annotation=GradNormMetricsMode,
    )
    AdamParams.__annotations__["emit_grad_norm_metrics"] = GradNormMetricsMode
    rebuild_model(AdamParams)

    rebuild_model(types.OptimStepRequest)
    logger.info(
        "Grad-norm metrics patch applied: emit_grad_norm_metrics added to AdamParams"
    )


_apply_grad_norm_metrics_patch()
