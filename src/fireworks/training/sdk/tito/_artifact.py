"""Versioned, deterministic codec for compact TITO trajectory artifacts."""

from __future__ import annotations

import json
import zlib
from types import MappingProxyType
from typing import Any, Mapping
from dataclasses import fields

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
    _canonical_bytes,
)

_MAGIC = b"TITOART\x01"


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
        "request": _request_value(value.request),
        "assistant": {
            "message": dict(value.assistant.message),
            "output_kind": value.assistant.output_kind,
            "parser_fallback": value.assistant.parser_fallback,
        },
        "exact_prompt_ids": list(value.exact_prompt_ids),
        "exact_completion_ids": list(value.exact_completion_ids),
        "inference_logprobs": value.inference_logprobs,
        "sampling_logprobs": value.sampling_logprobs,
        "routing_matrices": value.routing_matrices,
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
    return {
        "schema_version": 1,
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


def pack_trajectory_artifact(value: TITOTrajectoryArtifact) -> bytes:
    """Encode one artifact into the stable v1 wire representation."""
    return _MAGIC + zlib.compress(_canonical_bytes(_artifact_value(value)), level=6)


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
            decoded_wire_request = json.loads(wire_request_body)
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
    assistant = raw["assistant"]
    return TITOTurn(
        turn_id=str(raw["turn_id"]),
        request=_request(raw["request"]),
        assistant=TITOParsedAssistant(
            message=assistant["message"],
            output_kind=str(assistant["output_kind"]),
            parser_fallback=bool(assistant["parser_fallback"]),
        ),
        exact_prompt_ids=tuple(raw["exact_prompt_ids"]),
        exact_completion_ids=tuple(raw["exact_completion_ids"]),
        inference_logprobs=(None if raw.get("inference_logprobs") is None else tuple(raw["inference_logprobs"])),
        sampling_logprobs=(None if raw.get("sampling_logprobs") is None else tuple(raw["sampling_logprobs"])),
        routing_matrices=(None if raw.get("routing_matrices") is None else tuple(raw["routing_matrices"])),
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


def unpack_trajectory_artifact(payload: bytes) -> TITOTrajectoryArtifact:
    """Decode and validate one compact trajectory artifact."""
    try:
        if not payload.startswith(_MAGIC):
            raise ValueError("missing TITO artifact magic/version")
        raw = json.loads(zlib.decompress(payload[len(_MAGIC) :]))
        if raw.get("schema_version") != 1:
            raise ValueError(f"unsupported TITO artifact schema: {raw.get('schema_version')!r}")
        metrics = raw["metrics"]
        return TITOTrajectoryArtifact(
            trajectory_id=str(raw["trajectory_id"]),
            serving_affinity_key_hash=str(raw["serving_affinity_key_hash"]),
            metadata=MappingProxyType(_freeze_json(raw.get("metadata") or {})),
            status=raw["status"],
            terminal_reason=raw.get("terminal_reason"),
            segments=tuple(
                TITOSegmentResult(
                    segment_id=str(segment["segment_id"]),
                    start_reason=str(segment["start_reason"]),
                    render_contract_id=str(segment["render_contract_id"]),
                    turns=tuple(_turn(turn) for turn in segment["turns"]),
                    closed_reason=segment.get("closed_reason"),
                )
                for segment in raw["segments"]
            ),
            calls=tuple(
                TITOCallRecord(
                    call_id=str(call["call_id"]),
                    kind=call["kind"],
                    classification_source=str(call["classification_source"]),
                    outcome=call["outcome"],
                    started_at=float(call["started_at"]),
                    ended_at=float(call["ended_at"]),
                    request_fingerprint=call.get("request_fingerprint"),
                    prepared_prompt_hash=call.get("prepared_prompt_hash"),
                    turn_id=call.get("turn_id"),
                    logical_request_id=call.get("logical_request_id"),
                    upstream_response_id=call.get("upstream_response_id"),
                    attempts=int(call.get("attempts", 0)),
                    server_attempts=tuple(_server_attempt(item) for item in call.get("server_attempts") or ()),
                    error_code=call.get("error_code"),
                )
                for call in raw["calls"]
            ),
            response_attempts=tuple(
                TITOResponseAttempt(
                    attempt_id=str(attempt["attempt_id"]),
                    turn_id=str(attempt["turn_id"]),
                    emission=attempt["emission"],
                    created_at=float(attempt["created_at"]),
                )
                for attempt in raw["response_attempts"]
            ),
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
    except (KeyError, TypeError, ValueError, zlib.error, json.JSONDecodeError) as exc:
        raise TITOError("tito_artifact_invalid", 400, f"invalid TITO trajectory artifact: {exc}") from exc
