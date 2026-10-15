from __future__ import annotations

from typing import Optional
from typing_extensions import Literal

from fireworks.training.sdk._core._compat import ConfigDict
from fireworks.training.sdk._core._models import StrictBase

__all__ = ["CreateSamplingSessionRequest"]


class CreateSamplingSessionRequest(StrictBase):
    session_id: str
    """The session ID to create the sampling session within"""

    sampling_session_seq_id: int
    """Sequence ID for the sampling session within the session"""

    base_model: Optional[str] = None
    """Optional base model name to sample from.

    Is inferred from model_path, if provided. If sampling against a base model, this
    is required.
    """

    model_path: Optional[str] = None
    """Optional tinker:// path to your model weights or LoRA weights.

    If not provided, samples against the base model.
    """

    type: Literal["create_sampling_session"] = "create_sampling_session"

    model_config = ConfigDict(protected_namespaces=tuple())
