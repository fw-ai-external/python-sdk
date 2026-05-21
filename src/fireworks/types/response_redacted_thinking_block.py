from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["ResponseRedactedThinkingBlock"]


class ResponseRedactedThinkingBlock(BaseModel):
    data: str

    type: Literal["redacted_thinking"]
