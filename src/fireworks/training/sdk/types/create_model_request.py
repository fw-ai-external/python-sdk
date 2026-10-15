from typing import Any, Optional
from typing_extensions import Literal

from fireworks.training.sdk._core._compat import ConfigDict
from fireworks.training.sdk._core._models import StrictBase
from fireworks.training.sdk.types.lora_config import LoraConfig

__all__ = ["CreateModelRequest"]


class CreateModelRequest(StrictBase):
    projection_head_dim: Optional[int] = None

    session_id: str

    model_seq_id: int

    base_model: str
    """The name of the base model to fine-tune (e.g., 'Qwen/Qwen3-8B')."""

    user_metadata: Optional[dict[str, Any]] = None
    """Optional metadata about this model/training run, set by the end-user."""

    lora_config: Optional[LoraConfig] = None
    """LoRA configuration"""

    type: Literal["create_model"] = "create_model"

    model_config = ConfigDict(protected_namespaces=tuple())
