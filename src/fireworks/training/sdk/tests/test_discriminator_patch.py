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
        from tinker.types.dmel_chunk import DmelChunk
        from tinker.types.image_chunk import ImageChunk
        from tinker.types.model_input import ModelInput
        from tinker.types.encoded_text_chunk import EncodedTextChunk
        from tinker.types.image_asset_pointer_chunk import ImageAssetPointerChunk

        mi = ModelInput(
            chunks=[
                EncodedTextChunk(tokens=[1, 2, 3]),
                ImageChunk(data=b"fake", format="png"),
                ImageAssetPointerChunk(format="jpeg", location="s3://b/img.jpg"),
                DmelChunk(dmel=b"<dmel>example</dmel>"),
            ]
        )

        with warnings.catch_warnings():
            warnings.simplefilter("error")
            result = mi.model_dump(mode="json")

        assert result["chunks"][0]["type"] == "encoded_text"
        assert result["chunks"][1]["type"] == "image"
        assert result["chunks"][2]["type"] == "image_asset_pointer"
        assert result["chunks"][3]["type"] == "dmel"

    def test_dmel_deserialization_round_trip(self):
        """Tinker 0.23's DMEL renderer chunks remain in the patched union."""
        from tinker.types.dmel_chunk import DmelChunk
        from tinker.types.model_input import ModelInput

        model_input = ModelInput(chunks=[DmelChunk(dmel=b"<dmel>example</dmel>")])

        with warnings.catch_warnings():
            warnings.simplefilter("error")
            dumped = model_input.model_dump(mode="json")
            restored = ModelInput.model_validate(dumped)

        assert dumped["chunks"][0]["type"] == "dmel"
        assert isinstance(restored.chunks[0], DmelChunk)
        assert restored.chunks[0].dmel == b"<dmel>example</dmel>"

    def test_dmel_chunk_survives_wire_conversion(self):
        """The TML renderer's DMEL chunk reaches Tinker's JSON request body."""
        import tinker
        from tinker._compat import model_dump
        from tinker.types.dmel_chunk import DmelChunk
        from tinker.types.model_input import ModelInput
        from tinker.lib._pydantic_conv import to_pydantic_input
        from tinker.types.forward_backward_input import ForwardBackwardInput

        forward_backward_input = ForwardBackwardInput(
            data=[
                tinker.Datum(
                    model_input=ModelInput(chunks=[DmelChunk(dmel=b"<dmel>example</dmel>")]),
                    loss_fn_inputs={},
                )
            ],
            loss_fn="cross_entropy",
        )

        request_body = model_dump(
            to_pydantic_input(forward_backward_input),
            exclude_unset=False,
            exclude_none=True,
            mode="json",
        )

        chunk = request_body["data"][0]["model_input"]["chunks"][0]
        assert chunk["type"] == "dmel"

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

    def test_r3_patch_preserves_routing_matrices_in_wire_requests(self):
        """R3 matrices must survive Tinker's dataclass-to-wire conversion."""
        import tinker
        from tinker._compat import model_dump
        from tinker.types.model_input import ModelInput
        from tinker.lib._pydantic_conv import to_pydantic_request
        from tinker.types.forward_request import ForwardRequest
        from tinker.types.forward_backward_input import ForwardBackwardInput
        from tinker.types.forward_backward_request import ForwardBackwardRequest

        datum = tinker.Datum(
            model_input=ModelInput.from_ints(
                [1, 2, 3],
                routing_matrices=["", "rm1", "rm2"],
            ),
            loss_fn_inputs={
                "target_tokens": tinker.TensorData(
                    data=[2, 3, 4],
                    dtype="int64",
                    shape=[3],
                ),
            },
        )
        fb_input = ForwardBackwardInput(data=[datum], loss_fn="cross_entropy")

        forward_body = model_dump(
            to_pydantic_request(
                ForwardRequest(
                    forward_input=fb_input,
                    model_id="model",
                    seq_id=1,
                )
            ),
            exclude_unset=False,
            exclude_none=True,
            mode="json",
        )
        assert forward_body["forward_input"]["data"][0]["model_input"][
            "routing_matrices"
        ] == ["", "rm1", "rm2"]

        forward_backward_body = model_dump(
            to_pydantic_request(
                ForwardBackwardRequest(
                    forward_backward_input=fb_input,
                    model_id="model",
                    seq_id=2,
                )
            ),
            exclude_unset=False,
            exclude_none=True,
            mode="json",
        )
        assert forward_backward_body["forward_backward_input"]["data"][0][
            "model_input"
        ]["routing_matrices"] == ["", "rm1", "rm2"]
