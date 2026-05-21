# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, TypeAlias

from ..._models import BaseModel
from .log_probs import LogProbs
from .raw_output import RawOutput
from .new_log_probs import NewLogProbs

__all__ = ["Choice", "Logprobs"]

Logprobs: TypeAlias = Union[LogProbs, NewLogProbs, None]


class Choice(BaseModel):
    """A completion choice."""

    index: int
    """The index of the completion choice"""

    text: str
    """The completion response"""

    finish_reason: Optional[Literal["stop", "length", "error"]] = None
    """The reason the model stopped generating tokens.

    This will be "stop" if the model hit a natural stop point or a provided stop
    sequence, or "length" if the maximum number of tokens specified in the request
    was reached
    """

    logprobs: Optional[Logprobs] = None
    """The log probabilities of the most likely tokens"""

    prompt_token_ids: Optional[List[int]] = None
    """Token IDs for the prompt (when return_token_ids=true)"""

    raw_output: Optional[RawOutput] = None
    """
    Extension of OpenAI that returns low-level interaction of what the model sees,
    including the formatted prompt and function calls
    """

    token_ids: Optional[List[int]] = None
    """Token IDs for the generated completion (when return_token_ids=true)"""
