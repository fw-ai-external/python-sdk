# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["DpoConfig"]


class DpoConfig(TypedDict, total=False):
    """Hyperparameters for Direct Preference Optimization (DPO) training."""

    beta: float
    """DPO temperature parameter (beta in the paper). Must be > 0 and < 0.5."""

    ref_cache_concurrency: Annotated[int, PropertyInfo(alias="refCacheConcurrency")]
    """Max concurrent reference forward passes during cache warm-up."""

    ref_cache_batch_size: Annotated[int, PropertyInfo(alias="refCacheBatchSize")]
    """Number of preference pairs per reference forward call during caching."""
