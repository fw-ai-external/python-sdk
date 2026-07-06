"""Deployment completions sampling with client-side tokenization (token-in, token-out)."""

from __future__ import annotations

import json
import time
import random
import asyncio
import logging
import warnings
from math import ceil
from typing import TYPE_CHECKING, Any, List
from dataclasses import dataclass

import httpx

if TYPE_CHECKING:
    from transformers import PreTrainedTokenizerBase

from fireworks.training.sdk._sse import _SSEDecoder, _SSETruncationError
from fireworks.training.sdk.errors import (
    DOCS_SDK,
    format_sdk_error,
    async_request_with_retries,
)
from fireworks.training.sdk.concurrency import FixedConcurrencyController, AdaptiveConcurrencyController
from fireworks.training.sdk._rest_client import _RestClient

logger = logging.getLogger(__name__)

# =============================================================================
# DeploymentSampler — completions API with client-side tokenization
# =============================================================================


@dataclass
class ServerMetrics:
    """Server-side metrics extracted from response headers.

    Available on dedicated deployments.  Fields are ``None`` when the
    header is absent (e.g. serverless deployments).
    """

    num_concurrent_requests: int | None = None
    prefill_queue_duration: float | None = None
    generation_queue_duration: float | None = None
    server_ttft: float | None = None
    cached_prompt_tokens: int | None = None
    prompt_tokens: int | None = None
    server_processing_time: float | None = None
    client_ttft: float | None = None
    """Client-measured time-to-first-token (seconds).  Only set for streaming."""

    @staticmethod
    def from_headers(headers: dict[str, str], client_ttft: float | None = None) -> "ServerMetrics":
        """Parse server metrics from HTTP response headers."""

        def _float(key: str) -> float | None:
            v = headers.get(key)
            if v is None:
                return None
            try:
                return float(v)
            except (ValueError, TypeError):
                return None

        def _int(key: str) -> int | None:
            v = headers.get(key)
            if v is None:
                return None
            try:
                return int(v)
            except (ValueError, TypeError):
                return None

        return ServerMetrics(
            num_concurrent_requests=_int("num-concurrent-requests"),
            prefill_queue_duration=_float("prefill-queue-duration"),
            generation_queue_duration=_float("generation-queue-duration"),
            server_ttft=_float("server-time-to-first-token"),
            cached_prompt_tokens=_int("cached-prompt-tokens"),
            prompt_tokens=_int("prompt-tokens"),
            server_processing_time=_float("server-processing-time"),
            client_ttft=client_ttft,
        )


@dataclass
class SampledCompletion:
    """A single sampled completion with tokenized representation.

    Contains the full token sequence (prompt + completion) needed for training,
    with prompt tokens from client-side tokenization and completion tokens from
    the deployment's ``raw_output`` response.
    """

    text: str
    full_tokens: List[int]  # prompt_token_ids + completion_token_ids
    prompt_len: int
    finish_reason: str = "unknown"
    completion_len: int = 0
    inference_logprobs: List[float] | None = None
    logprobs_echoed: bool = False
    """True when echo=True was used: inference_logprobs has P+C-1 entries
    (training-aligned).  False: completion-only."""
    routing_matrices: List[str] | None = None


class DeploymentSamplerTimeoutError(RuntimeError):
    """Raised when deployment sampling repeatedly times out against inference."""


class DeploymentSampler(_RestClient):
    """Wraps Fireworks deployment completions API with client-side tokenization.

    Uses a local HuggingFace tokenizer to apply chat templates and tokenize
    prompts, then sends token IDs to the ``/inference/v1/completions`` endpoint
    (token-in, token-out).  Completion token IDs come back via ``raw_output``.

    BOS and special tokens are handled by the tokenizer's chat template --
    no manual prepend is needed.

    Handles URL construction, auth headers, SSL verification, and basic
    retries -- so training scripts never do raw HTTP for sampling.

    Example::

        from transformers import AutoTokenizer

        tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-1.7B")
        sampler = DeploymentSampler(
            inference_url="https://api.fireworks.ai",
            model="accounts/your-account/deployments/my-deploy",
            api_key="...",
            tokenizer=tokenizer,
        )

        completions = await sampler.sample_with_tokens(messages=[...], n=4)
        for c in completions:
            print(c.text, len(c.full_tokens), c.finish_reason)
    """

    def __init__(
        self,
        inference_url: str,
        model: str,
        api_key: str,
        tokenizer: PreTrainedTokenizerBase | None = None,
        concurrency_controller: "AdaptiveConcurrencyController | FixedConcurrencyController | None" = None,
        max_concurrency: int | None = None,  # TODO: remove after deprecation period
    ):
        super().__init__(api_key=api_key, base_url=inference_url)
        self.model = model
        self.tokenizer = tokenizer
        self._recent_metrics: list[ServerMetrics] = []

        if max_concurrency is not None:
            warnings.warn(
                "max_concurrency is deprecated and will be removed in a future release. "
                "Use concurrency_controller=FixedConcurrencyController(max_concurrency) "
                "or AdaptiveConcurrencyController() instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            if concurrency_controller is None:
                concurrency_controller = FixedConcurrencyController(max_concurrency)

        self._concurrency_controller = concurrency_controller

    def _inference_headers(self) -> dict[str, str]:
        """Headers for inference completions requests."""
        return self._headers(Authorization=f"Bearer {self.api_key}")

    _HOTLOAD_RETRY_INTERVAL_S = 5.0
    _HOTLOAD_MAX_RETRIES = 10

    async def async_completions_stream(
        self,
        prompt: list[int],
        max_tokens: int = 1024,
        temperature: float = 1.0,
        hotload_retry_interval: float = _HOTLOAD_RETRY_INTERVAL_S,
        hotload_max_retries: int = _HOTLOAD_MAX_RETRIES,
        **kwargs: Any,
    ) -> tuple[dict[str, Any], ServerMetrics]:
        """Streaming n=1 async completions request.

        Opens an SSE stream, accumulates chunks into the same response
        format that ``async_completions`` returns, and extracts
        ``ServerMetrics`` from both:

        * **HTTP response headers** -- available immediately (partial:
          ``prompt-tokens``, ``cached-prompt-tokens``, ``server-time-to-first-token``).
        * **``perf_metrics`` in the final SSE chunk** -- available after
          completion (full timing: ``prefill-queue-duration``,
          ``generation-queue-duration``, ``num-concurrent-requests``, etc.).

        The request automatically sets ``perf_metrics_in_response=True``
        so the server includes complete metrics in the last chunk.
        """
        http_timeout = kwargs.pop("http_timeout", 600)
        if kwargs.get("images"):
            kwargs.setdefault("return_token_ids", True)
        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "n": 1,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True,
            "perf_metrics_in_response": True,
            **kwargs,
        }
        # Default to full-distribution sampling for on-policy RL rollouts.
        # Without this the serving stack falls back to the model's
        # generation_config.json sampling defaults (e.g. Qwen3.5 ships
        # top_k=20/top_p=0.95), which silently truncate rollouts and bias the
        # policy-gradient estimator. Explicit caller kwargs still win.
        payload.setdefault("top_p", 1.0)
        payload.setdefault("top_k", 0)
        url = f"{self.base_url}/inference/v1/completions"
        headers = self._inference_headers()
        client = self._get_async_client()
        prompt_len = len(prompt)

        for hotload_attempt in range(hotload_max_retries + 1):
            t0 = time.time()
            resp = await async_request_with_retries(
                client.post,
                url,
                headers=headers,
                json=payload,
                timeout=http_timeout,
            )

            if resp.status_code in (404, 425) and hotload_attempt < hotload_max_retries:
                logger.info(
                    "Deployment not ready (HTTP %d), retry %d/%d in %ds...",
                    resp.status_code,
                    hotload_attempt + 1,
                    hotload_max_retries,
                    int(hotload_retry_interval),
                )
                await asyncio.sleep(hotload_retry_interval)
                continue

            resp.raise_for_status()

            accumulated_text = ""
            accumulated_logprobs: list[dict] = []
            finish_reason = None
            usage_info = None
            raw_output = None
            perf_metrics_dict: dict[str, str] | None = None
            first_token_time: float | None = None

            # Track whether the stream ended cleanly. A well-formed completion
            # must close with [DONE] and/or set finish_reason. A clean TCP close
            # without either signals server-side mid-stream truncation.
            has_seen_done = False
            has_seen_finish_reason = False

            decoder = _SSEDecoder()
            async for sse in decoder.aiter_events(resp):
                if sse.data.startswith("[DONE]"):
                    has_seen_done = True
                    break

                try:
                    chunk = json.loads(sse.data)
                except (ValueError, TypeError):
                    continue

                for choice in chunk.get("choices", []):
                    text_delta = choice.get("text", "")
                    if text_delta:
                        if first_token_time is None:
                            first_token_time = time.time()
                        accumulated_text += text_delta

                    lp = choice.get("logprobs")
                    if lp and isinstance(lp, dict):
                        content = lp.get("content")
                        if isinstance(content, list):
                            accumulated_logprobs.extend(content)

                    fr = choice.get("finish_reason")
                    if fr:
                        finish_reason = fr
                        has_seen_finish_reason = True

                    ro = choice.get("raw_output")
                    if ro:
                        raw_output = ro

                if "usage" in chunk:
                    usage_info = chunk["usage"]

                # perf_metrics is patched into the final chunk by the server
                # (with is_completed=True, so it has full timing data).
                if "perf_metrics" in chunk:
                    perf_metrics_dict = chunk["perf_metrics"]

            if not raw_output and not has_seen_done and not has_seen_finish_reason:
                raise _SSETruncationError(
                    "Transient server-side error: the inference deployment "
                    "closed the SSE stream mid-generation without sending "
                    "[DONE], finish_reason, or raw_output. The SDK is "
                    "retrying. If this persists across all retry attempts, "
                    "contact the Fireworks team."
                )

            client_ttft = (first_token_time - t0) if first_token_time else None

            # Build ServerMetrics: prefer perf_metrics from final chunk
            # (has complete timing), fall back to HTTP headers (partial).
            metrics_source = perf_metrics_dict or dict(resp.headers)
            server_metrics = ServerMetrics.from_headers(metrics_source, client_ttft=client_ttft)

            assembled_choice: dict[str, Any] = {
                "text": accumulated_text,
                "finish_reason": finish_reason or "stop",
            }
            if accumulated_logprobs:
                assembled_choice["logprobs"] = {"content": accumulated_logprobs}
            if raw_output:
                assembled_choice["raw_output"] = raw_output
            result: dict[str, Any] = {"choices": [assembled_choice]}
            if usage_info:
                result["usage"] = usage_info

            elapsed = time.time() - t0
            logger.debug(
                "Stream completions: prompt=%d, text_len=%d, %.1fs",
                prompt_len,
                len(accumulated_text),
                elapsed,
            )
            return result, server_metrics

        raise RuntimeError("Exhausted hotload retries in streaming mode")

    @staticmethod
    def _extract_logprobs(choice: dict[str, Any]) -> List[float] | None:
        """Extract per-token logprobs from a completions response.

        Expects modern structured logprobs format:
        ``choice.logprobs.content[].logprob``.

        Returns:
            List of per-token logprobs, or ``None`` if absent/empty.
        """
        lp_data = choice.get("logprobs")
        if not lp_data or not isinstance(lp_data, dict):
            return None
        content = lp_data.get("content")
        if isinstance(content, list) and content:
            return [tok.get("logprob", 0.0) for tok in content]
        return None

    @staticmethod
    def _extract_routing_matrices(choice: dict[str, Any]) -> List[str] | None:
        """Extract per-token routing matrices from logprobs content.

        When ``include_routing_matrix=True`` is passed to the API, each token
        in ``choice.logprobs.content`` may contain a ``routing_matrix`` field
        with a base64-encoded expert-index array for Router Replay (R3).

        Returns:
            List of base64-encoded routing matrix strings (one per completion
            token), or ``None`` if no routing matrices are present.
        """
        lp_data = choice.get("logprobs")
        if lp_data and isinstance(lp_data, dict):
            content = lp_data.get("content", [])
            if content:
                matrices = [tok.get("routing_matrix", "") for tok in content]
                if any(m for m in matrices):
                    return matrices
        return None

    async def sample_with_tokens(
        self,
        messages: list[dict[str, str]],
        n: int = 1,
        max_tokens: int = 1024,
        temperature: float = 1.0,
        max_seq_len: int | None = None,
        **kwargs: Any,
    ) -> List[SampledCompletion]:
        """Sample n completions via streaming, firing n individual requests concurrently.

        Each completion is an independent async streaming request.
        Server metrics from response headers are fed into the
        ``AdaptiveConcurrencyController`` (if one was provided).
        """
        if self.tokenizer is None:
            raise ValueError("Tokenizer is required for sample_with_tokens")
        user_requested_logprobs = kwargs.get("logprobs", False)
        routing_requested = kwargs.get("include_routing_matrix", False)
        echo_mode = kwargs.get("echo", False)

        prompt_ids: list[int] = self.tokenizer.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_dict=False,
        )

        if max_seq_len is not None and len(prompt_ids) >= max_seq_len:
            return []

        async def _one(idx: int) -> List[SampledCompletion]:
            return await self._do_one_completion(
                prompt_ids,
                max_tokens,
                temperature,
                max_seq_len,
                user_requested_logprobs,
                routing_requested,
                echo_mode,
                **kwargs,
            )

        results = await asyncio.gather(*[_one(i) for i in range(n)])
        return [c for batch in results for c in batch]

    async def sample_with_prompt_tokens(
        self,
        prompt_token_ids: list[int],
        n: int = 1,
        max_tokens: int = 1024,
        temperature: float = 1.0,
        max_seq_len: int | None = None,
        stop: list[str] | list[int] | None = None,
        **kwargs: Any,
    ) -> List[SampledCompletion]:
        """Sample n completions from a pre-tokenized prompt.

        Unlike :meth:`sample_with_tokens`, this primitive accepts ``prompt_token_ids``
        directly and never invokes ``tokenizer.apply_chat_template(...)``. It is the
        sampler entry point for renderer-backed RL rollouts where the prompt has
        already been built from a token-native renderer.

        Concurrency control, ``raw_output`` echo semantics, ``max_seq_len`` filtering,
        and logprob extraction are inherited from :meth:`_do_one_completion` and
        :meth:`_parse_completions_result`.

        Pass ``images`` (base64 data URLs) for vision models with an unexpanded
        token prompt (one ``<|image_pad|>`` token per image). The server expands
        image pads; ``return_token_ids`` is set automatically so
        :class:`SampledCompletion` uses the expanded ``prompt_token_ids``.

        ``list[str]`` stops are forwarded as string stop sequences. ``list[int]``
        stops are decoded with the sampler tokenizer before forwarding because
        the completions API only accepts string stop sequences.
        """
        if max_seq_len is not None and len(prompt_token_ids) >= max_seq_len:
            return []

        user_requested_logprobs = kwargs.get("logprobs", False)
        routing_requested = kwargs.get("include_routing_matrix", False)
        echo_mode = kwargs.get("echo", False)
        if stop is not None:
            if all(type(s) is str for s in stop):
                kwargs["stop"] = stop
            elif all(type(s) is int for s in stop):
                if self.tokenizer is None:
                    raise ValueError(
                        "Tokenizer is required to convert integer stop token IDs "
                        "to string stop sequences for the completions API"
                    )
                kwargs["stop"] = [self.tokenizer.decode([token_id], skip_special_tokens=False) for token_id in stop]
            else:
                raise ValueError("stop must be list[str] or list[int]")

        async def _one(_idx: int) -> List[SampledCompletion]:
            return await self._do_one_completion(
                prompt_token_ids,
                max_tokens,
                temperature,
                max_seq_len,
                user_requested_logprobs,
                routing_requested,
                echo_mode,
                **kwargs,
            )

        results = await asyncio.gather(*[_one(i) for i in range(n)])
        return [c for batch in results for c in batch]

    async def _acquire_concurrency(self) -> None:
        """Acquire a concurrency slot from the controller."""
        if self._concurrency_controller is not None:
            await self._concurrency_controller.acquire()

    def _release_concurrency(self, server_metrics: ServerMetrics | None = None) -> None:
        """Release a concurrency slot, feeding metrics to the controller."""
        if server_metrics is not None:
            self._recent_metrics.append(server_metrics)
        if self._concurrency_controller is not None:
            self._concurrency_controller.release(server_metrics)

    def drain_metrics(self) -> list[ServerMetrics]:
        """Return and clear all collected ServerMetrics since last drain."""
        out = list(self._recent_metrics)
        self._recent_metrics.clear()
        return out

    # Per-completion retry covers two transient server-side classes:
    # 1. SSE truncation: the deployment closes the stream mid-generation
    #    without [DONE]/finish_reason/raw_output. Surfaces as a RuntimeError
    #    raised from async_completions_stream.
    # 2. Transient HTTP / connection errors right after a fresh deployment
    #    or hotload: 408/429/502/503/504 plus httpx connection-level errors.
    # Backoff is exponential with jitter to avoid retry-storm
    # synchronization across concurrent in-flight completions.
    _RETRY_MAX_ATTEMPTS = 7
    _RETRY_BASE_BACKOFF_S = 2.0
    _RETRY_MAX_BACKOFF_S = 30.0
    _RETRY_HTTP_TRANSIENT_CODES = (408, 429, 502, 503, 504)
    _RETRY_HTTPX_CONNECTION_EXC = (
        httpx.RemoteProtocolError,
        httpx.ReadError,
        httpx.ReadTimeout,
        httpx.ConnectError,
        httpx.ConnectTimeout,
        httpx.WriteError,
        httpx.WriteTimeout,
        httpx.PoolTimeout,
    )

    _RETRY_TIMEOUT_STATUS_CODES = (408, 504)
    _RL_TIMEOUT_WORKLOADS = ("async_rl_rollout", "rl_rollout")

    async def _backoff_after_transient(
        self,
        label: str,
        attempt: int,
        current_backoff: float,
        diagnostic: str | None = None,
    ) -> float:
        """Sleep with jittered exponential backoff and return the next backoff.

        Caller is responsible for the retryability decision; this helper
        just emits the per-attempt log line and sleeps.
        """
        jittered = current_backoff * (0.5 + random.random())
        if diagnostic:
            logger.warning(
                "%s Transient %s (attempt %d/%d); retrying after %.1fs.",
                diagnostic,
                label,
                attempt,
                self._RETRY_MAX_ATTEMPTS,
                jittered,
            )
        else:
            logger.warning(
                "Transient %s (attempt %d/%d); retrying after %.1fs.",
                label,
                attempt,
                self._RETRY_MAX_ATTEMPTS,
                jittered,
            )
        await asyncio.sleep(jittered)
        return min(current_backoff * 2, self._RETRY_MAX_BACKOFF_S)

    def _is_timeout_like_transient(self, transient: BaseException) -> bool:
        if isinstance(transient, httpx.TimeoutException):
            return True
        if isinstance(transient, httpx.HTTPStatusError):
            return transient.response.status_code in self._RETRY_TIMEOUT_STATUS_CODES
        return False

    @staticmethod
    def _p95(values: list[float]) -> float | None:
        if not values:
            return None
        ordered = sorted(values)
        index = min(len(ordered) - 1, ceil(0.95 * len(ordered)) - 1)
        return ordered[index]

    @staticmethod
    def _format_seconds(value: float | None) -> str | None:
        if value is None:
            return None
        return f"{value:.1f}s"

    def _recent_metrics_diagnostic(self) -> list[str]:
        recent = self._recent_metrics[-32:]
        if not recent:
            return []

        fields: list[str] = []
        prefill_p95 = self._p95([m.prefill_queue_duration for m in recent if m.prefill_queue_duration is not None])
        generation_p95 = self._p95(
            [m.generation_queue_duration for m in recent if m.generation_queue_duration is not None]
        )
        ttft_p95 = self._p95([m.client_ttft for m in recent if m.client_ttft is not None])
        concurrent = [m.num_concurrent_requests for m in recent if m.num_concurrent_requests is not None]

        for name, value in (
            ("recent_prefill_queue_p95", prefill_p95),
            ("recent_generation_queue_p95", generation_p95),
            ("recent_client_ttft_p95", ttft_p95),
        ):
            formatted = self._format_seconds(value)
            if formatted:
                fields.append(f"{name}={formatted}")
        if concurrent:
            fields.append(f"recent_concurrent_requests_max={max(concurrent)}")
        return fields

    @staticmethod
    def _format_timeout_diagnostic_context(context: Any) -> list[str]:
        if not isinstance(context, dict):
            return []
        fields: list[str] = []
        for key in sorted(context):
            value = context[key]
            if value is None:
                continue
            fields.append(f"{key}={value}")
        return fields

    def _timeout_diagnostic(
        self,
        label: str,
        prompt_ids: list[int],
        max_tokens: int,
        kwargs: dict[str, Any],
        diagnostic_context: Any,
        *,
        exhausted: bool,
    ) -> str:
        http_timeout = kwargs.get("http_timeout", 600)
        is_rl_rollout = (
            isinstance(diagnostic_context, dict) and diagnostic_context.get("workload") in self._RL_TIMEOUT_WORKLOADS
        )
        if exhausted:
            summary = "DeploymentSampler request failed after exhausting retries on a timeout-like error."
        else:
            summary = "DeploymentSampler request hit a timeout-like transient."
        fields = [
            summary,
            f"raw_error={label}",
            f"model={self.model}",
            f"prompt_tokens={len(prompt_ids)}",
            f"max_tokens={max_tokens}",
            f"http_timeout={http_timeout}s",
        ]
        if not exhausted:
            if is_rl_rollout and isinstance(diagnostic_context, dict):
                max_concurrency = diagnostic_context.get("max_concurrency_rollout_sample")
                if max_concurrency is not None:
                    fields.append(f"max_concurrency_rollout_sample={max_concurrency}")
                fields.append(
                    "If this repeats and serving queue/TTFT metrics are high, "
                    "reduce rollout concurrency/completion tokens or increase sampler capacity."
                )
            return " ".join(fields)

        if is_rl_rollout:
            fields.append(
                "RL rollout context detected. If recent queue/TTFT metrics "
                "are high, rollout sampling may be exceeding sampler capacity."
            )

        window_size = getattr(self._concurrency_controller, "window_size", None)
        if window_size is not None:
            fields.append(f"sampler_concurrency_window={window_size}")
        fields.extend(self._format_timeout_diagnostic_context(diagnostic_context))
        fields.extend(self._recent_metrics_diagnostic())
        if is_rl_rollout:
            fields.append(
                "Check recent queue/TTFT metrics. If they are elevated, reduce "
                "rollout concurrency and/or max_completion_tokens, "
                "or increase sampler capacity; otherwise investigate gateway, "
                "network, or client timeout limits."
            )
        else:
            fields.append(
                "Check serving queue/TTFT metrics, gateway timeout limits, "
                "network stability, and request shape before changing capacity."
            )
        return " ".join(fields)

    async def _do_one_completion(
        self,
        prompt_ids: list[int],
        max_tokens: int,
        temperature: float,
        max_seq_len: int | None,
        user_requested_logprobs: bool,
        routing_requested: bool,
        echo_mode: bool,
        **kwargs: Any,
    ) -> List[SampledCompletion]:
        backoff = self._RETRY_BASE_BACKOFF_S
        diagnostic_context = kwargs.pop("timeout_diagnostic_context", None)
        for attempt in range(1, self._RETRY_MAX_ATTEMPTS + 1):
            await self._acquire_concurrency()
            server_metrics: ServerMetrics | None = None
            transient: BaseException | None = None
            label = ""
            try:
                result, server_metrics = await self.async_completions_stream(
                    prompt=prompt_ids,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    raw_output=True,
                    **kwargs,
                )
            except _SSETruncationError as e:
                transient, label = e, "SSE truncation"
            except httpx.HTTPStatusError as e:
                if e.response.status_code not in self._RETRY_HTTP_TRANSIENT_CODES:
                    self._release_concurrency(server_metrics)
                    raise
                transient, label = e, f"HTTP {e.response.status_code}"
            except self._RETRY_HTTPX_CONNECTION_EXC as e:
                transient, label = e, type(e).__name__

            self._release_concurrency(server_metrics)

            if transient is None:
                return self._parse_completions_result(
                    result,
                    prompt_ids,
                    max_seq_len,
                    user_requested_logprobs,
                    routing_requested,
                    echo_mode,
                )
            if attempt == self._RETRY_MAX_ATTEMPTS:
                if self._is_timeout_like_transient(transient):
                    raise DeploymentSamplerTimeoutError(
                        self._timeout_diagnostic(
                            label,
                            prompt_ids,
                            max_tokens,
                            kwargs,
                            diagnostic_context,
                            exhausted=True,
                        )
                    ) from transient
                raise transient
            diagnostic = (
                self._timeout_diagnostic(
                    label,
                    prompt_ids,
                    max_tokens,
                    kwargs,
                    diagnostic_context,
                    exhausted=False,
                )
                if self._is_timeout_like_transient(transient)
                else None
            )
            backoff = await self._backoff_after_transient(label, attempt, backoff, diagnostic=diagnostic)

        # Range above guarantees the last attempt either returns or re-raises.
        # This line is here only to satisfy the type checker's flow analysis.
        raise AssertionError("unreachable: retry loop exited without return/raise")

    def _parse_completions_result(
        self,
        result: dict[str, Any],
        prompt_ids: list[int],
        max_seq_len: int | None,
        user_requested_logprobs: bool,
        routing_requested: bool,
        echo_mode: bool,
    ) -> List[SampledCompletion]:
        """Parse a completions API response into SampledCompletion objects."""
        completions: List[SampledCompletion] = []
        for choice in result.get("choices", []):
            text = choice.get("text", "")
            finish_reason = choice.get("finish_reason", "unknown")
            raw = choice.get("raw_output") or {}
            completion_ids = raw.get("completion_token_ids")

            if completion_ids is None:
                raise RuntimeError(
                    format_sdk_error(
                        "Deployment did not return raw_output token IDs",
                        f"The API response is missing completion_token_ids. Got choice keys: {list(choice.keys())}",
                        "The sampler requested raw_output=True, which is required for token-in RL rollouts. "
                        "Use a deployment path that returns raw_output.completion_token_ids for completions.",
                        docs_url=DOCS_SDK,
                        show_support=True,
                    )
                )

            token_logprobs = self._extract_logprobs(choice) if user_requested_logprobs else None
            routing_matrices = self._extract_routing_matrices(choice) if routing_requested else None

            expanded_prompt_ids = choice.get("prompt_token_ids") or raw.get("prompt_token_ids")
            if expanded_prompt_ids is not None:
                prompt_for_full = [int(x) for x in expanded_prompt_ids]
            else:
                prompt_for_full = list(prompt_ids)

            # With echo=True the API returns P+C tokens in
            # completion_token_ids and logprobs cover all P+C positions.
            # Strip the prompt prefix (verified by actual content match)
            # and drop the unconditional first-token logprob to get
            # P+C-1 training-aligned entries.
            lp_is_echo = False
            if echo_mode:
                if (
                    len(completion_ids) < len(prompt_for_full)
                    or completion_ids[: len(prompt_for_full)] != prompt_for_full
                ):
                    raise RuntimeError(
                        format_sdk_error(
                            "Echo response format mismatch",
                            "echo=True was requested but completion_token_ids do not include the prompt prefix.",
                            "The sampler uses echo=True to align prompt and completion token logprobs. "
                            "Use a deployment path whose raw_output token IDs include the prompt prefix when echo is enabled.",
                            docs_url=DOCS_SDK,
                            show_support=True,
                        )
                    )

                completion_ids = completion_ids[len(prompt_for_full) :]
                if token_logprobs is not None:
                    token_logprobs = token_logprobs[1:]
                    lp_is_echo = True
                if routing_matrices is not None:
                    routing_matrices = routing_matrices[1:]

            full_tokens = prompt_for_full + list(completion_ids)
            if max_seq_len is not None and len(full_tokens) > max_seq_len:
                logger.debug(
                    "Completion post-filtered: %d tokens > max_seq_len %d",
                    len(full_tokens),
                    max_seq_len,
                )
                continue

            completions.append(
                SampledCompletion(
                    text=text,
                    full_tokens=full_tokens,
                    prompt_len=len(prompt_for_full),
                    finish_reason=finish_reason,
                    completion_len=len(completion_ids),
                    inference_logprobs=token_logprobs,
                    logprobs_echoed=lp_is_echo,
                    routing_matrices=routing_matrices,
                )
            )

        return completions
