from __future__ import annotations

from typing import List, Annotated

from pydantic import Discriminator

from fireworks.training.sdk.routing import (
    RoutingReferences,
    RoutingMatrixFormat,
    routing_model_input_kwargs,
    top_sampling_model_input_kwargs,
)
from fireworks.training.sdk._core._models import StrictBase
from fireworks.training.sdk.types.model_input_chunk import ModelInputChunk
from fireworks.training.sdk.types.encoded_text_chunk import EncodedTextChunk


class ModelInput(StrictBase):
    chunks: List[Annotated[ModelInputChunk, Discriminator("type")]]
    """Sequence of input chunks (formerly TokenSequence)."""
    routing_matrices: list[str] | None = None
    routing_references: dict | None = None
    routing_matrix_format: RoutingMatrixFormat | None = None
    top_sampling_references: dict | None = None

    @classmethod
    def from_ints(
        cls,
        tokens: List[int],
        routing_matrices: List[str] | RoutingReferences | None = None,
        top_sampling_references: RoutingReferences | dict | None = None,
    ) -> "ModelInput":
        kwargs = {"chunks": [EncodedTextChunk(tokens=tokens)]}
        kwargs.update(routing_model_input_kwargs(routing_matrices))
        if top_sampling_references is not None:
            kwargs.update(top_sampling_model_input_kwargs(top_sampling_references, len(tokens)))
        return cls(**kwargs)

    def to_ints(self) -> List[int]:
        """
        Convert the ModelInput to a list of ints (tokens)
        Throws exception if there are any non-token chunks
        """
        if not all(isinstance(chunk, EncodedTextChunk) for chunk in self.chunks):
            raise ValueError(
                f"to_ints only supported for ModelInput with EncodedTextChunks, got {[type(chunk) for chunk in self.chunks]}"
            )
        return [token for chunk in self.chunks for token in chunk.tokens]

    @property
    def length(self) -> int:
        """
        Return the total context length used by this ModelInput.
        """
        return sum(chunk.length for chunk in self.chunks)

    @classmethod
    def empty(cls) -> "ModelInput":
        """
        Create an empty ModelInput.
        """
        return cls(chunks=[])

    def append(self, chunk: ModelInputChunk) -> "ModelInput":
        """
        Add a new chunk, return a new ModelInput.
        """
        return ModelInput(chunks=self.chunks + [chunk])

    def append_int(self, token: int) -> "ModelInput":
        """
        Add a new token, return a new ModelInput.
        """
        return self.append(EncodedTextChunk(tokens=[token]))
