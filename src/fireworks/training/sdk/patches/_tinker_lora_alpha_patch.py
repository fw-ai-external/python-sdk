"""Patch tinker's LoraConfig for an explicit ``alpha`` field.

Tinker's client-side ``LoraConfig`` only carries ``rank`` (and the
``train_*`` flags); it has no ``alpha``, so the FireTitan backend falls back
to its own default of ``2 * rank``. The FireTitan server schema does accept an
optional ``alpha``, so we add the field here and rebuild the request models
that embed ``LoraConfig`` so the value is serialized onto the wire.

Safe to import multiple times -- patches are applied only once.
Remove this file when tinker adds native ``alpha`` support.
"""

import logging
from typing import Optional

from pydantic.fields import FieldInfo

from fireworks.training.sdk.patches._model_utils import rebuild_model

logger = logging.getLogger(__name__)


def _apply_lora_alpha_patch() -> None:
    from tinker.types.lora_config import LoraConfig

    if "alpha" in LoraConfig.model_fields:
        return

    LoraConfig.model_fields["alpha"] = FieldInfo(default=None, annotation=Optional[int])
    LoraConfig.__annotations__["alpha"] = Optional[int]
    rebuild_model(LoraConfig)

    from tinker.types.create_model_request import CreateModelRequest

    rebuild_model(CreateModelRequest)
    logger.info("LoRA alpha patch applied: alpha added to LoraConfig")


_apply_lora_alpha_patch()
