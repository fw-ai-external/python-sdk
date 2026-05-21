from typing import Optional

from ..._models import BaseModel

__all__ = ["PromptTokensDetails"]


class PromptTokensDetails(BaseModel):
    cached_tokens: Optional[int] = None
