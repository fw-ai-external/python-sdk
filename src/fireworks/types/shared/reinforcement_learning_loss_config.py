# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["ReinforcementLearningLossConfig", "Dpo", "Orpo"]


class Dpo(BaseModel):
    """DPO-specific configuration. Intended for METHOD=DPO."""

    beta: Optional[float] = None
    """DPO temperature parameter (beta in the paper)."""

    ref_cache_batch_size: Optional[int] = FieldInfo(alias="refCacheBatchSize", default=None)
    """Number of preference pairs per reference forward call during caching."""

    ref_cache_concurrency: Optional[int] = FieldInfo(alias="refCacheConcurrency", default=None)
    """Max concurrent reference forward passes during cache warm-up."""


class Orpo(BaseModel):
    """ORPO-specific configuration. Intended for METHOD=ORPO."""

    lambda_: Optional[float] = FieldInfo(alias="lambda", default=None)
    """Weight for the ORPO odds-ratio loss term."""


class ReinforcementLearningLossConfig(BaseModel):
    """Loss method + hyperparameters for reinforcement-learning-style fine-tuning (e.g.

    RFT / RL trainers).
    For preference jobs (DPO API), the default loss method is GRPO when METHOD_UNSPECIFIED.
    """

    dpo: Optional[Dpo] = None
    """DPO-specific configuration. Intended for METHOD=DPO."""

    kl_beta: Optional[float] = FieldInfo(alias="klBeta", default=None)
    """
    KL coefficient (beta) override for GRPO-like methods. If unset, the trainer
    default is used.
    """

    method: Optional[Literal["METHOD_UNSPECIFIED", "GRPO", "DAPO", "DPO", "ORPO", "GSPO_TOKEN"]] = None

    orpo: Optional[Orpo] = None
    """ORPO-specific configuration. Intended for METHOD=ORPO."""
