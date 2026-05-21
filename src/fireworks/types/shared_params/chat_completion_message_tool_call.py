# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from typing_extensions import Required, TypeAlias, TypedDict

from .chat_completion_message_tool_call_function import ChatCompletionMessageToolCallFunction

__all__ = ["ChatCompletionMessageToolCall", "Function"]

Function: TypeAlias = Union[ChatCompletionMessageToolCallFunction, str]


class ChatCompletionMessageToolCall(TypedDict, total=False):
    function: Required[Function]
    """The function that the model called."""

    id: Optional[str]
    """The ID of the tool call."""

    type: str
    """The type of the tool. Currently, only `function` is supported."""
