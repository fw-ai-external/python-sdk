"""Patch tinker's ModelInput for R3 routing and top-K sampling references.

Adds optional routing (R3) and top-K sampling reference fields to ModelInput
and rebuilds the Pydantic model chain so serialization includes them.

Safe to import multiple times -- patches are applied only once.
Remove this file when tinker supports these fields natively.
"""

from __future__ import annotations

import logging
from typing import List, Optional

from pydantic.fields import FieldInfo

from fireworks.training.sdk.routing import (
    RoutingReferences,
    RoutingMatrixFormat,
    routing_model_input_kwargs,
    top_sampling_model_input_kwargs,
)
from fireworks.training.sdk.patches._model_utils import rebuild_model

logger = logging.getLogger(__name__)


def _rebuild_wire_models() -> None:
    """Refresh Tinker's internal request serializers.

    Tinker 0.22 writes REST bodies through ``tinker.types._pydantic_types``
    mirrors. Rebuilding only the public request chain leaves those cached
    serializers stale, which silently drops dynamically-added ModelInput fields
    such as ``routing_matrices`` at the JSON boundary.
    """
    try:
        from tinker.types._pydantic_types.datum import Datum as PydanticDatum
        from tinker.types._pydantic_types.model_input import (
            ModelInput as PydanticModelInput,
        )
        from tinker.types._pydantic_types.forward_request import (
            ForwardRequest as PydanticForwardRequest,
        )
        from tinker.types._pydantic_types.forward_backward_input import (
            ForwardBackwardInput as PydanticForwardBackwardInput,
        )
        from tinker.types._pydantic_types.forward_backward_request import (
            ForwardBackwardRequest as PydanticForwardBackwardRequest,
        )
    except ImportError:
        return

    for model in (
        PydanticModelInput,
        PydanticDatum,
        PydanticForwardBackwardInput,
        PydanticForwardRequest,
        PydanticForwardBackwardRequest,
    ):
        rebuild_model(model)


def _apply_r3_patch() -> None:
    from tinker.types.model_input import ModelInput

    if "top_sampling_references" in ModelInput.model_fields:
        _rebuild_wire_models()
        return

    fields = {
        "routing_matrices": Optional[List[str]],
        "routing_references": Optional[dict],
        "routing_matrix_format": Optional[RoutingMatrixFormat],
        # Parquet references to the sampler's top-K distribution; row t produced target t.
        "top_sampling_references": Optional[dict],
    }
    for name, annotation in fields.items():
        if name not in ModelInput.model_fields:
            ModelInput.model_fields[name] = FieldInfo(default=None, annotation=annotation)
            ModelInput.__annotations__[name] = annotation
    rebuild_model(ModelInput)

    from tinker.types.datum import Datum
    from tinker.types.forward_request import ForwardRequest
    from tinker.types.forward_backward_input import ForwardBackwardInput
    from tinker.types.forward_backward_request import ForwardBackwardRequest

    rebuild_model(Datum)
    rebuild_model(ForwardBackwardInput)
    rebuild_model(ForwardRequest)
    rebuild_model(ForwardBackwardRequest)
    _rebuild_wire_models()

    from tinker.types.encoded_text_chunk import EncodedTextChunk

    @classmethod  # type: ignore[misc]
    def from_ints(
        cls,
        tokens: List[int],
        routing_matrices: List[str] | RoutingReferences | None = None,
        top_sampling_references: RoutingReferences | dict | None = None,
    ) -> ModelInput:
        kwargs: dict = {"chunks": [EncodedTextChunk(tokens=tokens)]}
        kwargs.update(routing_model_input_kwargs(routing_matrices))
        if top_sampling_references is not None:
            kwargs.update(top_sampling_model_input_kwargs(top_sampling_references, len(tokens)))
        return cls(**kwargs)

    ModelInput.from_ints = from_ints  # type: ignore[assignment]
    logger.info("R3 patch applied: routing and top-K sampling reference fields added to ModelInput")


_apply_r3_patch()
