# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal, TypeAlias

__all__ = ["DeploymentPrecision"]

DeploymentPrecision: TypeAlias = Literal[
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
