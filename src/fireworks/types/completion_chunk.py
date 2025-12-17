# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

import builtins
from typing import Dict, List, Union, Optional
from typing_extensions import Literal, TypeAlias

from .._models import BaseModel
from .shared.log_probs import LogProbs
from .shared.raw_output import RawOutput
from .shared.usage_info import UsageInfo
from .shared.new_log_probs import NewLogProbs

__all__ = ["CompletionChunk", "Choice", "ChoiceLogprobs"]

ChoiceLogprobs: TypeAlias = Union[LogProbs, NewLogProbs, None]


class Choice(BaseModel):
    """A streamed completion choice.

    Attributes:
      index (int): The index of the completion choice.
      text (str): The completion response.
      logprobs (float, optional): The log probabilities of the most likely tokens.
      finish_reason (str): The reason the model stopped generating tokens. This will be "stop" if
        the model hit a natural stop point or a provided stop sequence, or
        "length" if the maximum number of tokens specified in the request was
        reached.
      prompt_token_ids (Optional[List[int]]): Token IDs for the prompt (when return_token_ids=true, sent in first chunk)
      token_ids (Optional[List[int]]): Token IDs for this chunk (when return_token_ids=true)
    """

    index: int

    text: str

    finish_reason: Optional[Literal["stop", "length", "error"]] = None

    logprobs: Optional[ChoiceLogprobs] = None
    """Legacy log probabilities format"""

    prompt_token_ids: Optional[List[int]] = None

    raw_output: Optional[RawOutput] = None
    """
    Extension of OpenAI that returns low-level interaction of what the model sees,
    including the formatted prompt and function calls
    """

    token_ids: Optional[List[int]] = None


class CompletionChunk(BaseModel):
    """The streamed response message from a /v1/completions call."""

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

    usage: Optional[UsageInfo] = None
    """Usage statistics."""
