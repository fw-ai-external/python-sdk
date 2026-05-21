from typing import List, Optional

from ..._models import BaseModel
from .new_log_probs_content import NewLogProbsContent

__all__ = ["NewLogProbs"]


class NewLogProbs(BaseModel):
    """OpenAI-compatible log probabilities format"""

    content: Optional[List[NewLogProbsContent]] = None
