# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Annotated, TypeAlias

from .._utils import PropertyInfo
from .response_text_block import ResponseTextBlock
from .response_thinking_block import ResponseThinkingBlock
from .response_tool_use_block import ResponseToolUseBlock
from .response_redacted_thinking_block import ResponseRedactedThinkingBlock

__all__ = ["ContentBlock"]

ContentBlock: TypeAlias = Annotated[
    Union[ResponseTextBlock, ResponseThinkingBlock, ResponseRedactedThinkingBlock, ResponseToolUseBlock],
    PropertyInfo(discriminator="type"),
]
