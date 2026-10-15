from typing import Literal, Optional

from fireworks.training.sdk._core._compat import ConfigDict
from fireworks.training.sdk._core._models import BaseModel
from fireworks.training.sdk.types.model_id import ModelID


class ModelData(BaseModel):
    """Metadata about a model's architecture and configuration."""

    arch: Optional[str] = None
    """The model architecture identifier."""

    model_name: Optional[str] = None
    """The human-readable model name."""

    tokenizer_id: Optional[str] = None
    """The identifier of the tokenizer used by this model."""


class GetInfoResponse(BaseModel):
    """Response containing information about a training client's model."""

    type: Optional[Literal["get_info"]] = None
    """Response type identifier."""

    model_data: ModelData
    """Detailed metadata about the model."""

    model_id: ModelID
    """Unique identifier for the model."""

    is_lora: Optional[bool] = None
    """Whether this is a LoRA fine-tuned model."""

    lora_rank: Optional[int] = None
    """The rank of the LoRA adaptation, if applicable."""

    model_name: Optional[str] = None
    """The name of the model."""

    model_config = ConfigDict(protected_namespaces=tuple())
