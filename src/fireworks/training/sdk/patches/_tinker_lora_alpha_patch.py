"""Patch Tinker create-model types for FireTitan extensions.

Tinker's client-side ``LoraConfig`` only carries ``rank`` (and the
``train_*`` flags); it has no ``alpha``, so the FireTitan backend falls back
to its own default of ``2 * rank``. The FireTitan server schema does accept an
optional ``alpha``, so we add the field here and rebuild the request models
that embed ``LoraConfig`` so the value is serialized onto the wire.

This also adds ``projection_head_dim`` until the upstream Tinker request type
exposes the field. Safe to import multiple times; patches are idempotent.
"""

import logging
from typing import Optional

from pydantic.fields import FieldInfo

from fireworks.training.sdk.patches._model_utils import rebuild_model

logger = logging.getLogger(__name__)


def _apply_lora_alpha_patch() -> None:
    from tinker.types.lora_config import LoraConfig
    from tinker.types.create_model_request import CreateModelRequest

    changed = False
    if "alpha" not in LoraConfig.model_fields:
        LoraConfig.model_fields["alpha"] = FieldInfo(default=None, annotation=Optional[int])
        LoraConfig.__annotations__["alpha"] = Optional[int]
        rebuild_model(LoraConfig)
        changed = True
    if "projection_head_dim" not in CreateModelRequest.model_fields:
        CreateModelRequest.model_fields["projection_head_dim"] = FieldInfo(default=None, annotation=Optional[int])
        CreateModelRequest.__annotations__["projection_head_dim"] = Optional[int]
        changed = True
    if not changed:
        return
    rebuild_model(CreateModelRequest)
    logger.info("Tinker create-model extensions applied")


_apply_lora_alpha_patch()
