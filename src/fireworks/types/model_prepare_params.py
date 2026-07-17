# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["ModelPrepareParams"]


class ModelPrepareParams(TypedDict, total=False):
    account_id: str

    abort: bool
    """
    If true, abort an active prepare job and clear prepare tracking state. No new
    prepare job is launched in this request.
    """

    accelerator_count: Annotated[int, PropertyInfo(alias="acceleratorCount")]
    """Number of accelerators (GPUs) to use for quantization. Defaults to 8 if unset."""

    precision: Literal[
        "PRECISION_UNSPECIFIED",
        "FP16",
        "FP8",
        "FP8_MM",
        "FP8_AR",
        "FP8_MM_KV_ATTN",
        "FP8_KV",
        "FP8_MM_V2",
        "FP8_V2",
        "FP8_MM_KV_ATTN_V2",
        "NF4",
        "FP4",
        "BF16",
        "FP4_BLOCKSCALED_MM",
        "FP4_MX_MOE",
    ]

    read_mask: Annotated[str, PropertyInfo(alias="readMask")]
