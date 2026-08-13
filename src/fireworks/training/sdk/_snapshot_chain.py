"""Shared base/delta sampler-snapshot logic for weight sync and hotload.

Both :class:`WeightSyncer` and the SDK-managed ``_TinkerSamplerBackend`` push
trainer snapshots to an inference deployment and must agree on two things:

  - choosing ``base`` vs ``delta`` for the next checkpoint (LoRA is always
    ``base``; full-parameter is ``base`` first, then ``delta``),
  - building the incremental hotload metadata that pins a ``delta`` to the
    previously loaded snapshot.

Centralizing the logic here keeps the two callers in lock-step: a mismatch
between the save-side checkpoint type and the hotload-side metadata silently
corrupts the delta chain.
"""

from __future__ import annotations

from typing import Any, Literal

from fireworks.training.sdk.deployment import DEFAULT_CHECKSUM_FORMAT

SamplerCheckpointType = Literal["base", "delta", "merged_base"]
ExportPrecision = Literal["source", "bf16", "nvfp4", "mxfp8", "fp8_block128"]

# ``merged_base`` is a LoRA-only export: the trainer folds the active LoRA
# adapter into the base weights and saves a full base checkpoint (no adapter
# metadata), which the server classifies as ``INFERENCE_BASE`` / ``HF_BASE_MODEL``.
# Like ``base`` it is a standalone full checkpoint, so it never participates in
# the delta chain or carries incremental hotload metadata.
_VALID_CHECKPOINT_TYPES = ("base", "delta", "merged_base")
_VALID_EXPORT_PRECISIONS = ("source", "bf16", "nvfp4", "mxfp8", "fp8_block128")
DEFAULT_MERGED_BASE_EXPORT_PRECISION: ExportPrecision = "source"


def normalize_checkpoint_type(checkpoint_type: str | None) -> SamplerCheckpointType | None:
    """Lower-case and validate a checkpoint type, or return ``None``."""
    if checkpoint_type is None:
        return None
    normalized = checkpoint_type.lower()
    if normalized in _VALID_CHECKPOINT_TYPES:
        return normalized  # type: ignore[return-value]
    raise ValueError(f"checkpoint_type must be one of {_VALID_CHECKPOINT_TYPES}")


def normalize_export_precision(
    precision: str | None,
) -> ExportPrecision | None:
    """Lower-case and validate a merged-base export precision."""
    if precision is None:
        return None
    normalized = precision.lower()
    if normalized in _VALID_EXPORT_PRECISIONS:
        return normalized  # type: ignore[return-value]
    raise ValueError(
        "export_precision must be one of "
        f"{_VALID_EXPORT_PRECISIONS}"
    )


def resolve_export_precision(
    *,
    checkpoint_type: SamplerCheckpointType,
    precision: str | None,
) -> ExportPrecision | None:
    """Resolve output precision without exposing source-storage details.

    ``merged_base`` is the only checkpoint type with a final-export precision.
    Omitting it means ``source``: the trainer discovers the source encoding from
    model metadata and re-encodes after merging. Other checkpoint types reject
    an explicit precision and otherwise carry no precision field.
    """
    normalized = normalize_export_precision(precision)
    if checkpoint_type == "merged_base":
        return normalized or DEFAULT_MERGED_BASE_EXPORT_PRECISION
    if normalized is not None:
        raise ValueError("export_precision requires checkpoint_type='merged_base'")
    return None


def resolve_next_checkpoint_type(
    *,
    lora_rank: int,
    base_saved: bool,
    first_checkpoint_type: str,
    explicit: str | None = None,
) -> SamplerCheckpointType:
    """Decide the checkpoint type for the next sampler save.

    An explicit override wins (including ``"merged_base"`` to fold a LoRA
    adapter into the base on save). LoRA otherwise always saves ``base``
    (adapters are standalone). Full-parameter saves ``first_checkpoint_type``
    until a base exists, then ``delta``.
    """
    override = normalize_checkpoint_type(explicit)
    if override is not None:
        return override
    if lora_rank > 0:
        return "base"
    if base_saved:
        return "delta"
    return normalize_checkpoint_type(first_checkpoint_type) or "base"


def build_incremental_metadata(
    *,
    lora_rank: int,
    checkpoint_type: str | None,
    base_identity: str | None,
    compression_format: str,
) -> dict[str, Any] | None:
    """Incremental hotload metadata for a ``delta`` checkpoint, else ``None``.

    Without this metadata the deployment loads the snapshot as non-delta
    (see :meth:`DeploymentManager.hotload`), which corrupts the delta chain
    for full-parameter training. LoRA never sends incremental metadata
    because the adapter is standalone. ``base`` and ``merged_base`` are full
    standalone checkpoints and likewise carry no incremental metadata.
    """
    if lora_rank > 0:
        return None
    if checkpoint_type == "delta" and base_identity:
        return {
            "previous_snapshot_identity": base_identity,
            "compression_format": compression_format,
            "checksum_format": DEFAULT_CHECKSUM_FORMAT,
        }
    return None
