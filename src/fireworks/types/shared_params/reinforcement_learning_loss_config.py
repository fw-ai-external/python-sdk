# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["ReinforcementLearningLossConfig"]


class ReinforcementLearningLossConfig(TypedDict, total=False):
    """Loss method + hyperparameters for reinforcement-learning-style fine-tuning (e.g.

    RFT / RL trainers).
    For preference jobs (DPO API), the default loss method is DPO when METHOD_UNSPECIFIED.
    For RFT jobs, the default loss method is GRPO when METHOD_UNSPECIFIED.
    """

    kl_beta: Annotated[float, PropertyInfo(alias="klBeta")]
    """
    KL coefficient (beta) override for GRPO-like methods. If unset, the trainer
    default is used.
    """

    method: Literal["METHOD_UNSPECIFIED", "GRPO", "DAPO", "DPO", "ORPO", "GSPO_TOKEN"]
