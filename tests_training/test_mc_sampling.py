"""MC sampling payload contracts, including echo and malformed responses."""

import json

import httpx
import pytest

from fireworks.training.sdk.sampling import DeploymentSampler


def _payload(echo):
    rows = [
        {
            "logprob": -0.2,
            "sampling_logprob": -0.2,
            "extra_tokens": [7, 7, 9],
            "extra_logprobs": [-100.0] * 3,
            "extra_sampling_logprobs": [-0.3, -0.3, -1.2],
        }
        for _ in range(2)
    ]
    if echo:
        rows = [{"logprob": -0.1, "sampling_logprob": None} for _ in range(3)] + rows
    return {
        "choices": [
            {
                "text": "ok",
                "finish_reason": "length",
                "token_ids": ([1, 2, 3] if echo else []) + [4, 5],
                "prompt_token_ids": [1, 2, 3],
                "logprobs": {"content": rows},
            }
        ]
    }


def _parse(payload, echo=False, parquet=False):
    sampler = DeploymentSampler(inference_url="https://api.example.com", model="m", api_key="test", tokenizer=None)
    try:
        return sampler._parse_completions_result(
            payload, [1, 2, 3], None, True, False, echo, False, sample_extra_requested=parquet
        )[0]
    finally:
        sampler.close()


@pytest.mark.parametrize("echo", [False, True])
def test_plain_inline_response_keeps_main_behavior(echo):
    assert _parse(_payload(echo), echo).sample_extra_references is None
    with pytest.raises(ValueError, match="sample_extra references"):
        _parse(_payload(echo), echo, parquet=True)


def test_plain_response_without_extra_logprobs_remains_compatible():
    payload = _payload(False)
    for row in payload["choices"][0]["logprobs"]["content"]:
        row.pop("extra_sampling_logprobs")
    assert _parse(payload).sample_extra_references is None


@pytest.mark.parametrize("echo", [False, True])
def test_parquet_mc_returns_references_instead_of_inline_rows(echo):
    payload = _payload(echo)
    length = len(payload["choices"][0]["token_ids"])
    file = {"store_id": "store", "file_id": "f", "format": "parquet_v1", "expires_at": 2, "row_count": length}
    references = {
        "length": length,
        "files": [file],
        "spans": [{"input_token_start": 0, "count": length, "file_index": 0, "file_row_start": 0}],
    }
    for row in payload["choices"][0]["logprobs"]["content"]:
        for key in ("extra_tokens", "extra_logprobs", "extra_sampling_logprobs"):
            row.pop(key, None)
    payload["choices"][0].update(
        sample_extra_format="parquet_v1", sample_extra_references=references, r3_store_id="store"
    )
    sampler = DeploymentSampler(inference_url="https://api.example.com", model="m", api_key="test", tokenizer=None)
    sampler.r3_store_id = "store"
    try:
        (completion,) = sampler._parse_completions_result(
            payload, [1, 2, 3], None, True, False, echo, False, sample_extra_requested=True
        )
        assert len(completion.sample_extra_references) == 2
        payload["choices"][0].pop("sample_extra_references")
        with pytest.raises(ValueError, match="sample_extra references"):
            sampler._parse_completions_result(payload, [1, 2, 3], None, True, False, echo, False, sample_extra_requested=True)
    finally:
        sampler.close()
    assert DeploymentSampler._parquet_capture_requested({"sample_extra_format": "parquet_v1"})


@pytest.mark.parametrize("count_key", ["top_sampling_logprobs", "sample_extra_tokens"])
def test_only_explicit_parquet_requires_shared_storage(count_key):
    sampler = DeploymentSampler(inference_url="https://api.example.com", model="m", api_key="test", tokenizer=None)
    try:
        assert not sampler._parquet_capture_requested({count_key: 8})
        format_key = "top_sampling_format" if count_key == "top_sampling_logprobs" else "sample_extra_format"
        assert sampler._parquet_capture_requested({count_key: 8, format_key: "parquet_v1"})
        assert not sampler._parquet_capture_requested({count_key: 0})
        with pytest.raises(ValueError, match=rf"^{format_key}='parquet_v1' writes to trainer shared storage.*training_client="):
            sampler._validate_parquet_capture_request({count_key: 8, format_key: "parquet_v1", "logprobs": True})
    finally:
        sampler.close()


_CAPTURE_CHANNELS = (
    ("top_sampling_logprobs", "top_sampling_format", "top_sampling"),
    ("sample_extra_tokens", "sample_extra_format", "sample_extra"),
)


@pytest.mark.parametrize("count_key,format_key,column", _CAPTURE_CHANNELS)
async def test_explicit_parquet_capture_at_http_boundary(count_key, format_key, column):
    sampler = DeploymentSampler("https://api.example.com", "m", "test")
    sampler.r3_store_id = "store"
    calls = []
    payload = _payload(False)
    choice = payload["choices"][0]
    choice.update(
        r3_store_id="store",
        **{
            f"{column}_format": "parquet_v1",
            f"{column}_references": {
                "length": 2,
                "files": [
                    {"store_id": "store", "file_id": "f", "format": "parquet_v1", "expires_at": 2, "row_count": 2}
                ],
                "spans": [{"input_token_start": 0, "count": 2, "file_index": 0, "file_row_start": 0}],
            },
        },
    )
    for row in choice["logprobs"]["content"]:
        for key in ("extra_tokens", "extra_logprobs", "extra_sampling_logprobs"):
            row.pop(key)

    async def post(body, headers, timeout):
        calls.append((body.copy(), headers.copy()))
        return httpx.Response(
            200,
            content=f"data: {json.dumps(payload)}\n\ndata: [DONE]\n\n".encode(),
            request=httpx.Request("POST", "https://api.example.com/inference/v1/completions"),
        )

    sampler._post_completion = post
    try:
        result = await sampler.sample_with_prompt_tokens_result(
            [1, 2, 3], logprobs=True, r3_ttl_seconds=60, **{count_key: 3, format_key: "parquet_v1"}
        )
        assert len(getattr(result.completions[0], f"{column}_references")) == 2
        assert len(calls) == 1
        body, headers = calls[0]
        assert body[format_key] == "parquet_v1"
        assert body[count_key] == 3
        assert headers["x-fireworks-r3-store-id"] == "store"
        assert headers["x-fireworks-r3-ttl-seconds"] == "60"
        assert "include_routing_matrix" not in body
    finally:
        sampler.close()


@pytest.mark.parametrize("count_key,format_key,column", _CAPTURE_CHANNELS)
async def test_explicit_parquet_requires_binding_before_http(count_key, format_key, column):
    sampler = DeploymentSampler("https://api.example.com", "m", "test")
    calls = []

    async def post(*args):
        calls.append(args)
        raise AssertionError("unsupported capture must be rejected before HTTP")

    sampler._post_completion = post
    kwargs = {count_key: 3, format_key: "parquet_v1"}
    try:
        with pytest.raises(ValueError, match="writes to trainer shared storage"):
            await sampler.sample_with_prompt_tokens_result([1, 2, 3], logprobs=True, **kwargs)
        assert not calls
    finally:
        sampler.close()


@pytest.mark.parametrize("count_key,format_key,column", _CAPTURE_CHANNELS)
async def test_plain_count_does_not_select_parquet_or_require_binding(count_key, format_key, column):
    sampler = DeploymentSampler("https://api.example.com", "m", "test")
    calls = []

    async def post(body, headers, timeout):
        calls.append((body.copy(), headers.copy()))
        return httpx.Response(
            200,
            content=f"data: {json.dumps(_payload(False))}\n\ndata: [DONE]\n\n".encode(),
            request=httpx.Request("POST", "https://api.example.com/inference/v1/completions"),
        )

    sampler._post_completion = post
    try:
        result = await sampler.sample_with_prompt_tokens_result([1, 2, 3], logprobs=True, **{count_key: 3})
        assert getattr(result.completions[0], f"{column}_references") is None
        body, headers = calls[0]
        assert body[count_key] == 3
        assert format_key not in body
        assert "x-fireworks-r3-store-id" not in headers
    finally:
        sampler.close()


@pytest.mark.parametrize(
    "sampling,message",
    [
        ({"top_sampling_format": "parquet_v1", "top_sampling_logprobs": 4}, "mutually exclusive"),
        ({"logprobs": None}, "sample_extra_tokens requires logprobs=True; got logprobs=None"),
        ({"temperature": 0.0}, "temperature=0.0 makes decoding greedy"),
        ({"top_k": 1}, "top_k=1 makes decoding greedy"),
        ({"top_p": 0.0}, "top_p=0.0 makes decoding greedy"),
        ({"min_p": 1.0}, "min_p=1.0 makes decoding greedy"),
    ],
)
async def test_mc_capture_rejects_conflicting_sampling_before_http(sampling, message):
    sampler = DeploymentSampler("https://api.example.com", "m", "test")
    calls = []

    async def post(*args):
        calls.append(args)
        raise AssertionError("conflicting MC capture must be rejected before HTTP")

    sampler._post_completion = post
    kwargs = {"logprobs": True, "sample_extra_tokens": 4, "sample_extra_format": "parquet_v1", **sampling}
    try:
        with pytest.raises(ValueError, match=message):
            await sampler.sample_with_prompt_tokens_result([1, 2, 3], **kwargs)
        assert not calls
    finally:
        sampler.close()


@pytest.mark.parametrize("count_key,format_key,column", _CAPTURE_CHANNELS)
@pytest.mark.parametrize("reply", ["compatible", "missing", "empty", "different_store"])
async def test_rollout_validates_requested_references_in_trainers_store(count_key, format_key, column, reply):
    from contextlib import nullcontext

    sampler = DeploymentSampler("https://api.example.com", "m", "test")
    sampler.r3_store_id = "store"
    payload = _payload(False)
    choice = payload["choices"][0]
    choice["token_ids"] = [4]
    choice["logprobs"]["content"] = [{"logprob": -0.2, "sampling_logprob": -0.2}]
    store = "other" if reply == "different_store" else "store"
    file = {"store_id": store, "file_id": "f", "format": "parquet_v1", "expires_at": 2, "row_count": 1}
    refs = {
        "length": 1,
        "files": [file],
        "spans": [{"input_token_start": 0, "count": 1, "file_index": 0, "file_row_start": 0}],
    }
    choice.update(r3_store_id=store, sampling_mask_format="parquet_v1", sampling_mask_references=refs)
    if reply != "missing":
        choice[format_key] = "parquet_v1"
        choice[f"{column}_references"] = (
            {"length": 1, "files": [], "spans": [{"input_token_start": 0, "count": 1}]} if reply == "empty" else refs
        )

    async def post(body, headers, timeout):
        assert body["prompt"] == [1, 2, 3] and body["max_tokens"] == 100 and body["top_k"] == 8
        assert body[count_key] == 4 and body[format_key] == "parquet_v1"
        assert headers["x-fireworks-r3-store-id"] == "store" and "x-fireworks-r3-ttl-seconds" not in headers
        return httpx.Response(
            200,
            content=f"data: {json.dumps(payload)}\n\ndata: [DONE]\n\n".encode(),
            request=httpx.Request("POST", "https://api.example.com/inference/v1/completions"),
        )

    sampler._post_completion = post
    messages = {"missing": "did not return", "empty": "without stored rows", "different_store": "shared storage domain"}
    try:
        with pytest.raises(ValueError, match=messages[reply]) if reply in messages else nullcontext():
            await sampler.sample_with_prompt_tokens_result(
                [1, 2, 3],
                max_tokens=100,
                logprobs=True,
                top_k=8,
                sampling_mask="parquet_v1",
                **{count_key: 4, format_key: "parquet_v1"},
            )
    finally:
        sampler.close()
