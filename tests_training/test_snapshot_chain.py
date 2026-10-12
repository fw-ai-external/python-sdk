"""Tests for the shared base/delta sampler-snapshot helpers."""

from __future__ import annotations

import pytest

from fireworks.training.sdk._snapshot_chain import (
    DEFAULT_MERGED_BASE_EXPORT_PRECISION,
    resolve_export_precision,
    normalize_checkpoint_type,
    build_incremental_metadata,
    normalize_export_precision,
    resolve_next_checkpoint_type,
)


class TestNormalizeCheckpointType:
    def test_none_passthrough(self):
        assert normalize_checkpoint_type(None) is None

    def test_lowercases(self):
        assert normalize_checkpoint_type("BASE") == "base"
        assert normalize_checkpoint_type("Delta") == "delta"

    def test_accepts_merged_base(self):
        assert normalize_checkpoint_type("merged_base") == "merged_base"
        assert normalize_checkpoint_type("MERGED_BASE") == "merged_base"

    def test_rejects_unknown(self):
        with pytest.raises(ValueError, match="checkpoint_type"):
            normalize_checkpoint_type("full")


class TestNormalizeMergedBasePrecision:
    def test_none_passthrough(self):
        assert normalize_export_precision(None) is None

    def test_lowercases_supported_targets(self):
        assert normalize_export_precision("BF16") == "bf16"
        assert normalize_export_precision("source") == "source"
        assert normalize_export_precision("NVFP4") == "nvfp4"
        assert normalize_export_precision("mxfp8") == "mxfp8"
        assert normalize_export_precision("fp8_block128") == "fp8_block128"

    def test_rejects_unknown_target(self):
        with pytest.raises(ValueError, match="export_precision"):
            normalize_export_precision("fp6")

    def test_merged_base_defaults_to_source(self):
        assert DEFAULT_MERGED_BASE_EXPORT_PRECISION == "source"
        assert (
            resolve_export_precision(checkpoint_type="merged_base", precision=None)
            == "source"
        )

    def test_explicit_output_override_wins(self):
        assert (
            resolve_export_precision(checkpoint_type="merged_base", precision="NVFP4")
            == "nvfp4"
        )

    def test_non_merged_save_has_no_precision(self):
        assert resolve_export_precision(checkpoint_type="base", precision=None) is None
        with pytest.raises(ValueError, match="requires checkpoint_type='merged_base'"):
            resolve_export_precision(checkpoint_type="delta", precision="bf16")


class TestResolveNextCheckpointType:
    def test_full_param_base_then_delta(self):
        assert resolve_next_checkpoint_type(
            lora_rank=0, base_saved=False, first_checkpoint_type="base"
        ) == "base"
        assert resolve_next_checkpoint_type(
            lora_rank=0, base_saved=True, first_checkpoint_type="base"
        ) == "delta"

    def test_lora_always_base(self):
        assert resolve_next_checkpoint_type(
            lora_rank=8, base_saved=True, first_checkpoint_type="base"
        ) == "base"

    def test_explicit_override_wins(self):
        assert resolve_next_checkpoint_type(
            lora_rank=0, base_saved=True, first_checkpoint_type="base", explicit="base"
        ) == "base"

    def test_explicit_merged_base_override(self):
        assert resolve_next_checkpoint_type(
            lora_rank=8, base_saved=True, first_checkpoint_type="base", explicit="merged_base"
        ) == "merged_base"


class TestBuildIncrementalMetadata:
    def test_full_param_delta_pins_previous(self):
        meta = build_incremental_metadata(
            lora_rank=0, checkpoint_type="delta", base_identity="snap-1", compression_format="arc_v2"
        )
        assert meta == {
            "previous_snapshot_identity": "snap-1",
            "compression_format": "arc_v2",
            "checksum_format": "alder32",
        }

    def test_base_has_no_metadata(self):
        assert build_incremental_metadata(
            lora_rank=0, checkpoint_type="base", base_identity="snap-1", compression_format="arc_v2"
        ) is None

    def test_merged_base_has_no_metadata(self):
        assert build_incremental_metadata(
            lora_rank=8, checkpoint_type="merged_base", base_identity="snap-1", compression_format="arc_v2"
        ) is None

    def test_delta_without_base_identity_has_no_metadata(self):
        assert build_incremental_metadata(
            lora_rank=0, checkpoint_type="delta", base_identity=None, compression_format="arc_v2"
        ) is None

    def test_lora_never_sends_metadata(self):
        assert build_incremental_metadata(
            lora_rank=8, checkpoint_type="delta", base_identity="snap-1", compression_format="arc_v2"
        ) is None
