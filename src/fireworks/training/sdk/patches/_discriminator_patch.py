"""Patch tinker's ModelInput to use Pydantic-native union discrimination.

Tinker's ``ModelInputChunk`` is an ``Annotated`` union whose variants are
tagged by a ``PropertyInfo(discriminator="type")`` metadata value.

PropertyInfo is tinker's own metadata -- Pydantic V2's serializer does not
recognise it, so ``model_dump(mode="json")`` tries every variant per chunk
and emits a ``PydanticSerializationUnexpectedValue`` warning for each
mismatch.  With many chunks this produces hundreds of warnings per request.

This patch preserves every upstream union variant and adds
``pydantic.Discriminator("type")`` to the ``chunks`` field annotation so
Pydantic uses the ``type`` literal field for direct dispatch. Preserving the
upstream union is important when Tinker adds new chunk types such as
``DmelChunk``.

Safe to import multiple times -- the patch is applied only once.
Remove this file when tinker adds native Pydantic V2 discriminator support.
"""

import logging
from typing import List, get_args
from typing_extensions import Annotated

from pydantic import Discriminator

from fireworks.training.sdk.patches._model_utils import rebuild_model

logger = logging.getLogger(__name__)

_SENTINEL = "_discriminator_patch_applied"


def _apply_discriminator_patch() -> None:
    from tinker.types.model_input import ModelInput

    if getattr(ModelInput, _SENTINEL, False):
        return

    chunks_annotation = ModelInput.model_fields["chunks"].annotation
    chunk_annotation_args = get_args(chunks_annotation)
    if len(chunk_annotation_args) != 1:
        logger.warning(
            "Discriminator patch skipped: unexpected ModelInput.chunks annotation %r",
            chunks_annotation,
        )
        return

    chunk_annotation = chunk_annotation_args[0]
    annotated_args = get_args(chunk_annotation)
    if len(annotated_args) < 2:
        logger.warning(
            "Discriminator patch skipped: unexpected ModelInputChunk annotation %r",
            chunk_annotation,
        )
        return

    upstream_union, *upstream_metadata = annotated_args
    preserved_metadata = tuple(
        item for item in upstream_metadata if not isinstance(item, Discriminator)
    )
    # Use the public subscription form instead of calling ``__class_getitem__``
    # directly.  On Python 3.13 ``Annotated`` is a typing special form and no
    # longer exposes that private attribute, while ``Annotated[(...)]`` remains
    # supported across the Python versions in the SDK's compatibility matrix.
    PatchedModelInputChunk = Annotated[
        (upstream_union, Discriminator("type"), *preserved_metadata)
    ]

    ModelInput.model_fields["chunks"].annotation = List[PatchedModelInputChunk]
    ModelInput.__annotations__["chunks"] = List[PatchedModelInputChunk]
    rebuild_model(ModelInput)

    from tinker.types.datum import Datum
    from tinker.types.forward_request import ForwardRequest
    from tinker.types.forward_backward_input import ForwardBackwardInput
    from tinker.types.forward_backward_request import ForwardBackwardRequest

    rebuild_model(Datum)
    rebuild_model(ForwardBackwardInput)
    rebuild_model(ForwardRequest)
    rebuild_model(ForwardBackwardRequest)

    setattr(ModelInput, _SENTINEL, True)
    logger.info(
        "Discriminator patch applied: pydantic.Discriminator('type') "
        "added to ModelInput.chunks"
    )


_apply_discriminator_patch()
