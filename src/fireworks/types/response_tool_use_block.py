from typing import Dict
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["ResponseToolUseBlock"]


class ResponseToolUseBlock(BaseModel):
    id: str

    input: Dict[str, object]

    name: str

    type: Literal["tool_use"]
