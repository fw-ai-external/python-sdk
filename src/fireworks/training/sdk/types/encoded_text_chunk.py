from typing import Any, Sequence, Annotated
from typing_extensions import Literal

from pydantic import WithJsonSchema, SerializationInfo, field_serializer

from fireworks.training.sdk._core._models import StrictBase

__all__ = ["EncodedTextChunk"]


class EncodedTextChunk(StrictBase):
    tokens: Sequence[int]
    """Array of token IDs"""

    type: Literal["encoded_text"] = "encoded_text"

    @field_serializer("tokens")
    def _serialize_tokens(
        self, tokens: Sequence[int], info: SerializationInfo
    ) -> Annotated[Any, WithJsonSchema({"type": "array", "items": {"type": "integer"}})]:
        # Keep the public Sequence contract; use Pydantic's C list serializer
        # instead of its Python callback for every token. Python-mode dumps
        # retain their container type. Values have already passed validation.
        if info.mode != "json":
            return tokens
        return tokens if isinstance(tokens, list) else list(tokens)

    @property
    def length(self) -> int:
        return len(self.tokens)
