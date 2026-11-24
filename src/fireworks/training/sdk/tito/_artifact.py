"""Versioned, deterministic codec for compact TITO trajectory artifacts."""

from __future__ import annotations

import json
import time
import zlib
from types import MappingProxyType
from typing import Any, Literal, Mapping
from contextlib import closing
from dataclasses import fields
from collections.abc import Iterable

from fireworks.training.sdk.routing import routing_to_wire, routing_from_wire
from fireworks.training.sdk.sampling import ServerMetrics, SampledServerAttempt
from fireworks.training.sdk.tito._types import (
    TITOTurn,
    TITOError,
    TITOCallRecord,
    TITOChatRequest,
    TITODistribution,
    TITOMetricSummary,
    TITOSegmentResult,
    TITOParsedAssistant,
    TITOResponseAttempt,
    TITOTrajectoryArtifact,
    _freeze_json,
)
from fireworks.training.sdk.tito._native_runtime import require_native
from fireworks.training.sdk.tito._artifact_stream import ArtifactJSONReader, inflate_verified

_MAGIC = b"TITOART\x01"
_JSON_THREAD_YIELD_INTERVAL_SECONDS = 0.01


def _load_artifact_json(payload: bytes | str) -> Any:
    """Preserve standard JSON decoding while allowing other SDK threads to run."""
    last_yield = time.monotonic()

    def decoded_object(value: dict[str, Any]) -> dict[str, Any]:
        nonlocal last_yield
        if time.monotonic() - last_yield >= _JSON_THREAD_YIELD_INTERVAL_SECONDS:
            time.sleep(0)
            last_yield = time.monotonic()
        return value

    return json.loads(payload, object_hook=decoded_object)


def _server_metrics_value(value: ServerMetrics | None) -> dict[str, Any] | None:
    if value is None:
        return None
    return {item.name: getattr(value, item.name) for item in fields(ServerMetrics)}


def _server_attempt_value(value: SampledServerAttempt) -> dict[str, Any]:
    return {
        "index": value.index,
        "outcome": value.outcome,
        "status_code": value.status_code,
        "error_kind": value.error_kind,
        "response_request_id": value.response_request_id,
        "upstream_response_id": value.upstream_response_id,
        "server_metrics": _server_metrics_value(value.server_metrics),
    }


def _request_value(value: TITOChatRequest) -> dict[str, Any]:
    return {
        "messages": [dict(item) for item in value.messages],
        "tools": [dict(item) for item in value.tools],
        "model": value.model,
        "max_tokens": value.max_tokens,
        "temperature": value.temperature,
        "sampling_fields": dict(value.sampling_fields),
        "adapter_metadata": dict(value.adapter_metadata),
        "wire_request": value.wire_value(),
        "wire_request_body": value.wire_request_body,
        "normalization_steps": list(value.normalization_steps),
    }


def _turn_value(value: TITOTurn) -> dict[str, Any]:
    return {
        "turn_id": value.turn_id,
        **({"parent_turn_id": value.parent_turn_id} if value.parent_turn_id is not None else {}),
        "request": _request_value(value.request),
        "assistant": {
            "message": dict(value.assistant.message),
            **(
                {"response_message": dict(value.assistant.response_message)}
                if value.assistant.response_message != value.assistant.message
                else {}
            ),
            "output_kind": value.assistant.output_kind,
            "parser_fallback": value.assistant.parser_fallback,
        },
        "exact_prompt_ids": list(value.exact_prompt_ids),
        "exact_completion_ids": list(value.exact_completion_ids),
        "inference_logprobs": value.inference_logprobs,
        "sampling_logprobs": value.sampling_logprobs,
        **(
            {"top_sampling_references": routing_to_wire(value.top_sampling_references)}
            if value.top_sampling_references is not None
            else {}
        ),
        **(
            {"sampling_mask_references": routing_to_wire(value.sampling_mask_references)}
            if value.sampling_mask_references is not None
            else {}
        ),
        **(
            {"sample_extra_references": routing_to_wire(value.sample_extra_references)}
            if value.sample_extra_references is not None
            else {}
        ),
        "routing_matrices": routing_to_wire(value.routing_matrices),
        "prompt_routing_start": value.prompt_routing_start,
        "prompt_routing_matrices": routing_to_wire(value.prompt_routing_matrices),
        "response_id": value.response_id,
        "finish_reason": value.finish_reason,
        "prompt_disposition": value.prompt_disposition,
        "prefix_match_tokens": value.prefix_match_tokens,
        "realign_from_token": value.realign_from_token,
        "realigned_masked_tokens": value.realigned_masked_tokens,
        "prompt_mode": value.prompt_mode,
        "incremental_contract_id": value.incremental_contract_id,
        "incremental_junction_kind": value.incremental_junction_kind,
        "incremental_checkpoint_trim_tokens": value.incremental_checkpoint_trim_tokens,
        "incremental_fallback_reason": value.incremental_fallback_reason,
        "requested_output_tokens": value.requested_output_tokens,
        "effective_output_tokens": value.effective_output_tokens,
        "context_remaining_tokens": value.context_remaining_tokens,
        "server_metrics": _server_metrics_value(value.server_metrics),
        "sampler_wall_seconds": value.sampler_wall_seconds,
        "logical_request_id": value.logical_request_id,
        "upstream_response_id": value.upstream_response_id,
        "upstream_attempts": value.upstream_attempts,
        "server_attempts": [_server_attempt_value(item) for item in value.server_attempts],
        "parser_fallback": value.parser_fallback,
    }


def _artifact_value(value: TITOTrajectoryArtifact) -> dict[str, Any]:
    encoded: dict[str, Any] = {
        "schema_version": 2 if value.lineage_mode == "tree" else 1,
        "trajectory_id": value.trajectory_id,
        "serving_affinity_key_hash": value.serving_affinity_key_hash,
        "metadata": dict(value.metadata),
        "status": value.status,
        "terminal_reason": value.terminal_reason,
        "segments": [
            {
                "segment_id": segment.segment_id,
                "start_reason": segment.start_reason,
                "render_contract_id": segment.render_contract_id,
                "turns": [_turn_value(turn) for turn in segment.turns],
                "closed_reason": segment.closed_reason,
            }
            for segment in value.segments
        ],
        "calls": [
            {
                "call_id": call.call_id,
                "kind": call.kind,
                "classification_source": call.classification_source,
                "outcome": call.outcome,
                "started_at": call.started_at,
                "ended_at": call.ended_at,
                "request_fingerprint": call.request_fingerprint,
                "prepared_prompt_hash": call.prepared_prompt_hash,
                "turn_id": call.turn_id,
                "logical_request_id": call.logical_request_id,
                "upstream_response_id": call.upstream_response_id,
                "attempts": call.attempts,
                "server_attempts": [_server_attempt_value(item) for item in call.server_attempts],
                "error_code": call.error_code,
            }
            for call in value.calls
        ],
        "response_attempts": [
            {
                "attempt_id": attempt.attempt_id,
                "turn_id": attempt.turn_id,
                "emission": attempt.emission,
                "created_at": attempt.created_at,
            }
            for attempt in value.response_attempts
        ],
        "metrics": {
            "counters": dict(value.metrics.counters),
            "distributions": {
                name: {
                    "count": distribution.count,
                    "sum": distribution.sum,
                    "min": distribution.min,
                    "max": distribution.max,
                }
                for name, distribution in value.metrics.distributions.items()
            },
        },
        "started_at": value.started_at,
        "finished_at": value.finished_at,
    }

    if value.lineage_mode == "tree":
        encoded["lineage_mode"] = "tree"
    return encoded


def pack_trajectory_artifact(value: TITOTrajectoryArtifact) -> bytes:
    """Encode one artifact, using v1 for linear and v2 for tree lineage."""
    native = require_native()
    encoder = json.JSONEncoder(sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    wire = _artifact_value(value)
    if value.lineage_mode == "tree":
        return _MAGIC + native.compress_json(wire, encoder.encode)

    # Use this interpreter's zlib to preserve the v1 compression bytes.
    compressor = zlib.compressobj(level=6)
    compressed = [_MAGIC]

    def compress_chunk(chunk: bytes) -> None:
        compressed.append(compressor.compress(chunk))

    native.encode_json(wire, encoder.encode, compress_chunk)
    compressed.append(compressor.flush())
    return b"".join(compressed)


def _server_metrics(raw: Mapping[str, Any] | None) -> ServerMetrics | None:
    return None if raw is None else ServerMetrics(**dict(raw))


def _server_attempt(raw: Mapping[str, Any]) -> SampledServerAttempt:
    return SampledServerAttempt(
        index=int(raw["index"]),
        outcome=raw["outcome"],
        status_code=raw.get("status_code"),
        error_kind=raw.get("error_kind"),
        response_request_id=raw.get("response_request_id"),
        upstream_response_id=raw.get("upstream_response_id"),
        server_metrics=_server_metrics(raw.get("server_metrics")),
    )


def _request(raw: Mapping[str, Any]) -> TITOChatRequest:
    wire_request_body = raw.get("wire_request_body")
    wire_request = raw.get("wire_request")
    if isinstance(wire_request_body, str):
        try:
            decoded_wire_request = _load_artifact_json(wire_request_body)
        except json.JSONDecodeError:
            pass
        else:
            if isinstance(decoded_wire_request, Mapping):
                # The artifact codec sorts object keys for deterministic bytes.
                # Reconstruct the prompt-visible wire mapping from the retained
                # raw body so template-sensitive schema order remains exact.
                wire_request = decoded_wire_request
    return TITOChatRequest(
        messages=tuple(raw["messages"]),
        tools=tuple(raw.get("tools") or ()),
        model=str(raw["model"]),
        max_tokens=raw.get("max_tokens"),
        temperature=float(raw["temperature"]),
        sampling_fields=dict(raw.get("sampling_fields") or {}),
        adapter_metadata=dict(raw.get("adapter_metadata") or {}),
        wire_request=wire_request,
        wire_request_body=wire_request_body,
        normalization_steps=tuple(raw.get("normalization_steps") or ()),
    )


def _turn(raw: Mapping[str, Any]) -> TITOTurn:
    if any(raw.get(key) is not None for key in ("sample_extra_token_ids", "sample_extra_sampling_logprobs")):
        raise ValueError("Inline MC artifacts are unsupported; collect rollouts with sample_extra_references")
    if any(raw.get(key) is not None for key in ("inference_topk_token_ids", "inference_topk_logprobs")):
        raise ValueError("Inline top-k artifacts are unsupported; collect rollouts with top_sampling_references")
    if "prompt_prefix" in raw:
        raise ValueError("unsupported TITO turn prompt prefix")
    assistant = raw["assistant"]
    parsed = TITOParsedAssistant(
        message=assistant["message"],
        output_kind=str(assistant["output_kind"]),
        parser_fallback=bool(assistant["parser_fallback"]),
    )
    if "response_message" in assistant:
        response = TITOParsedAssistant(
            message=assistant["response_message"],
            output_kind=parsed.output_kind,
            parser_fallback=parsed.parser_fallback,
        )
        if response.message != parsed.message:
            raise ValueError("assistant response_message differs from canonical message")
        parsed = response
    return TITOTurn(
        turn_id=str(raw["turn_id"]),
        parent_turn_id=raw.get("parent_turn_id"),
        request=_request(raw["request"]),
        assistant=parsed,
        exact_prompt_ids=tuple(raw["exact_prompt_ids"]),
        exact_completion_ids=tuple(raw["exact_completion_ids"]),
        inference_logprobs=(None if raw.get("inference_logprobs") is None else tuple(raw["inference_logprobs"])),
        sampling_logprobs=(None if raw.get("sampling_logprobs") is None else tuple(raw["sampling_logprobs"])),
        top_sampling_references=routing_from_wire(raw.get("top_sampling_references")),
        sampling_mask_references=routing_from_wire(raw.get("sampling_mask_references")),
        sample_extra_references=routing_from_wire(raw.get("sample_extra_references")),
        routing_matrices=routing_from_wire(raw.get("routing_matrices")),
        prompt_routing_start=raw.get("prompt_routing_start"),
        prompt_routing_matrices=routing_from_wire(raw.get("prompt_routing_matrices")),
        response_id=str(raw["response_id"]),
        finish_reason=str(raw["finish_reason"]),
        prompt_disposition=raw["prompt_disposition"],
        prefix_match_tokens=(None if raw.get("prefix_match_tokens") is None else int(raw["prefix_match_tokens"])),
        realign_from_token=(None if raw.get("realign_from_token") is None else int(raw["realign_from_token"])),
        realigned_masked_tokens=int(raw["realigned_masked_tokens"]),
        prompt_mode=raw.get("prompt_mode", "full_history"),
        incremental_contract_id=raw.get("incremental_contract_id"),
        incremental_junction_kind=raw.get("incremental_junction_kind"),
        incremental_checkpoint_trim_tokens=int(raw.get("incremental_checkpoint_trim_tokens", 0)),
        incremental_fallback_reason=raw.get("incremental_fallback_reason"),
        requested_output_tokens=int(raw["requested_output_tokens"]),
        effective_output_tokens=int(raw["effective_output_tokens"]),
        context_remaining_tokens=int(raw["context_remaining_tokens"]),
        server_metrics=_server_metrics(raw.get("server_metrics")),
        sampler_wall_seconds=float(raw["sampler_wall_seconds"]),
        logical_request_id=str(raw["logical_request_id"]),
        upstream_response_id=raw.get("upstream_response_id"),
        upstream_attempts=int(raw["upstream_attempts"]),
        server_attempts=tuple(_server_attempt(item) for item in raw.get("server_attempts") or ()),
        parser_fallback=bool(raw.get("parser_fallback", False)),
    )


def _segment(raw: Mapping[str, Any], turns: Iterable[TITOTurn]) -> TITOSegmentResult:
    return TITOSegmentResult(
        segment_id=str(raw["segment_id"]),
        start_reason=str(raw["start_reason"]),
        render_contract_id=str(raw["render_contract_id"]),
        turns=tuple(turns),
        closed_reason=raw.get("closed_reason"),
    )


def _call(raw: Mapping[str, Any]) -> TITOCallRecord:
    return TITOCallRecord(
        call_id=str(raw["call_id"]),
        kind=raw["kind"],
        classification_source=str(raw["classification_source"]),
        outcome=raw["outcome"],
        started_at=float(raw["started_at"]),
        ended_at=float(raw["ended_at"]),
        request_fingerprint=raw.get("request_fingerprint"),
        prepared_prompt_hash=raw.get("prepared_prompt_hash"),
        turn_id=raw.get("turn_id"),
        logical_request_id=raw.get("logical_request_id"),
        upstream_response_id=raw.get("upstream_response_id"),
        attempts=int(raw.get("attempts", 0)),
        server_attempts=tuple(_server_attempt(item) for item in raw.get("server_attempts") or ()),
        error_code=raw.get("error_code"),
    )


def _response_attempt(raw: Mapping[str, Any]) -> TITOResponseAttempt:
    return TITOResponseAttempt(
        attempt_id=str(raw["attempt_id"]),
        turn_id=str(raw["turn_id"]),
        emission=raw["emission"],
        created_at=float(raw["created_at"]),
    )


def _validate_wire_schema(raw: Mapping[str, Any]) -> Literal["linear", "tree"]:
    version = raw.get("schema_version")
    lineage_mode = raw.get("lineage_mode", "linear")
    if type(version) is not int or (version, lineage_mode) not in ((1, "linear"), (2, "tree")):
        raise ValueError(f"unsupported TITO artifact schema or lineage: {version!r}, {lineage_mode!r}")
    if "prompt_prefixes" in raw:
        raise ValueError("unsupported TITO prompt prefix table")
    return lineage_mode


def _trajectory(raw: Mapping[str, Any], lineage_mode: Literal["linear", "tree"]) -> TITOTrajectoryArtifact:
    metrics = raw["metrics"]
    return TITOTrajectoryArtifact(
        lineage_mode=lineage_mode,
        trajectory_id=str(raw["trajectory_id"]),
        serving_affinity_key_hash=str(raw["serving_affinity_key_hash"]),
        metadata=MappingProxyType(_freeze_json(raw.get("metadata") or {})),
        status=raw["status"],
        terminal_reason=raw.get("terminal_reason"),
        segments=raw["segments"],
        calls=raw["calls"],
        response_attempts=raw["response_attempts"],
        metrics=TITOMetricSummary(
            counters=MappingProxyType({str(k): int(v) for k, v in metrics["counters"].items()}),
            distributions=MappingProxyType(
                {
                    str(name): TITODistribution(
                        count=int(distribution["count"]),
                        sum=float(distribution["sum"]),
                        min=distribution.get("min"),
                        max=distribution.get("max"),
                    )
                    for name, distribution in metrics["distributions"].items()
                }
            ),
        ),
        started_at=float(raw["started_at"]),
        finished_at=float(raw["finished_at"]),
    )


_ARTIFACT_ERRORS = (KeyError, TypeError, ValueError, AttributeError, OverflowError, RecursionError, zlib.error)


def unpack_trajectory_artifact(payload: bytes) -> TITOTrajectoryArtifact:
    """Decode a compact artifact already available as bytes."""
    try:
        if not payload.startswith(_MAGIC):
            raise ValueError("missing TITO artifact magic/version")
        raw = _load_artifact_json(zlib.decompress(payload[len(_MAGIC) :]))
        lineage_mode = _validate_wire_schema(raw)
        raw["segments"] = tuple(_segment(segment, map(_turn, segment["turns"])) for segment in raw["segments"])
        raw["calls"] = tuple(map(_call, raw["calls"]))
        raw["response_attempts"] = tuple(map(_response_attempt, raw["response_attempts"]))
        return _trajectory(raw, lineage_mode)
    except _ARTIFACT_ERRORS as exc:
        raise TITOError("tito_artifact_invalid", 400, f"invalid TITO trajectory artifact: {exc}") from exc


def unpack_trajectory_stream(
    chunks: Iterable[bytes],
    *,
    expected_bytes: int,
    expected_sha256: str | None,
    max_expanded_bytes: int,
) -> TITOTrajectoryArtifact:
    """Verify one canonical UTF-8 artifact from a caller-owned byte source."""
    plaintext = inflate_verified(
        chunks,
        magic=_MAGIC,
        expected_bytes=expected_bytes,
        expected_sha256=expected_sha256,
        max_expanded_bytes=max_expanded_bytes,
    )
    try:
        with closing(plaintext):
            reader = ArtifactJSONReader(plaintext)
            raw: dict[str, Any] = {}
            for field in reader.members():
                if field == "segments":
                    segments = []
                    for _ in reader.items():
                        segment: dict[str, Any] = {}
                        for name in reader.members():
                            if name == "turns":
                                segment[name] = tuple(_turn(reader.value()) for _ in reader.items())
                            else:
                                segment[name] = reader.value()
                        segments.append(_segment(segment, segment["turns"]))
                    raw[field] = tuple(segments)
                elif field == "calls":
                    raw[field] = tuple(_call(reader.value()) for _ in reader.items())
                elif field == "response_attempts":
                    raw[field] = tuple(_response_attempt(reader.value()) for _ in reader.items())
                elif field == "prompt_prefixes":
                    raise ValueError("unsupported TITO prompt prefix table")
                else:
                    raw[field] = reader.value()
                    if field == "schema_version" and (type(raw[field]) is not int or raw[field] not in (1, 2)):
                        raise ValueError(f"unsupported TITO artifact schema: {raw[field]!r}")
            reader.finish()
        return _trajectory(raw, _validate_wire_schema(raw))
    except _ARTIFACT_ERRORS as exc:
        raise TITOError("tito_artifact_invalid", 400, f"invalid TITO trajectory artifact: {exc}") from exc
