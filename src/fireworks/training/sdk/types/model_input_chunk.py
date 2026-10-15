from typing import Union
from typing_extensions import Annotated, TypeAlias

from fireworks.training.sdk._core._utils import PropertyInfo
from fireworks.training.sdk.types.dmel_chunk import DmelChunk
from fireworks.training.sdk.types.image_chunk import ImageChunk
from fireworks.training.sdk.types.encoded_text_chunk import EncodedTextChunk
from fireworks.training.sdk.types.image_asset_pointer_chunk import ImageAssetPointerChunk

__all__ = ["ModelInputChunk"]

ModelInputChunk: TypeAlias = Annotated[
    Union[EncodedTextChunk, ImageAssetPointerChunk, ImageChunk, DmelChunk],
    PropertyInfo(discriminator="type"),
]
