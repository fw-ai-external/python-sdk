# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

import builtins
from typing import Dict, List, Union, Optional
from typing_extensions import Literal, TypeAlias

from .._models import BaseModel

__all__ = [
    "CompletionChunk",
    "Choice",
    "ChoiceLogprobs",
    "ChoiceLogprobsLogProbs",
    "ChoiceLogprobsNewLogProbs",
    "ChoiceLogprobsNewLogProbsContent",
    "ChoiceLogprobsNewLogProbsContentTopLogprob",
    "ChoiceRawOutput",
    "ChoiceRawOutputCompletionLogprobs",
    "ChoiceRawOutputCompletionLogprobsContent",
    "ChoiceRawOutputCompletionLogprobsContentTopLogprob",
    "Usage",
    "UsagePromptTokensDetails",
]


class ChoiceLogprobsLogProbs(BaseModel):
    text_offset: Optional[List[int]] = None

    token_ids: Optional[List[int]] = None

    token_logprobs: Optional[List[float]] = None

    tokens: Optional[List[str]] = None

    top_logprobs: Optional[List[Dict[str, float]]] = None


class ChoiceLogprobsNewLogProbsContentTopLogprob(BaseModel):
    token: str

    logprob: float

    token_id: int

    bytes: Optional[List[int]] = None


class ChoiceLogprobsNewLogProbsContent(BaseModel):
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

    top_logprobs: Optional[List[ChoiceLogprobsNewLogProbsContentTopLogprob]] = None


class ChoiceLogprobsNewLogProbs(BaseModel):
    content: Optional[List[ChoiceLogprobsNewLogProbsContent]] = None


ChoiceLogprobs: TypeAlias = Union[ChoiceLogprobsLogProbs, ChoiceLogprobsNewLogProbs, None]


class ChoiceRawOutputCompletionLogprobsContentTopLogprob(BaseModel):
    token: str

    logprob: float

    token_id: int

    bytes: Optional[List[int]] = None


class ChoiceRawOutputCompletionLogprobsContent(BaseModel):
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

    top_logprobs: Optional[List[ChoiceRawOutputCompletionLogprobsContentTopLogprob]] = None


class ChoiceRawOutputCompletionLogprobs(BaseModel):
    content: Optional[List[ChoiceRawOutputCompletionLogprobsContent]] = None


class ChoiceRawOutput(BaseModel):
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

    completion_logprobs: Optional[ChoiceRawOutputCompletionLogprobs] = None
    """OpenAI-compatible log probabilities format"""

    completion_token_ids: Optional[List[int]] = None
    """Token IDs for the raw completion"""


class Choice(BaseModel):
    index: int

    text: str

    finish_reason: Optional[Literal["stop", "length", "error"]] = None

    logprobs: Optional[ChoiceLogprobs] = None
    """Legacy log probabilities format"""

    prompt_token_ids: Optional[List[int]] = None

    raw_output: Optional[ChoiceRawOutput] = None
    """
    Extension of OpenAI that returns low-level interaction of what the model sees,
    including the formatted prompt and function calls
    """

    token_ids: Optional[List[int]] = None


class UsagePromptTokensDetails(BaseModel):
    cached_tokens: Optional[int] = None


class Usage(BaseModel):
    prompt_tokens: int
    """The number of tokens in the prompt"""

    total_tokens: int
    """The total number of tokens used in the request (prompt + completion)"""

    completion_tokens: Optional[int] = None
    """The number of tokens in the generated completion"""

    prompt_tokens_details: Optional[UsagePromptTokensDetails] = None
    """Details about prompt tokens, including cached tokens"""


class CompletionChunk(BaseModel):
    id: str
    """A unique identifier of the response"""

    choices: List[Choice]
    """The list of streamed completion choices"""

    created: int
    """The Unix time in seconds when the response was generated"""

    model: str
    """The model used for the chat completion"""

    object: Optional[str] = None
    """The object type, which is always "text_completion" """

    perf_metrics: Optional[Dict[str, builtins.object]] = None
    """See parameter [perf_metrics_in_response](#body-perf-metrics-in-response)"""

    usage: Optional[Usage] = None
    """Usage statistics."""
