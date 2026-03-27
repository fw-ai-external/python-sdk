"""Patch tinker's ModelInput to use Pydantic-native union discrimination.

Tinker's ModelInputChunk type is::

    Annotated[
        Union[EncodedTextChunk, ImageAssetPointerChunk, ImageChunk],
        PropertyInfo(discriminator="type"),
    ]

PropertyInfo is tinker's own metadata -- Pydantic V2's serializer does not
recognise it, so ``model_dump(mode="json")`` tries all 3 variants per chunk
and emits a ``PydanticSerializationUnexpectedValue`` warning for each
mismatch.  With many chunks this produces hundreds of warnings per request.

This patch adds ``pydantic.Discriminator("type")`` to the ``chunks`` field
annotation so Pydantic uses the ``type`` literal field for direct dispatch.

Safe to import multiple times -- the patch is applied only once.
Remove this file when tinker adds native Pydantic V2 discriminator support.
"""

import logging
from typing import List, Union
from typing_extensions import Annotated

from pydantic import Discriminator

logger = logging.getLogger(__name__)

_SENTINEL = "_discriminator_patch_applied"


def _apply_discriminator_patch() -> None:
    from tinker._utils import PropertyInfo
    from tinker.types.image_chunk import ImageChunk
    from tinker.types.model_input import ModelInput
    from tinker.types.encoded_text_chunk import EncodedTextChunk
    from tinker.types.image_asset_pointer_chunk import ImageAssetPointerChunk

    if getattr(ModelInput, _SENTINEL, False):
        return

    PatchedModelInputChunk = Annotated[
        Union[EncodedTextChunk, ImageAssetPointerChunk, ImageChunk],
        Discriminator("type"),
        PropertyInfo(discriminator="type"),
    ]

    ModelInput.model_fields["chunks"].annotation = List[PatchedModelInputChunk]
    ModelInput.__annotations__["chunks"] = List[PatchedModelInputChunk]
    ModelInput.model_rebuild(force=True)

    from tinker.types.datum import Datum
    from tinker.types.forward_request import ForwardRequest
    from tinker.types.forward_backward_input import ForwardBackwardInput
    from tinker.types.forward_backward_request import ForwardBackwardRequest

    Datum.model_rebuild(force=True)
    ForwardBackwardInput.model_rebuild(force=True)
    ForwardRequest.model_rebuild(force=True)
    ForwardBackwardRequest.model_rebuild(force=True)

    setattr(ModelInput, _SENTINEL, True)
    logger.info(
        "Discriminator patch applied: pydantic.Discriminator('type') "
        "added to ModelInput.chunks"
    )


_apply_discriminator_patch()
