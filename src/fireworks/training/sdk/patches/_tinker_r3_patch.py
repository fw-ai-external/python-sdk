"""Patch tinker's ModelInput for R3 routing_matrices support.

Adds an optional routing_matrices field to ModelInput and rebuilds
the Pydantic model chain so serialization includes it.

Safe to import multiple times -- patches are applied only once.
Remove this file when tinker adds native routing_matrices support.
"""

import logging
from typing import List, Optional

from pydantic.fields import FieldInfo

from fireworks.training.sdk.patches._model_utils import rebuild_model

logger = logging.getLogger(__name__)


def _apply_r3_patch() -> None:
    from tinker.types.model_input import ModelInput

    if "routing_matrices" in ModelInput.model_fields:
        return

    ModelInput.model_fields["routing_matrices"] = FieldInfo(
        default=None, annotation=Optional[List[str]]
    )
    ModelInput.__annotations__["routing_matrices"] = Optional[List[str]]
    rebuild_model(ModelInput)

    from tinker.types.datum import Datum
    from tinker.types.forward_request import ForwardRequest
    from tinker.types.forward_backward_input import ForwardBackwardInput
    from tinker.types.forward_backward_request import ForwardBackwardRequest

    rebuild_model(Datum)
    rebuild_model(ForwardBackwardInput)
    rebuild_model(ForwardRequest)
    rebuild_model(ForwardBackwardRequest)

    from tinker.types.encoded_text_chunk import EncodedTextChunk

    @classmethod  # type: ignore[misc]
    def from_ints(
        cls, tokens: List[int], routing_matrices: Optional[List[str]] = None
    ) -> ModelInput:
        kwargs: dict = {"chunks": [EncodedTextChunk(tokens=tokens)]}
        if routing_matrices is not None:
            kwargs["routing_matrices"] = routing_matrices
        return cls(**kwargs)

    ModelInput.from_ints = from_ints  # type: ignore[assignment]
    logger.info("R3 patch applied: routing_matrices added to ModelInput")


_apply_r3_patch()
