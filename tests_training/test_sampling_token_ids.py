"""Exact-token SSE contracts; constructed fixtures, not incident captures."""

from __future__ import annotations

import json
from typing import Any

import httpx
import pytest

from fireworks.training.sdk._sse import _SSEProtocolError
from fireworks.training.sdk.sampling import DeploymentSampler


def _wire(choices: list[dict[str, Any]], generated: int = 2) -> bytes:
    events = [{"choices": [choice]} for choice in choices]
    events.append({"choices": [{"finish_reason": "stop"}], "usage": {"completion_tokens": generated}})
    return b"".join(b"data: " + json.dumps(event).encode() + b"\n\n" for event in events) + b"data: [DONE]\n\n"


def _delta(tokens: list[int], text: str = "") -> dict[str, Any]:
    return {
        "text": text,
        "token_ids": tokens,
        "logprobs": {"content": [{"token_id": token, "logprob": -0.5, "sampling_logprob": -0.2} for token in tokens]},
    }


@pytest.mark.parametrize("echo_last", [None, 0, 2, 3])
@pytest.mark.parametrize("raw_output", [None, False])
async def test_token_deltas_preserve_echo_and_server_prompt(echo_last: int | None, raw_output: bool | None) -> None:
    # Server-expanded prompt IDs must win over the submitted IDs.
    prompt = [10, 11, 12]
    echoed = prompt[-echo_last:] if echo_last else []
    tokens = echoed + [20, 21]
    first = _delta(tokens[:-1], text="你好")
    first["prompt_token_ids"] = prompt
    last = _delta(tokens[-1:])  # A token with no display text must survive.
    requests = []

    async def handle(request: httpx.Request) -> httpx.Response:
        requests.append(json.loads(request.content))
        return httpx.Response(200, content=_wire([first, last]))

    sampler = DeploymentSampler("https://example.invalid", "model", "unused")
    async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as client:
        sampler._get_async_client = lambda: client
        kwargs: dict[str, Any] = {"logprobs": True}
        if raw_output is not None:
            kwargs["raw_output"] = raw_output
        if echo_last == 3:
            kwargs["echo"] = True
        elif echo_last is not None:
            kwargs.update(echo=True, echo_last=echo_last)
        try:
            result = await sampler.sample_with_prompt_tokens_result([1], **kwargs)
            completion = result.completions[0]
            assert completion.full_tokens == prompt + [20, 21]
            assert completion.prompt_len == 3
            assert completion.completion_len == 2
            expected_echo = 2 if echo_last == 3 else (echo_last or 0)
            assert completion.echoed_prompt_logprob_count == expected_echo
            assert completion.inference_logprobs == [-0.5] * (2 + expected_echo)
            assert completion.sampling_logprobs == [-0.2] * (2 + expected_echo)
            assert len(requests) == 1
            assert requests[0]["return_token_ids"] is True
            assert requests[0]["raw_output"] is False
        finally:
            sampler.close()


@pytest.mark.parametrize("width", [2, 128])
async def test_raw_off_stream_preserves_top_logprobs_and_sampling_controls(width: int) -> None:
    deltas = [_delta([20]), _delta([21])]
    deltas[0]["prompt_token_ids"] = [1]
    heads = [[{"token_id": token + i, "logprob": -0.5 - i} for i in range(width)] for token in (20, 21)]
    for delta, head in zip(deltas, heads):
        delta["logprobs"]["content"][0]["top_logprobs"] = head

    async def handle(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content)
        assert payload["raw_output"] is False
        assert payload["return_token_ids"] is True
        assert payload["top_k"] == 10
        assert payload["top_p"] == 0.9
        assert payload["temperature"] == 0.7
        assert payload["top_logprobs"] == width
        return httpx.Response(200, content=_wire(deltas))

    sampler = DeploymentSampler("https://example.invalid", "model", "unused")
    async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as client:
        sampler._get_async_client = lambda: client
        try:
            result = await sampler.sample_with_prompt_tokens_result(
                [1], logprobs=True, top_logprobs=width, top_k=10, top_p=0.9, temperature=0.7
            )
            completion = result.completions[0]
            assert completion.full_tokens == [1, 20, 21]
            assert completion.inference_logprobs == [-0.5, -0.5]
            assert completion.sampling_logprobs == [-0.2, -0.2]
            assert completion.inference_topk_token_ids == [[row["token_id"] for row in head] for head in heads]
            assert completion.inference_topk_logprobs == [[row["logprob"] for row in head] for head in heads]
        finally:
            sampler.close()


@pytest.mark.parametrize(
    "fault", ["missing_ids", "missing_prompt", "row_count", "row_id", "usage", "prompt_change", "index"]
)
async def test_incomplete_token_stream_fails_without_retry(fault: str) -> None:
    first = _delta([20])
    first["prompt_token_ids"] = [1]
    last = _delta([21], text="x")
    generated = 2
    if fault == "missing_ids":
        del first["token_ids"]
    elif fault == "missing_prompt":
        del first["prompt_token_ids"]
    elif fault == "row_count":
        first["logprobs"]["content"] = []
    elif fault == "row_id":
        first["logprobs"]["content"][0]["token_id"] = 99
    elif fault == "usage":
        generated = 3
    elif fault == "prompt_change":
        last["prompt_token_ids"] = [2]
    else:
        last["index"] = 1
    calls = 0

    async def handle(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(200, content=_wire([first, last], generated=generated))

    sampler = DeploymentSampler("https://example.invalid", "model", "unused")
    async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as client:
        sampler._get_async_client = lambda: client
        try:
            with pytest.raises(_SSEProtocolError):
                await sampler.sample_with_prompt_tokens_result([1], logprobs=True, raw_output=False)
            assert calls == 1
        finally:
            sampler.close()


async def test_explicit_raw_mode_is_rejected_before_request() -> None:
    calls = 0

    async def handle(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(500)

    sampler = DeploymentSampler("https://example.invalid", "model", "unused")
    async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as client:
        sampler._get_async_client = lambda: client
        try:
            with pytest.raises(ValueError, match="requires raw_output=False"):
                await sampler.sample_with_prompt_tokens_result([1], raw_output=True)
            assert calls == 0
        finally:
            sampler.close()


async def test_raw_snapshot_does_not_replace_missing_incremental_ids() -> None:
    choice = {"text": "hi", "raw_output": {"completion_token_ids": [20, 21]}}
    calls = 0

    async def handle(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        assert json.loads(request.content)["raw_output"] is False
        return httpx.Response(200, content=_wire([choice]))

    sampler = DeploymentSampler("https://example.invalid", "model", "unused")
    async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as client:
        sampler._get_async_client = lambda: client
        try:
            with pytest.raises(_SSEProtocolError, match="complete token IDs"):
                await sampler.sample_with_prompt_tokens_result([1])
            assert calls == 1
        finally:
            sampler.close()


@pytest.mark.parametrize(
    "options", [{}, {"images": ["synthetic"]}, {"include_routing_matrix": True}, {"sampling_mask": "parquet_v1"}]
)
async def test_default_paths_use_incremental_ids(options: dict[str, Any]) -> None:
    sampler = DeploymentSampler("https://example.invalid", "model", "unused")

    async def capture(**kwargs: Any) -> Any:
        assert kwargs["raw_output"] is False
        assert kwargs["return_token_ids"] is True
        raise ValueError("captured request")

    sampler.async_completions_stream = capture
    try:
        with pytest.raises(ValueError, match="captured request"):
            await sampler.sample_with_prompt_tokens_result([1], **options)
    finally:
        sampler.close()
