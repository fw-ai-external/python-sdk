"""Tests for the Pydantic discriminator patch on ModelInput."""

import warnings
from typing import get_args

from pydantic import Discriminator


class TestDiscriminatorPatch:
    """Verify that model_dump(mode='json') on ModelInput emits no warnings."""

    def test_model_dump_no_warnings_encoded_text(self):
        """176 EncodedTextChunks should serialize without warnings."""
        from tinker.types.model_input import ModelInput
        from tinker.types.encoded_text_chunk import EncodedTextChunk

        chunks = [EncodedTextChunk(tokens=[i, i + 1]) for i in range(176)]
        mi = ModelInput(chunks=chunks)

        with warnings.catch_warnings():
            warnings.simplefilter("error")
            result = mi.model_dump(mode="json")

        assert len(result["chunks"]) == 176
        assert all(c["type"] == "encoded_text" for c in result["chunks"])

    def test_model_dump_no_warnings_mixed_types(self):
        """Mixed chunk types should serialize without warnings."""
        from tinker.types.image_chunk import ImageChunk
        from tinker.types.model_input import ModelInput
        from tinker.types.encoded_text_chunk import EncodedTextChunk
        from tinker.types.image_asset_pointer_chunk import ImageAssetPointerChunk

        mi = ModelInput(chunks=[
            EncodedTextChunk(tokens=[1, 2, 3]),
            ImageChunk(data=b"fake", format="png"),
            ImageAssetPointerChunk(format="jpeg", location="s3://b/img.jpg"),
        ])

        with warnings.catch_warnings():
            warnings.simplefilter("error")
            result = mi.model_dump(mode="json")

        assert result["chunks"][0]["type"] == "encoded_text"
        assert result["chunks"][1]["type"] == "image"
        assert result["chunks"][2]["type"] == "image_asset_pointer"

    def test_deserialization_round_trip(self):
        """model_validate should still correctly discriminate by type."""
        from tinker.types.model_input import ModelInput
        from tinker.types.encoded_text_chunk import EncodedTextChunk
        from tinker.types.image_asset_pointer_chunk import ImageAssetPointerChunk

        data = {
            "chunks": [
                {"tokens": [10, 20], "type": "encoded_text"},
                {
                    "format": "png",
                    "location": "s3://bucket/img.png",
                    "type": "image_asset_pointer",
                },
            ]
        }
        mi = ModelInput.model_validate(data)
        assert isinstance(mi.chunks[0], EncodedTextChunk)
        assert isinstance(mi.chunks[1], ImageAssetPointerChunk)

        # Round-trip
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            dumped = mi.model_dump(mode="json")

        assert dumped["chunks"][0]["type"] == "encoded_text"
        assert dumped["chunks"][1]["type"] == "image_asset_pointer"

    def test_discriminator_present_in_annotation(self):
        """Verify Discriminator metadata is present after patching."""
        from tinker.types.model_input import ModelInput

        fi = ModelInput.model_fields["chunks"]
        inner = get_args(fi.annotation)[0]  # List[inner] -> inner
        annotated_args = get_args(inner)

        has_discriminator = any(
            isinstance(a, Discriminator) for a in annotated_args
        )
        assert has_discriminator, f"No Discriminator found in: {annotated_args}"

    def test_idempotent_double_apply(self):
        """Calling the patch function twice should not break anything."""
        from tinker.types.model_input import ModelInput
        from tinker.types.encoded_text_chunk import EncodedTextChunk

        from fireworks.training.sdk.patches._discriminator_patch import (
            _apply_discriminator_patch,
        )

        _apply_discriminator_patch()  # second call (first was at import time)

        mi = ModelInput(chunks=[EncodedTextChunk(tokens=[1, 2, 3])])
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            result = mi.model_dump(mode="json")

        assert result["chunks"][0]["type"] == "encoded_text"

    def test_r3_patch_still_works(self):
        """The R3 routing_matrices field should still be present."""
        from tinker.types.model_input import ModelInput

        assert "routing_matrices" in ModelInput.model_fields

        mi = ModelInput.from_ints([1, 2, 3], routing_matrices=["rm1"])
        assert mi.routing_matrices == ["rm1"]

        with warnings.catch_warnings():
            warnings.simplefilter("error")
            result = mi.model_dump(mode="json")

        assert result["routing_matrices"] == ["rm1"]
