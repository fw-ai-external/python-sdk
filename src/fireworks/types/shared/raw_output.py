# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional

from ..._models import BaseModel
from .new_log_probs import NewLogProbs

__all__ = ["RawOutput"]


class RawOutput(BaseModel):
    """
    Extension of OpenAI that returns low-level interaction of what the model
    sees, including the formatted prompt and function calls
    """

    completion: str
    """Raw completion produced by the model before any tool calls are parsed"""

    prompt_fragments: List[Union[str, int]]
    """
    Pieces of the prompt (like individual messages) before truncation and
    concatenation. Depending on prompt_truncate_len some of the messages might be
    dropped. Contains a mix of strings to be tokenized and individual tokens (if
    dictated by the conversation template)
    """

    prompt_token_ids: List[int]
    """Fully processed prompt as seen by the model"""

    completion_logprobs: Optional[NewLogProbs] = None
    """OpenAI-compatible log probabilities format"""

    completion_token_ids: Optional[List[int]] = None
    """Token IDs for the raw completion"""

    grammar: Optional[str] = None
    """
    Grammar used for constrained decoding, can be either user provided (directly or
    JSON schema) or inferred by the chat template
    """

    images: Optional[List[str]] = None
    """Images in the prompt"""
