# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["ReinforcementLearningLossConfig"]


class ReinforcementLearningLossConfig(BaseModel):
    """Loss method + hyperparameters for reinforcement-learning-style fine-tuning (e.g.

    RFT / RL trainers).
    """

    kl_beta: Optional[float] = FieldInfo(alias="klBeta", default=None)
    """
    KL coefficient (beta) override for GRPO-like methods. If unset, the trainer
    default is used.
    """

    method: Optional[Literal["METHOD_UNSPECIFIED", "GRPO", "DAPO"]] = None
