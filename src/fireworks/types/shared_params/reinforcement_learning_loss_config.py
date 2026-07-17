# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["ReinforcementLearningLossConfig", "Dpo", "Orpo"]


class Dpo(TypedDict, total=False):
    """DPO-specific configuration. Intended for METHOD=DPO."""

    beta: float
    """DPO temperature parameter (beta in the paper). Must be > 0 and < 0.5."""

    ref_cache_batch_size: Annotated[int, PropertyInfo(alias="refCacheBatchSize")]
    """Number of preference pairs per reference forward call during caching."""

    ref_cache_concurrency: Annotated[int, PropertyInfo(alias="refCacheConcurrency")]
    """Max concurrent reference forward passes during cache warm-up."""


_OrpoReservedKeywords = TypedDict(
    "_OrpoReservedKeywords",
    {
        "lambda": float,
    },
    total=False,
)


class Orpo(_OrpoReservedKeywords, total=False):
    """ORPO-specific configuration. Intended for METHOD=ORPO."""

    pass


class ReinforcementLearningLossConfig(TypedDict, total=False):
    """Loss method + hyperparameters for reinforcement-learning-style fine-tuning (e.g.

    RFT / RL trainers).
    For preference jobs (DPO API), the default loss method is GRPO when METHOD_UNSPECIFIED.
    """

    dpo: Dpo
    """DPO-specific configuration. Intended for METHOD=DPO."""

    kl_beta: Annotated[float, PropertyInfo(alias="klBeta")]
    """
    KL coefficient (beta) override for GRPO-like methods. If unset, the trainer
    default is used.
    """

    method: Literal["METHOD_UNSPECIFIED", "GRPO", "DAPO", "DPO", "ORPO", "GSPO_TOKEN"]

    orpo: Orpo
    """ORPO-specific configuration. Intended for METHOD=ORPO."""
