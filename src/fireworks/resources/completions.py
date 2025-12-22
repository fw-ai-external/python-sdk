# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable, Optional
from typing_extensions import Literal, overload

import httpx

from ..types import completion_create_params
from .._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
from .._utils import required_args, maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._streaming import Stream, AsyncStream
from .._base_client import make_request_options
from ..types.completion_chunk import CompletionChunk
from ..types.completion_create_response import CompletionCreateResponse

__all__ = ["CompletionsResource", "AsyncCompletionsResource"]


class CompletionsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> CompletionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#accessing-raw-response-data-eg-headers
        """
        return CompletionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CompletionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#with_streaming_response
        """
        return CompletionsResourceWithStreamingResponse(self)

    @overload
    def create(
        self,
        *,
        model: str,
        prompt: Union[str, SequenceNotStr[str], Iterable[int], Iterable[Iterable[int]]],
        context_length_exceeded_behavior: Literal["error", "truncate"] | Omit = omit,
        echo: Optional[bool] | Omit = omit,
        echo_last: Optional[int] | Omit = omit,
        frequency_penalty: Optional[float] | Omit = omit,
        ignore_eos: bool | Omit = omit,
        images: Union[SequenceNotStr[str], Iterable[SequenceNotStr[str]], None] | Omit = omit,
        logit_bias: Optional[Dict[str, float]] | Omit = omit,
        logprobs: Union[int, bool, None] | Omit = omit,
        max_completion_tokens: Optional[int] | Omit = omit,
        max_tokens: Optional[int] | Omit = omit,
        metadata: Optional[Dict[str, str]] | Omit = omit,
        min_p: Optional[float] | Omit = omit,
        mirostat_lr: Optional[float] | Omit = omit,
        mirostat_target: Optional[float] | Omit = omit,
        n: int | Omit = omit,
        perf_metrics_in_response: Optional[bool] | Omit = omit,
        prediction: Optional[completion_create_params.Prediction] | Omit = omit,
        presence_penalty: Optional[float] | Omit = omit,
        prompt_cache_isolation_key: Optional[str] | Omit = omit,
        raw_output: Optional[bool] | Omit = omit,
        reasoning_effort: Union[Literal["low", "medium", "high", "none"], int, bool, None] | Omit = omit,
        reasoning_history: Optional[Literal["disabled", "interleaved", "preserved"]] | Omit = omit,
        repetition_penalty: Optional[float] | Omit = omit,
        response_format: Optional[completion_create_params.ResponseFormat] | Omit = omit,
        return_token_ids: Optional[bool] | Omit = omit,
        seed: Optional[int] | Omit = omit,
        speculation: Union[str, Iterable[int], None] | Omit = omit,
        stop: Union[str, SequenceNotStr[str], None] | Omit = omit,
        stream: Optional[Literal[False]] | Omit = omit,
        temperature: Optional[float] | Omit = omit,
        top_k: Optional[int] | Omit = omit,
        top_logprobs: Optional[int] | Omit = omit,
        top_p: Optional[float] | Omit = omit,
        typical_p: Optional[float] | Omit = omit,
        user: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CompletionCreateResponse:
        """
        Create a completion for the provided prompt and parameters.

        Args:
          model: The name of the model to use.

              Example: `"accounts/fireworks/models/kimi-k2-instruct-0905"`

          prompt: The prompt to generate completions for.

              It can be a single string or an array of strings.

              It can also be an array of integers or an array of integer arrays, which allows
              to pass already tokenized prompt.

              If multiple prompts are specified, several choices with corresponding `index`
              will be returned in the output.

          context_length_exceeded_behavior: What to do if the token count of prompt plus `max_tokens` exceeds the model's
              context window.

              Passing `truncate` limits the `max_tokens` to at most
              `context_window_length - prompt_length`. This is the default.

              Passing `error` would trigger a request error.

              The default of `'truncate'` is selected as it allows to ask for high
              `max_tokens` value while respecting the context window length without having to
              do client-side prompt tokenization.

              Note, that it differs from OpenAI's behavior that matches that of `error`.

          echo: Echo back the prompt in addition to the completion.

          echo_last: Echo back the last N tokens of the prompt in addition to the completion. This is
              useful for obtaining logprobs of the prompt suffix but without transferring too
              much data. Passing `echo_last=len(prompt)` is the same as `echo=True`

          frequency_penalty: Number between -2.0 and 2.0. Positive values penalize new tokens based on their
              existing frequency in the text so far, decreasing the model's likelihood to
              repeat the same line verbatim.

              Reasonable value is around 0.1 to 1 if the aim is to just reduce repetitive
              samples somewhat. If the aim is to strongly suppress repetition, then one can
              increase the coefficients up to 2, but this can noticeably degrade the quality
              of samples. Negative values can be used to increase the likelihood of
              repetition.

              See also `presence_penalty` for penalizing tokens that have at least one
              appearance at a fixed rate.

              OpenAI compatible (follows OpenAI's conventions for handling token frequency and
              repetition penalties).

              Required range: `-2 <= x <= 2`

          ignore_eos: This setting controls whether the model should ignore the End of Sequence (EOS)
              token. When set to `True`, the model will continue generating tokens even after
              the EOS token is produced. By default, it stops when the EOS token is reached.

          images: The list of base64 encoded images for visual language completition generation.

              They should be formatted as MIME_TYPE,<base64 encoded str>

              eg. data:image/jpeg;base64,<base64 encoded str>

              Additionally, the number of images provided should match the number of '<image>'
              special token in the prompt

          logit_bias: Modify the likelihood of specified tokens appearing in the completion. Accepts a
              json object that maps tokens (specified by their token ID in the tokenizer) to
              an associated bias value from -100 to 100. Mathematically, the bias is added to
              the logits generated by the model prior to sampling.

          logprobs: Include log probabilities in the response. This accepts either a boolean or an
              integer:

              If set to `true`, log probabilities are included and the number of alternatives
              can be controlled via `top_logprobs` (OpenAI-compatible behavior).

              If set to an integer N (0-5), include log probabilities for up to N most likely
              tokens per position in the legacy format.

              The API will always return the logprob of the sampled token, so there may be up
              to `logprobs+1` elements in the response when an integer is used. The maximum
              value for the integer form is 5.

          max_completion_tokens: Alias for max_tokens. Cannot be specified together with max_tokens.

          max_tokens: The maximum number of tokens to generate in the completion. If the token count
              of your prompt plus max_tokens exceeds the model's context length, the behavior
              depends on context_length_exceeded_behavior. By default, max_tokens will be
              lowered to fit in the context window instead of returning an error.

          metadata: Additional metadata to store with the request for tracing/distillation.

          min_p: Minimum probability threshold for token selection. Only tokens with
              probability >= min_p are considered for selection. This is an alternative to
              `top_p` and `top_k` sampling.

              Required range: `0 <= x <= 1`

          mirostat_lr: Specifies the learning rate for the Mirostat sampling algorithm, which controls
              how quickly the model adjusts its token distribution to maintain the target
              perplexity. A smaller value slows down the adjustments, leading to more stable
              but gradual shifts, while higher values speed up corrections at the cost of
              potential instability.

          mirostat_target: Defines the target perplexity for the Mirostat algorithm. Perplexity measures
              the unpredictability of the generated text, with higher values encouraging more
              diverse and creative outputs, while lower values prioritize predictability and
              coherence. The algorithm dynamically adjusts the token selection to maintain
              this target during text generation.

              If not specified, Mirostat sampling is disabled.

          n: How many completions to generate for each prompt.

              **Note:** Because this parameter generates many completions, it can quickly
              consume your token quota. Use carefully and ensure that you have reasonable
              settings for `max_tokens` and `stop`.

              Required range: `1 <= x <= 128`

              Example: `1`

          perf_metrics_in_response: Whether to include performance metrics in the response body.

              **Non-streaming requests:** Performance metrics are always included in response
              headers (e.g., `fireworks-prompt-tokens`,
              `fireworks-server-time-to-first-token`). Setting this to `true` additionally
              includes the same metrics in the response body under the `perf_metrics` field.

              **Streaming requests:** Performance metrics are only included in the response
              body under the `perf_metrics` field in the final chunk (when `finish_reason` is
              set). This is because headers may not be accessible during streaming.

              The response body `perf_metrics` field contains the following metrics:

              **Basic Metrics (all deployments):**

              - `prompt-tokens`: Number of tokens in the prompt
              - `server-time-to-first-token`: Time from request start to first token (in
                seconds)
              - `server-processing-time`: Total processing time (in seconds, only for
                completed requests)

              **Predicted Outputs Metrics:**

              - `speculation-prompt-tokens`: Number of speculative prompt tokens
              - `speculation-prompt-matched-tokens`: Number of matched speculative prompt
                tokens (for completed requests)

              **Dedicated Deployment Only Metrics:**

              - `speculation-generated-tokens`: Number of speculative generated tokens (for
                completed requests)
              - `speculation-acceptance`: Speculation acceptance rates by position
              - `cached-prompt-tokens`: Number of cached prompt tokens
              - `backend-host`: Hostname of the backend server
              - `num-concurrent-requests`: Number of concurrent requests
              - `deployment`: Deployment name
              - `tokenizer-queue-duration`: Time spent in tokenizer queue
              - `tokenizer-duration`: Time spent in tokenizer
              - `prefill-queue-duration`: Time spent in prefill queue
              - `prefill-duration`: Time spent in prefill
              - `generation-queue-duration`: Time spent in generation queue

          prediction: OpenAI-compatible predicted output for speculative decoding. Can be a
              PredictedOutput object or a simple string. Automatically transformed to
              speculation.

          presence_penalty: Number between -2.0 and 2.0. Positive values penalize new tokens based on
              whether they appear in the text so far, increasing the model's likelihood to
              talk about new topics.

              Reasonable value is around 0.1 to 1 if the aim is to just reduce repetitive
              samples somewhat. If the aim is to strongly suppress repetition, then one can
              increase the coefficients up to 2, but this can noticeably degrade the quality
              of samples. Negative values can be used to increase the likelihood of
              repetition.

              See also `frequency_penalty` for penalizing tokens at an increasing rate
              depending on how often they appear.

              OpenAI compatible (follows OpenAI's conventions for handling token frequency and
              repetition penalties).

              Required range: `-2 <= x <= 2`

          prompt_cache_isolation_key: Isolation key for prompt caching to separate cache entries.

          raw_output: Return raw output from the model.

          reasoning_effort: Controls reasoning behavior for supported models. When enabled, the model's
              reasoning appears in the `reasoning_content` field of the response, separate
              from the final answer in `content`.

              **Accepted values:**

              - **String** (OpenAI-compatible): `'low'`, `'medium'`, or `'high'` to enable
                reasoning with varying effort levels; `'none'` to disable reasoning.
              - **Boolean** (Fireworks extension): `true` to enable reasoning, `false` to
                disable it.
              - **Integer** (Fireworks extension): A positive integer to set a hard token
                limit on reasoning output (only effective for grammar-based reasoning models).

              **Important:** Boolean values are normalized internally: `true` becomes
              `'medium'`, and `false` becomes `'none'`. This normalization happens before
              model-specific validation, so if a model doesn't support `'none'`, passing
              `false` will produce an error referencing `'none'`.

              **Model-specific behavior:**

              - **Qwen3 (e.g., Qwen3-8B)**: Grammar-based reasoning. Default reasoning on. Use
                `'none'` or `false` to disable. Supports integer token limits to cap reasoning
                output. `'low'` maps to a default token limit (~3000 tokens).
              - **DeepSeek V3.1, DeepSeek V3.2**: Binary on/off reasoning. Default reasoning
                off. Any value except `'none'`/`false`/`null` enables reasoning; effort levels
                and integers have no additional effect.
              - **GLM 4.5, GLM 4.5 Air, GLM 4.6, GLM 4.7**: Binary on/off reasoning. Default
                reasoning on. Use `'none'` or `false` to disable; effort levels and integers
                have no additional effect.
              - **Harmony (OpenAI GPT-OSS 120B, GPT-OSS 20B)**: Accepts only `'low'`,
                `'medium'`, or `'high'`. Does not support `'none'`, `false`, or integer
                values—using these will return an error (e.g., "Invalid reasoning effort:
                none"). When omitted, defaults to `'medium'`. Lower effort produces faster
                responses with shorter reasoning.

          reasoning_history: Controls how historical assistant reasoning content is included in the prompt
              for multi-turn conversations.

              **Accepted values:**

              - `null`: Use model/template default behavior
              - `'disabled'`: Remove all historical reasoning content from the prompt
              - `'interleaved'`: Keep only reasoning content after the last user message
              - `'preserved'`: Retain all previous reasoning content across the conversation

              **Model support:**

              | Model            | Default         | Supported values                             |
              | ---------------- | --------------- | -------------------------------------------- |
              | Kimi K2 Instruct | `'preserved'`   | `'disabled'`, `'interleaved'`, `'preserved'` |
              | MiniMax M2       | `'interleaved'` | `'disabled'`, `'interleaved'`                |
              | GLM-4.7          | `'interleaved'` | `'disabled'`, `'interleaved'`, `'preserved'` |
              | GLM-4.6          | `'interleaved'` | `'disabled'`, `'interleaved'`                |

              For other models, refer to the model provider's documentation.

              **Note:** This parameter controls prompt formatting only. To disable reasoning
              computation entirely, use `reasoning_effort='none'`.

          repetition_penalty: Applies a penalty to repeated tokens to discourage or encourage repetition. A
              value of `1.0` means no penalty, allowing free repetition. Values above `1.0`
              penalize repetition, reducing the likelihood of repeating tokens. Values between
              `0.0` and `1.0` reward repetition, increasing the chance of repeated tokens. For
              a good balance, a value of `1.2` is often recommended. Note that the penalty is
              applied to both the generated output and the prompt in decoder-only models.

              Required range: `0 <= x <= 2`

          response_format: Allows to force the model to produce specific output format.

              Setting to `{ "type": "json_object" }` enables JSON mode, which guarantees the
              message the model generates is valid JSON.

              If `"type"` is `"json_schema"`, a JSON schema must be provided. E.g.,
              `response_format = {"type": "json_schema", "json_schema": <json_schema>}`.

              Important: when using JSON mode, it's crucial to also instruct the model to
              produce JSON via a system or user message. Without this, the model may generate
              an unending stream of whitespace until the generation reaches the token limit,
              resulting in a long-running and seemingly "stuck" request.

              Also note that the message content may be partially cut off if
              `finish_reason="length"`, which indicates the generation exceeded `max_tokens`
              or the conversation exceeded the max context length. In this case the return
              value might not be a valid JSON.

          return_token_ids: Return token IDs alongside text to avoid retokenization drift.

          seed: Random seed for deterministic sampling.

          speculation: Speculative decoding prompt or token IDs to speed up generation.

          stop: Up to 4 sequences where the API will stop generating further tokens. The
              returned text will NOT contain the stop sequence.

          stream: Whether to stream back partial progress. If set, tokens will be sent as
              data-only
              [server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format)
              as they become available, with the stream terminated by a `data: [DONE]`
              message.

          temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 will
              make the output more random, while lower values like 0.2 will make it more
              focused and deterministic.

              We generally recommend altering this or top_p but not both.

              Required range: `0 <= x <= 2`

              Example: `1`

          top_k: Top-k sampling is another sampling method where the k most probable next tokens
              are filtered and the probability mass is redistributed among only those k next
              tokens. The value of k controls the number of candidates for the next token at
              each step during text generation. Must be between 0 and 100.

              Required range: `0 <= x <= 100`

              Example: `50`

          top_logprobs: An integer between 0 and 5 specifying the number of most likely tokens to return
              at each token position, each with an associated log probability. The minimum
              value is 0 and the maximum value is 5.

              When `logprobs` is set, `top_logprobs` can be used to modify how many top log
              probabilities are returned. If `top_logprobs` is not set, the API will return up
              to `logprobs` tokens per position.

              Required range: `0 <= x <= 5`

          top_p: An alternative to sampling with temperature, called nucleus sampling, where the
              model considers the results of the tokens with top_p probability mass. So 0.1
              means only the tokens comprising the top 10% probability mass are considered.

              We generally recommend altering this or temperature but not both.

              Required range: `0 <= x <= 1`

              Example: `1`

          typical_p: Typical-p sampling is an alternative to nucleus sampling. It considers the most
              typical tokens whose cumulative probability is at most typical_p.

              Required range: `0 <= x <= 1`

          user: A unique identifier representing your end-user, which can help monitor and
              detect abuse.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def create(
        self,
        *,
        model: str,
        prompt: Union[str, SequenceNotStr[str], Iterable[int], Iterable[Iterable[int]]],
        stream: Literal[True],
        context_length_exceeded_behavior: Literal["error", "truncate"] | Omit = omit,
        echo: Optional[bool] | Omit = omit,
        echo_last: Optional[int] | Omit = omit,
        frequency_penalty: Optional[float] | Omit = omit,
        ignore_eos: bool | Omit = omit,
        images: Union[SequenceNotStr[str], Iterable[SequenceNotStr[str]], None] | Omit = omit,
        logit_bias: Optional[Dict[str, float]] | Omit = omit,
        logprobs: Union[int, bool, None] | Omit = omit,
        max_completion_tokens: Optional[int] | Omit = omit,
        max_tokens: Optional[int] | Omit = omit,
        metadata: Optional[Dict[str, str]] | Omit = omit,
        min_p: Optional[float] | Omit = omit,
        mirostat_lr: Optional[float] | Omit = omit,
        mirostat_target: Optional[float] | Omit = omit,
        n: int | Omit = omit,
        perf_metrics_in_response: Optional[bool] | Omit = omit,
        prediction: Optional[completion_create_params.Prediction] | Omit = omit,
        presence_penalty: Optional[float] | Omit = omit,
        prompt_cache_isolation_key: Optional[str] | Omit = omit,
        raw_output: Optional[bool] | Omit = omit,
        reasoning_effort: Union[Literal["low", "medium", "high", "none"], int, bool, None] | Omit = omit,
        reasoning_history: Optional[Literal["disabled", "interleaved", "preserved"]] | Omit = omit,
        repetition_penalty: Optional[float] | Omit = omit,
        response_format: Optional[completion_create_params.ResponseFormat] | Omit = omit,
        return_token_ids: Optional[bool] | Omit = omit,
        seed: Optional[int] | Omit = omit,
        speculation: Union[str, Iterable[int], None] | Omit = omit,
        stop: Union[str, SequenceNotStr[str], None] | Omit = omit,
        temperature: Optional[float] | Omit = omit,
        top_k: Optional[int] | Omit = omit,
        top_logprobs: Optional[int] | Omit = omit,
        top_p: Optional[float] | Omit = omit,
        typical_p: Optional[float] | Omit = omit,
        user: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Stream[CompletionChunk]:
        """
        Create a completion for the provided prompt and parameters.

        Args:
          model: The name of the model to use.

              Example: `"accounts/fireworks/models/kimi-k2-instruct-0905"`

          prompt: The prompt to generate completions for.

              It can be a single string or an array of strings.

              It can also be an array of integers or an array of integer arrays, which allows
              to pass already tokenized prompt.

              If multiple prompts are specified, several choices with corresponding `index`
              will be returned in the output.

          stream: Whether to stream back partial progress. If set, tokens will be sent as
              data-only
              [server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format)
              as they become available, with the stream terminated by a `data: [DONE]`
              message.

          context_length_exceeded_behavior: What to do if the token count of prompt plus `max_tokens` exceeds the model's
              context window.

              Passing `truncate` limits the `max_tokens` to at most
              `context_window_length - prompt_length`. This is the default.

              Passing `error` would trigger a request error.

              The default of `'truncate'` is selected as it allows to ask for high
              `max_tokens` value while respecting the context window length without having to
              do client-side prompt tokenization.

              Note, that it differs from OpenAI's behavior that matches that of `error`.

          echo: Echo back the prompt in addition to the completion.

          echo_last: Echo back the last N tokens of the prompt in addition to the completion. This is
              useful for obtaining logprobs of the prompt suffix but without transferring too
              much data. Passing `echo_last=len(prompt)` is the same as `echo=True`

          frequency_penalty: Number between -2.0 and 2.0. Positive values penalize new tokens based on their
              existing frequency in the text so far, decreasing the model's likelihood to
              repeat the same line verbatim.

              Reasonable value is around 0.1 to 1 if the aim is to just reduce repetitive
              samples somewhat. If the aim is to strongly suppress repetition, then one can
              increase the coefficients up to 2, but this can noticeably degrade the quality
              of samples. Negative values can be used to increase the likelihood of
              repetition.

              See also `presence_penalty` for penalizing tokens that have at least one
              appearance at a fixed rate.

              OpenAI compatible (follows OpenAI's conventions for handling token frequency and
              repetition penalties).

              Required range: `-2 <= x <= 2`

          ignore_eos: This setting controls whether the model should ignore the End of Sequence (EOS)
              token. When set to `True`, the model will continue generating tokens even after
              the EOS token is produced. By default, it stops when the EOS token is reached.

          images: The list of base64 encoded images for visual language completition generation.

              They should be formatted as MIME_TYPE,<base64 encoded str>

              eg. data:image/jpeg;base64,<base64 encoded str>

              Additionally, the number of images provided should match the number of '<image>'
              special token in the prompt

          logit_bias: Modify the likelihood of specified tokens appearing in the completion. Accepts a
              json object that maps tokens (specified by their token ID in the tokenizer) to
              an associated bias value from -100 to 100. Mathematically, the bias is added to
              the logits generated by the model prior to sampling.

          logprobs: Include log probabilities in the response. This accepts either a boolean or an
              integer:

              If set to `true`, log probabilities are included and the number of alternatives
              can be controlled via `top_logprobs` (OpenAI-compatible behavior).

              If set to an integer N (0-5), include log probabilities for up to N most likely
              tokens per position in the legacy format.

              The API will always return the logprob of the sampled token, so there may be up
              to `logprobs+1` elements in the response when an integer is used. The maximum
              value for the integer form is 5.

          max_completion_tokens: Alias for max_tokens. Cannot be specified together with max_tokens.

          max_tokens: The maximum number of tokens to generate in the completion. If the token count
              of your prompt plus max_tokens exceeds the model's context length, the behavior
              depends on context_length_exceeded_behavior. By default, max_tokens will be
              lowered to fit in the context window instead of returning an error.

          metadata: Additional metadata to store with the request for tracing/distillation.

          min_p: Minimum probability threshold for token selection. Only tokens with
              probability >= min_p are considered for selection. This is an alternative to
              `top_p` and `top_k` sampling.

              Required range: `0 <= x <= 1`

          mirostat_lr: Specifies the learning rate for the Mirostat sampling algorithm, which controls
              how quickly the model adjusts its token distribution to maintain the target
              perplexity. A smaller value slows down the adjustments, leading to more stable
              but gradual shifts, while higher values speed up corrections at the cost of
              potential instability.

          mirostat_target: Defines the target perplexity for the Mirostat algorithm. Perplexity measures
              the unpredictability of the generated text, with higher values encouraging more
              diverse and creative outputs, while lower values prioritize predictability and
              coherence. The algorithm dynamically adjusts the token selection to maintain
              this target during text generation.

              If not specified, Mirostat sampling is disabled.

          n: How many completions to generate for each prompt.

              **Note:** Because this parameter generates many completions, it can quickly
              consume your token quota. Use carefully and ensure that you have reasonable
              settings for `max_tokens` and `stop`.

              Required range: `1 <= x <= 128`

              Example: `1`

          perf_metrics_in_response: Whether to include performance metrics in the response body.

              **Non-streaming requests:** Performance metrics are always included in response
              headers (e.g., `fireworks-prompt-tokens`,
              `fireworks-server-time-to-first-token`). Setting this to `true` additionally
              includes the same metrics in the response body under the `perf_metrics` field.

              **Streaming requests:** Performance metrics are only included in the response
              body under the `perf_metrics` field in the final chunk (when `finish_reason` is
              set). This is because headers may not be accessible during streaming.

              The response body `perf_metrics` field contains the following metrics:

              **Basic Metrics (all deployments):**

              - `prompt-tokens`: Number of tokens in the prompt
              - `server-time-to-first-token`: Time from request start to first token (in
                seconds)
              - `server-processing-time`: Total processing time (in seconds, only for
                completed requests)

              **Predicted Outputs Metrics:**

              - `speculation-prompt-tokens`: Number of speculative prompt tokens
              - `speculation-prompt-matched-tokens`: Number of matched speculative prompt
                tokens (for completed requests)

              **Dedicated Deployment Only Metrics:**

              - `speculation-generated-tokens`: Number of speculative generated tokens (for
                completed requests)
              - `speculation-acceptance`: Speculation acceptance rates by position
              - `cached-prompt-tokens`: Number of cached prompt tokens
              - `backend-host`: Hostname of the backend server
              - `num-concurrent-requests`: Number of concurrent requests
              - `deployment`: Deployment name
              - `tokenizer-queue-duration`: Time spent in tokenizer queue
              - `tokenizer-duration`: Time spent in tokenizer
              - `prefill-queue-duration`: Time spent in prefill queue
              - `prefill-duration`: Time spent in prefill
              - `generation-queue-duration`: Time spent in generation queue

          prediction: OpenAI-compatible predicted output for speculative decoding. Can be a
              PredictedOutput object or a simple string. Automatically transformed to
              speculation.

          presence_penalty: Number between -2.0 and 2.0. Positive values penalize new tokens based on
              whether they appear in the text so far, increasing the model's likelihood to
              talk about new topics.

              Reasonable value is around 0.1 to 1 if the aim is to just reduce repetitive
              samples somewhat. If the aim is to strongly suppress repetition, then one can
              increase the coefficients up to 2, but this can noticeably degrade the quality
              of samples. Negative values can be used to increase the likelihood of
              repetition.

              See also `frequency_penalty` for penalizing tokens at an increasing rate
              depending on how often they appear.

              OpenAI compatible (follows OpenAI's conventions for handling token frequency and
              repetition penalties).

              Required range: `-2 <= x <= 2`

          prompt_cache_isolation_key: Isolation key for prompt caching to separate cache entries.

          raw_output: Return raw output from the model.

          reasoning_effort: Controls reasoning behavior for supported models. When enabled, the model's
              reasoning appears in the `reasoning_content` field of the response, separate
              from the final answer in `content`.

              **Accepted values:**

              - **String** (OpenAI-compatible): `'low'`, `'medium'`, or `'high'` to enable
                reasoning with varying effort levels; `'none'` to disable reasoning.
              - **Boolean** (Fireworks extension): `true` to enable reasoning, `false` to
                disable it.
              - **Integer** (Fireworks extension): A positive integer to set a hard token
                limit on reasoning output (only effective for grammar-based reasoning models).

              **Important:** Boolean values are normalized internally: `true` becomes
              `'medium'`, and `false` becomes `'none'`. This normalization happens before
              model-specific validation, so if a model doesn't support `'none'`, passing
              `false` will produce an error referencing `'none'`.

              **Model-specific behavior:**

              - **Qwen3 (e.g., Qwen3-8B)**: Grammar-based reasoning. Default reasoning on. Use
                `'none'` or `false` to disable. Supports integer token limits to cap reasoning
                output. `'low'` maps to a default token limit (~3000 tokens).
              - **DeepSeek V3.1, DeepSeek V3.2**: Binary on/off reasoning. Default reasoning
                off. Any value except `'none'`/`false`/`null` enables reasoning; effort levels
                and integers have no additional effect.
              - **GLM 4.5, GLM 4.5 Air, GLM 4.6, GLM 4.7**: Binary on/off reasoning. Default
                reasoning on. Use `'none'` or `false` to disable; effort levels and integers
                have no additional effect.
              - **Harmony (OpenAI GPT-OSS 120B, GPT-OSS 20B)**: Accepts only `'low'`,
                `'medium'`, or `'high'`. Does not support `'none'`, `false`, or integer
                values—using these will return an error (e.g., "Invalid reasoning effort:
                none"). When omitted, defaults to `'medium'`. Lower effort produces faster
                responses with shorter reasoning.

          reasoning_history: Controls how historical assistant reasoning content is included in the prompt
              for multi-turn conversations.

              **Accepted values:**

              - `null`: Use model/template default behavior
              - `'disabled'`: Remove all historical reasoning content from the prompt
              - `'interleaved'`: Keep only reasoning content after the last user message
              - `'preserved'`: Retain all previous reasoning content across the conversation

              **Model support:**

              | Model            | Default         | Supported values                             |
              | ---------------- | --------------- | -------------------------------------------- |
              | Kimi K2 Instruct | `'preserved'`   | `'disabled'`, `'interleaved'`, `'preserved'` |
              | MiniMax M2       | `'interleaved'` | `'disabled'`, `'interleaved'`                |
              | GLM-4.7          | `'interleaved'` | `'disabled'`, `'interleaved'`, `'preserved'` |
              | GLM-4.6          | `'interleaved'` | `'disabled'`, `'interleaved'`                |

              For other models, refer to the model provider's documentation.

              **Note:** This parameter controls prompt formatting only. To disable reasoning
              computation entirely, use `reasoning_effort='none'`.

          repetition_penalty: Applies a penalty to repeated tokens to discourage or encourage repetition. A
              value of `1.0` means no penalty, allowing free repetition. Values above `1.0`
              penalize repetition, reducing the likelihood of repeating tokens. Values between
              `0.0` and `1.0` reward repetition, increasing the chance of repeated tokens. For
              a good balance, a value of `1.2` is often recommended. Note that the penalty is
              applied to both the generated output and the prompt in decoder-only models.

              Required range: `0 <= x <= 2`

          response_format: Allows to force the model to produce specific output format.

              Setting to `{ "type": "json_object" }` enables JSON mode, which guarantees the
              message the model generates is valid JSON.

              If `"type"` is `"json_schema"`, a JSON schema must be provided. E.g.,
              `response_format = {"type": "json_schema", "json_schema": <json_schema>}`.

              Important: when using JSON mode, it's crucial to also instruct the model to
              produce JSON via a system or user message. Without this, the model may generate
              an unending stream of whitespace until the generation reaches the token limit,
              resulting in a long-running and seemingly "stuck" request.

              Also note that the message content may be partially cut off if
              `finish_reason="length"`, which indicates the generation exceeded `max_tokens`
              or the conversation exceeded the max context length. In this case the return
              value might not be a valid JSON.

          return_token_ids: Return token IDs alongside text to avoid retokenization drift.

          seed: Random seed for deterministic sampling.

          speculation: Speculative decoding prompt or token IDs to speed up generation.

          stop: Up to 4 sequences where the API will stop generating further tokens. The
              returned text will NOT contain the stop sequence.

          temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 will
              make the output more random, while lower values like 0.2 will make it more
              focused and deterministic.

              We generally recommend altering this or top_p but not both.

              Required range: `0 <= x <= 2`

              Example: `1`

          top_k: Top-k sampling is another sampling method where the k most probable next tokens
              are filtered and the probability mass is redistributed among only those k next
              tokens. The value of k controls the number of candidates for the next token at
              each step during text generation. Must be between 0 and 100.

              Required range: `0 <= x <= 100`

              Example: `50`

          top_logprobs: An integer between 0 and 5 specifying the number of most likely tokens to return
              at each token position, each with an associated log probability. The minimum
              value is 0 and the maximum value is 5.

              When `logprobs` is set, `top_logprobs` can be used to modify how many top log
              probabilities are returned. If `top_logprobs` is not set, the API will return up
              to `logprobs` tokens per position.

              Required range: `0 <= x <= 5`

          top_p: An alternative to sampling with temperature, called nucleus sampling, where the
              model considers the results of the tokens with top_p probability mass. So 0.1
              means only the tokens comprising the top 10% probability mass are considered.

              We generally recommend altering this or temperature but not both.

              Required range: `0 <= x <= 1`

              Example: `1`

          typical_p: Typical-p sampling is an alternative to nucleus sampling. It considers the most
              typical tokens whose cumulative probability is at most typical_p.

              Required range: `0 <= x <= 1`

          user: A unique identifier representing your end-user, which can help monitor and
              detect abuse.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def create(
        self,
        *,
        model: str,
        prompt: Union[str, SequenceNotStr[str], Iterable[int], Iterable[Iterable[int]]],
        stream: bool,
        context_length_exceeded_behavior: Literal["error", "truncate"] | Omit = omit,
        echo: Optional[bool] | Omit = omit,
        echo_last: Optional[int] | Omit = omit,
        frequency_penalty: Optional[float] | Omit = omit,
        ignore_eos: bool | Omit = omit,
        images: Union[SequenceNotStr[str], Iterable[SequenceNotStr[str]], None] | Omit = omit,
        logit_bias: Optional[Dict[str, float]] | Omit = omit,
        logprobs: Union[int, bool, None] | Omit = omit,
        max_completion_tokens: Optional[int] | Omit = omit,
        max_tokens: Optional[int] | Omit = omit,
        metadata: Optional[Dict[str, str]] | Omit = omit,
        min_p: Optional[float] | Omit = omit,
        mirostat_lr: Optional[float] | Omit = omit,
        mirostat_target: Optional[float] | Omit = omit,
        n: int | Omit = omit,
        perf_metrics_in_response: Optional[bool] | Omit = omit,
        prediction: Optional[completion_create_params.Prediction] | Omit = omit,
        presence_penalty: Optional[float] | Omit = omit,
        prompt_cache_isolation_key: Optional[str] | Omit = omit,
        raw_output: Optional[bool] | Omit = omit,
        reasoning_effort: Union[Literal["low", "medium", "high", "none"], int, bool, None] | Omit = omit,
        reasoning_history: Optional[Literal["disabled", "interleaved", "preserved"]] | Omit = omit,
        repetition_penalty: Optional[float] | Omit = omit,
        response_format: Optional[completion_create_params.ResponseFormat] | Omit = omit,
        return_token_ids: Optional[bool] | Omit = omit,
        seed: Optional[int] | Omit = omit,
        speculation: Union[str, Iterable[int], None] | Omit = omit,
        stop: Union[str, SequenceNotStr[str], None] | Omit = omit,
        temperature: Optional[float] | Omit = omit,
        top_k: Optional[int] | Omit = omit,
        top_logprobs: Optional[int] | Omit = omit,
        top_p: Optional[float] | Omit = omit,
        typical_p: Optional[float] | Omit = omit,
        user: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CompletionCreateResponse | Stream[CompletionChunk]:
        """
        Create a completion for the provided prompt and parameters.

        Args:
          model: The name of the model to use.

              Example: `"accounts/fireworks/models/kimi-k2-instruct-0905"`

          prompt: The prompt to generate completions for.

              It can be a single string or an array of strings.

              It can also be an array of integers or an array of integer arrays, which allows
              to pass already tokenized prompt.

              If multiple prompts are specified, several choices with corresponding `index`
              will be returned in the output.

          stream: Whether to stream back partial progress. If set, tokens will be sent as
              data-only
              [server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format)
              as they become available, with the stream terminated by a `data: [DONE]`
              message.

          context_length_exceeded_behavior: What to do if the token count of prompt plus `max_tokens` exceeds the model's
              context window.

              Passing `truncate` limits the `max_tokens` to at most
              `context_window_length - prompt_length`. This is the default.

              Passing `error` would trigger a request error.

              The default of `'truncate'` is selected as it allows to ask for high
              `max_tokens` value while respecting the context window length without having to
              do client-side prompt tokenization.

              Note, that it differs from OpenAI's behavior that matches that of `error`.

          echo: Echo back the prompt in addition to the completion.

          echo_last: Echo back the last N tokens of the prompt in addition to the completion. This is
              useful for obtaining logprobs of the prompt suffix but without transferring too
              much data. Passing `echo_last=len(prompt)` is the same as `echo=True`

          frequency_penalty: Number between -2.0 and 2.0. Positive values penalize new tokens based on their
              existing frequency in the text so far, decreasing the model's likelihood to
              repeat the same line verbatim.

              Reasonable value is around 0.1 to 1 if the aim is to just reduce repetitive
              samples somewhat. If the aim is to strongly suppress repetition, then one can
              increase the coefficients up to 2, but this can noticeably degrade the quality
              of samples. Negative values can be used to increase the likelihood of
              repetition.

              See also `presence_penalty` for penalizing tokens that have at least one
              appearance at a fixed rate.

              OpenAI compatible (follows OpenAI's conventions for handling token frequency and
              repetition penalties).

              Required range: `-2 <= x <= 2`

          ignore_eos: This setting controls whether the model should ignore the End of Sequence (EOS)
              token. When set to `True`, the model will continue generating tokens even after
              the EOS token is produced. By default, it stops when the EOS token is reached.

          images: The list of base64 encoded images for visual language completition generation.

              They should be formatted as MIME_TYPE,<base64 encoded str>

              eg. data:image/jpeg;base64,<base64 encoded str>

              Additionally, the number of images provided should match the number of '<image>'
              special token in the prompt

          logit_bias: Modify the likelihood of specified tokens appearing in the completion. Accepts a
              json object that maps tokens (specified by their token ID in the tokenizer) to
              an associated bias value from -100 to 100. Mathematically, the bias is added to
              the logits generated by the model prior to sampling.

          logprobs: Include log probabilities in the response. This accepts either a boolean or an
              integer:

              If set to `true`, log probabilities are included and the number of alternatives
              can be controlled via `top_logprobs` (OpenAI-compatible behavior).

              If set to an integer N (0-5), include log probabilities for up to N most likely
              tokens per position in the legacy format.

              The API will always return the logprob of the sampled token, so there may be up
              to `logprobs+1` elements in the response when an integer is used. The maximum
              value for the integer form is 5.

          max_completion_tokens: Alias for max_tokens. Cannot be specified together with max_tokens.

          max_tokens: The maximum number of tokens to generate in the completion. If the token count
              of your prompt plus max_tokens exceeds the model's context length, the behavior
              depends on context_length_exceeded_behavior. By default, max_tokens will be
              lowered to fit in the context window instead of returning an error.

          metadata: Additional metadata to store with the request for tracing/distillation.

          min_p: Minimum probability threshold for token selection. Only tokens with
              probability >= min_p are considered for selection. This is an alternative to
              `top_p` and `top_k` sampling.

              Required range: `0 <= x <= 1`

          mirostat_lr: Specifies the learning rate for the Mirostat sampling algorithm, which controls
              how quickly the model adjusts its token distribution to maintain the target
              perplexity. A smaller value slows down the adjustments, leading to more stable
              but gradual shifts, while higher values speed up corrections at the cost of
              potential instability.

          mirostat_target: Defines the target perplexity for the Mirostat algorithm. Perplexity measures
              the unpredictability of the generated text, with higher values encouraging more
              diverse and creative outputs, while lower values prioritize predictability and
              coherence. The algorithm dynamically adjusts the token selection to maintain
              this target during text generation.

              If not specified, Mirostat sampling is disabled.

          n: How many completions to generate for each prompt.

              **Note:** Because this parameter generates many completions, it can quickly
              consume your token quota. Use carefully and ensure that you have reasonable
              settings for `max_tokens` and `stop`.

              Required range: `1 <= x <= 128`

              Example: `1`

          perf_metrics_in_response: Whether to include performance metrics in the response body.

              **Non-streaming requests:** Performance metrics are always included in response
              headers (e.g., `fireworks-prompt-tokens`,
              `fireworks-server-time-to-first-token`). Setting this to `true` additionally
              includes the same metrics in the response body under the `perf_metrics` field.

              **Streaming requests:** Performance metrics are only included in the response
              body under the `perf_metrics` field in the final chunk (when `finish_reason` is
              set). This is because headers may not be accessible during streaming.

              The response body `perf_metrics` field contains the following metrics:

              **Basic Metrics (all deployments):**

              - `prompt-tokens`: Number of tokens in the prompt
              - `server-time-to-first-token`: Time from request start to first token (in
                seconds)
              - `server-processing-time`: Total processing time (in seconds, only for
                completed requests)

              **Predicted Outputs Metrics:**

              - `speculation-prompt-tokens`: Number of speculative prompt tokens
              - `speculation-prompt-matched-tokens`: Number of matched speculative prompt
                tokens (for completed requests)

              **Dedicated Deployment Only Metrics:**

              - `speculation-generated-tokens`: Number of speculative generated tokens (for
                completed requests)
              - `speculation-acceptance`: Speculation acceptance rates by position
              - `cached-prompt-tokens`: Number of cached prompt tokens
              - `backend-host`: Hostname of the backend server
              - `num-concurrent-requests`: Number of concurrent requests
              - `deployment`: Deployment name
              - `tokenizer-queue-duration`: Time spent in tokenizer queue
              - `tokenizer-duration`: Time spent in tokenizer
              - `prefill-queue-duration`: Time spent in prefill queue
              - `prefill-duration`: Time spent in prefill
              - `generation-queue-duration`: Time spent in generation queue

          prediction: OpenAI-compatible predicted output for speculative decoding. Can be a
              PredictedOutput object or a simple string. Automatically transformed to
              speculation.

          presence_penalty: Number between -2.0 and 2.0. Positive values penalize new tokens based on
              whether they appear in the text so far, increasing the model's likelihood to
              talk about new topics.

              Reasonable value is around 0.1 to 1 if the aim is to just reduce repetitive
              samples somewhat. If the aim is to strongly suppress repetition, then one can
              increase the coefficients up to 2, but this can noticeably degrade the quality
              of samples. Negative values can be used to increase the likelihood of
              repetition.

              See also `frequency_penalty` for penalizing tokens at an increasing rate
              depending on how often they appear.

              OpenAI compatible (follows OpenAI's conventions for handling token frequency and
              repetition penalties).

              Required range: `-2 <= x <= 2`

          prompt_cache_isolation_key: Isolation key for prompt caching to separate cache entries.

          raw_output: Return raw output from the model.

          reasoning_effort: Controls reasoning behavior for supported models. When enabled, the model's
              reasoning appears in the `reasoning_content` field of the response, separate
              from the final answer in `content`.

              **Accepted values:**

              - **String** (OpenAI-compatible): `'low'`, `'medium'`, or `'high'` to enable
                reasoning with varying effort levels; `'none'` to disable reasoning.
              - **Boolean** (Fireworks extension): `true` to enable reasoning, `false` to
                disable it.
              - **Integer** (Fireworks extension): A positive integer to set a hard token
                limit on reasoning output (only effective for grammar-based reasoning models).

              **Important:** Boolean values are normalized internally: `true` becomes
              `'medium'`, and `false` becomes `'none'`. This normalization happens before
              model-specific validation, so if a model doesn't support `'none'`, passing
              `false` will produce an error referencing `'none'`.

              **Model-specific behavior:**

              - **Qwen3 (e.g., Qwen3-8B)**: Grammar-based reasoning. Default reasoning on. Use
                `'none'` or `false` to disable. Supports integer token limits to cap reasoning
                output. `'low'` maps to a default token limit (~3000 tokens).
              - **DeepSeek V3.1, DeepSeek V3.2**: Binary on/off reasoning. Default reasoning
                off. Any value except `'none'`/`false`/`null` enables reasoning; effort levels
                and integers have no additional effect.
              - **GLM 4.5, GLM 4.5 Air, GLM 4.6, GLM 4.7**: Binary on/off reasoning. Default
                reasoning on. Use `'none'` or `false` to disable; effort levels and integers
                have no additional effect.
              - **Harmony (OpenAI GPT-OSS 120B, GPT-OSS 20B)**: Accepts only `'low'`,
                `'medium'`, or `'high'`. Does not support `'none'`, `false`, or integer
                values—using these will return an error (e.g., "Invalid reasoning effort:
                none"). When omitted, defaults to `'medium'`. Lower effort produces faster
                responses with shorter reasoning.

          reasoning_history: Controls how historical assistant reasoning content is included in the prompt
              for multi-turn conversations.

              **Accepted values:**

              - `null`: Use model/template default behavior
              - `'disabled'`: Remove all historical reasoning content from the prompt
              - `'interleaved'`: Keep only reasoning content after the last user message
              - `'preserved'`: Retain all previous reasoning content across the conversation

              **Model support:**

              | Model            | Default         | Supported values                             |
              | ---------------- | --------------- | -------------------------------------------- |
              | Kimi K2 Instruct | `'preserved'`   | `'disabled'`, `'interleaved'`, `'preserved'` |
              | MiniMax M2       | `'interleaved'` | `'disabled'`, `'interleaved'`                |
              | GLM-4.7          | `'interleaved'` | `'disabled'`, `'interleaved'`, `'preserved'` |
              | GLM-4.6          | `'interleaved'` | `'disabled'`, `'interleaved'`                |

              For other models, refer to the model provider's documentation.

              **Note:** This parameter controls prompt formatting only. To disable reasoning
              computation entirely, use `reasoning_effort='none'`.

          repetition_penalty: Applies a penalty to repeated tokens to discourage or encourage repetition. A
              value of `1.0` means no penalty, allowing free repetition. Values above `1.0`
              penalize repetition, reducing the likelihood of repeating tokens. Values between
              `0.0` and `1.0` reward repetition, increasing the chance of repeated tokens. For
              a good balance, a value of `1.2` is often recommended. Note that the penalty is
              applied to both the generated output and the prompt in decoder-only models.

              Required range: `0 <= x <= 2`

          response_format: Allows to force the model to produce specific output format.

              Setting to `{ "type": "json_object" }` enables JSON mode, which guarantees the
              message the model generates is valid JSON.

              If `"type"` is `"json_schema"`, a JSON schema must be provided. E.g.,
              `response_format = {"type": "json_schema", "json_schema": <json_schema>}`.

              Important: when using JSON mode, it's crucial to also instruct the model to
              produce JSON via a system or user message. Without this, the model may generate
              an unending stream of whitespace until the generation reaches the token limit,
              resulting in a long-running and seemingly "stuck" request.

              Also note that the message content may be partially cut off if
              `finish_reason="length"`, which indicates the generation exceeded `max_tokens`
              or the conversation exceeded the max context length. In this case the return
              value might not be a valid JSON.

          return_token_ids: Return token IDs alongside text to avoid retokenization drift.

          seed: Random seed for deterministic sampling.

          speculation: Speculative decoding prompt or token IDs to speed up generation.

          stop: Up to 4 sequences where the API will stop generating further tokens. The
              returned text will NOT contain the stop sequence.

          temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 will
              make the output more random, while lower values like 0.2 will make it more
              focused and deterministic.

              We generally recommend altering this or top_p but not both.

              Required range: `0 <= x <= 2`

              Example: `1`

          top_k: Top-k sampling is another sampling method where the k most probable next tokens
              are filtered and the probability mass is redistributed among only those k next
              tokens. The value of k controls the number of candidates for the next token at
              each step during text generation. Must be between 0 and 100.

              Required range: `0 <= x <= 100`

              Example: `50`

          top_logprobs: An integer between 0 and 5 specifying the number of most likely tokens to return
              at each token position, each with an associated log probability. The minimum
              value is 0 and the maximum value is 5.

              When `logprobs` is set, `top_logprobs` can be used to modify how many top log
              probabilities are returned. If `top_logprobs` is not set, the API will return up
              to `logprobs` tokens per position.

              Required range: `0 <= x <= 5`

          top_p: An alternative to sampling with temperature, called nucleus sampling, where the
              model considers the results of the tokens with top_p probability mass. So 0.1
              means only the tokens comprising the top 10% probability mass are considered.

              We generally recommend altering this or temperature but not both.

              Required range: `0 <= x <= 1`

              Example: `1`

          typical_p: Typical-p sampling is an alternative to nucleus sampling. It considers the most
              typical tokens whose cumulative probability is at most typical_p.

              Required range: `0 <= x <= 1`

          user: A unique identifier representing your end-user, which can help monitor and
              detect abuse.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["model", "prompt"], ["model", "prompt", "stream"])
    def create(
        self,
        *,
        model: str,
        prompt: Union[str, SequenceNotStr[str], Iterable[int], Iterable[Iterable[int]]],
        context_length_exceeded_behavior: Literal["error", "truncate"] | Omit = omit,
        echo: Optional[bool] | Omit = omit,
        echo_last: Optional[int] | Omit = omit,
        frequency_penalty: Optional[float] | Omit = omit,
        ignore_eos: bool | Omit = omit,
        images: Union[SequenceNotStr[str], Iterable[SequenceNotStr[str]], None] | Omit = omit,
        logit_bias: Optional[Dict[str, float]] | Omit = omit,
        logprobs: Union[int, bool, None] | Omit = omit,
        max_completion_tokens: Optional[int] | Omit = omit,
        max_tokens: Optional[int] | Omit = omit,
        metadata: Optional[Dict[str, str]] | Omit = omit,
        min_p: Optional[float] | Omit = omit,
        mirostat_lr: Optional[float] | Omit = omit,
        mirostat_target: Optional[float] | Omit = omit,
        n: int | Omit = omit,
        perf_metrics_in_response: Optional[bool] | Omit = omit,
        prediction: Optional[completion_create_params.Prediction] | Omit = omit,
        presence_penalty: Optional[float] | Omit = omit,
        prompt_cache_isolation_key: Optional[str] | Omit = omit,
        raw_output: Optional[bool] | Omit = omit,
        reasoning_effort: Union[Literal["low", "medium", "high", "none"], int, bool, None] | Omit = omit,
        reasoning_history: Optional[Literal["disabled", "interleaved", "preserved"]] | Omit = omit,
        repetition_penalty: Optional[float] | Omit = omit,
        response_format: Optional[completion_create_params.ResponseFormat] | Omit = omit,
        return_token_ids: Optional[bool] | Omit = omit,
        seed: Optional[int] | Omit = omit,
        speculation: Union[str, Iterable[int], None] | Omit = omit,
        stop: Union[str, SequenceNotStr[str], None] | Omit = omit,
        stream: Optional[Literal[False]] | Literal[True] | Omit = omit,
        temperature: Optional[float] | Omit = omit,
        top_k: Optional[int] | Omit = omit,
        top_logprobs: Optional[int] | Omit = omit,
        top_p: Optional[float] | Omit = omit,
        typical_p: Optional[float] | Omit = omit,
        user: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CompletionCreateResponse | Stream[CompletionChunk]:
        return self._post(
            "/v1/completions"
            if self._client._base_url_overridden
            else "https://api.fireworks.ai/inference/v1/completions",
            body=maybe_transform(
                {
                    "model": model,
                    "prompt": prompt,
                    "context_length_exceeded_behavior": context_length_exceeded_behavior,
                    "echo": echo,
                    "echo_last": echo_last,
                    "frequency_penalty": frequency_penalty,
                    "ignore_eos": ignore_eos,
                    "images": images,
                    "logit_bias": logit_bias,
                    "logprobs": logprobs,
                    "max_completion_tokens": max_completion_tokens,
                    "max_tokens": max_tokens,
                    "metadata": metadata,
                    "min_p": min_p,
                    "mirostat_lr": mirostat_lr,
                    "mirostat_target": mirostat_target,
                    "n": n,
                    "perf_metrics_in_response": perf_metrics_in_response,
                    "prediction": prediction,
                    "presence_penalty": presence_penalty,
                    "prompt_cache_isolation_key": prompt_cache_isolation_key,
                    "raw_output": raw_output,
                    "reasoning_effort": reasoning_effort,
                    "reasoning_history": reasoning_history,
                    "repetition_penalty": repetition_penalty,
                    "response_format": response_format,
                    "return_token_ids": return_token_ids,
                    "seed": seed,
                    "speculation": speculation,
                    "stop": stop,
                    "stream": stream,
                    "temperature": temperature,
                    "top_k": top_k,
                    "top_logprobs": top_logprobs,
                    "top_p": top_p,
                    "typical_p": typical_p,
                    "user": user,
                },
                completion_create_params.CompletionCreateParamsStreaming
                if stream
                else completion_create_params.CompletionCreateParamsNonStreaming,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CompletionCreateResponse,
            stream=stream or False,
            stream_cls=Stream[CompletionChunk],
        )


class AsyncCompletionsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncCompletionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncCompletionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCompletionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/fw-ai-external/python-sdk#with_streaming_response
        """
        return AsyncCompletionsResourceWithStreamingResponse(self)

    @overload
    async def create(
        self,
        *,
        model: str,
        prompt: Union[str, SequenceNotStr[str], Iterable[int], Iterable[Iterable[int]]],
        context_length_exceeded_behavior: Literal["error", "truncate"] | Omit = omit,
        echo: Optional[bool] | Omit = omit,
        echo_last: Optional[int] | Omit = omit,
        frequency_penalty: Optional[float] | Omit = omit,
        ignore_eos: bool | Omit = omit,
        images: Union[SequenceNotStr[str], Iterable[SequenceNotStr[str]], None] | Omit = omit,
        logit_bias: Optional[Dict[str, float]] | Omit = omit,
        logprobs: Union[int, bool, None] | Omit = omit,
        max_completion_tokens: Optional[int] | Omit = omit,
        max_tokens: Optional[int] | Omit = omit,
        metadata: Optional[Dict[str, str]] | Omit = omit,
        min_p: Optional[float] | Omit = omit,
        mirostat_lr: Optional[float] | Omit = omit,
        mirostat_target: Optional[float] | Omit = omit,
        n: int | Omit = omit,
        perf_metrics_in_response: Optional[bool] | Omit = omit,
        prediction: Optional[completion_create_params.Prediction] | Omit = omit,
        presence_penalty: Optional[float] | Omit = omit,
        prompt_cache_isolation_key: Optional[str] | Omit = omit,
        raw_output: Optional[bool] | Omit = omit,
        reasoning_effort: Union[Literal["low", "medium", "high", "none"], int, bool, None] | Omit = omit,
        reasoning_history: Optional[Literal["disabled", "interleaved", "preserved"]] | Omit = omit,
        repetition_penalty: Optional[float] | Omit = omit,
        response_format: Optional[completion_create_params.ResponseFormat] | Omit = omit,
        return_token_ids: Optional[bool] | Omit = omit,
        seed: Optional[int] | Omit = omit,
        speculation: Union[str, Iterable[int], None] | Omit = omit,
        stop: Union[str, SequenceNotStr[str], None] | Omit = omit,
        stream: Optional[Literal[False]] | Omit = omit,
        temperature: Optional[float] | Omit = omit,
        top_k: Optional[int] | Omit = omit,
        top_logprobs: Optional[int] | Omit = omit,
        top_p: Optional[float] | Omit = omit,
        typical_p: Optional[float] | Omit = omit,
        user: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CompletionCreateResponse:
        """
        Create a completion for the provided prompt and parameters.

        Args:
          model: The name of the model to use.

              Example: `"accounts/fireworks/models/kimi-k2-instruct-0905"`

          prompt: The prompt to generate completions for.

              It can be a single string or an array of strings.

              It can also be an array of integers or an array of integer arrays, which allows
              to pass already tokenized prompt.

              If multiple prompts are specified, several choices with corresponding `index`
              will be returned in the output.

          context_length_exceeded_behavior: What to do if the token count of prompt plus `max_tokens` exceeds the model's
              context window.

              Passing `truncate` limits the `max_tokens` to at most
              `context_window_length - prompt_length`. This is the default.

              Passing `error` would trigger a request error.

              The default of `'truncate'` is selected as it allows to ask for high
              `max_tokens` value while respecting the context window length without having to
              do client-side prompt tokenization.

              Note, that it differs from OpenAI's behavior that matches that of `error`.

          echo: Echo back the prompt in addition to the completion.

          echo_last: Echo back the last N tokens of the prompt in addition to the completion. This is
              useful for obtaining logprobs of the prompt suffix but without transferring too
              much data. Passing `echo_last=len(prompt)` is the same as `echo=True`

          frequency_penalty: Number between -2.0 and 2.0. Positive values penalize new tokens based on their
              existing frequency in the text so far, decreasing the model's likelihood to
              repeat the same line verbatim.

              Reasonable value is around 0.1 to 1 if the aim is to just reduce repetitive
              samples somewhat. If the aim is to strongly suppress repetition, then one can
              increase the coefficients up to 2, but this can noticeably degrade the quality
              of samples. Negative values can be used to increase the likelihood of
              repetition.

              See also `presence_penalty` for penalizing tokens that have at least one
              appearance at a fixed rate.

              OpenAI compatible (follows OpenAI's conventions for handling token frequency and
              repetition penalties).

              Required range: `-2 <= x <= 2`

          ignore_eos: This setting controls whether the model should ignore the End of Sequence (EOS)
              token. When set to `True`, the model will continue generating tokens even after
              the EOS token is produced. By default, it stops when the EOS token is reached.

          images: The list of base64 encoded images for visual language completition generation.

              They should be formatted as MIME_TYPE,<base64 encoded str>

              eg. data:image/jpeg;base64,<base64 encoded str>

              Additionally, the number of images provided should match the number of '<image>'
              special token in the prompt

          logit_bias: Modify the likelihood of specified tokens appearing in the completion. Accepts a
              json object that maps tokens (specified by their token ID in the tokenizer) to
              an associated bias value from -100 to 100. Mathematically, the bias is added to
              the logits generated by the model prior to sampling.

          logprobs: Include log probabilities in the response. This accepts either a boolean or an
              integer:

              If set to `true`, log probabilities are included and the number of alternatives
              can be controlled via `top_logprobs` (OpenAI-compatible behavior).

              If set to an integer N (0-5), include log probabilities for up to N most likely
              tokens per position in the legacy format.

              The API will always return the logprob of the sampled token, so there may be up
              to `logprobs+1` elements in the response when an integer is used. The maximum
              value for the integer form is 5.

          max_completion_tokens: Alias for max_tokens. Cannot be specified together with max_tokens.

          max_tokens: The maximum number of tokens to generate in the completion. If the token count
              of your prompt plus max_tokens exceeds the model's context length, the behavior
              depends on context_length_exceeded_behavior. By default, max_tokens will be
              lowered to fit in the context window instead of returning an error.

          metadata: Additional metadata to store with the request for tracing/distillation.

          min_p: Minimum probability threshold for token selection. Only tokens with
              probability >= min_p are considered for selection. This is an alternative to
              `top_p` and `top_k` sampling.

              Required range: `0 <= x <= 1`

          mirostat_lr: Specifies the learning rate for the Mirostat sampling algorithm, which controls
              how quickly the model adjusts its token distribution to maintain the target
              perplexity. A smaller value slows down the adjustments, leading to more stable
              but gradual shifts, while higher values speed up corrections at the cost of
              potential instability.

          mirostat_target: Defines the target perplexity for the Mirostat algorithm. Perplexity measures
              the unpredictability of the generated text, with higher values encouraging more
              diverse and creative outputs, while lower values prioritize predictability and
              coherence. The algorithm dynamically adjusts the token selection to maintain
              this target during text generation.

              If not specified, Mirostat sampling is disabled.

          n: How many completions to generate for each prompt.

              **Note:** Because this parameter generates many completions, it can quickly
              consume your token quota. Use carefully and ensure that you have reasonable
              settings for `max_tokens` and `stop`.

              Required range: `1 <= x <= 128`

              Example: `1`

          perf_metrics_in_response: Whether to include performance metrics in the response body.

              **Non-streaming requests:** Performance metrics are always included in response
              headers (e.g., `fireworks-prompt-tokens`,
              `fireworks-server-time-to-first-token`). Setting this to `true` additionally
              includes the same metrics in the response body under the `perf_metrics` field.

              **Streaming requests:** Performance metrics are only included in the response
              body under the `perf_metrics` field in the final chunk (when `finish_reason` is
              set). This is because headers may not be accessible during streaming.

              The response body `perf_metrics` field contains the following metrics:

              **Basic Metrics (all deployments):**

              - `prompt-tokens`: Number of tokens in the prompt
              - `server-time-to-first-token`: Time from request start to first token (in
                seconds)
              - `server-processing-time`: Total processing time (in seconds, only for
                completed requests)

              **Predicted Outputs Metrics:**

              - `speculation-prompt-tokens`: Number of speculative prompt tokens
              - `speculation-prompt-matched-tokens`: Number of matched speculative prompt
                tokens (for completed requests)

              **Dedicated Deployment Only Metrics:**

              - `speculation-generated-tokens`: Number of speculative generated tokens (for
                completed requests)
              - `speculation-acceptance`: Speculation acceptance rates by position
              - `cached-prompt-tokens`: Number of cached prompt tokens
              - `backend-host`: Hostname of the backend server
              - `num-concurrent-requests`: Number of concurrent requests
              - `deployment`: Deployment name
              - `tokenizer-queue-duration`: Time spent in tokenizer queue
              - `tokenizer-duration`: Time spent in tokenizer
              - `prefill-queue-duration`: Time spent in prefill queue
              - `prefill-duration`: Time spent in prefill
              - `generation-queue-duration`: Time spent in generation queue

          prediction: OpenAI-compatible predicted output for speculative decoding. Can be a
              PredictedOutput object or a simple string. Automatically transformed to
              speculation.

          presence_penalty: Number between -2.0 and 2.0. Positive values penalize new tokens based on
              whether they appear in the text so far, increasing the model's likelihood to
              talk about new topics.

              Reasonable value is around 0.1 to 1 if the aim is to just reduce repetitive
              samples somewhat. If the aim is to strongly suppress repetition, then one can
              increase the coefficients up to 2, but this can noticeably degrade the quality
              of samples. Negative values can be used to increase the likelihood of
              repetition.

              See also `frequency_penalty` for penalizing tokens at an increasing rate
              depending on how often they appear.

              OpenAI compatible (follows OpenAI's conventions for handling token frequency and
              repetition penalties).

              Required range: `-2 <= x <= 2`

          prompt_cache_isolation_key: Isolation key for prompt caching to separate cache entries.

          raw_output: Return raw output from the model.

          reasoning_effort: Controls reasoning behavior for supported models. When enabled, the model's
              reasoning appears in the `reasoning_content` field of the response, separate
              from the final answer in `content`.

              **Accepted values:**

              - **String** (OpenAI-compatible): `'low'`, `'medium'`, or `'high'` to enable
                reasoning with varying effort levels; `'none'` to disable reasoning.
              - **Boolean** (Fireworks extension): `true` to enable reasoning, `false` to
                disable it.
              - **Integer** (Fireworks extension): A positive integer to set a hard token
                limit on reasoning output (only effective for grammar-based reasoning models).

              **Important:** Boolean values are normalized internally: `true` becomes
              `'medium'`, and `false` becomes `'none'`. This normalization happens before
              model-specific validation, so if a model doesn't support `'none'`, passing
              `false` will produce an error referencing `'none'`.

              **Model-specific behavior:**

              - **Qwen3 (e.g., Qwen3-8B)**: Grammar-based reasoning. Default reasoning on. Use
                `'none'` or `false` to disable. Supports integer token limits to cap reasoning
                output. `'low'` maps to a default token limit (~3000 tokens).
              - **DeepSeek V3.1, DeepSeek V3.2**: Binary on/off reasoning. Default reasoning
                off. Any value except `'none'`/`false`/`null` enables reasoning; effort levels
                and integers have no additional effect.
              - **GLM 4.5, GLM 4.5 Air, GLM 4.6, GLM 4.7**: Binary on/off reasoning. Default
                reasoning on. Use `'none'` or `false` to disable; effort levels and integers
                have no additional effect.
              - **Harmony (OpenAI GPT-OSS 120B, GPT-OSS 20B)**: Accepts only `'low'`,
                `'medium'`, or `'high'`. Does not support `'none'`, `false`, or integer
                values—using these will return an error (e.g., "Invalid reasoning effort:
                none"). When omitted, defaults to `'medium'`. Lower effort produces faster
                responses with shorter reasoning.

          reasoning_history: Controls how historical assistant reasoning content is included in the prompt
              for multi-turn conversations.

              **Accepted values:**

              - `null`: Use model/template default behavior
              - `'disabled'`: Remove all historical reasoning content from the prompt
              - `'interleaved'`: Keep only reasoning content after the last user message
              - `'preserved'`: Retain all previous reasoning content across the conversation

              **Model support:**

              | Model            | Default         | Supported values                             |
              | ---------------- | --------------- | -------------------------------------------- |
              | Kimi K2 Instruct | `'preserved'`   | `'disabled'`, `'interleaved'`, `'preserved'` |
              | MiniMax M2       | `'interleaved'` | `'disabled'`, `'interleaved'`                |
              | GLM-4.7          | `'interleaved'` | `'disabled'`, `'interleaved'`, `'preserved'` |
              | GLM-4.6          | `'interleaved'` | `'disabled'`, `'interleaved'`                |

              For other models, refer to the model provider's documentation.

              **Note:** This parameter controls prompt formatting only. To disable reasoning
              computation entirely, use `reasoning_effort='none'`.

          repetition_penalty: Applies a penalty to repeated tokens to discourage or encourage repetition. A
              value of `1.0` means no penalty, allowing free repetition. Values above `1.0`
              penalize repetition, reducing the likelihood of repeating tokens. Values between
              `0.0` and `1.0` reward repetition, increasing the chance of repeated tokens. For
              a good balance, a value of `1.2` is often recommended. Note that the penalty is
              applied to both the generated output and the prompt in decoder-only models.

              Required range: `0 <= x <= 2`

          response_format: Allows to force the model to produce specific output format.

              Setting to `{ "type": "json_object" }` enables JSON mode, which guarantees the
              message the model generates is valid JSON.

              If `"type"` is `"json_schema"`, a JSON schema must be provided. E.g.,
              `response_format = {"type": "json_schema", "json_schema": <json_schema>}`.

              Important: when using JSON mode, it's crucial to also instruct the model to
              produce JSON via a system or user message. Without this, the model may generate
              an unending stream of whitespace until the generation reaches the token limit,
              resulting in a long-running and seemingly "stuck" request.

              Also note that the message content may be partially cut off if
              `finish_reason="length"`, which indicates the generation exceeded `max_tokens`
              or the conversation exceeded the max context length. In this case the return
              value might not be a valid JSON.

          return_token_ids: Return token IDs alongside text to avoid retokenization drift.

          seed: Random seed for deterministic sampling.

          speculation: Speculative decoding prompt or token IDs to speed up generation.

          stop: Up to 4 sequences where the API will stop generating further tokens. The
              returned text will NOT contain the stop sequence.

          stream: Whether to stream back partial progress. If set, tokens will be sent as
              data-only
              [server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format)
              as they become available, with the stream terminated by a `data: [DONE]`
              message.

          temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 will
              make the output more random, while lower values like 0.2 will make it more
              focused and deterministic.

              We generally recommend altering this or top_p but not both.

              Required range: `0 <= x <= 2`

              Example: `1`

          top_k: Top-k sampling is another sampling method where the k most probable next tokens
              are filtered and the probability mass is redistributed among only those k next
              tokens. The value of k controls the number of candidates for the next token at
              each step during text generation. Must be between 0 and 100.

              Required range: `0 <= x <= 100`

              Example: `50`

          top_logprobs: An integer between 0 and 5 specifying the number of most likely tokens to return
              at each token position, each with an associated log probability. The minimum
              value is 0 and the maximum value is 5.

              When `logprobs` is set, `top_logprobs` can be used to modify how many top log
              probabilities are returned. If `top_logprobs` is not set, the API will return up
              to `logprobs` tokens per position.

              Required range: `0 <= x <= 5`

          top_p: An alternative to sampling with temperature, called nucleus sampling, where the
              model considers the results of the tokens with top_p probability mass. So 0.1
              means only the tokens comprising the top 10% probability mass are considered.

              We generally recommend altering this or temperature but not both.

              Required range: `0 <= x <= 1`

              Example: `1`

          typical_p: Typical-p sampling is an alternative to nucleus sampling. It considers the most
              typical tokens whose cumulative probability is at most typical_p.

              Required range: `0 <= x <= 1`

          user: A unique identifier representing your end-user, which can help monitor and
              detect abuse.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create(
        self,
        *,
        model: str,
        prompt: Union[str, SequenceNotStr[str], Iterable[int], Iterable[Iterable[int]]],
        stream: Literal[True],
        context_length_exceeded_behavior: Literal["error", "truncate"] | Omit = omit,
        echo: Optional[bool] | Omit = omit,
        echo_last: Optional[int] | Omit = omit,
        frequency_penalty: Optional[float] | Omit = omit,
        ignore_eos: bool | Omit = omit,
        images: Union[SequenceNotStr[str], Iterable[SequenceNotStr[str]], None] | Omit = omit,
        logit_bias: Optional[Dict[str, float]] | Omit = omit,
        logprobs: Union[int, bool, None] | Omit = omit,
        max_completion_tokens: Optional[int] | Omit = omit,
        max_tokens: Optional[int] | Omit = omit,
        metadata: Optional[Dict[str, str]] | Omit = omit,
        min_p: Optional[float] | Omit = omit,
        mirostat_lr: Optional[float] | Omit = omit,
        mirostat_target: Optional[float] | Omit = omit,
        n: int | Omit = omit,
        perf_metrics_in_response: Optional[bool] | Omit = omit,
        prediction: Optional[completion_create_params.Prediction] | Omit = omit,
        presence_penalty: Optional[float] | Omit = omit,
        prompt_cache_isolation_key: Optional[str] | Omit = omit,
        raw_output: Optional[bool] | Omit = omit,
        reasoning_effort: Union[Literal["low", "medium", "high", "none"], int, bool, None] | Omit = omit,
        reasoning_history: Optional[Literal["disabled", "interleaved", "preserved"]] | Omit = omit,
        repetition_penalty: Optional[float] | Omit = omit,
        response_format: Optional[completion_create_params.ResponseFormat] | Omit = omit,
        return_token_ids: Optional[bool] | Omit = omit,
        seed: Optional[int] | Omit = omit,
        speculation: Union[str, Iterable[int], None] | Omit = omit,
        stop: Union[str, SequenceNotStr[str], None] | Omit = omit,
        temperature: Optional[float] | Omit = omit,
        top_k: Optional[int] | Omit = omit,
        top_logprobs: Optional[int] | Omit = omit,
        top_p: Optional[float] | Omit = omit,
        typical_p: Optional[float] | Omit = omit,
        user: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncStream[CompletionChunk]:
        """
        Create a completion for the provided prompt and parameters.

        Args:
          model: The name of the model to use.

              Example: `"accounts/fireworks/models/kimi-k2-instruct-0905"`

          prompt: The prompt to generate completions for.

              It can be a single string or an array of strings.

              It can also be an array of integers or an array of integer arrays, which allows
              to pass already tokenized prompt.

              If multiple prompts are specified, several choices with corresponding `index`
              will be returned in the output.

          stream: Whether to stream back partial progress. If set, tokens will be sent as
              data-only
              [server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format)
              as they become available, with the stream terminated by a `data: [DONE]`
              message.

          context_length_exceeded_behavior: What to do if the token count of prompt plus `max_tokens` exceeds the model's
              context window.

              Passing `truncate` limits the `max_tokens` to at most
              `context_window_length - prompt_length`. This is the default.

              Passing `error` would trigger a request error.

              The default of `'truncate'` is selected as it allows to ask for high
              `max_tokens` value while respecting the context window length without having to
              do client-side prompt tokenization.

              Note, that it differs from OpenAI's behavior that matches that of `error`.

          echo: Echo back the prompt in addition to the completion.

          echo_last: Echo back the last N tokens of the prompt in addition to the completion. This is
              useful for obtaining logprobs of the prompt suffix but without transferring too
              much data. Passing `echo_last=len(prompt)` is the same as `echo=True`

          frequency_penalty: Number between -2.0 and 2.0. Positive values penalize new tokens based on their
              existing frequency in the text so far, decreasing the model's likelihood to
              repeat the same line verbatim.

              Reasonable value is around 0.1 to 1 if the aim is to just reduce repetitive
              samples somewhat. If the aim is to strongly suppress repetition, then one can
              increase the coefficients up to 2, but this can noticeably degrade the quality
              of samples. Negative values can be used to increase the likelihood of
              repetition.

              See also `presence_penalty` for penalizing tokens that have at least one
              appearance at a fixed rate.

              OpenAI compatible (follows OpenAI's conventions for handling token frequency and
              repetition penalties).

              Required range: `-2 <= x <= 2`

          ignore_eos: This setting controls whether the model should ignore the End of Sequence (EOS)
              token. When set to `True`, the model will continue generating tokens even after
              the EOS token is produced. By default, it stops when the EOS token is reached.

          images: The list of base64 encoded images for visual language completition generation.

              They should be formatted as MIME_TYPE,<base64 encoded str>

              eg. data:image/jpeg;base64,<base64 encoded str>

              Additionally, the number of images provided should match the number of '<image>'
              special token in the prompt

          logit_bias: Modify the likelihood of specified tokens appearing in the completion. Accepts a
              json object that maps tokens (specified by their token ID in the tokenizer) to
              an associated bias value from -100 to 100. Mathematically, the bias is added to
              the logits generated by the model prior to sampling.

          logprobs: Include log probabilities in the response. This accepts either a boolean or an
              integer:

              If set to `true`, log probabilities are included and the number of alternatives
              can be controlled via `top_logprobs` (OpenAI-compatible behavior).

              If set to an integer N (0-5), include log probabilities for up to N most likely
              tokens per position in the legacy format.

              The API will always return the logprob of the sampled token, so there may be up
              to `logprobs+1` elements in the response when an integer is used. The maximum
              value for the integer form is 5.

          max_completion_tokens: Alias for max_tokens. Cannot be specified together with max_tokens.

          max_tokens: The maximum number of tokens to generate in the completion. If the token count
              of your prompt plus max_tokens exceeds the model's context length, the behavior
              depends on context_length_exceeded_behavior. By default, max_tokens will be
              lowered to fit in the context window instead of returning an error.

          metadata: Additional metadata to store with the request for tracing/distillation.

          min_p: Minimum probability threshold for token selection. Only tokens with
              probability >= min_p are considered for selection. This is an alternative to
              `top_p` and `top_k` sampling.

              Required range: `0 <= x <= 1`

          mirostat_lr: Specifies the learning rate for the Mirostat sampling algorithm, which controls
              how quickly the model adjusts its token distribution to maintain the target
              perplexity. A smaller value slows down the adjustments, leading to more stable
              but gradual shifts, while higher values speed up corrections at the cost of
              potential instability.

          mirostat_target: Defines the target perplexity for the Mirostat algorithm. Perplexity measures
              the unpredictability of the generated text, with higher values encouraging more
              diverse and creative outputs, while lower values prioritize predictability and
              coherence. The algorithm dynamically adjusts the token selection to maintain
              this target during text generation.

              If not specified, Mirostat sampling is disabled.

          n: How many completions to generate for each prompt.

              **Note:** Because this parameter generates many completions, it can quickly
              consume your token quota. Use carefully and ensure that you have reasonable
              settings for `max_tokens` and `stop`.

              Required range: `1 <= x <= 128`

              Example: `1`

          perf_metrics_in_response: Whether to include performance metrics in the response body.

              **Non-streaming requests:** Performance metrics are always included in response
              headers (e.g., `fireworks-prompt-tokens`,
              `fireworks-server-time-to-first-token`). Setting this to `true` additionally
              includes the same metrics in the response body under the `perf_metrics` field.

              **Streaming requests:** Performance metrics are only included in the response
              body under the `perf_metrics` field in the final chunk (when `finish_reason` is
              set). This is because headers may not be accessible during streaming.

              The response body `perf_metrics` field contains the following metrics:

              **Basic Metrics (all deployments):**

              - `prompt-tokens`: Number of tokens in the prompt
              - `server-time-to-first-token`: Time from request start to first token (in
                seconds)
              - `server-processing-time`: Total processing time (in seconds, only for
                completed requests)

              **Predicted Outputs Metrics:**

              - `speculation-prompt-tokens`: Number of speculative prompt tokens
              - `speculation-prompt-matched-tokens`: Number of matched speculative prompt
                tokens (for completed requests)

              **Dedicated Deployment Only Metrics:**

              - `speculation-generated-tokens`: Number of speculative generated tokens (for
                completed requests)
              - `speculation-acceptance`: Speculation acceptance rates by position
              - `cached-prompt-tokens`: Number of cached prompt tokens
              - `backend-host`: Hostname of the backend server
              - `num-concurrent-requests`: Number of concurrent requests
              - `deployment`: Deployment name
              - `tokenizer-queue-duration`: Time spent in tokenizer queue
              - `tokenizer-duration`: Time spent in tokenizer
              - `prefill-queue-duration`: Time spent in prefill queue
              - `prefill-duration`: Time spent in prefill
              - `generation-queue-duration`: Time spent in generation queue

          prediction: OpenAI-compatible predicted output for speculative decoding. Can be a
              PredictedOutput object or a simple string. Automatically transformed to
              speculation.

          presence_penalty: Number between -2.0 and 2.0. Positive values penalize new tokens based on
              whether they appear in the text so far, increasing the model's likelihood to
              talk about new topics.

              Reasonable value is around 0.1 to 1 if the aim is to just reduce repetitive
              samples somewhat. If the aim is to strongly suppress repetition, then one can
              increase the coefficients up to 2, but this can noticeably degrade the quality
              of samples. Negative values can be used to increase the likelihood of
              repetition.

              See also `frequency_penalty` for penalizing tokens at an increasing rate
              depending on how often they appear.

              OpenAI compatible (follows OpenAI's conventions for handling token frequency and
              repetition penalties).

              Required range: `-2 <= x <= 2`

          prompt_cache_isolation_key: Isolation key for prompt caching to separate cache entries.

          raw_output: Return raw output from the model.

          reasoning_effort: Controls reasoning behavior for supported models. When enabled, the model's
              reasoning appears in the `reasoning_content` field of the response, separate
              from the final answer in `content`.

              **Accepted values:**

              - **String** (OpenAI-compatible): `'low'`, `'medium'`, or `'high'` to enable
                reasoning with varying effort levels; `'none'` to disable reasoning.
              - **Boolean** (Fireworks extension): `true` to enable reasoning, `false` to
                disable it.
              - **Integer** (Fireworks extension): A positive integer to set a hard token
                limit on reasoning output (only effective for grammar-based reasoning models).

              **Important:** Boolean values are normalized internally: `true` becomes
              `'medium'`, and `false` becomes `'none'`. This normalization happens before
              model-specific validation, so if a model doesn't support `'none'`, passing
              `false` will produce an error referencing `'none'`.

              **Model-specific behavior:**

              - **Qwen3 (e.g., Qwen3-8B)**: Grammar-based reasoning. Default reasoning on. Use
                `'none'` or `false` to disable. Supports integer token limits to cap reasoning
                output. `'low'` maps to a default token limit (~3000 tokens).
              - **DeepSeek V3.1, DeepSeek V3.2**: Binary on/off reasoning. Default reasoning
                off. Any value except `'none'`/`false`/`null` enables reasoning; effort levels
                and integers have no additional effect.
              - **GLM 4.5, GLM 4.5 Air, GLM 4.6, GLM 4.7**: Binary on/off reasoning. Default
                reasoning on. Use `'none'` or `false` to disable; effort levels and integers
                have no additional effect.
              - **Harmony (OpenAI GPT-OSS 120B, GPT-OSS 20B)**: Accepts only `'low'`,
                `'medium'`, or `'high'`. Does not support `'none'`, `false`, or integer
                values—using these will return an error (e.g., "Invalid reasoning effort:
                none"). When omitted, defaults to `'medium'`. Lower effort produces faster
                responses with shorter reasoning.

          reasoning_history: Controls how historical assistant reasoning content is included in the prompt
              for multi-turn conversations.

              **Accepted values:**

              - `null`: Use model/template default behavior
              - `'disabled'`: Remove all historical reasoning content from the prompt
              - `'interleaved'`: Keep only reasoning content after the last user message
              - `'preserved'`: Retain all previous reasoning content across the conversation

              **Model support:**

              | Model            | Default         | Supported values                             |
              | ---------------- | --------------- | -------------------------------------------- |
              | Kimi K2 Instruct | `'preserved'`   | `'disabled'`, `'interleaved'`, `'preserved'` |
              | MiniMax M2       | `'interleaved'` | `'disabled'`, `'interleaved'`                |
              | GLM-4.7          | `'interleaved'` | `'disabled'`, `'interleaved'`, `'preserved'` |
              | GLM-4.6          | `'interleaved'` | `'disabled'`, `'interleaved'`                |

              For other models, refer to the model provider's documentation.

              **Note:** This parameter controls prompt formatting only. To disable reasoning
              computation entirely, use `reasoning_effort='none'`.

          repetition_penalty: Applies a penalty to repeated tokens to discourage or encourage repetition. A
              value of `1.0` means no penalty, allowing free repetition. Values above `1.0`
              penalize repetition, reducing the likelihood of repeating tokens. Values between
              `0.0` and `1.0` reward repetition, increasing the chance of repeated tokens. For
              a good balance, a value of `1.2` is often recommended. Note that the penalty is
              applied to both the generated output and the prompt in decoder-only models.

              Required range: `0 <= x <= 2`

          response_format: Allows to force the model to produce specific output format.

              Setting to `{ "type": "json_object" }` enables JSON mode, which guarantees the
              message the model generates is valid JSON.

              If `"type"` is `"json_schema"`, a JSON schema must be provided. E.g.,
              `response_format = {"type": "json_schema", "json_schema": <json_schema>}`.

              Important: when using JSON mode, it's crucial to also instruct the model to
              produce JSON via a system or user message. Without this, the model may generate
              an unending stream of whitespace until the generation reaches the token limit,
              resulting in a long-running and seemingly "stuck" request.

              Also note that the message content may be partially cut off if
              `finish_reason="length"`, which indicates the generation exceeded `max_tokens`
              or the conversation exceeded the max context length. In this case the return
              value might not be a valid JSON.

          return_token_ids: Return token IDs alongside text to avoid retokenization drift.

          seed: Random seed for deterministic sampling.

          speculation: Speculative decoding prompt or token IDs to speed up generation.

          stop: Up to 4 sequences where the API will stop generating further tokens. The
              returned text will NOT contain the stop sequence.

          temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 will
              make the output more random, while lower values like 0.2 will make it more
              focused and deterministic.

              We generally recommend altering this or top_p but not both.

              Required range: `0 <= x <= 2`

              Example: `1`

          top_k: Top-k sampling is another sampling method where the k most probable next tokens
              are filtered and the probability mass is redistributed among only those k next
              tokens. The value of k controls the number of candidates for the next token at
              each step during text generation. Must be between 0 and 100.

              Required range: `0 <= x <= 100`

              Example: `50`

          top_logprobs: An integer between 0 and 5 specifying the number of most likely tokens to return
              at each token position, each with an associated log probability. The minimum
              value is 0 and the maximum value is 5.

              When `logprobs` is set, `top_logprobs` can be used to modify how many top log
              probabilities are returned. If `top_logprobs` is not set, the API will return up
              to `logprobs` tokens per position.

              Required range: `0 <= x <= 5`

          top_p: An alternative to sampling with temperature, called nucleus sampling, where the
              model considers the results of the tokens with top_p probability mass. So 0.1
              means only the tokens comprising the top 10% probability mass are considered.

              We generally recommend altering this or temperature but not both.

              Required range: `0 <= x <= 1`

              Example: `1`

          typical_p: Typical-p sampling is an alternative to nucleus sampling. It considers the most
              typical tokens whose cumulative probability is at most typical_p.

              Required range: `0 <= x <= 1`

          user: A unique identifier representing your end-user, which can help monitor and
              detect abuse.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create(
        self,
        *,
        model: str,
        prompt: Union[str, SequenceNotStr[str], Iterable[int], Iterable[Iterable[int]]],
        stream: bool,
        context_length_exceeded_behavior: Literal["error", "truncate"] | Omit = omit,
        echo: Optional[bool] | Omit = omit,
        echo_last: Optional[int] | Omit = omit,
        frequency_penalty: Optional[float] | Omit = omit,
        ignore_eos: bool | Omit = omit,
        images: Union[SequenceNotStr[str], Iterable[SequenceNotStr[str]], None] | Omit = omit,
        logit_bias: Optional[Dict[str, float]] | Omit = omit,
        logprobs: Union[int, bool, None] | Omit = omit,
        max_completion_tokens: Optional[int] | Omit = omit,
        max_tokens: Optional[int] | Omit = omit,
        metadata: Optional[Dict[str, str]] | Omit = omit,
        min_p: Optional[float] | Omit = omit,
        mirostat_lr: Optional[float] | Omit = omit,
        mirostat_target: Optional[float] | Omit = omit,
        n: int | Omit = omit,
        perf_metrics_in_response: Optional[bool] | Omit = omit,
        prediction: Optional[completion_create_params.Prediction] | Omit = omit,
        presence_penalty: Optional[float] | Omit = omit,
        prompt_cache_isolation_key: Optional[str] | Omit = omit,
        raw_output: Optional[bool] | Omit = omit,
        reasoning_effort: Union[Literal["low", "medium", "high", "none"], int, bool, None] | Omit = omit,
        reasoning_history: Optional[Literal["disabled", "interleaved", "preserved"]] | Omit = omit,
        repetition_penalty: Optional[float] | Omit = omit,
        response_format: Optional[completion_create_params.ResponseFormat] | Omit = omit,
        return_token_ids: Optional[bool] | Omit = omit,
        seed: Optional[int] | Omit = omit,
        speculation: Union[str, Iterable[int], None] | Omit = omit,
        stop: Union[str, SequenceNotStr[str], None] | Omit = omit,
        temperature: Optional[float] | Omit = omit,
        top_k: Optional[int] | Omit = omit,
        top_logprobs: Optional[int] | Omit = omit,
        top_p: Optional[float] | Omit = omit,
        typical_p: Optional[float] | Omit = omit,
        user: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CompletionCreateResponse | AsyncStream[CompletionChunk]:
        """
        Create a completion for the provided prompt and parameters.

        Args:
          model: The name of the model to use.

              Example: `"accounts/fireworks/models/kimi-k2-instruct-0905"`

          prompt: The prompt to generate completions for.

              It can be a single string or an array of strings.

              It can also be an array of integers or an array of integer arrays, which allows
              to pass already tokenized prompt.

              If multiple prompts are specified, several choices with corresponding `index`
              will be returned in the output.

          stream: Whether to stream back partial progress. If set, tokens will be sent as
              data-only
              [server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format)
              as they become available, with the stream terminated by a `data: [DONE]`
              message.

          context_length_exceeded_behavior: What to do if the token count of prompt plus `max_tokens` exceeds the model's
              context window.

              Passing `truncate` limits the `max_tokens` to at most
              `context_window_length - prompt_length`. This is the default.

              Passing `error` would trigger a request error.

              The default of `'truncate'` is selected as it allows to ask for high
              `max_tokens` value while respecting the context window length without having to
              do client-side prompt tokenization.

              Note, that it differs from OpenAI's behavior that matches that of `error`.

          echo: Echo back the prompt in addition to the completion.

          echo_last: Echo back the last N tokens of the prompt in addition to the completion. This is
              useful for obtaining logprobs of the prompt suffix but without transferring too
              much data. Passing `echo_last=len(prompt)` is the same as `echo=True`

          frequency_penalty: Number between -2.0 and 2.0. Positive values penalize new tokens based on their
              existing frequency in the text so far, decreasing the model's likelihood to
              repeat the same line verbatim.

              Reasonable value is around 0.1 to 1 if the aim is to just reduce repetitive
              samples somewhat. If the aim is to strongly suppress repetition, then one can
              increase the coefficients up to 2, but this can noticeably degrade the quality
              of samples. Negative values can be used to increase the likelihood of
              repetition.

              See also `presence_penalty` for penalizing tokens that have at least one
              appearance at a fixed rate.

              OpenAI compatible (follows OpenAI's conventions for handling token frequency and
              repetition penalties).

              Required range: `-2 <= x <= 2`

          ignore_eos: This setting controls whether the model should ignore the End of Sequence (EOS)
              token. When set to `True`, the model will continue generating tokens even after
              the EOS token is produced. By default, it stops when the EOS token is reached.

          images: The list of base64 encoded images for visual language completition generation.

              They should be formatted as MIME_TYPE,<base64 encoded str>

              eg. data:image/jpeg;base64,<base64 encoded str>

              Additionally, the number of images provided should match the number of '<image>'
              special token in the prompt

          logit_bias: Modify the likelihood of specified tokens appearing in the completion. Accepts a
              json object that maps tokens (specified by their token ID in the tokenizer) to
              an associated bias value from -100 to 100. Mathematically, the bias is added to
              the logits generated by the model prior to sampling.

          logprobs: Include log probabilities in the response. This accepts either a boolean or an
              integer:

              If set to `true`, log probabilities are included and the number of alternatives
              can be controlled via `top_logprobs` (OpenAI-compatible behavior).

              If set to an integer N (0-5), include log probabilities for up to N most likely
              tokens per position in the legacy format.

              The API will always return the logprob of the sampled token, so there may be up
              to `logprobs+1` elements in the response when an integer is used. The maximum
              value for the integer form is 5.

          max_completion_tokens: Alias for max_tokens. Cannot be specified together with max_tokens.

          max_tokens: The maximum number of tokens to generate in the completion. If the token count
              of your prompt plus max_tokens exceeds the model's context length, the behavior
              depends on context_length_exceeded_behavior. By default, max_tokens will be
              lowered to fit in the context window instead of returning an error.

          metadata: Additional metadata to store with the request for tracing/distillation.

          min_p: Minimum probability threshold for token selection. Only tokens with
              probability >= min_p are considered for selection. This is an alternative to
              `top_p` and `top_k` sampling.

              Required range: `0 <= x <= 1`

          mirostat_lr: Specifies the learning rate for the Mirostat sampling algorithm, which controls
              how quickly the model adjusts its token distribution to maintain the target
              perplexity. A smaller value slows down the adjustments, leading to more stable
              but gradual shifts, while higher values speed up corrections at the cost of
              potential instability.

          mirostat_target: Defines the target perplexity for the Mirostat algorithm. Perplexity measures
              the unpredictability of the generated text, with higher values encouraging more
              diverse and creative outputs, while lower values prioritize predictability and
              coherence. The algorithm dynamically adjusts the token selection to maintain
              this target during text generation.

              If not specified, Mirostat sampling is disabled.

          n: How many completions to generate for each prompt.

              **Note:** Because this parameter generates many completions, it can quickly
              consume your token quota. Use carefully and ensure that you have reasonable
              settings for `max_tokens` and `stop`.

              Required range: `1 <= x <= 128`

              Example: `1`

          perf_metrics_in_response: Whether to include performance metrics in the response body.

              **Non-streaming requests:** Performance metrics are always included in response
              headers (e.g., `fireworks-prompt-tokens`,
              `fireworks-server-time-to-first-token`). Setting this to `true` additionally
              includes the same metrics in the response body under the `perf_metrics` field.

              **Streaming requests:** Performance metrics are only included in the response
              body under the `perf_metrics` field in the final chunk (when `finish_reason` is
              set). This is because headers may not be accessible during streaming.

              The response body `perf_metrics` field contains the following metrics:

              **Basic Metrics (all deployments):**

              - `prompt-tokens`: Number of tokens in the prompt
              - `server-time-to-first-token`: Time from request start to first token (in
                seconds)
              - `server-processing-time`: Total processing time (in seconds, only for
                completed requests)

              **Predicted Outputs Metrics:**

              - `speculation-prompt-tokens`: Number of speculative prompt tokens
              - `speculation-prompt-matched-tokens`: Number of matched speculative prompt
                tokens (for completed requests)

              **Dedicated Deployment Only Metrics:**

              - `speculation-generated-tokens`: Number of speculative generated tokens (for
                completed requests)
              - `speculation-acceptance`: Speculation acceptance rates by position
              - `cached-prompt-tokens`: Number of cached prompt tokens
              - `backend-host`: Hostname of the backend server
              - `num-concurrent-requests`: Number of concurrent requests
              - `deployment`: Deployment name
              - `tokenizer-queue-duration`: Time spent in tokenizer queue
              - `tokenizer-duration`: Time spent in tokenizer
              - `prefill-queue-duration`: Time spent in prefill queue
              - `prefill-duration`: Time spent in prefill
              - `generation-queue-duration`: Time spent in generation queue

          prediction: OpenAI-compatible predicted output for speculative decoding. Can be a
              PredictedOutput object or a simple string. Automatically transformed to
              speculation.

          presence_penalty: Number between -2.0 and 2.0. Positive values penalize new tokens based on
              whether they appear in the text so far, increasing the model's likelihood to
              talk about new topics.

              Reasonable value is around 0.1 to 1 if the aim is to just reduce repetitive
              samples somewhat. If the aim is to strongly suppress repetition, then one can
              increase the coefficients up to 2, but this can noticeably degrade the quality
              of samples. Negative values can be used to increase the likelihood of
              repetition.

              See also `frequency_penalty` for penalizing tokens at an increasing rate
              depending on how often they appear.

              OpenAI compatible (follows OpenAI's conventions for handling token frequency and
              repetition penalties).

              Required range: `-2 <= x <= 2`

          prompt_cache_isolation_key: Isolation key for prompt caching to separate cache entries.

          raw_output: Return raw output from the model.

          reasoning_effort: Controls reasoning behavior for supported models. When enabled, the model's
              reasoning appears in the `reasoning_content` field of the response, separate
              from the final answer in `content`.

              **Accepted values:**

              - **String** (OpenAI-compatible): `'low'`, `'medium'`, or `'high'` to enable
                reasoning with varying effort levels; `'none'` to disable reasoning.
              - **Boolean** (Fireworks extension): `true` to enable reasoning, `false` to
                disable it.
              - **Integer** (Fireworks extension): A positive integer to set a hard token
                limit on reasoning output (only effective for grammar-based reasoning models).

              **Important:** Boolean values are normalized internally: `true` becomes
              `'medium'`, and `false` becomes `'none'`. This normalization happens before
              model-specific validation, so if a model doesn't support `'none'`, passing
              `false` will produce an error referencing `'none'`.

              **Model-specific behavior:**

              - **Qwen3 (e.g., Qwen3-8B)**: Grammar-based reasoning. Default reasoning on. Use
                `'none'` or `false` to disable. Supports integer token limits to cap reasoning
                output. `'low'` maps to a default token limit (~3000 tokens).
              - **DeepSeek V3.1, DeepSeek V3.2**: Binary on/off reasoning. Default reasoning
                off. Any value except `'none'`/`false`/`null` enables reasoning; effort levels
                and integers have no additional effect.
              - **GLM 4.5, GLM 4.5 Air, GLM 4.6, GLM 4.7**: Binary on/off reasoning. Default
                reasoning on. Use `'none'` or `false` to disable; effort levels and integers
                have no additional effect.
              - **Harmony (OpenAI GPT-OSS 120B, GPT-OSS 20B)**: Accepts only `'low'`,
                `'medium'`, or `'high'`. Does not support `'none'`, `false`, or integer
                values—using these will return an error (e.g., "Invalid reasoning effort:
                none"). When omitted, defaults to `'medium'`. Lower effort produces faster
                responses with shorter reasoning.

          reasoning_history: Controls how historical assistant reasoning content is included in the prompt
              for multi-turn conversations.

              **Accepted values:**

              - `null`: Use model/template default behavior
              - `'disabled'`: Remove all historical reasoning content from the prompt
              - `'interleaved'`: Keep only reasoning content after the last user message
              - `'preserved'`: Retain all previous reasoning content across the conversation

              **Model support:**

              | Model            | Default         | Supported values                             |
              | ---------------- | --------------- | -------------------------------------------- |
              | Kimi K2 Instruct | `'preserved'`   | `'disabled'`, `'interleaved'`, `'preserved'` |
              | MiniMax M2       | `'interleaved'` | `'disabled'`, `'interleaved'`                |
              | GLM-4.7          | `'interleaved'` | `'disabled'`, `'interleaved'`, `'preserved'` |
              | GLM-4.6          | `'interleaved'` | `'disabled'`, `'interleaved'`                |

              For other models, refer to the model provider's documentation.

              **Note:** This parameter controls prompt formatting only. To disable reasoning
              computation entirely, use `reasoning_effort='none'`.

          repetition_penalty: Applies a penalty to repeated tokens to discourage or encourage repetition. A
              value of `1.0` means no penalty, allowing free repetition. Values above `1.0`
              penalize repetition, reducing the likelihood of repeating tokens. Values between
              `0.0` and `1.0` reward repetition, increasing the chance of repeated tokens. For
              a good balance, a value of `1.2` is often recommended. Note that the penalty is
              applied to both the generated output and the prompt in decoder-only models.

              Required range: `0 <= x <= 2`

          response_format: Allows to force the model to produce specific output format.

              Setting to `{ "type": "json_object" }` enables JSON mode, which guarantees the
              message the model generates is valid JSON.

              If `"type"` is `"json_schema"`, a JSON schema must be provided. E.g.,
              `response_format = {"type": "json_schema", "json_schema": <json_schema>}`.

              Important: when using JSON mode, it's crucial to also instruct the model to
              produce JSON via a system or user message. Without this, the model may generate
              an unending stream of whitespace until the generation reaches the token limit,
              resulting in a long-running and seemingly "stuck" request.

              Also note that the message content may be partially cut off if
              `finish_reason="length"`, which indicates the generation exceeded `max_tokens`
              or the conversation exceeded the max context length. In this case the return
              value might not be a valid JSON.

          return_token_ids: Return token IDs alongside text to avoid retokenization drift.

          seed: Random seed for deterministic sampling.

          speculation: Speculative decoding prompt or token IDs to speed up generation.

          stop: Up to 4 sequences where the API will stop generating further tokens. The
              returned text will NOT contain the stop sequence.

          temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 will
              make the output more random, while lower values like 0.2 will make it more
              focused and deterministic.

              We generally recommend altering this or top_p but not both.

              Required range: `0 <= x <= 2`

              Example: `1`

          top_k: Top-k sampling is another sampling method where the k most probable next tokens
              are filtered and the probability mass is redistributed among only those k next
              tokens. The value of k controls the number of candidates for the next token at
              each step during text generation. Must be between 0 and 100.

              Required range: `0 <= x <= 100`

              Example: `50`

          top_logprobs: An integer between 0 and 5 specifying the number of most likely tokens to return
              at each token position, each with an associated log probability. The minimum
              value is 0 and the maximum value is 5.

              When `logprobs` is set, `top_logprobs` can be used to modify how many top log
              probabilities are returned. If `top_logprobs` is not set, the API will return up
              to `logprobs` tokens per position.

              Required range: `0 <= x <= 5`

          top_p: An alternative to sampling with temperature, called nucleus sampling, where the
              model considers the results of the tokens with top_p probability mass. So 0.1
              means only the tokens comprising the top 10% probability mass are considered.

              We generally recommend altering this or temperature but not both.

              Required range: `0 <= x <= 1`

              Example: `1`

          typical_p: Typical-p sampling is an alternative to nucleus sampling. It considers the most
              typical tokens whose cumulative probability is at most typical_p.

              Required range: `0 <= x <= 1`

          user: A unique identifier representing your end-user, which can help monitor and
              detect abuse.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["model", "prompt"], ["model", "prompt", "stream"])
    async def create(
        self,
        *,
        model: str,
        prompt: Union[str, SequenceNotStr[str], Iterable[int], Iterable[Iterable[int]]],
        context_length_exceeded_behavior: Literal["error", "truncate"] | Omit = omit,
        echo: Optional[bool] | Omit = omit,
        echo_last: Optional[int] | Omit = omit,
        frequency_penalty: Optional[float] | Omit = omit,
        ignore_eos: bool | Omit = omit,
        images: Union[SequenceNotStr[str], Iterable[SequenceNotStr[str]], None] | Omit = omit,
        logit_bias: Optional[Dict[str, float]] | Omit = omit,
        logprobs: Union[int, bool, None] | Omit = omit,
        max_completion_tokens: Optional[int] | Omit = omit,
        max_tokens: Optional[int] | Omit = omit,
        metadata: Optional[Dict[str, str]] | Omit = omit,
        min_p: Optional[float] | Omit = omit,
        mirostat_lr: Optional[float] | Omit = omit,
        mirostat_target: Optional[float] | Omit = omit,
        n: int | Omit = omit,
        perf_metrics_in_response: Optional[bool] | Omit = omit,
        prediction: Optional[completion_create_params.Prediction] | Omit = omit,
        presence_penalty: Optional[float] | Omit = omit,
        prompt_cache_isolation_key: Optional[str] | Omit = omit,
        raw_output: Optional[bool] | Omit = omit,
        reasoning_effort: Union[Literal["low", "medium", "high", "none"], int, bool, None] | Omit = omit,
        reasoning_history: Optional[Literal["disabled", "interleaved", "preserved"]] | Omit = omit,
        repetition_penalty: Optional[float] | Omit = omit,
        response_format: Optional[completion_create_params.ResponseFormat] | Omit = omit,
        return_token_ids: Optional[bool] | Omit = omit,
        seed: Optional[int] | Omit = omit,
        speculation: Union[str, Iterable[int], None] | Omit = omit,
        stop: Union[str, SequenceNotStr[str], None] | Omit = omit,
        stream: Optional[Literal[False]] | Literal[True] | Omit = omit,
        temperature: Optional[float] | Omit = omit,
        top_k: Optional[int] | Omit = omit,
        top_logprobs: Optional[int] | Omit = omit,
        top_p: Optional[float] | Omit = omit,
        typical_p: Optional[float] | Omit = omit,
        user: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CompletionCreateResponse | AsyncStream[CompletionChunk]:
        return await self._post(
            "/v1/completions"
            if self._client._base_url_overridden
            else "https://api.fireworks.ai/inference/v1/completions",
            body=await async_maybe_transform(
                {
                    "model": model,
                    "prompt": prompt,
                    "context_length_exceeded_behavior": context_length_exceeded_behavior,
                    "echo": echo,
                    "echo_last": echo_last,
                    "frequency_penalty": frequency_penalty,
                    "ignore_eos": ignore_eos,
                    "images": images,
                    "logit_bias": logit_bias,
                    "logprobs": logprobs,
                    "max_completion_tokens": max_completion_tokens,
                    "max_tokens": max_tokens,
                    "metadata": metadata,
                    "min_p": min_p,
                    "mirostat_lr": mirostat_lr,
                    "mirostat_target": mirostat_target,
                    "n": n,
                    "perf_metrics_in_response": perf_metrics_in_response,
                    "prediction": prediction,
                    "presence_penalty": presence_penalty,
                    "prompt_cache_isolation_key": prompt_cache_isolation_key,
                    "raw_output": raw_output,
                    "reasoning_effort": reasoning_effort,
                    "reasoning_history": reasoning_history,
                    "repetition_penalty": repetition_penalty,
                    "response_format": response_format,
                    "return_token_ids": return_token_ids,
                    "seed": seed,
                    "speculation": speculation,
                    "stop": stop,
                    "stream": stream,
                    "temperature": temperature,
                    "top_k": top_k,
                    "top_logprobs": top_logprobs,
                    "top_p": top_p,
                    "typical_p": typical_p,
                    "user": user,
                },
                completion_create_params.CompletionCreateParamsStreaming
                if stream
                else completion_create_params.CompletionCreateParamsNonStreaming,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CompletionCreateResponse,
            stream=stream or False,
            stream_cls=AsyncStream[CompletionChunk],
        )


class CompletionsResourceWithRawResponse:
    def __init__(self, completions: CompletionsResource) -> None:
        self._completions = completions

        self.create = to_raw_response_wrapper(
            completions.create,
        )


class AsyncCompletionsResourceWithRawResponse:
    def __init__(self, completions: AsyncCompletionsResource) -> None:
        self._completions = completions

        self.create = async_to_raw_response_wrapper(
            completions.create,
        )


class CompletionsResourceWithStreamingResponse:
    def __init__(self, completions: CompletionsResource) -> None:
        self._completions = completions

        self.create = to_streamed_response_wrapper(
            completions.create,
        )


class AsyncCompletionsResourceWithStreamingResponse:
    def __init__(self, completions: AsyncCompletionsResource) -> None:
        self._completions = completions

        self.create = async_to_streamed_response_wrapper(
            completions.create,
        )
