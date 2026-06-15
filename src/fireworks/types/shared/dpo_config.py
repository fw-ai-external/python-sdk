# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["DpoConfig"]


class DpoConfig(BaseModel):
    """Hyperparameters for Direct Preference Optimization (DPO) training."""

    beta: Optional[float] = None
    """DPO temperature parameter (beta in the paper). Must be > 0 and < 0.5."""

    ref_cache_concurrency: Optional[int] = FieldInfo(alias="refCacheConcurrency", default=None)
    """Max concurrent reference forward passes during cache warm-up."""

    ref_cache_batch_size: Optional[int] = FieldInfo(alias="refCacheBatchSize", default=None)
    """Number of preference pairs per reference forward call during caching."""
