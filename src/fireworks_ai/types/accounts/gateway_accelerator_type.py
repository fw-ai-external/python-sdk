# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal, TypeAlias

__all__ = ["GatewayAcceleratorType"]

GatewayAcceleratorType: TypeAlias = Literal[
    "ACCELERATOR_TYPE_UNSPECIFIED",
    "NVIDIA_A100_80GB",
    "NVIDIA_H100_80GB",
    "AMD_MI300X_192GB",
    "NVIDIA_A10G_24GB",
    "NVIDIA_A100_40GB",
    "NVIDIA_L4_24GB",
    "NVIDIA_H200_141GB",
    "NVIDIA_B200_180GB",
    "AMD_MI325X_256GB",
]
