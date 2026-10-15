from typing import Optional

from fireworks.training.sdk._core._models import StrictBase

__all__ = ["LoraConfig"]


class LoraConfig(StrictBase):
    alpha: Optional[int] = None
    init_method: Optional[str] = None

    rank: int
    """LoRA rank (dimension of low-rank matrices)"""

    seed: Optional[int] = None
    """Seed used for initialization of LoRA weights.

    Useful if you need deterministic or reproducible initialization of weights.
    """

    train_unembed: bool = True
    """Whether to add lora to the unembedding layer"""

    train_mlp: bool = True
    """Whether to add loras to the MLP layers (including MoE layers)"""

    train_attn: bool = True
    """Whether to add loras to the attention layers"""
