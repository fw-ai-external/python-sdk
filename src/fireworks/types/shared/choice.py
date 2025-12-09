# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional
from typing_extensions import Literal, TypeAlias

from ..._models import BaseModel

__all__ = [
    "Choice",
    "Logprobs",
    "LogprobsLogProbs",
    "LogprobsNewLogProbs",
    "LogprobsNewLogProbsContent",
    "LogprobsNewLogProbsContentTopLogprob",
    "RawOutput",
    "RawOutputCompletionLogprobs",
    "RawOutputCompletionLogprobsContent",
    "RawOutputCompletionLogprobsContentTopLogprob",
]


class LogprobsLogProbs(BaseModel):
    """Legacy log probabilities format"""

    text_offset: Optional[List[int]] = None

    token_ids: Optional[List[int]] = None

    token_logprobs: Optional[List[float]] = None

    tokens: Optional[List[str]] = None

    top_logprobs: Optional[List[Dict[str, float]]] = None


class LogprobsNewLogProbsContentTopLogprob(BaseModel):
    token: str

    logprob: float

    token_id: int

    bytes: Optional[List[int]] = None


class LogprobsNewLogProbsContent(BaseModel):
    token: str

    bytes: List[int]

    logprob: float

    sampling_logprob: Optional[float] = None

    text_offset: int

    token_id: int

    extra_logprobs: Optional[List[float]] = None

    extra_tokens: Optional[List[int]] = None

    last_activation: Optional[str] = None

    routing_matrix: Optional[str] = None

    top_logprobs: Optional[List[LogprobsNewLogProbsContentTopLogprob]] = None


class LogprobsNewLogProbs(BaseModel):
    """OpenAI-compatible log probabilities format"""

    content: Optional[List[LogprobsNewLogProbsContent]] = None


Logprobs: TypeAlias = Union[LogprobsLogProbs, LogprobsNewLogProbs, None]


class RawOutputCompletionLogprobsContentTopLogprob(BaseModel):
    token: str

    logprob: float

    token_id: int

    bytes: Optional[List[int]] = None


class RawOutputCompletionLogprobsContent(BaseModel):
    token: str

    bytes: List[int]

    logprob: float

    sampling_logprob: Optional[float] = None

    text_offset: int

    token_id: int

    extra_logprobs: Optional[List[float]] = None

    extra_tokens: Optional[List[int]] = None

    last_activation: Optional[str] = None

    routing_matrix: Optional[str] = None

    top_logprobs: Optional[List[RawOutputCompletionLogprobsContentTopLogprob]] = None


class RawOutputCompletionLogprobs(BaseModel):
    """OpenAI-compatible log probabilities format"""

    content: Optional[List[RawOutputCompletionLogprobsContent]] = None


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

    completion_logprobs: Optional[RawOutputCompletionLogprobs] = None
    """OpenAI-compatible log probabilities format"""

    completion_token_ids: Optional[List[int]] = None
    """Token IDs for the raw completion"""


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
