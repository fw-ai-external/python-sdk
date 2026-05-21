from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["ResponseThinkingBlock"]


class ResponseThinkingBlock(BaseModel):
    signature: str

    thinking: str

    type: Literal["thinking"]
