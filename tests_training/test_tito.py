from __future__ import annotations

import os
import sys
import json
import time
import zlib
import asyncio
import hashlib
import threading
import subprocess
from types import ModuleType, MappingProxyType
from typing import Any, Literal, Mapping, Sequence
from pathlib import Path
from collections import deque
from dataclasses import replace

import httpx
import pytest

from fireworks.training.sdk.tito import (
    TITOError,
    TITOSidecar,
    TITOParseError,
    TITOChatRequest,
    TITOParsedAssistant,
    TITOIncrementalPrompt,
    TrajectoryDriftPolicy,
    TITOTrajectoryArtifact,
    _artifact,
    _native_runtime,
)
from fireworks.training.sdk.routing import RoutingReferences
from fireworks.training.sdk.sampling import (
    ServerMetrics,
    DeploymentSampler,
    SampledCompletion,
    SampledRequestResult,
    SampledServerAttempt,
)
from fireworks.training.sdk.tito_debug import TITOLocalDebugSink, TITOLocalDebugConfig
from fireworks.training.sdk.tito._types import _freeze_json, _copy_json_in_order
from fireworks.training.sdk.tito._engine import _TrajectoryCore


def test_public_sidecar_import_does_not_load_torch_or_trainer_stack() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys; "
                "from fireworks.training.sdk import DeploymentSampler, TITOSidecar; "
                "assert 'torch' not in sys.modules; "
                "assert 'fireworks.training.sdk.client' not in sys.modules"
            ),
        ],
        check=False,
        capture_output=True,
        text=True,
        env={
            **os.environ,
            "PYTHONPATH": os.pathsep.join(
                (
                    str(Path(__file__).resolve().parents[1] / "src"),
                    os.environ.get("PYTHONPATH", ""),
                )
            ),
        },
    )
    assert completed.returncode == 0, completed.stderr


def _debug_events(sink: TITOLocalDebugSink, trajectory_id: str):
    storage_key = hashlib.sha256(trajectory_id.encode("utf-8")).hexdigest()
    path = sink.trajectories_dir / storage_key / "events.jsonl"
    return [json.loads(line) for line in path.read_text().splitlines()]


def _content(message: Mapping[str, Any]) -> str:
    value = message.get("content", "")
    return value if isinstance(value, str) else str(value)


class FakeRenderer:
    renderer_id = "fake-v1"

    def __init__(
        self,
        *,
        canonical_stop: int = 3,
        contract_suffix: str = "",
        fail_parse: bool = False,
    ) -> None:
        self.canonical_stop = canonical_stop
        self.contract_suffix = contract_suffix
        self.fail_parse = fail_parse
        self.render_calls = 0

    @staticmethod
    def _text(value: str) -> list[int]:
        return [100 + ord(char) for char in value]

    def _message(self, message: Mapping[str, Any]) -> list[int]:
        role = message["role"]
        content = self._text(_content(message))
        if role == "assistant":
            return [2, *content, self.canonical_stop]
        if role == "user":
            return [10, *content, 11]
        if role == "tool":
            return [20, *content, 21]
        if role == "system":
            return [30, *content, 31]
        return [40, *content, 41]

    def render_conversation_tokens(self, request: TITOChatRequest) -> Sequence[int]:
        self.render_calls += 1
        output = [1]
        for message in request.messages:
            output.extend(self._message(message))
        output.append(2)
        return output

    def parse_assistant(
        self,
        request: TITOChatRequest,
        completion_ids: Sequence[int],
        completion_text: str,
        finish_reason: str,
    ) -> TITOParsedAssistant:
        if self.fail_parse:
            raise TITOParseError("parser failed")
        body = completion_ids[:-1] if completion_ids else completion_ids
        text = "".join(chr(token - 100) for token in body)
        return TITOParsedAssistant(
            message={"role": "assistant", "content": text},
            output_kind="text",
        )

    def render_contract_id(self, request: TITOChatRequest) -> str:
        return f"fake:{self.contract_suffix}:{len(request.tools)}"

    def stop_sequences(self, request: TITOChatRequest) -> Sequence[str] | None:
        return ["<stop>"]


class FakeIncrementalRenderer(FakeRenderer):
    def __init__(
        self,
        *,
        incremental_supported: bool = True,
        corrupt_incremental_prompt: bool = False,
        checkpoint_trim_tokens: int = 0,
        replacement_token: int | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.incremental_supported = incremental_supported
        self.corrupt_incremental_prompt = corrupt_incremental_prompt
        self.checkpoint_trim_tokens = checkpoint_trim_tokens
        self.replacement_token = replacement_token
        self.incremental_calls = 0

    def prepare_incremental_prompt(
        self,
        request: TITOChatRequest,
        stored_messages: Sequence[Mapping[str, Any]],
        appended_messages: Sequence[Mapping[str, Any]],
        exact_checkpoint_ids: Sequence[int],
    ) -> TITOIncrementalPrompt | None:
        del request, stored_messages
        self.incremental_calls += 1
        if not self.incremental_supported or not appended_messages:
            return None
        checkpoint = tuple(int(token) for token in exact_checkpoint_ids)
        if self.corrupt_incremental_prompt:
            checkpoint = (999, *checkpoint[1:])
        if self.checkpoint_trim_tokens:
            retained = checkpoint[: -self.checkpoint_trim_tokens]
            replacement = (
                (self.replacement_token,)
                if self.replacement_token is not None
                else checkpoint[-self.checkpoint_trim_tokens :]
            )
            checkpoint = (*retained, *replacement)
        return TITOIncrementalPrompt(
            prompt_ids=(*checkpoint, 77, 2),
            contract_id="fake-incremental-v1",
            junction_kind=("replace_role_boundary" if self.replacement_token is not None else "append"),
            checkpoint_trim_tokens=self.checkpoint_trim_tokens,
        )


def _top_sampling_refs(length: int, *, row_start: int = 0) -> RoutingReferences:
    return RoutingReferences.from_dict(
        {
            "length": length,
            "files": [
                {
                    "store_id": "store",
                    "file_id": f"file-{row_start}",
                    "format": "parquet_v1",
                    "row_count": row_start + length,
                }
            ],
            "spans": [{"input_token_start": 0, "count": length, "file_index": 0, "file_row_start": row_start}],
        }
    )


class FakeSampler:
    def __init__(
        self,
        outputs: Sequence[Sequence[int]] | None = None,
        *,
        finishes: Sequence[str] | None = None,
        additional_headers: dict[str, str] | None = None,
    ) -> None:
        self.outputs = deque(tuple(item) for item in (outputs or ([197, 3],)))
        self.finishes = deque(finishes or ("stop",))
        self.additional_headers = additional_headers
        self.calls: list[dict[str, Any]] = []
        self.started = asyncio.Event()
        self.release = asyncio.Event()
        self.block = False
        self.top_sampling_rows_delta = 0

    async def sample_with_prompt_tokens_result(
        self, prompt_token_ids: list[int], **kwargs: Any
    ) -> SampledRequestResult:
        self.calls.append({"prompt": tuple(prompt_token_ids), **kwargs})
        self.started.set()
        if self.block:
            await self.release.wait()
        output = self.outputs.popleft() if len(self.outputs) > 1 else self.outputs[0]
        finish = self.finishes.popleft() if len(self.finishes) > 1 else self.finishes[0]
        routes = _top_sampling_refs(len(output)) if kwargs.get("include_routing_matrix") else None
        completion = SampledCompletion(
            text="fake",
            full_tokens=[*prompt_token_ids, *output],
            prompt_len=len(prompt_token_ids),
            finish_reason=finish,
            completion_len=len(output),
            inference_logprobs=[-0.1] * len(output),
            sampling_logprobs=[-0.2] * len(output),
            routing_matrices=routes,
            sample_extra_references=(
                _top_sampling_refs(len(output) + self.top_sampling_rows_delta, row_start=10 * len(self.calls))
                if kwargs.get("sample_extra_tokens")
                else None
            ),
            top_sampling_references=(
                _top_sampling_refs(len(output) + self.top_sampling_rows_delta, row_start=10 * len(self.calls))
                if kwargs.get("top_sampling_logprobs")
                else None
            ),
            sampling_mask_references=(
                _top_sampling_refs(len(output) + self.top_sampling_rows_delta, row_start=10 * len(self.calls))
                if kwargs.get("sampling_mask")
                else None
            ),
        )
        return SampledRequestResult(
            completions=[completion],
            server_metrics=(
                metrics := ServerMetrics(
                    prompt_tokens=len(prompt_token_ids),
                    cached_prompt_tokens=max(0, len(prompt_token_ids) - 2),
                    prefill_duration=0.02,
                    generation_duration=0.03,
                    response_request_id=f"request-{len(self.calls)}",
                    backend_host=f"pod-{len(self.calls)}",
                )
            ),
            logical_request_id=kwargs.get("logical_request_id") or f"logical-{len(self.calls)}",
            attempts=1,
            wall_seconds=0.05,
            upstream_response_id=f"cmpl-upstream-{len(self.calls)}",
            server_attempts=(
                SampledServerAttempt(
                    index=1,
                    outcome="succeeded",
                    status_code=200,
                    response_request_id=metrics.response_request_id,
                    upstream_response_id=f"cmpl-upstream-{len(self.calls)}",
                    server_metrics=metrics,
                ),
            ),
        )


def _request(messages: Sequence[Mapping[str, Any]], **kwargs: Any) -> TITOChatRequest:
    return TITOChatRequest(messages=tuple(messages), **kwargs)


def _first_request(**kwargs: Any) -> TITOChatRequest:
    return _request(({"role": "user", "content": "q"},), **kwargs)


def test_openai_normalization_separates_chat_protocol_controls_from_sampling() -> None:
    request = TITOChatRequest.from_openai(
        {
            "model": "policy",
            "messages": [{"role": "user", "content": "q"}],
            "stream": True,
            "stream_options": {"include_usage": True},
            "tool_choice": "auto",
            "parallel_tool_calls": True,
            "store": False,
            "top_p": 0.9,
        }
    )
    assert request.sampling_fields == {"top_p": 0.9}


def test_null_max_completion_tokens_falls_back_to_legacy_max_tokens() -> None:
    request = TITOChatRequest.from_openai(
        {
            "model": "policy",
            "messages": [{"role": "user", "content": "q"}],
            "max_completion_tokens": None,
            "max_tokens": 37,
        }
    )

    assert request.max_tokens == 37


def test_openai_normalization_canonicalizes_json_equivalent_tool_arguments() -> None:
    spaced = TITOChatRequest.from_openai(
        {
            "messages": [
                {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": "call-1",
                            "type": "function",
                            "function": {
                                "name": "run",
                                "arguments": '{"z": 1, "nested": {"b": 2, "a": 1}}',
                            },
                        }
                    ],
                }
            ]
        }
    )
    compact = TITOChatRequest.from_openai(
        {
            "messages": [
                {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "id": "call-1",
                            "type": "function",
                            "function": {
                                "name": "run",
                                "arguments": '{"nested":{"a":1,"b":2},"z":1}',
                            },
                        }
                    ],
                }
            ]
        }
    )

    assert spaced.messages == compact.messages
    function = spaced.messages[0]["tool_calls"][0]["function"]
    assert function["arguments"] == '{"nested":{"a":1,"b":2},"z":1}'
    assert spaced.wire_value()["messages"][0]["content"] is None  # type: ignore[index]
    assert spaced.normalization_steps == (
        "messages[0].content:null_to_empty",
        "messages[0].tool_calls[0].function.arguments:canonical_json",
    )


def test_openai_normalization_canonicalizes_whitespace_only_tool_content() -> None:
    request = TITOChatRequest.from_openai(
        {
            "messages": [
                {
                    "role": "assistant",
                    "content": "  \n\t",
                    "tool_calls": [
                        {
                            "id": "call-1",
                            "type": "function",
                            "function": {"name": "run", "arguments": "{}"},
                        }
                    ],
                }
            ]
        }
    )

    assert request.messages[0]["content"] == ""
    assert request.normalization_steps == ("messages[0].content:whitespace_to_empty",)


def test_openai_normalization_preserves_invalid_tool_argument_string() -> None:
    request = TITOChatRequest.from_openai(
        {
            "messages": [
                {
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "function": {
                                "name": "run",
                                "arguments": "not-json",
                            }
                        }
                    ],
                }
            ]
        }
    )

    assert request.messages[0]["tool_calls"][0]["function"]["arguments"] == "not-json"


@pytest.mark.parametrize(
    "field,value",
    [
        ("tool_choice", "none"),
        ("tool_choice", "required"),
        ("tool_choice", {"type": "function", "function": {"name": "forced"}}),
        ("parallel_tool_calls", False),
        ("store", True),
    ],
)
def test_openai_normalization_rejects_tool_policies_it_cannot_enforce(
    field: str,
    value: Any,
) -> None:
    with pytest.raises(TITOError) as exc_info:
        TITOChatRequest.from_openai(
            {
                "model": "policy",
                "messages": [{"role": "user", "content": "q"}],
                field: value,
            }
        )
    assert exc_info.value.code == "tito_invalid_request"
    assert exc_info.value.status == 400


def _second_request(**kwargs: Any) -> TITOChatRequest:
    return _request(
        (
            {"role": "user", "content": "q"},
            {"role": "assistant", "content": "a"},
            {"role": "user", "content": "b"},
        ),
        **kwargs,
    )


def _engine(
    sampler: FakeSampler,
    renderer: FakeRenderer | None = None,
    **kwargs: Any,
) -> _TrajectoryCore:
    return _TrajectoryCore(
        sampler,  # type: ignore[arg-type]
        renderer or FakeRenderer(),
        max_context_tokens=256,
        max_output_tokens=32,
        **kwargs,
    )


def _assert_call_accounting(metrics: Mapping[str, int]) -> None:
    assert metrics["calls/total"] == metrics.get("calls/policy", 0) + metrics.get("calls/auxiliary", 0)
    assert metrics["calls/total"] == sum(
        metrics.get(f"calls/{outcome}", 0)
        for outcome in (
            "succeeded",
            "replayed",
            "model_malformed",
            "rejected",
            "failed",
            "cancelled",
        )
    )


async def test_exact_append_preserves_sampled_checkpoint() -> None:
    sampler = FakeSampler(outputs=([197, 3], [198, 3]))
    engine = _engine(sampler)
    trajectory_id = engine.create_trajectory(serving_affinity_key="affinity-one")

    first = await engine.complete(trajectory_id, _first_request())
    second = await engine.complete(trajectory_id, _second_request())
    assert first.turn_id and second.turn_id

    result = engine.finish(trajectory_id)
    assert len(result.segments) == 1
    first_turn, second_turn = result.segments[0].turns
    assert second_turn.exact_prompt_ids[: len(first_turn.exact_checkpoint_ids)] == first_turn.exact_checkpoint_ids
    assert second_turn.prompt_disposition == "append"
    assert sampler.calls[0]["prompt_cache_key"] == "affinity-one"
    assert sampler.calls[1]["prompt_cache_key"] == "affinity-one"
    metrics = result.metrics.flattened()
    assert metrics["tito/lineage/append"] == 1
    assert metrics["tito/trajectory/policy_turns_mean"] == 2
    assert metrics["tito/cache/affinity_bound"] == 1
    assert metrics["tito/cache/affinity_reused"] == 1
    assert metrics["tito/turn/inter_call_gap_seconds_count"] == 2
    assert metrics["tito/turn/request_wall_seconds_count"] == 2
    assert result.calls[1].server_attempts[0].response_request_id == "request-2"
    attempt_metrics = result.segments[0].turns[1].server_attempts[0].server_metrics
    assert attempt_metrics is not None and attempt_metrics.backend_host == "pod-2"


@pytest.mark.parametrize(
    "sampling_defaults",
    [
        {"top_sampling_logprobs": 128, "top_sampling_format": "parquet_v1"},
        {"top_sampling_logprobs": 128},
        {"sample_extra_tokens": 3},
        {"sample_extra_tokens": 3, "sample_extra_format": "parquet_v1"},
        {"sampling_mask": "parquet_v1", "sample_extra_tokens": 3, "sample_extra_format": "parquet_v1"},
        {"sampling_mask": "parquet_v1"},
        {"sampling_mask": "parquet_v1", "top_sampling_logprobs": 128, "top_sampling_format": "parquet_v1"},
    ],
)
async def test_policy_turns_record_completion_only_top_sampling_references(sampling_defaults) -> None:
    sampler = FakeSampler(outputs=([197, 3], [198, 199, 3]))
    engine = _engine(
        sampler,
        sampling_defaults=sampling_defaults,
    )
    trajectory_id = engine.create_trajectory()

    await engine.complete(trajectory_id, _first_request())
    await engine.complete(trajectory_id, _second_request())
    artifact = engine.finish(trajectory_id)

    assert all(all(call[key] == value for key, value in sampling_defaults.items()) for call in sampler.calls)
    turns = [turn for segment in artifact.segments for turn in segment.turns]
    for channel, enabled in (
        ("top_sampling", bool(sampling_defaults.get("top_sampling_logprobs"))),
        ("sample_extra", bool(sampling_defaults.get("sample_extra_tokens"))),
        ("sampling_mask", "sampling_mask" in sampling_defaults),
    ):
        assert [getattr(turn, channel + "_references") for turn in turns] == (
            [_top_sampling_refs(2, row_start=10), _top_sampling_refs(3, row_start=20)] if enabled else [None, None]
        )
    restored = type(artifact).unpack(artifact.pack())
    assert [turn.top_sampling_references for segment in restored.segments for turn in segment.turns] == [
        turn.top_sampling_references for turn in turns
    ]

    auxiliary_sampler = FakeSampler(outputs=([197, 3],))
    auxiliary = _engine(
        auxiliary_sampler,
        sampling_defaults=sampling_defaults,
        call_classifier=lambda _request: ("auxiliary", "test_auxiliary"),
    )
    await auxiliary.complete(auxiliary.create_trajectory(), _first_request())
    assert not {"top_sampling_format", "top_sampling_logprobs", "sampling_mask"} & auxiliary_sampler.calls[0].keys()
    if bool(sampling_defaults.get("sample_extra_tokens")):
        assert not {"sample_extra_tokens", "sample_extra_format"} & auxiliary_sampler.calls[0].keys()


    misaligned = FakeSampler(outputs=([197, 3],))
    misaligned.top_sampling_rows_delta = -1
    engine = _engine(misaligned, sampling_defaults=sampling_defaults)
    trajectory_id = engine.create_trajectory()
    with pytest.raises(TITOError, match="references"):
        await engine.complete(trajectory_id, _first_request())


async def test_default_full_history_mode_never_calls_incremental_renderer() -> None:
    sampler = FakeSampler(outputs=([197, 3], [198, 3]))
    renderer = FakeIncrementalRenderer()
    engine = _engine(sampler, renderer)
    trajectory_id = engine.create_trajectory()

    await engine.complete(trajectory_id, _first_request())
    await engine.complete(trajectory_id, _second_request())
    result = engine.finish(trajectory_id)

    assert renderer.render_calls == 2
    assert renderer.incremental_calls == 0
    assert [turn.prompt_mode for turn in result.segments[0].turns] == [
        "full_history",
        "full_history",
    ]
    assert sampler.calls[0]["prompt"] == tuple(FakeRenderer().render_conversation_tokens(_first_request()))
    assert sampler.calls[1]["prompt"] == tuple(FakeRenderer().render_conversation_tokens(_second_request()))


async def test_incremental_mode_reuses_checkpoint_without_full_history_oracle() -> None:
    sampler = FakeSampler(outputs=([197, 3], [198, 3]))
    renderer = FakeIncrementalRenderer(canonical_stop=4)
    engine = _engine(sampler, renderer, prompt_mode="incremental")
    trajectory_id = engine.create_trajectory()

    await engine.complete(trajectory_id, _first_request())
    await engine.complete(trajectory_id, _second_request())
    result = engine.finish(trajectory_id)

    assert renderer.render_calls == 1
    assert renderer.incremental_calls == 1
    assert len(result.segments) == 1
    first, second = result.segments[0].turns
    assert second.exact_prompt_ids == (*first.exact_checkpoint_ids, 77, 2)
    assert second.prompt_disposition == "append"
    assert second.prompt_mode == "incremental"
    assert second.incremental_contract_id == "fake-incremental-v1"
    assert second.incremental_junction_kind == "append"
    assert second.incremental_fallback_reason is None
    assert result.metrics.counters["prompt_construction/full_history"] == 1
    assert result.metrics.counters["prompt_construction/incremental"] == 1


async def test_incremental_unsupported_falls_back_to_full_rendered_segment() -> None:
    sampler = FakeSampler(outputs=([197, 3], [198, 3]))
    renderer = FakeIncrementalRenderer(incremental_supported=False)
    engine = _engine(sampler, renderer, prompt_mode="incremental")
    trajectory_id = engine.create_trajectory()

    await engine.complete(trajectory_id, _first_request())
    await engine.complete(trajectory_id, _second_request())
    result = engine.finish(trajectory_id)

    assert renderer.render_calls == 2
    assert len(result.segments) == 2
    assert result.segments[1].start_reason == "incremental_unsupported"
    second = result.segments[1].turns[0]
    assert second.prompt_mode == "full_history"
    assert second.incremental_fallback_reason == "unsupported_incremental_join"
    assert result.metrics.counters["lineage/boundary_reason_incremental_unsupported"] == 1
    assert result.metrics.counters["prompt_construction/incremental_fallback"] == 1


async def test_incremental_unsupported_rejects_under_strict_policy() -> None:
    sampler = FakeSampler(outputs=([197, 3], [198, 3]))
    renderer = FakeIncrementalRenderer(incremental_supported=False)
    engine = _engine(sampler, renderer, prompt_mode="incremental")
    trajectory_id = engine.create_trajectory(drift_policy=TrajectoryDriftPolicy(on_other_mismatch="reject"))
    await engine.complete(trajectory_id, _first_request())

    with pytest.raises(TITOError) as exc_info:
        await engine.complete(trajectory_id, _second_request())

    assert exc_info.value.code == "tito_lineage_divergence"
    assert len(sampler.calls) == 1
    assert renderer.render_calls == 1


async def test_incremental_renderer_cannot_rewrite_the_checkpoint() -> None:
    sampler = FakeSampler(outputs=([197, 3], [198, 3]))
    renderer = FakeIncrementalRenderer(corrupt_incremental_prompt=True)
    engine = _engine(sampler, renderer, prompt_mode="incremental")
    trajectory_id = engine.create_trajectory()
    await engine.complete(trajectory_id, _first_request())

    with pytest.raises(TITOError) as exc_info:
        await engine.complete(trajectory_id, _second_request())

    assert exc_info.value.code == "tito_renderer_contract_error"
    assert len(sampler.calls) == 1


async def test_incremental_renderer_may_replace_declared_checkpoint_tail() -> None:
    sampler = FakeSampler(outputs=([197, 3], [198, 3]))
    renderer = FakeIncrementalRenderer(
        checkpoint_trim_tokens=1,
        replacement_token=55,
    )
    engine = _engine(sampler, renderer, prompt_mode="incremental")
    trajectory_id = engine.create_trajectory()

    await engine.complete(trajectory_id, _first_request())
    await engine.complete(trajectory_id, _second_request())
    result = engine.finish(trajectory_id)

    first, second = result.segments[0].turns
    assert second.exact_prompt_ids == (
        *first.exact_checkpoint_ids[:-1],
        55,
        77,
        2,
    )
    assert second.prefix_match_tokens == len(first.exact_checkpoint_ids) - 1
    assert second.incremental_checkpoint_trim_tokens == 1
    assert second.incremental_junction_kind == "replace_role_boundary"
    assert result.metrics.counters["prompt_construction/incremental_checkpoint_trim_tokens"] == 1


async def test_incremental_renderer_cannot_trim_beyond_checkpoint() -> None:
    sampler = FakeSampler(outputs=([197, 3], [198, 3]))
    renderer = FakeIncrementalRenderer(checkpoint_trim_tokens=10)
    engine = _engine(sampler, renderer, prompt_mode="incremental")
    trajectory_id = engine.create_trajectory()
    await engine.complete(trajectory_id, _first_request())

    with pytest.raises(TITOError) as exc_info:
        await engine.complete(trajectory_id, _second_request())

    assert exc_info.value.code == "tito_renderer_contract_error"
    assert len(sampler.calls) == 1


def test_incremental_mode_requires_the_optional_renderer_capability() -> None:
    with pytest.raises(TypeError, match="experimental incremental prompt mode"):
        _engine(FakeSampler(), FakeRenderer(), prompt_mode="incremental")


async def test_empty_renderer_stops_are_omitted_from_sampler_request() -> None:
    class NoStopRenderer(FakeRenderer):
        def stop_sequences(self, request: TITOChatRequest) -> Sequence[str] | None:
            return None

    sampler = FakeSampler(outputs=([197, 3],))
    engine = _engine(sampler, NoStopRenderer())
    trajectory_id = engine.create_trajectory()

    await engine.complete(trajectory_id, _first_request())
    engine.finish(trajectory_id)

    assert sampler.calls[0]["stop"] is None


async def test_non_text_renderer_stop_is_rejected_before_sampling() -> None:
    class InvalidStopRenderer(FakeRenderer):
        def stop_sequences(self, request: TITOChatRequest) -> Sequence[str] | None:
            return [3]  # type: ignore[list-item]

    sampler = FakeSampler(outputs=([197, 3],))
    engine = _engine(sampler, InvalidStopRenderer())
    trajectory_id = engine.create_trajectory()

    with pytest.raises(TITOError) as exc_info:
        await engine.complete(trajectory_id, _first_request())

    assert exc_info.value.code == "tito_renderer_contract_error"
    assert exc_info.value.should_retry is False
    assert sampler.calls == []
    engine.finish(trajectory_id)


async def test_finish_rejects_active_transport_before_summary_metrics() -> None:
    sampler = FakeSampler(outputs=([197, 3],))
    engine = _engine(sampler)
    trajectory_id = engine.create_trajectory()
    await engine.complete(trajectory_id, _first_request())
    state = engine._state  # noqa: SLF001 - lifecycle invariant
    assert state is not None and state.trajectory_id == trajectory_id
    transport = asyncio.create_task(asyncio.Event().wait())
    state.transport_tasks.add(transport)

    try:
        with pytest.raises(TITOError, match="in flight"):
            engine.finish(trajectory_id)
        assert not any(name.startswith("trajectory/") for name in state.metrics.distributions)
    finally:
        transport.cancel()
        await asyncio.gather(transport, return_exceptions=True)

    result = engine.finish(trajectory_id)
    assert result.metrics.distributions["trajectory/policy_turns"].count == 1


@pytest.mark.parametrize("terminal_method", ("abandon", "fail"))
async def test_sync_terminal_methods_reject_in_flight_before_summary_metrics(
    terminal_method: str,
) -> None:
    engine = _engine(FakeSampler(outputs=([197, 3],)))
    trajectory_id = engine.create_trajectory()
    await engine.complete(trajectory_id, _first_request())
    state = engine._state  # noqa: SLF001 - lifecycle invariant
    assert state is not None
    state.policy_in_flight = True

    try:
        with pytest.raises(TITOError, match="in flight"):
            getattr(engine, terminal_method)(trajectory_id, "test")
        assert not any(name.startswith("trajectory/") for name in state.metrics.distributions)
    finally:
        state.policy_in_flight = False

    result = engine.finish(trajectory_id)
    assert result.metrics.distributions["trajectory/policy_turns"].count == 1


def test_nested_immutable_request_values_are_json_normalized() -> None:
    request = TITOChatRequest(
        messages=(
            {
                "role": "assistant",
                "tool_calls": (
                    MappingProxyType(
                        {
                            "id": "call-1",
                            "function": MappingProxyType({"name": "search", "arguments": '{"q":"x"}'}),
                        }
                    ),
                ),
            },
        )
    )
    assert request.messages[0]["tool_calls"][0]["function"]["name"] == "search"


def test_drift_policy_has_one_explicit_coverage_bound() -> None:
    assert TrajectoryDriftPolicy(max_masked_tokens=17).max_masked_tokens == 17
    with pytest.raises(ValueError, match="non-negative"):
        TrajectoryDriftPolicy(max_masked_tokens=-1)


def test_tool_call_only_assistant_null_content_is_canonical_empty_string() -> None:
    request = TITOChatRequest(
        messages=(
            {"role": "user", "content": "Use a tool."},
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "call-1",
                        "type": "function",
                        "function": {"name": "search", "arguments": '{"q":"x"}'},
                    }
                ],
            },
        )
    )

    assert request.messages[1]["content"] == ""

    parsed = TITOParsedAssistant(
        message={
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": "call-1",
                    "type": "function",
                    "function": {
                        "name": "search",
                        "arguments": '{"q":"x","a":1}',
                    },
                }
            ],
        },
        output_kind="tool_calls",
    )
    assert parsed.message["content"] == ""
    assert parsed.message["tool_calls"][0]["function"]["arguments"] == ('{"a":1,"q":"x"}')


async def test_parsed_assistant_and_harness_echo_share_protocol_canonicalization() -> None:
    class NonCanonicalToolRenderer(FakeRenderer):
        def parse_assistant(
            self,
            request: TITOChatRequest,
            completion_ids: Sequence[int],
            completion_text: str,
            finish_reason: str,
        ) -> TITOParsedAssistant:
            del request, completion_ids, completion_text, finish_reason
            return TITOParsedAssistant(
                message={
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": "call-1",
                            "type": "function",
                            "function": {
                                "name": "search",
                                "arguments": '{"q":"x","a":1}',
                            },
                        }
                    ],
                },
                output_kind="tool_calls",
            )

    sampler = FakeSampler(outputs=([3], [3]))
    engine = _engine(sampler, NonCanonicalToolRenderer())
    trajectory_id = engine.create_trajectory()
    tools = ({"type": "function", "function": {"name": "search"}},)
    first = _request(({"role": "user", "content": "search"},), tools=tools)
    await engine.complete(trajectory_id, first)
    await engine.complete(
        trajectory_id,
        _request(
            (
                {"role": "user", "content": "search"},
                {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "id": "call-1",
                            "type": "function",
                            "function": {
                                "name": "search",
                                "arguments": '{"a":1,"q":"x"}',
                            },
                        }
                    ],
                },
                {
                    "role": "tool",
                    "tool_call_id": "call-1",
                    "content": "done",
                },
            ),
            tools=tools,
        ),
    )
    result = engine.finish(trajectory_id)

    assert len(result.segments) == 1
    assert result.segments[0].turns[1].prompt_disposition == "append"
    assert "lineage/boundary_reason_history_rewrite" not in result.metrics.counters


async def test_latest_response_drift_realigns_and_masks_the_complete_replacement_span() -> None:
    sampler = FakeSampler(outputs=([197, 3], [198, 3]))
    renderer = FakeRenderer(canonical_stop=4)
    engine = _engine(sampler, renderer)
    trajectory_id = engine.create_trajectory()
    await engine.complete(trajectory_id, _first_request())
    await engine.complete(trajectory_id, _second_request())
    result = engine.finish(trajectory_id)

    assert len(result.segments) == 1
    first_turn, second_turn = result.segments[0].turns
    expected_masked_tokens = len(second_turn.exact_prompt_ids) - len(first_turn.exact_prompt_ids)
    assert second_turn.prompt_disposition == "realign"
    assert second_turn.realign_from_token == len(first_turn.exact_prompt_ids)
    assert second_turn.realigned_masked_tokens == expected_masked_tokens
    assert sampler.calls[1]["prompt"] == second_turn.exact_prompt_ids
    assert second_turn.upstream_response_id == "cmpl-upstream-2"
    assert result.calls[1].upstream_response_id == "cmpl-upstream-2"
    assert result.metrics.counters["lineage/realign"] == 1
    assert result.metrics.counters["lineage/realigned_masked_tokens"] == expected_masked_tokens


async def test_disabled_realign_keeps_prior_branch_and_starts_a_training_example() -> None:
    sampler = FakeSampler(outputs=([197, 3], [198, 3]))
    engine = _engine(sampler, FakeRenderer(canonical_stop=4))
    trajectory_id = engine.create_trajectory(drift_policy=TrajectoryDriftPolicy(max_masked_tokens=0))
    await engine.complete(trajectory_id, _first_request())
    await engine.complete(trajectory_id, _second_request())
    result = engine.finish(trajectory_id)

    assert len(result.segments) == 2
    assert result.segments[0].closed_reason == "trajectory_completed"
    assert result.segments[1].start_reason == "token_drift"
    assert len(result.segments[0].turns) == len(result.segments[1].turns) == 1
    assert result.segments[0].turns[0].prompt_disposition == "new_segment"
    assert result.segments[1].turns[0].prompt_disposition == "new_segment"
    assert result.metrics.counters["lineage/prefix_mismatch"] == 1
    assert result.metrics.counters["lineage/boundary_reason_unbounded_or_ambiguous_drift"] == 1


async def test_masked_span_equal_to_bound_splits_instead_of_realigning() -> None:
    sampler = FakeSampler(outputs=([197, 3], [198, 3]))
    renderer = FakeRenderer(canonical_stop=4)
    first_prompt_tokens = len(renderer.render_conversation_tokens(_first_request()))
    second_prompt_tokens = len(renderer.render_conversation_tokens(_second_request()))
    masked_tokens = second_prompt_tokens - first_prompt_tokens
    renderer.render_calls = 0
    engine = _engine(sampler, renderer)
    trajectory_id = engine.create_trajectory(drift_policy=TrajectoryDriftPolicy(max_masked_tokens=masked_tokens))

    await engine.complete(trajectory_id, _first_request())
    await engine.complete(trajectory_id, _second_request())
    result = engine.finish(trajectory_id)

    assert len(result.segments) == 2
    assert result.segments[1].turns[0].prompt_disposition == "new_segment"
    assert result.metrics.counters.get("lineage/realign", 0) == 0


async def test_each_policy_request_is_full_rendered_exactly_once() -> None:
    sampler = FakeSampler(outputs=([197, 3], [198, 3]))
    renderer = FakeRenderer()
    engine = _engine(sampler, renderer)
    trajectory_id = engine.create_trajectory()
    await engine.complete(trajectory_id, _first_request())
    await engine.complete(trajectory_id, _second_request())
    result = engine.finish(trajectory_id)

    assert renderer.render_calls == 2
    assert [call["prompt"] for call in sampler.calls] == [
        turn.exact_prompt_ids for segment in result.segments for turn in segment.turns
    ]


async def test_trajectory_engine_uses_real_deployment_sampler_request_path() -> None:
    sampler = DeploymentSampler(
        inference_url="https://in-process.invalid",
        model="policy",
        api_key="request-local-key",
        tokenizer=None,
    )
    calls: list[dict[str, Any]] = []

    async def controlled_transport(*args: Any, **kwargs: Any):
        del args
        calls.append(kwargs)
        return (
            {
                "id": "cmpl-controlled",
                "choices": [
                    {
                        "text": "a",
                        "finish_reason": "stop",
                        "token_ids": [197, 3],
                    }
                ],
            },
            ServerMetrics(prompt_tokens=len(kwargs["prompt"]), cached_prompt_tokens=0),
        )

    sampler.async_completions_stream = controlled_transport  # type: ignore[method-assign]
    engine = _TrajectoryCore(
        sampler,
        FakeRenderer(),
        max_context_tokens=128,
        max_output_tokens=16,
    )
    trajectory_id = engine.create_trajectory()
    call = await engine.complete(trajectory_id, _first_request())
    result = engine.finish(trajectory_id)
    sampler.close()

    assert call.turn_id == result.segments[0].turns[0].turn_id
    assert calls[0]["prompt"] == list(FakeRenderer().render_conversation_tokens(_first_request()))
    assert calls[0]["prompt_cache_key"]
    assert calls[0]["max_tokens"] == 16


@pytest.mark.parametrize("copy", [_freeze_json, _copy_json_in_order])
def test_json_copy_preserves_order_values_and_detaches_shared_containers(copy):
    class FloatSubclass(float):
        pass

    values = [None, True, -0.0, FloatSubclass(0.125), "é🔥", float("nan"), float("inf"), 2**200]
    shared = {"z": values, "a": (1, 2)}
    source = MappingProxyType({"z": shared, "a": shared, 1: object(), "1": "valid surviving value"})
    expected_shared = {"z": list(values), "a": [1, 2]}
    expected = {"z": expected_shared, "a": expected_shared, "1": "valid surviving value"}
    expected = json.loads(json.dumps(expected, sort_keys=copy is _freeze_json))
    actual = copy(source)
    # Comparing serialized output checks nested key order, NaN, and signed zero.
    assert json.dumps(actual) == json.dumps(expected)
    assert type(actual["z"]["z"][3]) is float
    actual["z"]["z"].append("changed")
    assert len(values) == len(actual["a"]["z"]) == 8


@pytest.mark.parametrize("copy", [_freeze_json, _copy_json_in_order])
@pytest.mark.parametrize("invalid", [object(), b"bytes", {1, 2}, complex(1, 2)])
def test_json_copy_rejects_non_json_values(copy, invalid):
    with pytest.raises(TITOError) as failure:
        copy({"nested": [invalid]})
    assert failure.value.code == "tito_invalid_request"


@pytest.mark.parametrize("copy", [_freeze_json, _copy_json_in_order])
def test_json_copy_preserves_integer_digit_limit(copy):
    if not hasattr(sys, "get_int_max_str_digits") or not sys.get_int_max_str_digits():
        pytest.skip("This Python runtime has no integer digit limit")
    with pytest.raises(TITOError):
        copy(10 ** (sys.get_int_max_str_digits() + 10))


async def test_native_artifact_matches_canonical_json() -> None:
    engine = _engine(FakeSampler(outputs=([197, 3],)))
    trajectory = engine.create_trajectory(
        metadata={"unicode": "雪 🔥", "scores": [-0.0, 1e-15, 2**80, None, True]},
    )
    await engine.complete(trajectory, _first_request())
    result = engine.finish(trajectory)
    native = result.pack()
    canonical = json.dumps(
        _artifact._artifact_value(result), sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()

    magic = b"TITOART\x01"
    assert native.startswith(magic)
    assert zlib.decompress(native[len(magic) :]) == canonical
    assert type(result).unpack(native) == result


async def test_missing_native_extension_still_allows_artifact_read(monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _engine(FakeSampler())
    trajectory = engine.create_trajectory()
    await engine.complete(trajectory, _first_request())
    artifact = engine.finish(trajectory)
    payload = artifact.pack()

    monkeypatch.setattr(_native_runtime, "_native", None)
    assert type(artifact).unpack(payload) == artifact
    with pytest.raises(RuntimeError, match="require the native Training SDK extension"):
        artifact.pack()
    with pytest.raises(RuntimeError, match="require the native Training SDK extension"):
        _engine(FakeSampler())
    with pytest.raises(RuntimeError, match="require the native Training SDK extension"):
        TITOSidecar.runtime_files()


def test_stale_native_extension_fails_before_sampling(monkeypatch: pytest.MonkeyPatch) -> None:
    sampler = FakeSampler()
    monkeypatch.setattr(_native_runtime, "_native", ModuleType("_native"))
    with pytest.raises(RuntimeError, match="rebuild the extension from this SDK checkout"):
        _engine(sampler)
    assert not sampler.calls


async def test_compact_trajectory_artifact_round_trip_is_versioned_and_exact() -> None:
    engine = _engine(FakeSampler(outputs=([197, 3],)))
    # Exercise multiple UTF-8/compression buffers; small artifacts are covered by other sidecar tests.
    trajectory_id = engine.create_trajectory(
        metadata={"task": "codec", "unicode": "é🔥" * 40000, "tokens": list(range(20000))},
    )
    wire_body = json.dumps(
        {
            "messages": [{"role": "user", "content": "hello"}],
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "search",
                        "parameters": {
                            "type": "object",
                            "properties": {"query": {"type": "string"}},
                            "required": ["query"],
                        },
                    },
                }
            ],
        }
    )
    request = TITOChatRequest.from_openai(
        json.loads(wire_body),
        wire_request_body=wire_body,
    )
    await engine.complete(trajectory_id, request)
    artifact = engine.finish(trajectory_id)

    packed = artifact.pack()
    restored = type(artifact).unpack(packed)
    with pytest.raises(ValueError, match="artifact encoding requires tree lineage"):
        replace(artifact, lineage_mode="linear").pack()  # type: ignore[arg-type]

    assert packed.startswith(b"TITOART\x01")
    body = zlib.decompress(packed[len(b"TITOART\x01") :])
    encoded = json.loads(body)
    assert encoded["lineage_mode"] == "tree"
    assert encoded["schema_version"] == 2
    canonical = json.dumps(encoded, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    assert body == canonical
    assert restored == artifact
    restored_parameters = restored.segments[0].turns[0].request.wire_value()["tools"][0]["function"]["parameters"]
    assert list(restored_parameters) == ["type", "properties", "required"]
    assert restored.segments[0].turns[0].request.wire_request_body == wire_body
    assert restored.pack() == packed
    with pytest.raises(TITOError) as exc_info:
        type(artifact).unpack(packed[:-1] + bytes([packed[-1] ^ 1]))
    assert exc_info.value.code == "tito_artifact_invalid"


async def test_legacy_linear_argument_warns_and_uses_tree() -> None:
    with pytest.warns(FutureWarning, match="linear lineage has been retired"):
        policy = TrajectoryDriftPolicy(lineage_mode="linear")
    engine = _engine(FakeSampler(outputs=([197, 3], [198, 3])))
    trajectory_id = engine.create_trajectory(drift_policy=policy)
    first = await engine.complete(trajectory_id, _first_request())
    await engine.complete(trajectory_id, _second_request())
    artifact = engine.finish(trajectory_id)
    assert artifact.segments[0].turns[1].parent_turn_id == first.turn_id


def test_linear_v1_artifact_is_rejected_by_both_readers() -> None:
    wire = {"schema_version": 1, "segments": [], "calls": [], "response_attempts": []}
    packed = b"TITOART\x01" + zlib.compress(json.dumps(wire, sort_keys=True).encode())
    with pytest.raises(TITOError, match="unsupported TITO artifact schema"):
        TITOTrajectoryArtifact.unpack(packed)
    with pytest.raises(TITOError, match="unsupported TITO artifact schema"):
        TITOTrajectoryArtifact.unpack_stream(
            [packed],
            expected_bytes=len(packed),
            expected_sha256=hashlib.sha256(packed).hexdigest(),
            max_expanded_bytes=4096,
        )


@pytest.mark.parametrize("prompt_mode", ["full_history", "incremental"])
async def test_artifact_round_trip_preserves_fork_boundaries(
    prompt_mode: Literal["full_history", "incremental"]
) -> None:
    sampler = FakeSampler(outputs=([197, 3], [198, 3], [199, 3], [200, 3]))
    engine = _TrajectoryCore(
        sampler, FakeIncrementalRenderer(), max_context_tokens=4096, max_output_tokens=128, prompt_mode=prompt_mode
    )
    trajectory_id = engine.create_trajectory()
    root_request = _request(({"role": "user", "content": "long tool context " * 50},))
    root = await engine.complete(trajectory_id, root_request)

    def follow(request, result, tool_output):
        return _request(
            (*request.messages, result.response["choices"][0]["message"], {"role": "tool", "content": tool_output})
        )

    left_request = follow(root_request, root, "left")
    left = await engine.complete(trajectory_id, left_request)
    await engine.complete(trajectory_id, follow(root_request, root, "right"))
    await engine.complete(trajectory_id, follow(left_request, left, "back to left"))
    artifact = engine.finish(trajectory_id)
    assert [len(segment.turns) for segment in artifact.segments] == [3, 1]
    packed = artifact.pack()
    restored = type(artifact).unpack(packed)
    assert restored == artifact
    assert restored.pack() == packed
    for chunk_size in (1, 257, 64 * 1024):
        streamed = type(artifact).unpack_stream(
            (packed[offset : offset + chunk_size] for offset in range(0, len(packed), chunk_size)),
            expected_bytes=len(packed),
            expected_sha256=hashlib.sha256(packed).hexdigest(),
            max_expanded_bytes=16 * 1024 * 1024,
        )
        assert streamed == restored
    header = b"TITOART\x01"
    decoded = json.loads(zlib.decompress(packed[len(header) :]))
    assert decoded["schema_version"] == 2
    assert decoded["lineage_mode"] == "tree"
    decoded["segments"][0]["turns"][0]["prompt_prefix"] = 0
    with pytest.raises(TITOError, match="unsupported TITO turn prompt prefix"):
        type(artifact).unpack(header + zlib.compress(json.dumps(decoded).encode("utf-8")))


@pytest.mark.parametrize(
    ("fault", "match"),
    [
        ("truncated", "byte count"),
        ("checksum", "checksum"),
        ("trailing", "trailing bytes"),
        ("incomplete_zlib", "incomplete TITO artifact compression stream"),
        ("expanded_limit", "expanded size"),
        ("oversize", "byte count"),
    ],
)
async def test_artifact_stream_never_returns_a_corrupt_or_incomplete_trajectory(fault: str, match: str) -> None:
    engine = _engine(FakeSampler())
    trajectory = engine.create_trajectory(metadata={"unicode": "雪🔥" * (64 * 1024)})
    await engine.complete(trajectory, _first_request())
    artifact = engine.finish(trajectory)
    packed = artifact.pack()
    wire = packed
    size = len(packed)
    sha256 = hashlib.sha256(packed).hexdigest()
    expanded_limit = 2 * 1024 * 1024

    if fault == "truncated":
        wire = packed[:-1]
    elif fault == "checksum":
        sha256 = "0" * 64
    elif fault == "trailing":
        wire = packed + b"garbage"
        size = len(wire)
        sha256 = hashlib.sha256(wire).hexdigest()
    elif fault == "incomplete_zlib":
        wire = packed[:-1]
        size = len(wire)
        sha256 = hashlib.sha256(wire).hexdigest()
    elif fault == "expanded_limit":
        expanded_limit = 64 * 1024
    else:
        size -= 1

    with pytest.raises(TITOError, match=match) as exc_info:
        type(artifact).unpack_stream(
            (wire[offset : offset + 17] for offset in range(0, len(wire), 17)),
            expected_bytes=size,
            expected_sha256=sha256,
            max_expanded_bytes=expanded_limit,
        )
    assert exc_info.value.code == "tito_artifact_invalid"


async def test_artifact_stream_retains_cancellation_after_wire_body() -> None:
    engine = _engine(FakeSampler())
    trajectory = engine.create_trajectory()
    await engine.complete(trajectory, _first_request())
    artifact = engine.finish(trajectory)
    packed = artifact.pack()

    def cancelled_stream():
        yield packed
        raise asyncio.CancelledError()

    with pytest.raises(asyncio.CancelledError):
        type(artifact).unpack_stream(
            cancelled_stream(),
            expected_bytes=len(packed),
            expected_sha256=hashlib.sha256(packed).hexdigest(),
            max_expanded_bytes=16 * 1024 * 1024,
        )


async def test_strict_mismatch_rejects_without_mutation() -> None:
    sampler = FakeSampler(outputs=([197, 3], [198, 3]))
    engine = _engine(sampler, FakeRenderer(canonical_stop=4))
    trajectory_id = engine.create_trajectory(
        drift_policy=TrajectoryDriftPolicy(max_masked_tokens=0, on_other_mismatch="reject")
    )
    await engine.complete(trajectory_id, _first_request())
    with pytest.raises(TITOError, match="does not safely extend") as exc_info:
        await engine.complete(trajectory_id, _second_request())
    assert exc_info.value.code == "tito_lineage_divergence"
    result = engine.finish(trajectory_id)
    assert len(result.segments) == 1 and len(result.segments[0].turns) == 1
    assert len(sampler.calls) == 1


async def test_strict_contract_change_rejects_without_mutation() -> None:
    sampler = FakeSampler(outputs=([197, 3], [198, 3]))
    engine = _engine(sampler)
    trajectory_id = engine.create_trajectory(drift_policy=TrajectoryDriftPolicy(on_other_mismatch="reject"))
    await engine.complete(trajectory_id, _first_request())
    with pytest.raises(TITOError) as exc_info:
        await engine.complete(
            trajectory_id,
            _second_request(tools=({"type": "function", "function": {"name": "search"}},)),
        )
    assert exc_info.value.code == "tito_lineage_divergence"
    result = engine.finish(trajectory_id)
    assert len(result.segments) == 1 and len(result.segments[0].turns) == 1
    assert len(sampler.calls) == 1
    assert result.metrics.counters["lineage/boundary_reason_contract_change"] == 1
    assert "lineage/contract_change" not in result.metrics.counters


async def test_full_history_renders_before_strict_contract_rejection() -> None:
    class FailingRenderer(FakeRenderer):
        def render_conversation_tokens(self, request: TITOChatRequest) -> Sequence[int]:
            if len(request.messages) > 1:
                raise RuntimeError("full render failed")
            return super().render_conversation_tokens(request)

    renderer = FailingRenderer()
    engine = _engine(FakeSampler(outputs=([197, 3], [198, 3])), renderer)
    trajectory_id = engine.create_trajectory(drift_policy=TrajectoryDriftPolicy(on_other_mismatch="reject"))
    await engine.complete(trajectory_id, _first_request())

    with pytest.raises(TITOError, match="local TITO SDK operation failed"):
        await engine.complete(
            trajectory_id,
            _second_request(tools=({"type": "function", "function": {"name": "search"}},)),
        )

    assert renderer.render_calls == 1


@pytest.mark.parametrize("prompt_mode", ["full_history", "incremental"])
async def test_history_rewrite_records_one_boundary_reason(prompt_mode: Literal["full_history", "incremental"]) -> None:
    sampler = FakeSampler(outputs=([197, 3], [198, 3]))
    engine = _engine(sampler, FakeIncrementalRenderer(), prompt_mode=prompt_mode)
    trajectory_id = engine.create_trajectory()
    await engine.complete(trajectory_id, _first_request())
    await engine.complete(
        trajectory_id,
        _request(({"role": "user", "content": "rewritten"},)),
    )
    result = engine.finish(trajectory_id)

    assert [segment.start_reason for segment in result.segments] == [
        "initial",
        "history_rewrite",
    ]
    assert result.metrics.counters["lineage/boundary_reason_history_rewrite"] == 1
    assert result.metrics.counters["lineage/history_rewrite_prior_context"] == 1
    assert "lineage/history_rewrite" not in result.metrics.counters
    incremental = prompt_mode == "incremental"
    assert result.segments[-1].turns[0].incremental_fallback_reason == ("history_rewrite" if incremental else None)
    assert result.metrics.counters.get("prompt_construction/incremental_fallback", 0) == int(incremental)


@pytest.mark.parametrize(
    ("messages", "detail_counter"),
    (
        (
            (
                {"role": "user", "content": "q"},
                {"role": "assistant", "content": "rewritten"},
                {"role": "user", "content": "b"},
            ),
            "lineage/history_rewrite_assistant_roundtrip",
        ),
        (
            ({"role": "user", "content": "q"},),
            "lineage/history_rewrite_truncated",
        ),
    ),
)
async def test_history_rewrite_detail_partitions_aggregate_counter(
    messages: Sequence[Mapping[str, Any]],
    detail_counter: str,
) -> None:
    sampler = FakeSampler(outputs=([197, 3], [198, 3]))
    engine = _engine(sampler)
    trajectory_id = engine.create_trajectory()
    await engine.complete(trajectory_id, _first_request())
    await engine.complete(trajectory_id, _request(messages))
    result = engine.finish(trajectory_id)

    assert result.metrics.counters["lineage/boundary_reason_history_rewrite"] == 1
    assert result.metrics.counters[detail_counter] == 1


async def test_length_turn_commits_and_forces_next_segment() -> None:
    sampler = FakeSampler(outputs=([197], [198, 3]), finishes=("length", "stop"))
    engine = _engine(sampler)
    trajectory_id = engine.create_trajectory()
    request = _first_request(max_tokens=1)
    first = await engine.complete(trajectory_id, request)
    continuation = _request(
        (*request.messages, first.response["choices"][0]["message"], {"role": "user", "content": "continue"})
    )
    await engine.complete(trajectory_id, continuation)
    result = engine.finish(trajectory_id)

    assert [segment.start_reason for segment in result.segments] == [
        "initial",
        "length_truncation",
    ]
    assert result.segments[0].closed_reason == "length_truncation"
    assert len(result.segments[0].turns[0].exact_completion_ids) == 1

    assert result.segments[1].turns[0].parent_turn_id == first.turn_id
    assert result.metrics.counters["lineage/boundary_reason_length_truncation"] == 1


async def test_sampler_cannot_exceed_effective_output_budget() -> None:
    sampler = FakeSampler(outputs=([197, 3],))
    engine = _engine(sampler)
    trajectory_id = engine.create_trajectory()
    with pytest.raises(TITOError) as exc_info:
        await engine.complete(trajectory_id, _first_request(max_tokens=1))
    assert exc_info.value.code == "tito_sdk_sampling_parse_error"
    assert exc_info.value.context["validation_error_code"] == "tito_completion_alignment_error"
    assert exc_info.value.discard_trajectory is True
    result = engine.finish(trajectory_id)
    assert result.status == "failed"
    assert not result.segments
    assert result.metrics.distributions["calls/sampler_wall_seconds"].count == 1


async def test_failed_sampler_call_still_records_sampler_wall_time() -> None:
    sampler = FakeSampler()

    async def fail(*args: Any, **kwargs: Any) -> SampledRequestResult:
        await asyncio.sleep(0)
        raise RuntimeError("upstream failed")

    sampler.sample_with_prompt_tokens_result = fail  # type: ignore[method-assign]
    engine = _engine(sampler)
    trajectory_id = engine.create_trajectory()
    with pytest.raises(TITOError, match="local TITO SDK operation failed"):
        await engine.complete(trajectory_id, _first_request())
    result = engine.finish(trajectory_id)
    assert result.metrics.distributions["calls/sampler_wall_seconds"].count == 1


async def test_debug_commit_failure_does_not_advance_policy_cursor() -> None:
    class FailCommitObserver:
        def record(self, event: str, *args: Any, **kwargs: Any) -> int:
            if event == "commit":
                raise OSError("commit storage failed")
            return 1

        def close_trajectory(self, *args: Any, **kwargs: Any) -> int:
            return 1

    sampler = FakeSampler()
    engine = _engine(sampler, observer=FailCommitObserver())
    trajectory_id = engine.create_trajectory()
    with pytest.raises(TITOError) as exc_info:
        await engine.complete(trajectory_id, _first_request(), idempotency_key="operation-1")
    assert exc_info.value.code == "tito_debug_storage_error"
    state = engine._state  # noqa: SLF001
    assert state is not None and state.trajectory_id == trajectory_id
    assert not state.segments and state.last_call is None
    assert state.calls[-1].outcome == "failed"


async def test_debug_commit_barrier_returns_committed_turn_after_raced_cancellation() -> None:
    class BlockingCommitObserver:
        def __init__(self) -> None:
            self.commit_started = threading.Event()
            self.release_commit = threading.Event()

        def record(self, event: str, *args: Any, **kwargs: Any) -> int:
            if event == "commit":
                self.commit_started.set()
                self.release_commit.wait(timeout=2)
            return 1

        def close_trajectory(self, *args: Any, **kwargs: Any) -> int:
            return 1

    observer = BlockingCommitObserver()
    engine = _engine(FakeSampler(), observer=observer)
    trajectory_id = engine.create_trajectory()
    call = asyncio.create_task(engine.complete(trajectory_id, _first_request()))
    assert await asyncio.to_thread(observer.commit_started.wait, 2)

    call.cancel()
    await asyncio.sleep(0)
    assert not call.done()
    observer.release_commit.set()

    committed = await call
    assert committed.turn_id is not None
    state = engine._state  # noqa: SLF001
    assert state is not None and state.trajectory_id == trajectory_id
    assert len(state.segments) == 1 and len(state.segments[0].turns) == 1
    assert state.calls[-1].outcome == "succeeded"
    engine.finish(trajectory_id)


async def test_call_is_registered_before_request_normalized_debug_write() -> None:
    class BlockingNormalizationObserver:
        def __init__(self) -> None:
            self.started = threading.Event()
            self.release = threading.Event()

        def record(self, event: str, *args: Any, **kwargs: Any) -> int:
            if event == "request_normalized":
                self.started.set()
                self.release.wait(timeout=2)
            return 1

        def close_trajectory(self, *args: Any, **kwargs: Any) -> int:
            return 1

    observer = BlockingNormalizationObserver()
    sampler = FakeSampler()
    engine = _engine(sampler, observer=observer)
    trajectory_id = engine.create_trajectory()
    call = asyncio.create_task(engine.complete(trajectory_id, _first_request()))
    assert await asyncio.to_thread(observer.started.wait, 2)

    terminal = asyncio.create_task(
        engine._cancel_and_terminalize(  # noqa: SLF001
            trajectory_id,
            "abandoned",
            "test_cancel",
        )
    )
    await asyncio.sleep(0)
    assert not terminal.done()
    observer.release.set()

    with pytest.raises(asyncio.CancelledError):
        await call
    tombstone = await terminal
    assert tombstone.status == "abandoned"
    assert sampler.calls == []


async def test_request_normalized_debug_failure_is_accounted_once() -> None:
    class FailingNormalizationObserver:
        def record(self, event: str, *args: Any, **kwargs: Any) -> int:
            if event == "request_normalized":
                raise OSError("normalization storage failed")
            return 1

        def close_trajectory(self, *args: Any, **kwargs: Any) -> int:
            return 1

    engine = _engine(FakeSampler(), observer=FailingNormalizationObserver())
    trajectory_id = engine.create_trajectory()

    with pytest.raises(TITOError) as exc_info:
        await engine.complete(trajectory_id, _first_request())

    assert exc_info.value.code == "tito_debug_storage_error"
    state = engine._state  # noqa: SLF001
    assert state is not None
    assert len(state.calls) == 1
    assert state.calls[0].outcome == "failed"
    assert state.calls[0].error_code == "tito_debug_storage_error"
    assert state.metrics.counters["calls/total"] == 1
    assert state.metrics.counters["calls/failed"] == 1
    assert not state.policy_lock.locked()
    assert not state.policy_in_flight


async def test_finish_async_rejects_late_calls_during_debug_close() -> None:
    class BlockingCloseObserver:
        def __init__(self) -> None:
            self.started = threading.Event()
            self.release = threading.Event()

        def record(self, *args: Any, **kwargs: Any) -> int:
            return 1

        def close_trajectory(self, *args: Any, **kwargs: Any) -> int:
            self.started.set()
            self.release.wait(timeout=2)
            return 1

    observer = BlockingCloseObserver()
    engine = _engine(FakeSampler(), observer=observer)
    trajectory_id = await engine.create_trajectory_async()
    await engine.complete(trajectory_id, _first_request())
    finishing = asyncio.create_task(engine.finish_async(trajectory_id))
    assert await asyncio.to_thread(observer.started.wait, 2)

    with pytest.raises(TITOError) as exc_info:
        await engine.complete(trajectory_id, _second_request())
    assert exc_info.value.code == "tito_trajectory_closed"
    observer.release.set()
    result = await finishing
    assert len(result.segments) == 1 and len(result.segments[0].turns) == 1


async def test_render_and_debug_barriers_do_not_block_the_event_loop() -> None:
    class SlowRenderer(FakeRenderer):
        def render_conversation_tokens(self, request: TITOChatRequest) -> Sequence[int]:
            time.sleep(0.03)
            return super().render_conversation_tokens(request)

    class SlowObserver:
        def record(self, *args: Any, **kwargs: Any) -> int:
            time.sleep(0.03)
            return 1

        def close_trajectory(self, *args: Any, **kwargs: Any) -> int:
            return 1

    engine = _engine(FakeSampler(), SlowRenderer(), observer=SlowObserver())

    async def run_trajectory() -> Any:
        trajectory_id = await engine.create_trajectory_async()
        await engine.complete(trajectory_id, _first_request())
        return await engine.finish_async(trajectory_id)

    call = asyncio.create_task(run_trajectory())
    loop_ticks = 0
    while not call.done():
        await asyncio.sleep(0.005)
        loop_ticks += 1

    result = await call
    assert loop_ticks >= 6
    assert result.metrics.distributions["renderer/render_queue_seconds"].count >= 1


async def test_full_render_time_is_observed_when_rendering_raises() -> None:
    class FailingRenderer(FakeRenderer):
        def render_conversation_tokens(self, request: TITOChatRequest) -> Sequence[int]:
            if len(request.messages) > 1:
                raise RuntimeError("full render failed")
            return super().render_conversation_tokens(request)

    engine = _engine(FakeSampler(outputs=([197, 3], [198, 3])), FailingRenderer())
    trajectory_id = engine.create_trajectory()
    await engine.complete(trajectory_id, _first_request())
    with pytest.raises(TITOError, match="local TITO SDK operation failed"):
        await engine.complete(trajectory_id, _second_request())
    result = engine.finish(trajectory_id)
    assert result.metrics.distributions["renderer/full_render_seconds"].count == 2


@pytest.mark.parametrize("kind", ["policy", "auxiliary"])
async def test_server_timing_and_retry_counts_are_observed_once_per_logical_request(kind: str) -> None:
    class TimedSampler(FakeSampler):
        async def sample_with_prompt_tokens_result(self, prompt_token_ids, **kwargs):
            result = await super().sample_with_prompt_tokens_result(prompt_token_ids, **kwargs)
            result.attempts = 2
            result.server_metrics = ServerMetrics(client_ttft=0.25, generation_duration=0.75)
            return result

    engine = _engine(TimedSampler(outputs=([197, 3],)), call_classifier=lambda _: (kind, "test"))
    trajectory_id = engine.create_trajectory()
    await engine.complete(trajectory_id, _first_request(), idempotency_key="same")
    if kind == "policy":
        replay = await engine.complete(trajectory_id, _first_request(), idempotency_key="same")
        assert replay.replayed
    metrics = engine.finish(trajectory_id).metrics
    assert metrics.counters["calls/model_requests"] == 1
    assert metrics.counters["calls/upstream_attempts"] == 2
    assert metrics.counters["calls/upstream_retry_attempts"] == 1
    assert metrics.counters["calls/upstream_completions"] == 1
    assert metrics.counters["calls/generated_tokens"] == 2
    assert metrics.distributions["server/generation_seconds"].count == 1
    assert metrics.distributions["server/generation_seconds"].sum == 0.75
    assert metrics.distributions["server/client_ttft_seconds"].count == 1
    assert metrics.distributions["server/client_ttft_seconds"].sum == 0.25


async def test_idempotency_replays_only_same_key_and_fingerprint() -> None:
    sampler = FakeSampler(outputs=([197, 3], [198, 3], [199, 3]))
    renderer = FakeRenderer()
    engine = _engine(sampler, renderer)
    trajectory_id = engine.create_trajectory()
    first = await engine.complete(trajectory_id, _first_request(), idempotency_key="operation-1")
    first.response["choices"][0]["message"]["content"] = "mutated by caller"
    replay = await engine.complete(trajectory_id, _first_request(), idempotency_key="operation-1")
    assert replay.replayed and replay.turn_id == first.turn_id and len(sampler.calls) == 1
    assert replay.response["choices"][0]["message"]["content"] == "a"
    assert renderer.render_calls == 2

    with pytest.raises(TITOError) as exc_info:
        await engine.complete(
            trajectory_id,
            _request(({"role": "user", "content": "changed"},)),
            idempotency_key="operation-1",
        )
    assert exc_info.value.code == "idempotency_key_reused"

    await engine.complete(trajectory_id, _first_request())
    result = engine.finish(trajectory_id)
    assert len(sampler.calls) == 2
    assert len(result.segments) == 2
    assert result.metrics.counters["calls/replayed"] == 1


async def test_incremental_idempotency_replays_the_committed_prompt() -> None:
    sampler = FakeSampler(outputs=([197, 3], [198, 3]))
    renderer = FakeIncrementalRenderer()
    engine = _engine(sampler, renderer, prompt_mode="incremental")
    trajectory_id = engine.create_trajectory()

    await engine.complete(trajectory_id, _first_request())
    second = await engine.complete(
        trajectory_id,
        _second_request(),
        idempotency_key="operation-2",
    )
    replay = await engine.complete(
        trajectory_id,
        _second_request(),
        idempotency_key="operation-2",
    )

    assert replay.replayed and replay.turn_id == second.turn_id
    assert len(sampler.calls) == 2
    assert renderer.render_calls == 1
    assert renderer.incremental_calls == 2


async def test_idempotency_rejects_semantically_equal_request_with_different_prompt() -> None:
    class OrderedWireRenderer(FakeRenderer):
        def render_conversation_tokens(self, request: TITOChatRequest) -> Sequence[int]:
            self.render_calls += 1
            wire = request.wire_value()
            assert wire is not None
            function = wire["tools"][0]["function"]
            return [1, *(100 + ord(key[0]) for key in function), 2]

    first_body = json.dumps(
        {
            "messages": [{"role": "user", "content": "q"}],
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "tool",
                        "description": "description",
                        "parameters": {"type": "object"},
                    },
                }
            ],
        }
    )
    reordered_body = json.dumps(
        {
            "messages": [{"role": "user", "content": "q"}],
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "description": "description",
                        "name": "tool",
                        "parameters": {"type": "object"},
                    },
                }
            ],
        }
    )
    first_request = TITOChatRequest.from_openai(
        json.loads(first_body),
        wire_request_body=first_body,
    )
    reordered_request = TITOChatRequest.from_openai(
        json.loads(reordered_body),
        wire_request_body=reordered_body,
    )
    assert first_request.canonical_value() == reordered_request.canonical_value()

    sampler = FakeSampler(outputs=([197, 3],))
    renderer = OrderedWireRenderer()
    engine = _engine(sampler, renderer)
    trajectory_id = engine.create_trajectory()
    await engine.complete(
        trajectory_id,
        first_request,
        idempotency_key="operation-1",
    )

    with pytest.raises(TITOError) as exc_info:
        await engine.complete(
            trajectory_id,
            reordered_request,
            idempotency_key="operation-1",
        )

    assert exc_info.value.code == "idempotency_key_reused"
    assert len(sampler.calls) == 1
    assert renderer.render_calls == 2


async def test_policy_overlap_waits_in_fifo_while_auxiliary_bypasses_guard() -> None:
    sampler = FakeSampler(outputs=([197, 3], [198, 3], [199, 3]))
    sampler.block = True

    def classifier(request: TITOChatRequest) -> str:
        return "auxiliary" if request.model == "aux" else "policy"

    engine = _engine(sampler, call_classifier=classifier)
    trajectory_id = engine.create_trajectory()
    first_policy = asyncio.create_task(engine.complete(trajectory_id, _first_request()))
    await sampler.started.wait()
    second_policy = asyncio.create_task(engine.complete(trajectory_id, _first_request()))
    await asyncio.sleep(0)
    assert not second_policy.done()
    assert len(sampler.calls) == 1

    auxiliary = asyncio.create_task(engine.complete(trajectory_id, _first_request(model="aux")))
    for _ in range(100):
        if len(sampler.calls) == 2:
            break
        await asyncio.sleep(0.001)
    assert len(sampler.calls) == 2
    sampler.release.set()
    await asyncio.gather(first_policy, second_policy, auxiliary)
    result = engine.finish(trajectory_id)
    assert len({call["prompt_cache_key"] for call in sampler.calls}) == 1
    assert len(result.segments) == 2
    assert sum(len(segment.turns) for segment in result.segments) == 2
    assert result.metrics.counters["queue/policy_waited"] == 1
    assert result.metrics.distributions["queue/policy_wait_seconds"].count == 1
    assert result.metrics.counters["calls/auxiliary"] == 1
    assert result.metrics.counters["calls/policy"] == 2
    assert result.metrics.counters["cache/affinity_reused"] == 2


async def test_cancelled_policy_fifo_waiter_never_samples_or_mutates_call_state() -> None:
    sampler = FakeSampler(outputs=([197, 3], [198, 3]))
    sampler.block = True
    engine = _engine(sampler)
    trajectory_id = engine.create_trajectory()
    first_policy = asyncio.create_task(engine.complete(trajectory_id, _first_request()))
    await sampler.started.wait()

    queued_policy = asyncio.create_task(engine.complete(trajectory_id, _first_request()))
    await asyncio.sleep(0)
    state = engine._state  # noqa: SLF001
    assert state is not None and state.trajectory_id == trajectory_id
    assert queued_policy in state.policy_waiters
    queued_policy.cancel()
    with pytest.raises(asyncio.CancelledError):
        await queued_policy
    assert not state.policy_waiters
    assert len(sampler.calls) == 1

    sampler.release.set()
    await first_policy
    result = engine.finish(trajectory_id)
    assert len(result.calls) == 1
    assert result.metrics.counters["calls/total"] == 1
    assert result.metrics.counters["queue/policy_waited"] == 1
    assert result.metrics.counters["queue/policy_wait_cancelled"] == 1
    assert result.metrics.distributions["queue/policy_wait_seconds"].count == 1


async def test_completion_only_r3_is_carried_without_lineage_logic() -> None:
    sampler = FakeSampler(outputs=([197, 3],))
    engine = _engine(sampler)
    trajectory_id = engine.create_trajectory()
    await engine.complete(
        trajectory_id,
        _first_request(sampling_fields={"include_routing_matrix": True}),
    )
    result = engine.finish(trajectory_id)
    turn = result.segments[0].turns[0]
    assert turn.routing_matrices == _top_sampling_refs(2)
    assert len(turn.routing_matrices) == len(turn.exact_completion_ids)


async def test_sidecar_sampling_defaults_override_provider_policy_and_strip_training_length() -> None:
    sampler = FakeSampler(outputs=([197, 3],))
    sidecar = TITOSidecar.from_deployment_sampler(
        sampler,  # type: ignore[arg-type]
        renderer=FakeRenderer(),
        max_context_tokens=256,
        max_output_tokens=32,
        sampling_defaults={
            "temperature": 0.7,
            "top_p": 1.0,
            "top_k": 0,
            "max_seq_len": 2048,
            "include_routing_matrix": True,
        },
    )
    await sidecar.start()
    trajectory = sidecar.create_trajectory()
    await sidecar._engine_for(trajectory.trajectory_id).complete(  # noqa: SLF001
        _first_request(
            temperature=0.2,
            sampling_fields={"top_p": 0.5},
        )
    )

    call = sampler.calls[0]
    assert call["temperature"] == 0.7
    assert call["top_p"] == 1.0
    assert call["top_k"] == 0
    assert call["logprobs"] is True
    assert call["include_routing_matrix"] is True
    assert "max_seq_len" not in call
    await sidecar.abandon_trajectory(trajectory.trajectory_id)
    await sidecar.close()


async def test_context_budget_rejects_before_inference() -> None:
    sampler = FakeSampler()
    engine = _TrajectoryCore(
        sampler,  # type: ignore[arg-type]
        FakeRenderer(),
        max_context_tokens=4,
        max_output_tokens=2,
    )
    trajectory_id = engine.create_trajectory()
    with pytest.raises(TITOError) as exc_info:
        await engine.complete(trajectory_id, _first_request())
    assert exc_info.value.code == "tito_context_overflow"
    assert sampler.calls == []


async def test_budget_cap_metrics_name_the_enforcing_limit() -> None:
    sidecar_sampler = FakeSampler(outputs=([197],))
    sidecar_engine = _TrajectoryCore(
        sidecar_sampler,  # type: ignore[arg-type]
        FakeRenderer(),
        max_context_tokens=32,
        max_output_tokens=1,
    )
    sidecar_id = sidecar_engine.create_trajectory()
    await sidecar_engine.complete(sidecar_id, _first_request(max_tokens=2))
    sidecar_result = sidecar_engine.finish(sidecar_id)

    context_sampler = FakeSampler(outputs=([197],))
    context_engine = _TrajectoryCore(
        context_sampler,  # type: ignore[arg-type]
        FakeRenderer(),
        max_context_tokens=6,
        max_output_tokens=2,
    )
    context_id = context_engine.create_trajectory()
    await context_engine.complete(context_id, _first_request(max_tokens=2))
    context_result = context_engine.finish(context_id)

    assert sidecar_result.metrics.counters["budget/output_capped_by_sidecar_limit"] == 1
    assert context_result.metrics.counters["budget/output_capped_by_context_limit"] == 1
    assert not any(
        name in {"budget/length_client_cap", "budget/length_context_cap"}
        for name in (*sidecar_result.metrics.counters, *context_result.metrics.counters)
    )


async def test_malformed_output_is_atomic_and_discards_trajectory() -> None:
    reject_sampler = FakeSampler()
    reject_engine = _engine(reject_sampler, FakeRenderer(fail_parse=True))
    rejected_id = reject_engine.create_trajectory()
    with pytest.raises(TITOError) as exc_info:
        await reject_engine.complete(rejected_id, _first_request())
    assert exc_info.value.code == "tito_sdk_parse_error"
    rejected = reject_engine.finish(rejected_id)
    assert rejected.segments == ()
    assert rejected.metrics.counters["parser/model_malformed"] == 1
    assert rejected.metrics.counters["calls/model_malformed"] == 1
    assert rejected.metrics.counters.get("calls/rejected", 0) == 0
    assert rejected.metrics.counters.get("calls/failed", 0) == 0
    assert rejected.calls[0].outcome == "model_malformed"
    _assert_call_accounting(rejected.metrics.counters)

    auxiliary_engine = _engine(
        FakeSampler(),
        FakeRenderer(fail_parse=True),
        call_classifier=lambda _request: ("auxiliary", "test_auxiliary"),
    )
    auxiliary_id = auxiliary_engine.create_trajectory()
    with pytest.raises(TITOError) as exc_info:
        await auxiliary_engine.complete(auxiliary_id, _first_request())
    assert exc_info.value.code == "tito_sdk_parse_error"
    auxiliary_rejected = auxiliary_engine.finish(auxiliary_id)
    assert auxiliary_rejected.metrics.counters["parser/model_malformed"] == 1
    assert auxiliary_rejected.metrics.counters["calls/model_malformed"] == 1
    assert auxiliary_rejected.metrics.counters.get("calls/rejected", 0) == 0
    assert auxiliary_rejected.metrics.counters.get("calls/failed", 0) == 0
    assert auxiliary_rejected.calls[0].outcome == "model_malformed"
    _assert_call_accounting(auxiliary_rejected.metrics.counters)


async def test_call_accounting_closes_over_replay_reject_failure_and_cancellation() -> None:
    replay_sampler = FakeSampler(outputs=([197, 3],))
    replay_engine = _engine(replay_sampler)
    replay_id = replay_engine.create_trajectory()
    await replay_engine.complete(replay_id, _first_request(), idempotency_key="same")
    await replay_engine.complete(replay_id, _first_request(), idempotency_key="same")
    with pytest.raises(TITOError):
        await replay_engine.complete(replay_id, _second_request(), idempotency_key="same")
    replay_result = replay_engine.finish(replay_id)
    _assert_call_accounting(replay_result.metrics.counters)
    assert replay_result.metrics.counters["calls/succeeded"] == 1
    assert replay_result.metrics.counters["calls/replayed"] == 1
    assert replay_result.metrics.counters["calls/rejected"] == 1

    class FailingSampler(FakeSampler):
        async def sample_with_prompt_tokens_result(
            self, prompt_token_ids: list[int], **kwargs: Any
        ) -> SampledRequestResult:
            self.calls.append({"prompt": tuple(prompt_token_ids), **kwargs})
            error = RuntimeError("upstream failed")
            error.attempts = 3
            raise error

    failing_engine = _engine(FailingSampler())
    failing_id = failing_engine.create_trajectory()
    with pytest.raises(TITOError, match="local TITO SDK operation failed"):
        await failing_engine.complete(failing_id, _first_request())
    failed = failing_engine.finish(failing_id)
    _assert_call_accounting(failed.metrics.counters)
    assert failed.metrics.counters["calls/failed"] == 1
    assert failed.calls[0].logical_request_id
    assert failed.calls[0].attempts == 3
    assert failed.metrics.counters["calls/model_requests"] == 1
    assert failed.metrics.counters["calls/upstream_attempts"] == 3
    assert failed.metrics.counters["calls/upstream_retry_attempts"] == 2
    assert not failed.metrics.counters.get("calls/upstream_completions")

    cancelled_sampler = FakeSampler()
    cancelled_sampler.block = True
    cancelled_engine = _engine(cancelled_sampler)
    cancelled_id = cancelled_engine.create_trajectory()
    task = asyncio.create_task(cancelled_engine.complete(cancelled_id, _first_request()))
    await cancelled_sampler.started.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    cancelled = cancelled_engine.finish(cancelled_id)
    _assert_call_accounting(cancelled.metrics.counters)
    assert cancelled.metrics.counters["calls/cancelled"] == 1
    assert cancelled.calls[0].logical_request_id
    assert cancelled.calls[0].attempts == 1


async def test_terminal_state_is_irreversible() -> None:
    engine = _engine(FakeSampler())
    trajectory_id = engine.create_trajectory()
    await engine.complete(trajectory_id, _first_request())
    engine.finish(trajectory_id)
    with pytest.raises(TITOError) as exc_info:
        await engine.complete(trajectory_id, _first_request())
    assert exc_info.value.status == 410
    tombstone = engine._tombstone  # noqa: SLF001
    assert tombstone is not None
    terminal_metrics = tombstone.metrics.snapshot()
    assert terminal_metrics.counters["admission/trajectory_closed"] == 1
    assert terminal_metrics.counters["calls/rejected"] == 1
    with pytest.raises(TITOError):
        engine.abandon(trajectory_id, "late cleanup")


async def test_sidecar_shutdown_abandons() -> None:
    engine = _engine(FakeSampler())
    engine.create_trajectory()
    await engine.close()

    tombstone = engine._tombstone  # noqa: SLF001
    assert tombstone is not None
    assert tombstone.status == "abandoned"


async def test_sidecar_shutdown_retires_every_trajectory_after_debug_close_failures() -> None:
    class FailCloseObserver:
        def __init__(self) -> None:
            self.close_calls: list[str] = []

        def record(self, *args: Any, **kwargs: Any) -> int:
            return 1

        def close_trajectory(self, trajectory_id: str, *args: Any, **kwargs: Any) -> int:
            self.close_calls.append(trajectory_id)
            raise OSError("debug close failed")

    observer = FailCloseObserver()
    sidecar = TITOSidecar.from_deployment_sampler(
        FakeSampler(),  # type: ignore[arg-type]
        renderer=FakeRenderer(),
        max_context_tokens=256,
        max_output_tokens=32,
        observer=observer,
    )
    await sidecar.start()
    trajectory_ids = [
        sidecar.create_trajectory().trajectory_id,
        sidecar.create_trajectory().trajectory_id,
    ]

    with pytest.raises(TITOError) as exc_info:
        await sidecar.close()

    assert exc_info.value.code == "tito_debug_storage_error"
    assert observer.close_calls == trajectory_ids
    assert all(
        sidecar._terminal_engines[trajectory_id]._core._tombstone.status  # noqa: SLF001
        == "abandoned"
        for trajectory_id in trajectory_ids
    )


async def test_sidecar_abandon_cancels_in_flight_policy_before_terminalization() -> None:
    sampler = FakeSampler()
    sampler.block = True
    sidecar = TITOSidecar.from_deployment_sampler(
        sampler,  # type: ignore[arg-type]
        renderer=FakeRenderer(),
        max_context_tokens=256,
        max_output_tokens=32,
    )
    await sidecar.start()
    trajectory = sidecar.create_trajectory()
    engine = sidecar._engine_for(trajectory.trajectory_id)  # noqa: SLF001
    call = asyncio.create_task(engine.complete(_first_request()))
    await sampler.started.wait()
    queued = asyncio.create_task(engine.complete(_first_request()))
    await asyncio.sleep(0)
    state = engine._core._state  # noqa: SLF001
    assert state is not None and queued in state.policy_waiters

    artifact = await sidecar.abandon_trajectory(trajectory.trajectory_id, "rollout_cancelled")

    with pytest.raises(asyncio.CancelledError):
        await call
    with pytest.raises(asyncio.CancelledError):
        await queued
    tombstone = engine._core._tombstone  # noqa: SLF001
    assert tombstone is not None
    assert tombstone.status == "abandoned"
    assert tombstone.reason == "rollout_cancelled"
    assert artifact.status == "abandoned"
    assert artifact.terminal_reason == "rollout_cancelled"
    assert trajectory.trajectory_id not in sidecar._engines  # noqa: SLF001
    assert trajectory.trajectory_id in sidecar._terminal_engines  # noqa: SLF001
    metrics = tombstone.metrics.snapshot()
    assert metrics.counters["calls/cancelled"] == 1
    assert engine._core._state is None  # noqa: SLF001
    await sidecar.close()


async def test_sidecar_freezes_backend_headers_and_forwards_distinct_affinity() -> None:
    source_headers = {"X-Custom": "original"}
    sampler = FakeSampler(outputs=([197, 3], [197, 3]), additional_headers=source_headers)
    sidecar = TITOSidecar.from_deployment_sampler(
        sampler,  # type: ignore[arg-type]
        renderer=FakeRenderer(),
        max_context_tokens=256,
        max_output_tokens=32,
    )
    await sidecar.start()
    left = sidecar.create_trajectory()
    right = sidecar.create_trajectory()
    left_engine = sidecar._engine_for(left.trajectory_id)  # noqa: SLF001
    right_engine = sidecar._engine_for(right.trajectory_id)  # noqa: SLF001
    sampler.block = True
    first = asyncio.create_task(left_engine.complete(_first_request()))
    await sampler.started.wait()
    source_headers["X-Custom"] = "rotated"
    sampler.additional_headers = {"X-Custom": "replaced"}
    sampler.release.set()
    await first
    await right_engine.complete(_first_request())

    assert sampler.calls[0]["additional_headers_snapshot"] == {"x-custom": "original"}
    assert sampler.calls[1]["additional_headers_snapshot"] == {"x-custom": "original"}
    assert sampler.calls[0]["prompt_cache_key"] != sampler.calls[1]["prompt_cache_key"]
    await sidecar.abandon_trajectory(left.trajectory_id)
    await sidecar.abandon_trajectory(right.trajectory_id)
    await sidecar.close()


async def test_four_same_prompt_rollout_members_are_independent_sampler_requests() -> None:
    sampler = FakeSampler(outputs=([197, 3],))
    sidecar = TITOSidecar.from_deployment_sampler(
        sampler,  # type: ignore[arg-type]
        renderer=FakeRenderer(),
        max_context_tokens=256,
        max_output_tokens=32,
    )
    await sidecar.start()
    members = [
        sidecar.create_trajectory(
            metadata={
                "rollout_group_id": "same-prompt-group",
                "rollout_member_index": index,
                "canonical_initial_prompt_hash": "same-prompt-hash",
            }
        )
        for index in range(4)
    ]

    results = await asyncio.gather(
        *(sidecar._engine_for(member.trajectory_id).complete(_first_request()) for member in members)  # noqa: SLF001
    )

    assert len(sampler.calls) == 4
    assert len({member.trajectory_id for member in members}) == 4
    assert len({id(sidecar._engine_for(member.trajectory_id)._core) for member in members}) == 4  # noqa: SLF001
    assert len({call["prompt_cache_key"] for call in sampler.calls}) == 4
    assert len({call["prompt"] for call in sampler.calls}) == 1
    assert len({result.call.logical_request_id for result in results}) == 4
    completed = [await sidecar.finish_trajectory(member.trajectory_id) for member in members]
    assert {result.metadata["rollout_member_index"] for result in completed} == set(range(4))
    assert {result.metadata["rollout_group_id"] for result in completed} == {"same-prompt-group"}
    await sidecar.close()


def test_sidecar_rejects_higher_precedence_fixed_affinity_header() -> None:
    sampler = FakeSampler(additional_headers={"X-Multi-Turn-Session-ID": "fixed"})
    with pytest.raises(ValueError, match="fixed affinity header"):
        TITOSidecar.from_deployment_sampler(
            sampler,  # type: ignore[arg-type]
            renderer=FakeRenderer(),
            max_context_tokens=256,
            max_output_tokens=32,
        )


@pytest.mark.parametrize("header", ["Authorization", "X-Api-Key", "X-Fireworks-Session-Id"])
def test_sidecar_rejects_custom_overrides_of_request_local_sdk_headers(header: str) -> None:
    sampler = FakeSampler(additional_headers={header: "fixed"})
    with pytest.raises(ValueError, match="request-local headers"):
        TITOSidecar.from_deployment_sampler(
            sampler,  # type: ignore[arg-type]
            renderer=FakeRenderer(),
            max_context_tokens=256,
            max_output_tokens=32,
        )


async def test_sidecar_ignores_affinity_header_added_after_construction() -> None:
    sampler = FakeSampler(additional_headers={"X-Custom": "original"})
    sidecar = TITOSidecar.from_deployment_sampler(
        sampler,  # type: ignore[arg-type]
        renderer=FakeRenderer(),
        max_context_tokens=256,
        max_output_tokens=32,
    )
    await sidecar.start()
    trajectory = sidecar.create_trajectory()
    sampler.additional_headers = {"X-Session-Affinity": "harness-owned"}

    await sidecar._engine_for(trajectory.trajectory_id).complete(_first_request())  # noqa: SLF001

    assert len(sampler.calls) == 1
    assert sampler.calls[0]["additional_headers_snapshot"] == {"x-custom": "original"}
    assert sampler.calls[0]["prompt_cache_key"] is not None
    await sidecar.abandon_trajectory(trajectory.trajectory_id)
    await sidecar.close()


async def test_request_affinity_override_is_rejected_and_counted() -> None:
    sampler = FakeSampler()
    engine = _engine(sampler)
    trajectory_id = engine.create_trajectory()

    with pytest.raises(TITOError) as exc_info:
        await engine.complete(
            trajectory_id,
            _first_request(sampling_fields={"prompt_cache_key": "harness-key"}),
        )
    assert exc_info.value.code == "tito_affinity_override"
    assert sampler.calls == []

    result = engine.finish(trajectory_id)
    assert result.metrics.counters["cache/affinity_conflict"] == 1
    assert result.metrics.counters["calls/rejected"] == 1
    _assert_call_accounting(result.metrics.counters)


def test_sidecar_rejects_affinity_in_sampling_defaults() -> None:
    with pytest.raises(ValueError, match="sidecar-owned fields"):
        _engine(
            FakeSampler(),
            sampling_defaults={"prompt_cache_key": "fixed-for-every-trajectory"},
        )


@pytest.mark.parametrize("field,value", [("max_seq_len", 4), ("n", 4), ("echo", True)])
async def test_request_cannot_override_sidecar_sampling_controls(field: str, value: Any) -> None:
    sampler = FakeSampler()
    engine = _engine(sampler)
    trajectory_id = engine.create_trajectory()

    with pytest.raises(TITOError) as exc_info:
        await engine.complete(
            trajectory_id,
            _first_request(sampling_fields={field: value}),
        )
    assert exc_info.value.code == "tito_invalid_sampling_field"
    assert sampler.calls == []
    result = engine.finish(trajectory_id)
    assert result.metrics.counters["calls/rejected"] == 1
    _assert_call_accounting(result.metrics.counters)


async def test_successful_same_key_replay_resolves_an_ambiguous_emission() -> None:
    sampler = FakeSampler(outputs=([197, 3],))
    engine = _engine(sampler)
    trajectory_id = engine.create_trajectory()

    first = await engine.complete(
        trajectory_id,
        _first_request(),
        idempotency_key="logical-operation",
    )
    assert first.turn_id is not None
    engine.record_response_emission(
        trajectory_id,
        first.turn_id,
        "ambiguous",
        wire_evidence={"transport": "test", "write": "interrupted"},
    )

    replay = await engine.complete(
        trajectory_id,
        _first_request(),
        idempotency_key="logical-operation",
    )
    assert replay.replayed and replay.turn_id == first.turn_id
    assert replay.turn_id is not None
    engine.record_response_emission(
        trajectory_id,
        replay.turn_id,
        "completed",
        wire_evidence={"transport": "test", "write": "complete"},
    )

    result = engine.finish(trajectory_id)
    assert len(sampler.calls) == 1
    assert [attempt.emission for attempt in result.response_attempts] == [
        "ambiguous",
        "completed",
    ]
    assert result.metrics.counters["transport/response_emission_ambiguous"] == 1
    assert result.metrics.counters["transport/response_emission_completed"] == 1
    assert result.metrics.counters["calls/succeeded"] == 1
    assert result.metrics.counters["calls/replayed"] == 1


def test_server_ttft_metric_uses_server_value_not_client_observation() -> None:
    engine = _engine(FakeSampler())
    trajectory_id = engine.create_trajectory()
    state = engine._state  # noqa: SLF001
    assert state is not None and state.trajectory_id == trajectory_id

    engine._observe_server_metrics(  # noqa: SLF001
        state,
        ServerMetrics(server_ttft=0.25, client_ttft=0.75),
    )

    metrics = state.metrics.snapshot().distributions
    assert metrics["server/upstream_ttft_seconds"].sum == 0.25


async def test_http_sse_same_key_replay_waits_for_transport_preparation() -> None:
    sampler = FakeSampler(outputs=([197, 3],))
    sidecar = TITOSidecar.from_deployment_sampler(
        sampler,  # type: ignore[arg-type]
        renderer=FakeRenderer(),
        max_context_tokens=256,
        max_output_tokens=32,
    )
    await sidecar.start()
    trajectory = sidecar.create_trajectory()
    assert trajectory.openai_base_url and trajectory.api_key
    headers = {
        "authorization": f"Bearer {trajectory.api_key}",
        "idempotency-key": "same-stream-operation",
    }
    body = {
        "model": "policy",
        "messages": [{"role": "user", "content": "q"}],
        "stream": True,
    }
    try:
        async with httpx.AsyncClient(timeout=2) as client:
            first = await client.post(
                f"{trajectory.openai_base_url}/chat/completions",
                headers=headers,
                json=body,
            )
            replay = await client.post(
                f"{trajectory.openai_base_url}/chat/completions",
                headers=headers,
                json=body,
            )
        assert first.status_code == 200
        assert replay.status_code == 200
        assert "data: [DONE]" in replay.text
        chunks = [
            json.loads(line.removeprefix("data: ")) for line in replay.text.splitlines() if line.startswith("data: {")
        ]
        assert chunks and all(chunk["created"] > 0 and chunk["model"] == "policy" for chunk in chunks)
        result = await sidecar.finish_trajectory(trajectory.trajectory_id)
        assert result.metrics.counters["calls/replayed"] == 1
        assert len(sampler.calls) == 1
    finally:
        await sidecar.close()


def _sse_data_chunks(text: str) -> list[dict[str, Any]]:
    return [json.loads(line.removeprefix("data: ")) for line in text.splitlines() if line.startswith("data: {")]


def _expected_usage(prompt_tokens: int) -> dict[str, Any]:
    # FakeSampler samples two tokens and reports all but two prompt tokens as cached.
    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": 2,
        "total_tokens": prompt_tokens + 2,
        "prompt_tokens_details": {"cached_tokens": prompt_tokens - 2},
    }


@pytest.mark.parametrize("kind", ["policy", "auxiliary"])
async def test_http_json_response_reports_exact_token_usage(kind: str) -> None:
    sampler = FakeSampler(outputs=([197, 3],))
    sidecar = TITOSidecar.from_deployment_sampler(
        sampler,  # type: ignore[arg-type]
        renderer=FakeRenderer(),
        max_context_tokens=256,
        max_output_tokens=32,
        call_classifier=((lambda _request: ("auxiliary", "test_auxiliary")) if kind == "auxiliary" else None),
    )
    await sidecar.start()
    trajectory = sidecar.create_trajectory()
    assert trajectory.openai_base_url and trajectory.api_key
    try:
        async with httpx.AsyncClient(timeout=2) as client:
            response = await client.post(
                f"{trajectory.openai_base_url}/chat/completions",
                headers={"authorization": f"Bearer {trajectory.api_key}"},
                json={"model": "policy", "messages": [{"role": "user", "content": "q"}]},
            )
        assert response.status_code == 200
        assert response.json()["usage"] == _expected_usage(len(sampler.calls[0]["prompt"]))
    finally:
        await sidecar.close()


async def test_http_sse_include_usage_streams_final_usage_chunk() -> None:
    sampler = FakeSampler(outputs=([197, 3],))
    sidecar = TITOSidecar.from_deployment_sampler(
        sampler,  # type: ignore[arg-type]
        renderer=FakeRenderer(),
        max_context_tokens=256,
        max_output_tokens=32,
    )
    await sidecar.start()
    trajectory = sidecar.create_trajectory()
    assert trajectory.openai_base_url and trajectory.api_key
    headers = {
        "authorization": f"Bearer {trajectory.api_key}",
        "idempotency-key": "usage-stream-operation",
    }
    body = {
        "model": "policy",
        "messages": [{"role": "user", "content": "q"}],
        "stream": True,
        "stream_options": {"include_usage": True},
    }
    try:
        async with httpx.AsyncClient(timeout=2) as client:
            first = await client.post(f"{trajectory.openai_base_url}/chat/completions", headers=headers, json=body)
            replay = await client.post(f"{trajectory.openai_base_url}/chat/completions", headers=headers, json=body)
        assert len(sampler.calls) == 1
        for response in (first, replay):
            assert response.status_code == 200
            assert response.text.rstrip().endswith("data: [DONE]")
            delta, terminal, usage = _sse_data_chunks(response.text)
            assert delta["usage"] is None
            assert terminal["usage"] is None
            assert terminal["choices"][0]["finish_reason"] == "stop"
            assert usage["id"] == delta["id"]
            assert usage["object"] == "chat.completion.chunk"
            assert usage["choices"] == []
            assert usage["usage"] == _expected_usage(len(sampler.calls[0]["prompt"]))
    finally:
        await sidecar.close()


@pytest.mark.parametrize(
    "stream_options",
    [{}, {"stream_options": None}, {"stream_options": {}}, {"stream_options": {"include_usage": False}}],
)
async def test_http_sse_omits_usage_unless_requested(stream_options: dict[str, Any]) -> None:
    sampler = FakeSampler(outputs=([197, 3],))
    sidecar = TITOSidecar.from_deployment_sampler(
        sampler,  # type: ignore[arg-type]
        renderer=FakeRenderer(),
        max_context_tokens=256,
        max_output_tokens=32,
    )
    await sidecar.start()
    trajectory = sidecar.create_trajectory()
    assert trajectory.openai_base_url and trajectory.api_key
    try:
        async with httpx.AsyncClient(timeout=2) as client:
            response = await client.post(
                f"{trajectory.openai_base_url}/chat/completions",
                headers={"authorization": f"Bearer {trajectory.api_key}"},
                json={
                    "model": "policy",
                    "messages": [{"role": "user", "content": "q"}],
                    "stream": True,
                    **stream_options,
                },
            )
        assert response.status_code == 200
        chunks = _sse_data_chunks(response.text)
        assert len(chunks) == 2
        assert all("usage" not in chunk for chunk in chunks)
    finally:
        await sidecar.close()


@pytest.mark.parametrize(
    ("server_metrics", "details"),
    [
        (None, None),
        (ServerMetrics(), None),
        (ServerMetrics(cached_prompt_tokens=0), {"cached_tokens": 0}),
        (ServerMetrics(cached_prompt_tokens=3), {"cached_tokens": 3}),
        (ServerMetrics(cached_prompt_tokens=6), None),
        (ServerMetrics(cached_prompt_tokens=-1), None),
    ],
)
def test_usage_reports_cached_prompt_tokens_only_within_prompt(
    server_metrics: ServerMetrics | None,
    details: dict[str, int] | None,
) -> None:
    usage = _TrajectoryCore._usage(  # noqa: SLF001
        prompt_tokens=5,
        completion_tokens=2,
        server_metrics=server_metrics,
    )
    assert usage["total_tokens"] == 7
    assert usage.get("prompt_tokens_details") == details


@pytest.mark.parametrize("kind", ["policy", "auxiliary"])
async def test_http_sse_rejects_sampling_admission_before_committing_200(
    kind: str,
) -> None:
    sampler = FakeSampler(outputs=([197, 3],))
    sidecar = TITOSidecar.from_deployment_sampler(
        sampler,  # type: ignore[arg-type]
        renderer=FakeRenderer(),
        max_context_tokens=256,
        max_output_tokens=32,
        call_classifier=((lambda _request: ("auxiliary", "test_auxiliary")) if kind == "auxiliary" else None),
    )
    await sidecar.start()
    trajectory = sidecar.create_trajectory()
    assert trajectory.openai_base_url and trajectory.api_key
    try:
        async with httpx.AsyncClient(timeout=2) as client:
            response = await client.post(
                f"{trajectory.openai_base_url}/chat/completions",
                headers={"authorization": f"Bearer {trajectory.api_key}"},
                json={
                    "model": "policy",
                    "messages": [{"role": "user", "content": "q"}],
                    "stream": True,
                    "user": "harness-owned-affinity",
                },
            )
        assert response.status_code == 400
        assert response.headers["content-type"].startswith("application/json")
        assert response.headers["x-should-retry"] == "false"
        assert response.json()["error"]["code"] == "tito_affinity_override"
        assert sampler.calls == []
        result = await sidecar.finish_trajectory(trajectory.trajectory_id)
        assert result.metrics.counters["calls/rejected"] == 1
        _assert_call_accounting(result.metrics.counters)
    finally:
        await sidecar.close()


async def test_http_sidecar_binds_and_advertises_loopback_only() -> None:
    sidecar = TITOSidecar.from_deployment_sampler(
        FakeSampler(outputs=([197, 3],)),  # type: ignore[arg-type]
        renderer=FakeRenderer(),
        max_context_tokens=256,
        max_output_tokens=32,
    )
    await sidecar.start()
    try:
        trajectory = sidecar.create_trajectory()
        assert trajectory.openai_base_url is not None
        assert trajectory.openai_base_url.startswith("http://127.0.0.1:")
    finally:
        await sidecar.close()


async def test_evicted_trajectory_id_gets_a_fresh_credential(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from fireworks.training.sdk.tito import _sidecar as sidecar_module

    monkeypatch.setattr(sidecar_module, "_TERMINAL_ENGINE_LIMIT", 1)
    sidecar = TITOSidecar.from_deployment_sampler(
        FakeSampler(),  # type: ignore[arg-type]
        renderer=FakeRenderer(),
        max_context_tokens=256,
        max_output_tokens=32,
    )
    await sidecar.start()
    try:
        first = sidecar.create_trajectory(trajectory_id="reused")
        await sidecar.abandon_trajectory(first.trajectory_id)
        evictor = sidecar.create_trajectory(trajectory_id="evictor")
        await sidecar.abandon_trajectory(evictor.trajectory_id)

        replacement = sidecar.create_trajectory(trajectory_id="reused")
        assert replacement.api_key != first.api_key
        async with httpx.AsyncClient(timeout=2) as client:
            stale = await client.get(
                f"{replacement.openai_base_url}/models",
                headers={"authorization": f"Bearer {first.api_key}"},
            )
            current = await client.get(
                f"{replacement.openai_base_url}/models",
                headers={"authorization": f"Bearer {replacement.api_key}"},
            )
        assert stale.status_code == 401
        assert current.status_code == 200
    finally:
        await sidecar.close()


async def test_http_conflicts_and_terminal_state_are_explicitly_non_retryable() -> None:
    sampler = FakeSampler(outputs=([197, 3], [197, 3]))
    sidecar = TITOSidecar.from_deployment_sampler(
        sampler,  # type: ignore[arg-type]
        renderer=FakeRenderer(),
        max_context_tokens=256,
        max_output_tokens=32,
    )
    await sidecar.start()
    headers: dict[str, str]

    try:
        replay_trajectory = sidecar.create_trajectory()
        assert replay_trajectory.openai_base_url and replay_trajectory.api_key
        headers = {
            "authorization": f"Bearer {replay_trajectory.api_key}",
            "idempotency-key": "same-operation",
        }
        async with httpx.AsyncClient(timeout=2) as client:
            first = await client.post(
                f"{replay_trajectory.openai_base_url}/chat/completions",
                headers=headers,
                json={
                    "model": "policy",
                    "messages": [{"role": "user", "content": "q"}],
                },
            )
            assert first.status_code == 200
            reused = await client.post(
                f"{replay_trajectory.openai_base_url}/chat/completions",
                headers=headers,
                json={
                    "model": "policy",
                    "messages": [{"role": "user", "content": "changed"}],
                },
            )
            assert reused.status_code == 409
            assert reused.headers["x-should-retry"] == "false"
            assert reused.json()["error"]["code"] == "idempotency_key_reused"

            await sidecar.finish_trajectory(replay_trajectory.trajectory_id)
            terminal = await client.post(
                f"{replay_trajectory.openai_base_url}/chat/completions",
                headers=headers,
                json={
                    "model": "policy",
                    "messages": [{"role": "user", "content": "q"}],
                },
            )
            assert terminal.status_code == 410
            assert terminal.headers["x-should-retry"] == "false"
            assert terminal.json()["error"]["code"] == "tito_trajectory_closed"

            lineage_trajectory = sidecar.create_trajectory(
                drift_policy=TrajectoryDriftPolicy(
                    max_masked_tokens=0,
                    on_other_mismatch="reject",
                )
            )
            assert lineage_trajectory.openai_base_url and lineage_trajectory.api_key
            lineage_headers = {"authorization": f"Bearer {lineage_trajectory.api_key}"}
            accepted = await client.post(
                f"{lineage_trajectory.openai_base_url}/chat/completions",
                headers=lineage_headers,
                json={
                    "model": "policy",
                    "messages": [{"role": "user", "content": "q"}],
                },
            )
            assert accepted.status_code == 200
            divergent = await client.post(
                f"{lineage_trajectory.openai_base_url}/chat/completions",
                headers=lineage_headers,
                json={
                    "model": "policy",
                    "messages": [
                        {"role": "user", "content": "different"},
                        {"role": "assistant", "content": "a"},
                        {"role": "user", "content": "next"},
                    ],
                },
            )
            assert divergent.status_code == 409
            assert divergent.headers["x-should-retry"] == "false"
            assert divergent.json()["error"]["code"] == "tito_lineage_divergence"
            await sidecar.finish_trajectory(lineage_trajectory.trajectory_id)
    finally:
        await sidecar.close()

    blocked_sampler = FakeSampler(outputs=([197, 3], [198, 3]))
    blocked_sampler.block = True
    blocked_sidecar = TITOSidecar.from_deployment_sampler(
        blocked_sampler,  # type: ignore[arg-type]
        renderer=FakeRenderer(),
        max_context_tokens=256,
        max_output_tokens=32,
    )
    await blocked_sidecar.start()
    blocked_trajectory = blocked_sidecar.create_trajectory()
    assert blocked_trajectory.openai_base_url and blocked_trajectory.api_key
    blocked_headers = {"authorization": f"Bearer {blocked_trajectory.api_key}"}
    try:
        async with httpx.AsyncClient(timeout=2) as client:
            in_flight = asyncio.create_task(
                client.post(
                    f"{blocked_trajectory.openai_base_url}/chat/completions",
                    headers=blocked_headers,
                    json={
                        "model": "policy",
                        "messages": [{"role": "user", "content": "q"}],
                    },
                )
            )
            await blocked_sampler.started.wait()
            queued = asyncio.create_task(
                client.post(
                    f"{blocked_trajectory.openai_base_url}/chat/completions",
                    headers=blocked_headers,
                    json={
                        "model": "policy",
                        "messages": [{"role": "user", "content": "q"}],
                    },
                )
            )
            await asyncio.sleep(0.01)
            assert not queued.done()
            assert len(blocked_sampler.calls) == 1
            blocked_sampler.release.set()
            assert (await in_flight).status_code == 200
            assert (await queued).status_code == 200
        await blocked_sidecar.finish_trajectory(blocked_trajectory.trajectory_id)
    finally:
        await blocked_sidecar.close()


async def test_sidecar_abandon_waits_for_post_commit_http_disconnect(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from aiohttp import web

    write_started = asyncio.Event()
    original_write = web.StreamResponse.write

    async def block_committed_response(
        response: web.StreamResponse,
        data: bytes,
    ) -> None:
        if b'"choices"' in data:
            write_started.set()
            await asyncio.Future()
        await original_write(response, data)

    monkeypatch.setattr(web.StreamResponse, "write", block_committed_response)
    sidecar = TITOSidecar.from_deployment_sampler(
        FakeSampler(outputs=([197, 3],)),  # type: ignore[arg-type]
        renderer=FakeRenderer(),
        max_context_tokens=256,
        max_output_tokens=32,
    )
    await sidecar.start()
    trajectory = sidecar.create_trajectory()
    assert trajectory.openai_base_url and trajectory.api_key
    headers = {"authorization": f"Bearer {trajectory.api_key}"}

    try:
        async with httpx.AsyncClient(timeout=2) as client:
            request = asyncio.create_task(
                client.post(
                    f"{trajectory.openai_base_url}/chat/completions",
                    headers=headers,
                    json={
                        "model": "policy",
                        "messages": [{"role": "user", "content": "q"}],
                    },
                )
            )
            await asyncio.wait_for(write_started.wait(), timeout=1)
            await sidecar.abandon_trajectory(trajectory.trajectory_id, "client_disconnected_after_commit")
            await asyncio.wait_for(
                asyncio.gather(request, return_exceptions=True),
                timeout=1,
            )

        engine = sidecar._engine_for(trajectory.trajectory_id)  # noqa: SLF001
        tombstone = engine._core._tombstone  # noqa: SLF001
        assert tombstone is not None
        metrics = tombstone.metrics.snapshot().counters
        assert tombstone.status == "abandoned"
        assert metrics["calls/succeeded"] == 1
        assert metrics["transport/response_emission_ambiguous"] == 1
        assert engine._core._state is None  # noqa: SLF001
    finally:
        await sidecar.close()


async def test_stream_handler_cancellation_before_preparation_cancels_sampler_task() -> None:
    outcomes: list[str | None] = []
    sidecar = TITOSidecar.from_deployment_sampler(
        FakeSampler(outputs=([197, 3],)),  # type: ignore[arg-type]
        renderer=FakeRenderer(),
        max_context_tokens=256,
        max_output_tokens=32,
        on_chat_outcome=outcomes.append,
    )
    await sidecar.start()
    trajectory = sidecar.create_trajectory()
    engine = sidecar._engine_for(trajectory.trajectory_id)  # noqa: SLF001
    completion_started = asyncio.Event()
    completion_cancelled = asyncio.Event()

    async def blocked_complete(*_args: Any, **_kwargs: Any) -> Any:
        completion_started.set()
        try:
            await asyncio.Future()
        finally:
            completion_cancelled.set()

    engine.complete = blocked_complete  # type: ignore[method-assign]

    class Request:
        headers = {"authorization": f"Bearer {trajectory.api_key}"}
        match_info = {"trajectory_id": trajectory.trajectory_id}

        @staticmethod
        async def read() -> bytes:
            return json.dumps(
                {
                    "model": "policy",
                    "messages": [{"role": "user", "content": "q"}],
                    "stream": True,
                }
            ).encode()

    handler = asyncio.create_task(sidecar._handle_openai_chat(Request()))  # noqa: SLF001
    await completion_started.wait()
    handler.cancel()
    with pytest.raises(asyncio.CancelledError):
        await handler
    await asyncio.wait_for(completion_cancelled.wait(), timeout=1)
    assert outcomes == []
    assert not engine._core._state.calls  # noqa: SLF001
    await sidecar.close()


async def test_non_stream_unexpected_write_failure_records_ambiguous_emission(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from aiohttp import web

    async def fail_prepare(*_args: Any, **_kwargs: Any) -> None:
        raise RuntimeError("unexpected transport failure")

    monkeypatch.setattr(web.StreamResponse, "prepare", fail_prepare)
    sidecar = TITOSidecar.from_deployment_sampler(
        FakeSampler(outputs=([197, 3],)),  # type: ignore[arg-type]
        renderer=FakeRenderer(),
        max_context_tokens=256,
        max_output_tokens=32,
    )
    await sidecar.start()
    trajectory = sidecar.create_trajectory()

    class Request:
        headers = {"authorization": f"Bearer {trajectory.api_key}"}
        match_info = {"trajectory_id": trajectory.trajectory_id}

        @staticmethod
        async def read() -> bytes:
            return json.dumps(
                {
                    "model": "policy",
                    "messages": [{"role": "user", "content": "q"}],
                }
            ).encode()

    try:
        handler = asyncio.create_task(
            sidecar._handle_openai_chat(Request())  # noqa: SLF001
        )
        with pytest.raises(RuntimeError, match="unexpected transport failure"):
            await handler
        await asyncio.sleep(0)
        result = await sidecar.finish_trajectory(trajectory.trajectory_id)
        assert result.metrics.counters["calls/succeeded"] == 1
        assert result.metrics.counters["transport/response_emission_ambiguous"] == 1
    finally:
        await sidecar.close()


async def test_stream_disconnect_during_commit_records_the_raced_turn_as_ambiguous(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from aiohttp import web

    class BlockingCommitObserver:
        def __init__(self) -> None:
            self.started = threading.Event()
            self.release = threading.Event()

        def record(self, event: str, *args: Any, **kwargs: Any) -> int:
            if event == "commit":
                self.started.set()
                self.release.wait(timeout=2)
            return 1

        def close_trajectory(self, *args: Any, **kwargs: Any) -> int:
            return 1

    observer = BlockingCommitObserver()
    original_write = web.StreamResponse.write

    async def disconnect_on_keepalive(response: web.StreamResponse, data: bytes) -> None:
        if data == b": keepalive\n\n" and observer.started.is_set():
            observer.release.set()
            raise ConnectionResetError("client disconnected during commit")
        await original_write(response, data)

    monkeypatch.setattr(web.StreamResponse, "write", disconnect_on_keepalive)
    sidecar = TITOSidecar.from_deployment_sampler(
        FakeSampler(outputs=([197, 3],)),  # type: ignore[arg-type]
        renderer=FakeRenderer(),
        max_context_tokens=256,
        max_output_tokens=32,
        observer=observer,
        keepalive_seconds=0.01,
    )
    await sidecar.start()
    trajectory = sidecar.create_trajectory()
    assert trajectory.openai_base_url and trajectory.api_key

    try:
        async with httpx.AsyncClient(timeout=2) as client:
            await client.post(
                f"{trajectory.openai_base_url}/chat/completions",
                headers={"authorization": f"Bearer {trajectory.api_key}"},
                json={
                    "model": "policy",
                    "messages": [{"role": "user", "content": "q"}],
                    "stream": True,
                },
            )
        result = await sidecar.finish_trajectory(trajectory.trajectory_id)
        assert len(result.segments) == 1
        assert len(result.segments[0].turns) == 1
        assert result.metrics.counters["calls/succeeded"] == 1
        assert result.metrics.counters["transport/response_emission_ambiguous"] == 1
    finally:
        observer.release.set()
        await sidecar.close()


async def test_http_sidecar_buffers_content_and_sends_keepalive() -> None:
    sampler = FakeSampler(outputs=([197, 3],))
    sampler.block = True
    sidecar = TITOSidecar.from_deployment_sampler(
        sampler,  # type: ignore[arg-type]
        renderer=FakeRenderer(),
        max_context_tokens=256,
        max_output_tokens=32,
        keepalive_seconds=0.01,
    )
    await sidecar.start()
    trajectory = sidecar.create_trajectory()
    assert trajectory.openai_base_url and trajectory.api_key

    async with httpx.AsyncClient(timeout=2) as client:
        async with client.stream(
            "POST",
            f"{trajectory.openai_base_url}/chat/completions",
            headers={"authorization": f"Bearer {trajectory.api_key}"},
            json={
                "model": "policy",
                "messages": [{"role": "user", "content": "q"}],
                "stream": True,
            },
        ) as response:
            iterator = response.aiter_lines()
            first_line = await iterator.__anext__()
            assert first_line == ": keepalive"
            sampler.release.set()
            remaining = [line async for line in iterator]
            assert any(line.startswith("data: {") for line in remaining)
            assert "data: [DONE]" in remaining

    result = await sidecar.finish_trajectory(trajectory.trajectory_id)
    assert result.metrics.counters["transport/keepalives_sent"] >= 1
    assert result.metrics.counters["transport/response_emission_completed"] == 1
    await sidecar.close()


@pytest.mark.parametrize("stream", [False, True])
async def test_chat_outcome_reports_pre_header_overflow_and_success(stream: bool) -> None:
    outcomes: list[str | None] = []
    renderer = FakeRenderer()

    class LegacySidecar(TITOSidecar):
        # Older Cookbook bundles still override and call this private route.
        async def _handle_openai_chat(self, request: Any) -> Any:
            response = await super()._handle_openai_chat(request)
            assert outcomes[-1] == response.headers.get("x-fireworks-error-code")
            return response

    sidecar = LegacySidecar.from_deployment_sampler(
        FakeSampler(outputs=([197, 3], [198, 3])),  # type: ignore[arg-type]
        renderer=renderer,
        max_context_tokens=32,
        max_output_tokens=8,
        on_chat_outcome=outcomes.append,
    )
    await sidecar.start()
    try:
        trajectory = sidecar.create_trajectory()
        assert trajectory.openai_base_url and trajectory.api_key
        headers = {"authorization": f"Bearer {trajectory.api_key}"}
        async with httpx.AsyncClient(timeout=2) as client:
            overflow = await client.post(
                f"{trajectory.openai_base_url}/chat/completions",
                headers=headers,
                json={"model": "policy", "messages": [{"role": "user", "content": "q" * 60}], "stream": stream},
            )
            assert overflow.headers["x-fireworks-error-code"] == "tito_context_overflow"
            success = await client.post(
                f"{trajectory.openai_base_url}/chat/completions",
                headers=headers,
                json={"model": "policy", "messages": [{"role": "user", "content": "q"}], "stream": stream},
            )
            assert success.status_code == 200
            models = await client.get(f"{trajectory.openai_base_url}/models", headers=headers)
            assert models.status_code == 200
            assert outcomes == ["tito_context_overflow", None]
            if stream:
                renderer.fail_parse = True
                malformed = await client.post(
                    f"{trajectory.openai_base_url}/chat/completions",
                    headers=headers,
                    json={"model": "policy", "messages": [{"role": "user", "content": "p"}], "stream": True},
                )
                assert malformed.status_code == 200
                assert "tito_sdk_parse_error" in malformed.text
                assert outcomes == ["tito_context_overflow", None, None]
    finally:
        await sidecar.close()


async def test_http_sidecar_scopes_models_and_chat_routes_to_one_trajectory() -> None:
    sampler = FakeSampler(outputs=([197, 3],))
    sidecar = TITOSidecar.from_deployment_sampler(
        sampler,  # type: ignore[arg-type]
        renderer=FakeRenderer(),
        max_context_tokens=256,
        max_output_tokens=32,
    )
    await sidecar.start()
    trajectory = sidecar.create_trajectory()
    assert trajectory.openai_base_url and trajectory.api_key
    headers = {"authorization": f"Bearer {trajectory.api_key}"}

    async with httpx.AsyncClient(timeout=2) as client:
        models = await client.get(f"{trajectory.openai_base_url}/models", headers=headers)
        assert models.status_code == 200
        assert {item["id"] for item in models.json()["data"]} >= {"policy"}

        invalid = await client.post(
            f"{trajectory.openai_base_url}/chat/completions",
            headers=headers,
            json={"model": "policy", "messages": []},
        )
        assert invalid.status_code == 400

        response = await client.post(
            f"{trajectory.openai_base_url}/chat/completions",
            headers=headers,
            json={
                "model": "policy",
                "messages": [{"role": "user", "content": "q"}],
            },
        )
        assert response.status_code == 200

    result = await sidecar.finish_trajectory(trajectory.trajectory_id)
    assert result.metrics.counters["admission/normalization_reject"] == 1
    assert result.metrics.counters["calls/total"] == 2
    await sidecar.close()


async def test_http_debug_preserves_wire_and_canonical_request_forms(tmp_path) -> None:
    sink = TITOLocalDebugSink(
        TITOLocalDebugConfig(
            root_dir=tmp_path.resolve(),
            run_id="wire-provenance",
            max_local_bytes=20_000_000,
            min_free_bytes=0,
        )
    )
    sidecar = TITOSidecar.from_deployment_sampler(
        FakeSampler(outputs=([197, 3],)),  # type: ignore[arg-type]
        renderer=FakeRenderer(),
        max_context_tokens=256,
        max_output_tokens=32,
        observer=sink,
    )
    await sidecar.start()
    trajectory = sidecar.create_trajectory()
    assert trajectory.openai_base_url and trajectory.api_key
    body = (
        '{ "model": "policy", "messages": [{"role":"assistant",'
        '"content":null,"tool_calls":[{"type":"function",'
        '"function":{"name":"run","arguments":"{\\"z\\": 1}"}}]}] }'
    )
    try:
        async with httpx.AsyncClient(timeout=2) as client:
            malformed = await client.post(
                f"{trajectory.openai_base_url}/chat/completions",
                headers={
                    "authorization": f"Bearer {trajectory.api_key}",
                    "content-type": "application/json",
                },
                content='{"messages":',
            )
            assert malformed.status_code == 400
            response = await client.post(
                f"{trajectory.openai_base_url}/chat/completions",
                headers={
                    "authorization": f"Bearer {trajectory.api_key}",
                    "content-type": "application/json",
                },
                content=body,
            )
        assert response.status_code == 200
        await sidecar.finish_trajectory(trajectory.trajectory_id)
    finally:
        await sidecar.close()
        sink.close()

    event = next(
        frame["payload"]
        for frame in _debug_events(sink, trajectory.trajectory_id)
        if frame["event"] == "request_normalized"
    )
    assert event["wire_request_body"] == body
    assert event["wire_request"]["messages"][0]["content"] is None
    assert event["canonical_request"]["messages"][0]["content"] == ""
    assert event["normalization_steps"] == [
        "messages[0].content:null_to_empty",
        "messages[0].tool_calls[0].function.arguments:canonical_json",
    ]
    rejected = next(
        frame["payload"]
        for frame in _debug_events(sink, trajectory.trajectory_id)
        if frame["event"] == "request_rejected"
    )
    assert rejected["phase"] == "normalization"
    assert rejected["error"]["type"] == "JSONDecodeError"
    assert rejected["wire_request_body"] == '{"messages":'


async def test_http_sidecar_identifies_unexpected_sdk_failure_without_retrying() -> None:
    sampler = FakeSampler()

    async def fail(*args: Any, **kwargs: Any) -> SampledRequestResult:
        raise RuntimeError("sensitive upstream detail")

    sampler.sample_with_prompt_tokens_result = fail  # type: ignore[method-assign]
    sidecar = TITOSidecar.from_deployment_sampler(
        sampler,  # type: ignore[arg-type]
        renderer=FakeRenderer(),
        max_context_tokens=256,
        max_output_tokens=32,
    )
    await sidecar.start()
    trajectory = sidecar.create_trajectory()
    assert trajectory.openai_base_url and trajectory.api_key
    try:
        async with httpx.AsyncClient(timeout=2) as client:
            response = await client.post(
                f"{trajectory.openai_base_url}/chat/completions",
                headers={"authorization": f"Bearer {trajectory.api_key}"},
                json={
                    "model": "policy",
                    "messages": [{"role": "user", "content": "q"}],
                },
            )
        assert response.status_code == 500
        assert response.headers["x-should-retry"] == "false"
        assert response.json()["error"]["code"] == "tito_sdk_internal_error"
        assert "sensitive upstream detail" not in response.text
        result = await sidecar.finish_trajectory(trajectory.trajectory_id)
        assert result.metrics.counters["calls/failed"] == 1
        assert not result.segments
    finally:
        await sidecar.close()


async def test_local_debug_sink_writes_searchable_events_and_exact_arrays(tmp_path) -> None:
    sink = TITOLocalDebugSink(
        TITOLocalDebugConfig(
            root_dir=tmp_path.resolve(),
            run_id="contract-test",
            max_local_bytes=20_000_000,
            min_free_bytes=0,
        )
    )
    sampler = FakeSampler(outputs=([197, 3], [198, 3]))
    engine = _engine(sampler, observer=sink)
    trajectory_id = engine.create_trajectory()
    await engine.complete(trajectory_id, _first_request())
    await engine.complete(trajectory_id, _second_request())
    result = engine.finish(trajectory_id)
    sink.close()

    events = _debug_events(sink, trajectory_id)
    assert {item["event"] for item in events} >= {
        "prepare",
        "commit",
        "trajectory_terminal",
    }
    prepare_payloads = [frame["payload"] for frame in events if frame["event"] == "prepare"]
    assert prepare_payloads[0]["disposition"] == "new_segment"
    assert prepare_payloads[1]["prompt_tokens"] > 0
    assert prepare_payloads[1]["disposition"] == "append"
    assert result.metrics.distributions["renderer/full_render_seconds"].count == 2


async def test_classifier_failure_is_fail_closed_and_self_diagnosing(tmp_path) -> None:
    sink = TITOLocalDebugSink(
        TITOLocalDebugConfig(
            root_dir=tmp_path.resolve(),
            run_id="classifier-failure",
            max_local_bytes=20_000_000,
            min_free_bytes=0,
        )
    )

    def fail_classifier(_request: TITOChatRequest) -> str:
        raise RuntimeError("changed harness signature")

    engine = _engine(FakeSampler(), observer=sink)
    engine.call_classifier = fail_classifier
    trajectory_id = engine.create_trajectory()
    await engine.complete(trajectory_id, _first_request())
    result = engine.finish(trajectory_id)
    sink.close()

    normalized = next(
        frame["payload"] for frame in _debug_events(sink, trajectory_id) if frame["event"] == "request_normalized"
    )
    assert normalized["classification_source"] == "fail_closed"
    assert normalized["classifier_error"] == {
        "type": "RuntimeError",
        "message": "changed harness signature",
    }
    assert result.metrics.counters["admission/classifier_failed"] == 1
    assert result.calls[0].kind == "policy"


async def test_mc_extras_survive_two_policy_turns_and_artifact_round_trip() -> None:
    sampler = FakeSampler(outputs=([197, 3], [198, 199, 3]))
    engine = _engine(sampler, sampling_defaults={"sample_extra_tokens": 3})
    trajectory = engine.create_trajectory()
    await engine.complete(trajectory, _first_request())
    await engine.complete(trajectory, _second_request())
    artifact = engine.finish(trajectory)
    restored = type(artifact).unpack(artifact.pack())
    turns = [turn for segment in restored.segments for turn in segment.turns]
    assert len(turns) == 2
    for turn in turns:
        assert len(turn.sample_extra_references) == len(turn.exact_completion_ids)
    assert all(call["sample_extra_tokens"] == 3 for call in sampler.calls)


@pytest.mark.parametrize("call_kind", ["policy", "auxiliary"])
async def test_mixed_sc_capture_fails_before_custom_sampler(call_kind):
    sampler = FakeSampler(outputs=([197, 3],))
    engine = _engine(
        sampler,
        sampling_defaults={
            "top_sampling_logprobs": 128,
            "top_sampling_format": "parquet_v1",
            "sample_extra_tokens": 4,
            "sample_extra_format": "parquet_v1",
        },
        call_classifier=lambda _request: (call_kind, "test"),
    )
    with pytest.raises(TITOError, match="mutually exclusive"):
        await engine.complete(engine.create_trajectory(), _first_request())
    assert not sampler.calls


@pytest.mark.parametrize("mode", ["full_history", "incremental"])
async def test_lineage_and_prompt_modes_for_interleaved_policy_calls(
    mode: Literal["full_history", "incremental"],
) -> None:
    renderer = FakeIncrementalRenderer()
    sampler = FakeSampler(outputs=([197, 3], [198, 3], [199, 3], [200, 3], [201, 3]))
    engine = _engine(sampler, renderer, prompt_mode=mode)
    trajectory = engine.create_trajectory()

    def follow(request, response, tool_result):
        return _request(
            (*request.messages, response.response["choices"][0]["message"], {"role": "tool", "content": tool_result})
        )

    root_request = _first_request()
    root = await engine.complete(trajectory, root_request)
    left_request = follow(root_request, root, "left")
    left = await engine.complete(trajectory, left_request)
    right_request = follow(root_request, root, "right")
    right = await engine.complete(trajectory, right_request, idempotency_key="fork")
    replay = await engine.complete(trajectory, right_request, idempotency_key="fork")
    assert replay.replayed and replay.turn_id == right.turn_id
    left_leaf = await engine.complete(trajectory, follow(left_request, left, "left again"))
    right_leaf = await engine.complete(trajectory, follow(right_request, right, "right again"))
    result = engine.finish(trajectory)
    assert type(result).unpack(result.pack()) == result
    assert len(sampler.calls) == 5
    assert (renderer.incremental_calls > 0) == (mode == "incremental")
    assert result.continued_turn_ids() == {root.turn_id, left.turn_id, right.turn_id}
    assert [(s.start_reason, s.closed_reason) for s in result.segments] == [
        ("initial", "trajectory_completed"),
        ("fork", "trajectory_completed"),
    ]
    assert [[(t.turn_id, t.parent_turn_id) for t in s.turns] for s in result.segments] == [
        [(root.turn_id, None), (left.turn_id, root.turn_id), (left_leaf.turn_id, left.turn_id)],
        [(right.turn_id, root.turn_id), (right_leaf.turn_id, right.turn_id)],
    ]
    assert renderer.render_calls == (6 if mode == "full_history" else 1)
    assert renderer.incremental_calls == (0 if mode == "full_history" else 5)
    for segment in result.segments:
        for turn in segment.turns:
            if mode == "full_history":
                assert turn.exact_prompt_ids == tuple(FakeRenderer().render_conversation_tokens(turn.request))
            elif turn.parent_turn_id:
                parent = next(t for s in result.segments for t in s.turns if t.turn_id == turn.parent_turn_id)
                assert turn.exact_prompt_ids == (*parent.exact_checkpoint_ids, 77, 2)


@pytest.mark.parametrize("boundary", ["ambiguous_parent", "length_truncation", "contract_change"])
async def test_tree_does_not_reuse_unsafe_checkpoint(boundary: str) -> None:
    renderer = FakeIncrementalRenderer()
    sampler = FakeSampler(finishes=["length" if boundary == "length_truncation" else "stop", "stop"])
    engine = _engine(sampler, renderer, prompt_mode="incremental")
    trajectory = engine.create_trajectory()
    root = await engine.complete(trajectory, _first_request())
    if boundary == "ambiguous_parent":
        await engine.complete(trajectory, _first_request())
    if boundary == "contract_change":
        renderer.contract_suffix = "different"
    await engine.complete(trajectory, _second_request())
    result = engine.finish(trajectory)
    assert result.segments[-1].start_reason == boundary
    assert result.segments[-1].turns[0].parent_turn_id == (None if boundary == "ambiguous_parent" else root.turn_id)
    assert renderer.incremental_calls == 0
    assert result.segments[-1].turns[0].incremental_fallback_reason == (
        None if boundary == "length_truncation" else boundary
    )


async def test_tree_strict_policy_rejects_unrelated_history_after_length() -> None:
    engine = _engine(FakeSampler(finishes=["length", "stop"]))
    policy = TrajectoryDriftPolicy(on_other_mismatch="reject")
    trajectory = engine.create_trajectory(drift_policy=policy)
    root = await engine.complete(trajectory, _first_request())
    with pytest.raises(TITOError) as rejected:
        await engine.complete(trajectory, _request([{"role": "user", "content": "unrelated root"}]))
    assert rejected.value.code == "tito_lineage_divergence"
    await engine.complete(trajectory, _second_request())
    segment = engine.finish(trajectory).segments[-1]
    assert segment.start_reason == "length_truncation"
    assert segment.turns[0].parent_turn_id == root.turn_id


async def test_tree_checks_ambiguity_across_render_contracts_before_reusing_tokens() -> None:
    sampler = FakeSampler(outputs=([197, 3], [197, 4], [198, 3]))
    renderer = FakeIncrementalRenderer()
    engine = _engine(sampler, renderer, prompt_mode="incremental")
    trajectory = engine.create_trajectory()
    tools = ({"type": "function", "function": {"name": "lookup"}},)
    first = await engine.complete(trajectory, _first_request())
    second = await engine.complete(trajectory, _first_request(tools=tools))
    assert first.response["choices"][0]["message"] == second.response["choices"][0]["message"]
    await engine.complete(trajectory, _second_request())
    artifact = engine.finish(trajectory)
    assert artifact.segments[-1].start_reason == "ambiguous_parent"
    assert artifact.segments[-1].turns[0].parent_turn_id is None
    assert renderer.incremental_calls == 0


@pytest.mark.parametrize("mode", ["full_history", "incremental"])
async def test_tree_resumes_with_a_masked_prompt_when_a_join_would_overwrite_prior_loss(mode: str) -> None:
    renderer = FakeIncrementalRenderer(canonical_stop=4, checkpoint_trim_tokens=1, replacement_token=9)
    engine = _engine(FakeSampler(), renderer, prompt_mode=mode)
    trajectory = engine.create_trajectory()
    root = await engine.complete(trajectory, _first_request())
    await engine.complete(trajectory, _request([{"role": "user", "content": "unrelated root"}]))
    await engine.complete(trajectory, _second_request())
    result = engine.finish(trajectory)
    assert [len(segment.turns) for segment in result.segments] == [1, 1, 1]
    resumed = result.segments[-1]
    assert resumed.start_reason == "branch_token_drift"
    assert resumed.turns[0].parent_turn_id == root.turn_id
    assert resumed.turns[0].prompt_disposition == "new_segment"


@pytest.mark.parametrize(
    "resume_sampling",
    [
        {},
        {"include_routing_matrix": True},
        {"top_sampling_logprobs": 4},
        {"sampling_mask": True},
        {"sample_extra_tokens": 3},
    ],
    ids=["same", "r3-enabled", "top-k-enabled", "mask-enabled", "extra-sampling-enabled"],
)
async def test_tree_queues_sibling_forks_and_uses_the_correct_routing_prefix(resume_sampling) -> None:
    class EchoRoutingSampler(FakeSampler):
        async def sample_with_prompt_tokens_result(self, prompt_token_ids, **kwargs):
            sampled = await super().sample_with_prompt_tokens_result(prompt_token_ids, **kwargs)
            if not kwargs.get("include_routing_matrix"):
                return sampled
            completion = sampled.completions[0]
            count = min(kwargs["echo_last"], len(prompt_token_ids) - 1)
            start = len(prompt_token_ids) - 1 - count
            completion.routing_matrices = _top_sampling_refs(
                count + len(completion.routing_matrices), row_start=start
            )
            completion.logprobs_echoed = True
            completion.echoed_prompt_logprob_count = count
            completion.inference_logprobs = [-0.9] * count + completion.inference_logprobs
            completion.sampling_logprobs = [-0.9] * count + completion.sampling_logprobs
            return sampled

    sampler = EchoRoutingSampler()
    engine = _engine(sampler, sampling_defaults={"incremental_prompt_routing": True})
    initial_routing = "include_routing_matrix" not in resume_sampling
    initial_sampling = {"include_routing_matrix": initial_routing}
    trajectory_id = engine.create_trajectory()
    root_request = _first_request(sampling_fields=initial_sampling)
    root = await engine.complete(trajectory_id, root_request)
    shared_prefix = (*root_request.messages, root.response["choices"][0]["message"])
    left_request = _request((*shared_prefix, {"role": "tool", "content": "left"}), sampling_fields=initial_sampling)
    right_request = _request((*shared_prefix, {"role": "tool", "content": "right"}), sampling_fields=initial_sampling)
    sampler.started.clear()
    sampler.block = True
    left_task = asyncio.create_task(engine.complete(trajectory_id, left_request))
    await asyncio.wait_for(sampler.started.wait(), timeout=2)
    right_task = asyncio.create_task(engine.complete(trajectory_id, right_request))
    await asyncio.sleep(0)
    assert len(sampler.calls) == 2
    sampler.release.set()
    left, right = await asyncio.gather(left_task, right_task)
    resume = _request(
        (*left_request.messages, left.response["choices"][0]["message"], {"role": "tool", "content": "left again"}),
        sampling_fields={**initial_sampling, **resume_sampling},
    )
    await engine.complete(trajectory_id, resume)
    artifact = engine.finish(trajectory_id)
    assert artifact.metrics.counters["queue/policy_waited"] == 1
    assert [len(s.turns) for s in artifact.segments] == ([2, 1, 1] if resume_sampling else [3, 1])
    root_turn, left_turn = artifact.segments[0].turns[:2]
    resumed = artifact.segments[-1].turns[0] if resume_sampling else artifact.segments[0].turns[-1]
    (right_turn,) = artifact.segments[1].turns
    assert (left_turn.turn_id, right_turn.turn_id) == (left.turn_id, right.turn_id)
    assert left_turn.parent_turn_id == right_turn.parent_turn_id == root_turn.turn_id
    assert resumed.parent_turn_id == left_turn.turn_id
    assert [t.prompt_routing_start for t in (root_turn, left_turn, right_turn, resumed)] == [
        0 if initial_routing else None,
        len(root_turn.exact_checkpoint_ids) - 1 if initial_routing else None,
        0 if initial_routing else None,
        0 if resume_sampling else len(left_turn.exact_checkpoint_ids) - 1,
    ]
    if resume_sampling:
        assert artifact.segments[-1].start_reason == "sampling_evidence_change"
        assert sampler.calls[-1]["echo_last"] == len(resumed.exact_prompt_ids)
    for turn in (root_turn, left_turn, right_turn, resumed):
        if turn.prompt_routing_matrices is not None:
            assert turn.prompt_routing_start + len(turn.prompt_routing_matrices) == len(turn.exact_prompt_ids) - 1
        assert turn.sampling_logprobs == (-0.2, -0.2)
