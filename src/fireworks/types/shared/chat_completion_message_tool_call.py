# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union, Optional
from typing_extensions import TypeAlias

from ..._models import BaseModel
from .chat_completion_message_tool_call_function import ChatCompletionMessageToolCallFunction

__all__ = ["ChatCompletionMessageToolCall", "Function"]

Function: TypeAlias = Union[ChatCompletionMessageToolCallFunction, str]


class ChatCompletionMessageToolCall(BaseModel):
    function: Function
    """The function that the model called."""

    id: Optional[str] = None
    """The ID of the tool call."""

    type: Optional[str] = None
    """The type of the tool. Currently, only `function` is supported."""
