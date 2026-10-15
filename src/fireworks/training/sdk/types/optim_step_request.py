from __future__ import annotations

from typing import Optional
from typing_extensions import Literal

from fireworks.training.sdk._core._compat import ConfigDict
from fireworks.training.sdk._core._models import StrictBase
from fireworks.training.sdk.types.model_id import ModelID

__all__ = ["OptimStepRequest", "AdamParams"]


class AdamParams(StrictBase):
    emit_grad_norm_metrics: Literal["off", "basic", "detailed"] | bool | None = None

    learning_rate: float = 0.0001
    """Learning rate for the optimizer"""

    beta1: float = 0.9
    """Coefficient used for computing running averages of gradient"""

    beta2: float = 0.95
    """Coefficient used for computing running averages of gradient square"""

    eps: float = 1e-12
    """Term added to the denominator to improve numerical stability"""

    weight_decay: float = 0.0
    """Weight decay for the optimizer. Uses decoupled weight decay."""

    grad_clip_norm: float = 0.0
    """Maximum global gradient norm. If the global gradient norm is greater than this value, it will be clipped to this value. 0.0 means no clipping."""


class OptimStepRequest(StrictBase):
    adam_params: AdamParams

    model_id: ModelID

    seq_id: Optional[int] = None

    type: Literal["optim_step"] = "optim_step"

    model_config = ConfigDict(protected_namespaces=tuple())
