# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable, Optional
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from .._types import SequenceNotStr, Base64FileInput
from .._utils import PropertyInfo
from .._models import set_pydantic_config
from .content_block import ContentBlock
from .request_text_block_param import RequestTextBlockParam
from .request_image_block_param import RequestImageBlockParam
from .cache_control_ephemeral_param import CacheControlEphemeralParam

__all__ = [
    "MessageCreateParams",
    "Message",
    "MessageContentUnionMember1AnthropicRequestDocumentBlock",
    "MessageContentUnionMember1AnthropicRequestDocumentBlockSource",
    "MessageContentUnionMember1AnthropicRequestDocumentBlockSourceAnthropicBase64PdfSource",
    "MessageContentUnionMember1AnthropicRequestDocumentBlockSourceAnthropicPlainTextSource",
    "MessageContentUnionMember1AnthropicRequestDocumentBlockSourceAnthropicContentBlockSource",
    "MessageContentUnionMember1AnthropicRequestDocumentBlockSourceAnthropicContentBlockSourceContentContentBlockSourceContent",
    "MessageContentUnionMember1AnthropicRequestDocumentBlockSourceAnthropicUrlpdfSource",
    "MessageContentUnionMember1AnthropicRequestDocumentBlockCitations",
    "MessageContentUnionMember1AnthropicRequestThinkingBlock",
    "MessageContentUnionMember1AnthropicRequestRedactedThinkingBlock",
    "MessageContentUnionMember1AnthropicRequestToolUseBlock",
    "MessageContentUnionMember1AnthropicRequestToolResultBlock",
    "Content",
    "ContentAnthropicRequestDocumentBlock",
    "ContentAnthropicRequestDocumentBlockSource",
    "ContentAnthropicRequestDocumentBlockSourceAnthropicBase64PdfSource",
    "ContentAnthropicRequestDocumentBlockSourceAnthropicPlainTextSource",
    "ContentAnthropicRequestDocumentBlockSourceAnthropicContentBlockSource",
    "ContentAnthropicRequestDocumentBlockSourceAnthropicContentBlockSourceContentContentBlockSourceContent",
    "ContentAnthropicRequestDocumentBlockSourceAnthropicUrlpdfSource",
    "ContentAnthropicRequestDocumentBlockCitations",
    "Metadata",
    "OutputConfig",
    "OutputConfigFormat",
    "Thinking",
    "ThinkingAnthropicThinkingConfigEnabled",
    "ThinkingAnthropicThinkingConfigDisabled",
    "ThinkingAnthropicThinkingConfigAdaptive",
    "ToolChoice",
    "ToolChoiceAnthropicToolChoiceAuto",
    "ToolChoiceAnthropicToolChoiceAny",
    "ToolChoiceAnthropicToolChoiceTool",
    "ToolChoiceAnthropicToolChoiceNone",
    "Tool",
    "ToolInputSchema",
]


class MessageCreateParams(TypedDict, total=False):
    messages: Required[Iterable[Message]]
    """Input messages.

    Models are trained to operate on alternating `user` and `assistant`
    conversational turns. When creating a new `Message`, you specify the prior
    conversational turns with the `messages` parameter, and the model then generates
    the next `Message` in the conversation. Consecutive `user` or `assistant` turns
    in your request will be combined into a single turn.

    Each input message must be an object with a `role` and `content`. You can
    specify a single `user`-role message, or you can include multiple `user` and
    `assistant` messages.

    If the final message uses the `assistant` role, the response content will
    continue immediately from the content in that message. This can be used to
    constrain part of the model's response.

    Example with a single `user` message:

    ```json
    [{ "role": "user", "content": "Hello" }]
    ```

    Example with multiple conversational turns:

    ```json
    [
      { "role": "user", "content": "Hello there." },
      {
        "role": "assistant",
        "content": "Hi, I'm here to help. How can I help you?"
      },
      { "role": "user", "content": "Can you explain LLMs in plain English?" }
    ]
    ```

    Example with a partially-filled response from the model:

    ```json
    [
      {
        "role": "user",
        "content": "What's the Greek name for Sun? (A) Sol (B) Helios (C) Sun"
      },
      { "role": "assistant", "content": "The best answer is (" }
    ]
    ```

    Each input message `content` may be either a single `string` or an array of
    content blocks, where each block has a specific `type`. Using a `string` for
    `content` is shorthand for an array of one content block of type `"text"`. The
    following input messages are equivalent:

    ```json
    { "role": "user", "content": "Hello" }
    ```

    ```json
    { "role": "user", "content": [{ "type": "text", "text": "Hello" }] }
    ```

    See [input examples](https://docs.claude.com/en/api/messages-examples).

    Note that if you want to include a
    [system prompt](/guides/querying-text-models), you can use the top-level
    `system` parameter — there is no `"system"` role for input messages in the
    Messages API.

    There is a limit of 100,000 messages in a single request.
    """

    model: Required[str]
    """The model that will complete your prompt.

    See the [Fireworks Model Library](https://app.fireworks.ai/models) for available
    models.
    """

    max_tokens: int
    """The maximum number of tokens to generate before stopping.

    Note that models may stop _before_ reaching this maximum. This parameter only
    specifies the absolute maximum number of tokens to generate.

    Different models have different maximum values for this parameter. See
    [models](https://app.fireworks.ai/models) for details.
    """

    metadata: Metadata
    """An object describing metadata about the request."""

    output_config: OutputConfig
    """Configuration options for the model's output, such as the output format."""

    raw_output: Optional[bool]
    """Return raw output from the model."""

    stop_sequences: SequenceNotStr[str]
    """Custom text sequences that will cause the model to stop generating.

    Models will normally stop when they have naturally completed their turn, which
    will result in a response `stop_reason` of `"end_turn"`.

    If you want the model to stop generating when it encounters custom strings of
    text, you can use the `stop_sequences` parameter. If the model encounters one of
    the custom sequences, the response `stop_reason` value will be `"stop_sequence"`
    and the response `stop_sequence` value will contain the matched stop sequence.
    """

    stream: bool
    """Whether to incrementally stream the response using server-sent events.

    See [streaming](/guides/querying-text-models) for details.
    """

    system: Union[str, Iterable[RequestTextBlockParam]]
    """System prompt.

    A system prompt is a way of providing context and instructions to the model,
    such as specifying a particular goal or role. See the
    [guide to system prompts](/guides/querying-text-models).
    """

    temperature: float
    """Amount of randomness injected into the response.

    Defaults to `1.0`. Ranges from `0.0` to `1.0`. Use `temperature` closer to `0.0`
    for analytical / multiple choice, and closer to `1.0` for creative and
    generative tasks.

    Note that even with `temperature` of `0.0`, the results will not be fully
    deterministic.
    """

    thinking: Thinking
    """Configuration for enabling the model's extended thinking.

    When enabled, responses include `thinking` content blocks showing the model's
    thinking process before the final answer. Requires a minimum budget of 1,024
    tokens and counts towards your `max_tokens` limit.

    See [reasoning](/guides/reasoning) for details.

    **Note:** The `adaptive` thinking type is not supported yet.
    """

    tool_choice: ToolChoice
    """How the model should use the provided tools.

    The model can use a specific tool, any available tool, decide by itself, or not
    use tools at all.
    """

    tools: Iterable[Tool]
    """Definitions of tools that the model may use.

    If you include `tools` in your API request, the model may return `tool_use`
    content blocks that represent the model's use of those tools. You can then run
    those tools using the tool input generated by the model and then optionally
    return results back to the model using `tool_result` content blocks.

    Each tool definition includes:

    - `name`: Name of the tool.
    - `description`: Optional, but strongly-recommended description of the tool.
    - `input_schema`: [JSON schema](https://json-schema.org/draft/2020-12) for the
      tool `input` shape that the model will produce in `tool_use` output content
      blocks.

    For example, if you defined `tools` as:

    ```json
    [
      {
        "name": "get_stock_price",
        "description": "Get the current stock price for a given ticker symbol.",
        "input_schema": {
          "type": "object",
          "properties": {
            "ticker": {
              "type": "string",
              "description": "The stock ticker symbol, e.g. AAPL for Apple Inc."
            }
          },
          "required": ["ticker"]
        }
      }
    ]
    ```

    And then asked the model "What's the S&P 500 at today?", the model might produce
    `tool_use` content blocks in the response like this:

    ```json
    [
      {
        "type": "tool_use",
        "id": "toolu_01D7FLrfh4GYq7yT1ULFeyMV",
        "name": "get_stock_price",
        "input": { "ticker": "^GSPC" }
      }
    ]
    ```

    You might then run your `get_stock_price` tool with `{"ticker": "^GSPC"}` as an
    input, and return the following back to the model in a subsequent `user`
    message:

    ```json
    [
      {
        "type": "tool_result",
        "tool_use_id": "toolu_01D7FLrfh4GYq7yT1ULFeyMV",
        "content": "259.75 USD"
      }
    ]
    ```

    Tools can be used for workflows that include running client-side tools and
    functions, or more generally whenever you want the model to produce a particular
    JSON structure of output.

    See the [guide](/guides/function-calling) for more details.
    """

    top_k: int
    """Only sample from the top K options for each subsequent token.

    Used to remove "long tail" low probability responses.
    [Learn more technical details here](https://towardsdatascience.com/how-to-sample-from-language-models-682bceb97277).

    Recommended for advanced use cases only. You usually only need to use
    `temperature`.
    """

    top_p: float
    """Use nucleus sampling.

    In nucleus sampling, we compute the cumulative distribution over all the options
    for each subsequent token in decreasing probability order and cut it off once it
    reaches a particular probability specified by `top_p`. You should either alter
    `temperature` or `top_p`, but not both.

    Recommended for advanced use cases only. You usually only need to use
    `temperature`.
    """


class MessageContentUnionMember1AnthropicRequestDocumentBlockSourceAnthropicBase64PdfSource(TypedDict, total=False):
    data: Required[Annotated[Union[str, Base64FileInput], PropertyInfo(format="base64")]]

    media_type: Required[Literal["application/pdf"]]

    type: Required[Literal["base64"]]


set_pydantic_config(
    MessageContentUnionMember1AnthropicRequestDocumentBlockSourceAnthropicBase64PdfSource,
    {"arbitrary_types_allowed": True},
)


class MessageContentUnionMember1AnthropicRequestDocumentBlockSourceAnthropicPlainTextSource(TypedDict, total=False):
    data: Required[str]

    media_type: Required[Literal["text/plain"]]

    type: Required[Literal["text"]]


MessageContentUnionMember1AnthropicRequestDocumentBlockSourceAnthropicContentBlockSourceContentContentBlockSourceContent: TypeAlias = Union[
    RequestTextBlockParam, RequestImageBlockParam
]


class MessageContentUnionMember1AnthropicRequestDocumentBlockSourceAnthropicContentBlockSource(TypedDict, total=False):
    content: Required[
        Union[
            str,
            Iterable[
                MessageContentUnionMember1AnthropicRequestDocumentBlockSourceAnthropicContentBlockSourceContentContentBlockSourceContent
            ],
        ]
    ]

    type: Required[Literal["content"]]


class MessageContentUnionMember1AnthropicRequestDocumentBlockSourceAnthropicUrlpdfSource(TypedDict, total=False):
    type: Required[Literal["url"]]

    url: Required[str]


MessageContentUnionMember1AnthropicRequestDocumentBlockSource: TypeAlias = Union[
    MessageContentUnionMember1AnthropicRequestDocumentBlockSourceAnthropicBase64PdfSource,
    MessageContentUnionMember1AnthropicRequestDocumentBlockSourceAnthropicPlainTextSource,
    MessageContentUnionMember1AnthropicRequestDocumentBlockSourceAnthropicContentBlockSource,
    MessageContentUnionMember1AnthropicRequestDocumentBlockSourceAnthropicUrlpdfSource,
]


class MessageContentUnionMember1AnthropicRequestDocumentBlockCitations(TypedDict, total=False):
    enabled: bool


class MessageContentUnionMember1AnthropicRequestDocumentBlock(TypedDict, total=False):
    """
    Document content, either specified directly as base64 data, as text, or as a reference via a URL.
    """

    source: Required[MessageContentUnionMember1AnthropicRequestDocumentBlockSource]

    type: Required[Literal["document"]]

    cache_control: Optional[CacheControlEphemeralParam]
    """Create a cache control breakpoint at this content block."""

    citations: Optional[MessageContentUnionMember1AnthropicRequestDocumentBlockCitations]

    context: Optional[str]

    title: Optional[str]


class MessageContentUnionMember1AnthropicRequestThinkingBlock(TypedDict, total=False):
    """A block specifying internal thinking by the model."""

    signature: Required[str]

    thinking: Required[str]

    type: Required[Literal["thinking"]]


class MessageContentUnionMember1AnthropicRequestRedactedThinkingBlock(TypedDict, total=False):
    """A block specifying internal, redacted thinking by the model."""

    data: Required[str]

    type: Required[Literal["redacted_thinking"]]


class MessageContentUnionMember1AnthropicRequestToolUseBlock(TypedDict, total=False):
    """A block indicating a tool use by the model."""

    id: Required[str]

    input: Required[Dict[str, object]]

    name: Required[str]

    type: Required[Literal["tool_use"]]

    cache_control: Optional[CacheControlEphemeralParam]
    """Create a cache control breakpoint at this content block."""


class ContentAnthropicRequestDocumentBlockSourceAnthropicBase64PdfSource(TypedDict, total=False):
    data: Required[Annotated[Union[str, Base64FileInput], PropertyInfo(format="base64")]]

    media_type: Required[Literal["application/pdf"]]

    type: Required[Literal["base64"]]


set_pydantic_config(
    ContentAnthropicRequestDocumentBlockSourceAnthropicBase64PdfSource, {"arbitrary_types_allowed": True}
)


class ContentAnthropicRequestDocumentBlockSourceAnthropicPlainTextSource(TypedDict, total=False):
    data: Required[str]

    media_type: Required[Literal["text/plain"]]

    type: Required[Literal["text"]]


ContentAnthropicRequestDocumentBlockSourceAnthropicContentBlockSourceContentContentBlockSourceContent: TypeAlias = (
    Union[RequestTextBlockParam, RequestImageBlockParam]
)


class ContentAnthropicRequestDocumentBlockSourceAnthropicContentBlockSource(TypedDict, total=False):
    content: Required[
        Union[
            str,
            Iterable[
                ContentAnthropicRequestDocumentBlockSourceAnthropicContentBlockSourceContentContentBlockSourceContent
            ],
        ]
    ]

    type: Required[Literal["content"]]


class ContentAnthropicRequestDocumentBlockSourceAnthropicUrlpdfSource(TypedDict, total=False):
    type: Required[Literal["url"]]

    url: Required[str]


ContentAnthropicRequestDocumentBlockSource: TypeAlias = Union[
    ContentAnthropicRequestDocumentBlockSourceAnthropicBase64PdfSource,
    ContentAnthropicRequestDocumentBlockSourceAnthropicPlainTextSource,
    ContentAnthropicRequestDocumentBlockSourceAnthropicContentBlockSource,
    ContentAnthropicRequestDocumentBlockSourceAnthropicUrlpdfSource,
]


class ContentAnthropicRequestDocumentBlockCitations(TypedDict, total=False):
    enabled: bool


class ContentAnthropicRequestDocumentBlock(TypedDict, total=False):
    source: Required[ContentAnthropicRequestDocumentBlockSource]

    type: Required[Literal["document"]]

    cache_control: Optional[CacheControlEphemeralParam]
    """Create a cache control breakpoint at this content block."""

    citations: Optional[ContentAnthropicRequestDocumentBlockCitations]

    context: Optional[str]

    title: Optional[str]


Content: TypeAlias = Union[RequestTextBlockParam, RequestImageBlockParam, ContentAnthropicRequestDocumentBlock]


class MessageContentUnionMember1AnthropicRequestToolResultBlock(TypedDict, total=False):
    """A block specifying the results of a tool use by the model."""

    tool_use_id: Required[str]

    type: Required[Literal["tool_result"]]

    cache_control: Optional[CacheControlEphemeralParam]
    """Create a cache control breakpoint at this content block."""

    content: Union[str, Iterable[Content]]

    is_error: bool


class Message(TypedDict, total=False):
    content: Required[
        Union[
            str,
            Iterable[
                Union[
                    RequestTextBlockParam,
                    RequestImageBlockParam,
                    MessageContentUnionMember1AnthropicRequestDocumentBlock,
                    MessageContentUnionMember1AnthropicRequestThinkingBlock,
                    MessageContentUnionMember1AnthropicRequestRedactedThinkingBlock,
                    MessageContentUnionMember1AnthropicRequestToolUseBlock,
                    MessageContentUnionMember1AnthropicRequestToolResultBlock,
                    ContentBlock,
                ]
            ],
        ]
    ]

    role: Required[Literal["user", "assistant"]]


class Metadata(TypedDict, total=False):
    """An object describing metadata about the request."""

    user_id: Optional[str]
    """An external identifier for the user who is associated with the request.

    This should be a uuid, hash value, or other opaque identifier. This id may be
    used to help detect abuse. Do not include any identifying information such as
    name, email address, or phone number.
    """


class OutputConfigFormat(TypedDict, total=False):
    """A schema to specify the model's output format in responses.

    See [structured outputs](/structured-responses/structured-output-grammar-based)
    """

    schema: Required[Dict[str, object]]
    """The JSON schema of the format"""

    type: Required[Literal["json_schema"]]


class OutputConfig(TypedDict, total=False):
    """Configuration options for the model's output, such as the output format."""

    effort: Optional[Literal["low", "medium", "high", "max"]]
    """All possible effort levels."""

    format: Optional[OutputConfigFormat]
    """A schema to specify the model's output format in responses.

    See [structured outputs](/structured-responses/structured-output-grammar-based)
    """


class ThinkingAnthropicThinkingConfigEnabled(TypedDict, total=False):
    budget_tokens: Required[int]
    """Determines how many tokens the model can use for its internal reasoning process.

    Larger budgets can enable more thorough analysis for complex problems, improving
    response quality.

    Must be ≥1024 and less than `max_tokens`.

    See [reasoning](/guides/reasoning) for details.
    """

    type: Required[Literal["enabled"]]


class ThinkingAnthropicThinkingConfigDisabled(TypedDict, total=False):
    type: Required[Literal["disabled"]]


class ThinkingAnthropicThinkingConfigAdaptive(TypedDict, total=False):
    """**Not supported yet.**"""

    type: Required[Literal["adaptive"]]


Thinking: TypeAlias = Union[
    ThinkingAnthropicThinkingConfigEnabled,
    ThinkingAnthropicThinkingConfigDisabled,
    ThinkingAnthropicThinkingConfigAdaptive,
]


class ToolChoiceAnthropicToolChoiceAuto(TypedDict, total=False):
    """The model will automatically decide whether to use tools."""

    type: Required[Literal["auto"]]

    disable_parallel_tool_use: bool
    """Whether to disable parallel tool use.

    Defaults to `false`. If set to `true`, the model will output at most one tool
    use.
    """


class ToolChoiceAnthropicToolChoiceAny(TypedDict, total=False):
    """The model will use any available tools."""

    type: Required[Literal["any"]]

    disable_parallel_tool_use: bool
    """Whether to disable parallel tool use.

    Defaults to `false`. If set to `true`, the model will output exactly one tool
    use.
    """


class ToolChoiceAnthropicToolChoiceTool(TypedDict, total=False):
    """The model will use the specified tool with `tool_choice.name`."""

    name: Required[str]
    """The name of the tool to use."""

    type: Required[Literal["tool"]]

    disable_parallel_tool_use: bool
    """Whether to disable parallel tool use.

    Defaults to `false`. If set to `true`, the model will output exactly one tool
    use.
    """


class ToolChoiceAnthropicToolChoiceNone(TypedDict, total=False):
    """The model will not be allowed to use tools."""

    type: Required[Literal["none"]]


ToolChoice: TypeAlias = Union[
    ToolChoiceAnthropicToolChoiceAuto,
    ToolChoiceAnthropicToolChoiceAny,
    ToolChoiceAnthropicToolChoiceTool,
    ToolChoiceAnthropicToolChoiceNone,
]


class ToolInputSchemaTyped(TypedDict, total=False):
    """[JSON schema](https://json-schema.org/draft/2020-12) for this tool's input.

    This defines the shape of the `input` that your tool accepts and that the model will produce.
    """

    type: Required[Literal["object"]]

    properties: Optional[Dict[str, object]]

    required: Optional[SequenceNotStr[str]]


ToolInputSchema: TypeAlias = Union[ToolInputSchemaTyped, Dict[str, object]]


class Tool(TypedDict, total=False):
    input_schema: Required[ToolInputSchema]
    """[JSON schema](https://json-schema.org/draft/2020-12) for this tool's input.

    This defines the shape of the `input` that your tool accepts and that the model
    will produce.
    """

    name: Required[str]
    """Name of the tool.

    This is how the tool will be called by the model and in `tool_use` blocks.
    """

    description: str
    """Description of what this tool does.

    Tool descriptions should be as detailed as possible. The more information that
    the model has about what the tool is and how to use it, the better it will
    perform. You can use natural language descriptions to reinforce important
    aspects of the tool input JSON schema.
    """

    strict: bool
    """When true, guarantees schema validation on tool names and inputs"""

    type: Optional[Literal["custom"]]
