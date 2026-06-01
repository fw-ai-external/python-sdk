"""Shared helpers for patching generated tinker models."""

from __future__ import annotations


def rebuild_model(model: type) -> None:
    rebuild = getattr(model, "model_rebuild", None)
    if rebuild is not None:
        rebuild(force=True)
        return
    update_forward_refs = getattr(model, "update_forward_refs", None)
    if update_forward_refs is not None:
        update_forward_refs()
