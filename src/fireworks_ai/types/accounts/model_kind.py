# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal, TypeAlias

__all__ = ["ModelKind"]

ModelKind: TypeAlias = Literal[
    "KIND_UNSPECIFIED",
    "HF_BASE_MODEL",
    "HF_PEFT_ADDON",
    "HF_TEFT_ADDON",
    "FLUMINA_BASE_MODEL",
    "FLUMINA_ADDON",
    "DRAFT_ADDON",
    "FIRE_AGENT",
    "LIVE_MERGE",
    "CUSTOM_MODEL",
    "EMBEDDING_MODEL",
    "SNAPSHOT_MODEL",
]
