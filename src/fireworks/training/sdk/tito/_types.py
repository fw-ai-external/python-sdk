"""Public contracts and immutable values for exact-token TITO rollouts."""

from __future__ import annotations

import json
import math
import hashlib
import warnings
from types import MappingProxyType
from typing import Any, Union, Literal, Mapping, Protocol, Sequence, get_args, runtime_checkable
from dataclasses import InitVar, field, dataclass
from collections.abc import Iterable

from fireworks.training.sdk.routing import RoutingReferences
from fireworks.training.sdk.sampling import ServerMetrics, SampledServerAttempt

TITOCallKind = Literal["policy", "auxiliary"]
TITOClassification = Union[TITOCallKind, tuple[TITOCallKind, str]]
TITOCallOutcome = Literal[
    "succeeded",
    "replayed",
    "model_malformed",
    "rejected",
    "failed",
    "cancelled",
]
TITOEmission = Literal["completed", "ambiguous"]
TITOTrajectoryStatus = Literal["active", "completed", "abandoned", "failed"]
TITOErrorOrigin = Literal["sdk", "sdk_parser", "server", "transport", "adapter", "environment", "unknown"]
TITOPromptDisposition = Literal["append", "realign", "new_segment"]
TITOPromptMode = Literal["full_history", "incremental"]


def _plain_json(value: Any) -> Any:
    """Recursively detach immutable SDK containers before JSON validation."""
    if value is None or type(value) in (str, int, float, bool):
        return value
    if isinstance(value, Mapping):
        return {str(key): _plain_json(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain_json(item) for item in value]
    return value


def _clone_json_value(value: Any, *, sort_keys: bool) -> Any:
    """Copy detached JSON containers without encoding their immutable leaves."""
    value_type = type(value)
    if value is None or value_type is str or value_type is bool:
        return value
    if value_type is int and value.bit_length() <= 63:
        return value
    if value_type is float and math.isfinite(value):
        return value
    if value_type is dict:
        keys = sorted(value) if sort_keys else value
        return {key: _clone_json_value(value[key], sort_keys=sort_keys) for key in keys}
    if value_type is list:
        return [_clone_json_value(item, sort_keys=sort_keys) for item in value]
    # Preserve JSON's validation, scalar-subclass normalization, nonfinite
    # constants and large-integer limits for values outside the common path.
    return json.loads(json.dumps(value))


def _freeze_json(value: Any) -> Any:
    """Return a detached, JSON-compatible value with deterministic mappings."""
    try:
        return _clone_json_value(_plain_json(value), sort_keys=True)
    except (TypeError, ValueError) as exc:
        raise TITOError(
            "tito_invalid_request",
            400,
            f"request contains a non-JSON value: {exc}",
        ) from exc


def _copy_json_in_order(value: Any) -> Any:
    """Return a detached JSON value while preserving admitted mapping order."""
    try:
        return _clone_json_value(_plain_json(value), sort_keys=False)
    except (TypeError, ValueError) as exc:
        raise TITOError(
            "tito_invalid_request",
            400,
            f"request contains a non-JSON value: {exc}",
        ) from exc


def normalize_openai_tool_arguments(value: Any) -> str:
    """Canonicalize JSON-equivalent OpenAI function arguments.

    OpenAI-compatible harnesses replay function arguments as JSON strings, but
    are free to change insignificant whitespace or object-key order. Invalid
    argument strings are preserved so renderer/parser error handling remains
    authoritative.
    """
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _normalize_chat_message(message: Mapping[str, Any]) -> dict[str, Any]:
    """Canonicalize protocol-equivalent OpenAI message forms before lineage checks."""
    normalized = _plain_json(message)
    tool_calls = normalized.get("tool_calls") or []
    is_tool_assistant = normalized.get("role") == "assistant" and bool(tool_calls)
    if is_tool_assistant:
        normalized_calls: list[dict[str, Any]] = []
        for raw_call in tool_calls:
            call = dict(raw_call)
            function = dict(call.get("function") or {})
            function["arguments"] = normalize_openai_tool_arguments(function.get("arguments", ""))
            call["function"] = function
            normalized_calls.append(call)
        normalized["tool_calls"] = normalized_calls
    content = normalized.get("content")
    if is_tool_assistant and (content is None or (isinstance(content, str) and not content.strip())):
        # OpenAI-compatible harnesses vary between null, empty, and whitespace-
        # only content for tool-call-only assistant messages. They are the same
        # protocol value and must not create a false history rewrite.
        normalized["content"] = ""
    return normalized


def _chat_normalization_steps(
    wire_messages: Sequence[Mapping[str, Any]],
    canonical_messages: Sequence[Mapping[str, Any]],
) -> tuple[str, ...]:
    """Describe every protocol-level rewrite made at request admission."""
    steps: list[str] = []
    for message_index, (wire_message, canonical_message) in enumerate(zip(wire_messages, canonical_messages)):
        if "provider_specific_fields" in wire_message and "provider_specific_fields" not in canonical_message:
            steps.append(f"messages[{message_index}].provider_specific_fields:empty_refusal_removed")
        wire_calls = wire_message.get("tool_calls") or []
        canonical_calls = canonical_message.get("tool_calls") or []
        wire_content = wire_message.get("content")
        if canonical_message.get("role") == "assistant" and wire_calls and canonical_message.get("content") == "":
            if wire_content is None:
                steps.append(f"messages[{message_index}].content:null_to_empty")
            elif isinstance(wire_content, str) and wire_content and not wire_content.strip():
                steps.append(f"messages[{message_index}].content:whitespace_to_empty")
        for call_index, (wire_call, canonical_call) in enumerate(zip(wire_calls, canonical_calls)):
            if "index" in wire_call and "index" not in canonical_call:
                steps.append(f"messages[{message_index}].tool_calls[{call_index}].index:stream_index_removed")
            wire_function = wire_call.get("function") or {}
            canonical_function = canonical_call.get("function") or {}
            if wire_function.get("arguments", "") != canonical_function.get("arguments", ""):
                steps.append(f"messages[{message_index}].tool_calls[{call_index}].function.arguments:canonical_json")
    return tuple(steps)


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _hash_json(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _hash_tokens(tokens: Sequence[int]) -> str:
    return _hash_json([int(token) for token in tokens])


def _server_attempt_value(attempt: SampledServerAttempt) -> dict[str, Any]:
    return {
        "index": attempt.index,
        "outcome": attempt.outcome,
        "status_code": attempt.status_code,
        "error_kind": attempt.error_kind,
        "response_request_id": attempt.response_request_id,
        "upstream_response_id": attempt.upstream_response_id,
        "server_metrics": (vars(attempt.server_metrics) if attempt.server_metrics is not None else None),
    }


@dataclass(frozen=True)
class TITOParsedAssistant:
    """Canonical lineage message plus the order-preserving client response.

    ``response_message`` preserves parser-produced argument strings, including
    their whitespace and key order. ``message`` retains protocol canonicalization
    for semantic history comparisons, never as a substitute for token alignment.
    """

    message: Mapping[str, Any]
    output_kind: str = "text"
    parser_fallback: bool = False
    response_message: Mapping[str, Any] = field(init=False, compare=False, repr=False)

    def __post_init__(self) -> None:
        response = _copy_json_in_order(self.message)
        for call in response.get("tool_calls") or ():
            function = call.get("function") or {}
            if "arguments" in function and not isinstance(function["arguments"], str):
                function["arguments"] = json.dumps(function["arguments"], separators=(",", ":"), ensure_ascii=False)
        object.__setattr__(self, "response_message", MappingProxyType(response))
        object.__setattr__(
            self,
            "message",
            MappingProxyType(_freeze_json(_normalize_chat_message(self.message))),
        )


@dataclass(frozen=True)
class TITOChatRequest:
    """Canonical request plus its optional pre-normalization wire value."""

    messages: tuple[Mapping[str, Any], ...]
    tools: tuple[Mapping[str, Any], ...] = ()
    model: str = "policy"
    max_tokens: int | None = None
    temperature: float = 1.0
    sampling_fields: Mapping[str, Any] = field(default_factory=dict)
    adapter_metadata: Mapping[str, Any] = field(default_factory=dict)
    wire_request: Mapping[str, Any] | None = field(
        default=None,
        compare=False,
        repr=False,
    )
    wire_request_body: str | None = field(
        default=None,
        compare=False,
        repr=False,
    )
    normalization_steps: tuple[str, ...] = field(
        default=(),
        compare=False,
    )

    def __post_init__(self) -> None:
        messages = tuple(MappingProxyType(_freeze_json(_normalize_chat_message(item))) for item in self.messages)
        tools = tuple(MappingProxyType(_freeze_json(item)) for item in self.tools)
        sampling = MappingProxyType(_freeze_json(self.sampling_fields))
        adapter_metadata = MappingProxyType(_freeze_json(self.adapter_metadata))
        wire_request = None if self.wire_request is None else MappingProxyType(_copy_json_in_order(self.wire_request))
        if not messages:
            raise TITOError("tito_invalid_request", 400, "messages must not be empty")
        for item in messages:
            if not isinstance(item.get("role"), str):
                raise TITOError("tito_invalid_request", 400, "every message requires a string role")
        if self.max_tokens is not None and self.max_tokens < 1:
            raise TITOError("tito_invalid_request", 400, "max_tokens must be positive")
        object.__setattr__(self, "messages", messages)
        object.__setattr__(self, "tools", tools)
        object.__setattr__(self, "sampling_fields", sampling)
        object.__setattr__(self, "adapter_metadata", adapter_metadata)
        object.__setattr__(self, "wire_request", wire_request)
        object.__setattr__(
            self,
            "normalization_steps",
            tuple(str(step) for step in self.normalization_steps),
        )

    @classmethod
    def from_openai(
        cls,
        payload: Mapping[str, Any],
        *,
        wire_request_body: str | None = None,
    ) -> "TITOChatRequest":
        tool_choice = payload.get("tool_choice")
        if tool_choice not in (None, "auto"):
            raise TITOError(
                "tito_invalid_request",
                400,
                "TITO currently supports only the default or tool_choice='auto'",
            )
        parallel_tool_calls = payload.get("parallel_tool_calls")
        if parallel_tool_calls is False:
            raise TITOError(
                "tito_invalid_request",
                400,
                "TITO currently supports only the default parallel tool-call policy",
            )
        if payload.get("store") not in (None, False):
            raise TITOError(
                "tito_invalid_request",
                400,
                "TITO does not support server-side response storage",
            )
        known = {
            "messages",
            "tools",
            "model",
            "max_tokens",
            "max_completion_tokens",
            "temperature",
            "stream",
            "stream_options",
            "tool_choice",
            "parallel_tool_calls",
            "store",
            "_tito",
        }
        max_tokens = payload.get("max_completion_tokens")
        if max_tokens is None:
            max_tokens = payload.get("max_tokens")
        wire_request = _copy_json_in_order(payload)
        messages = [dict(message) for message in payload.get("messages") or ()]
        for message in messages:
            # Compatible clients add this empty response marker on roundtrip.
            # Normalize admission only: decoding old artifacts must preserve
            # their already canonical messages and request fingerprints.
            if message.get("role") == "assistant" and message.get("provider_specific_fields") == {"refusal": None}:
                del message["provider_specific_fields"]
            if message.get("role") == "assistant" and message.get("tool_calls"):
                # SSE indices identify chunks, not calls in a replayed message.
                # Keep the original wire value and legacy artifact identities.
                message["tool_calls"] = [
                    {key: value for key, value in call.items() if key != "index"} for call in message["tool_calls"]
                ]
        normalized = cls(
            messages=tuple(messages),
            tools=tuple(payload.get("tools") or ()),
            model=str(payload.get("model") or "policy"),
            max_tokens=int(max_tokens) if max_tokens is not None else None,
            temperature=float(payload.get("temperature", 1.0)),
            sampling_fields={key: value for key, value in payload.items() if key not in known},
            adapter_metadata=dict(payload.get("_tito") or {}),
            wire_request=wire_request,
            wire_request_body=wire_request_body,
        )
        wire_messages = tuple(wire_request.get("messages") or ())
        steps = _chat_normalization_steps(wire_messages, normalized.messages)
        object.__setattr__(normalized, "normalization_steps", steps)
        return normalized

    def canonical_value(self) -> dict[str, Any]:
        return {
            "messages": [dict(item) for item in self.messages],
            "tools": [dict(item) for item in self.tools],
            "model": self.model,
        }

    def wire_value(self) -> dict[str, Any] | None:
        """Return the decoded JSON value received before canonicalization."""
        if self.wire_request is None:
            return None
        return _plain_json(self.wire_request)

    def sampling_value(self) -> dict[str, Any]:
        return {
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            **dict(self.sampling_fields),
        }


@runtime_checkable
class TITORenderer(Protocol):
    """Complete-conversation contract implemented by cookbook renderers."""

    renderer_id: str

    def render_conversation_tokens(self, request: TITOChatRequest) -> Sequence[int]: ...

    def parse_assistant(
        self,
        request: TITOChatRequest,
        completion_ids: Sequence[int],
        completion_text: str,
        finish_reason: str,
    ) -> TITOParsedAssistant: ...

    def render_contract_id(self, request: TITOChatRequest) -> str: ...

    def stop_sequences(self, request: TITOChatRequest) -> Sequence[str] | None: ...


@dataclass(frozen=True)
class TITOIncrementalPrompt:
    """Experimental renderer-owned join against an exact checkpoint.

    ``checkpoint_trim_tokens`` is the bounded trailing portion of the prior
    checkpoint that the renderer intentionally replaced at the model-specific
    role junction. Renderer authors must validate this contract against their
    pinned tokenizer/chat template; renderers without that model-specific
    evidence should use ``full_history`` instead.
    """

    prompt_ids: tuple[int, ...]
    contract_id: str
    junction_kind: str
    checkpoint_trim_tokens: int = 0

    def __post_init__(self) -> None:
        prompt_ids = tuple(int(token) for token in self.prompt_ids)
        if not prompt_ids:
            raise ValueError("incremental prompt must not be empty")
        if not self.contract_id:
            raise ValueError("incremental contract_id must not be empty")
        if not self.junction_kind:
            raise ValueError("incremental junction_kind must not be empty")
        if self.checkpoint_trim_tokens < 0:
            raise ValueError("incremental checkpoint_trim_tokens must be non-negative")
        object.__setattr__(self, "prompt_ids", prompt_ids)


@runtime_checkable
class TITOIncrementalRenderer(Protocol):
    """Experimental opt-in contract for incremental prompt construction.

    Implementing this protocol is an explicit renderer-author assertion that
    synthetic-anchor suffixes and every declared junction have been checked
    against the supported model/template pair. The API and model coverage may
    change while incremental mode remains experimental.
    """

    def prepare_incremental_prompt(
        self,
        request: TITOChatRequest,
        stored_messages: Sequence[Mapping[str, Any]],
        appended_messages: Sequence[Mapping[str, Any]],
        exact_checkpoint_ids: Sequence[int],
    ) -> TITOIncrementalPrompt | None: ...


@dataclass(frozen=True)
class TrajectoryDriftPolicy:
    """Model-neutral full-render drift and training-coverage policy."""

    max_masked_tokens: int = 1024
    on_other_mismatch: Literal["new_segment", "reject"] = "new_segment"
    # Older Harbor versions still pass this keyword. Tree is the only runtime policy.
    lineage_mode: InitVar[Literal["tree", "linear"] | None] = None

    def __post_init__(self, lineage_mode: Literal["tree", "linear"] | None) -> None:
        if self.max_masked_tokens < 0:
            raise ValueError("max_masked_tokens must be non-negative")
        if self.on_other_mismatch not in {"new_segment", "reject"}:
            raise ValueError(f"unknown mismatch disposition: {self.on_other_mismatch}")
        if lineage_mode == "linear":
            warnings.warn(
                "TITO linear lineage has been retired. This rollout uses tree lineage.",
                FutureWarning,
                stacklevel=3,
            )
        elif lineage_mode not in (None, "tree"):
            raise ValueError(f"unknown lineage mode: {lineage_mode}")


@dataclass(frozen=True)
class TITODistribution:
    count: int = 0
    sum: float = 0.0
    min: float | None = None
    max: float | None = None

    def add(self, value: float) -> "TITODistribution":
        return TITODistribution(
            count=self.count + 1,
            sum=self.sum + value,
            min=value if self.min is None else min(self.min, value),
            max=value if self.max is None else max(self.max, value),
        )

    def merge(self, other: "TITODistribution") -> "TITODistribution":
        if other.count == 0:
            return self
        if self.count == 0:
            return other
        return TITODistribution(
            count=self.count + other.count,
            sum=self.sum + other.sum,
            min=min(self.min, other.min),  # type: ignore[arg-type]
            max=max(self.max, other.max),  # type: ignore[arg-type]
        )


@dataclass(frozen=True)
class TITOMetricSummary:
    counters: Mapping[str, int]
    distributions: Mapping[str, TITODistribution]

    def flattened(self, root: str = "tito") -> dict[str, float]:
        output: dict[str, float] = {f"{root}/{name}": float(value) for name, value in self.counters.items()}
        for name, dist in self.distributions.items():
            prefix = f"{root}/{name}"
            output[f"{prefix}_count"] = float(dist.count)
            output[f"{prefix}_sum"] = dist.sum
            if dist.count:
                output[f"{prefix}_mean"] = dist.sum / dist.count
                output[f"{prefix}_min"] = float(dist.min)  # type: ignore[arg-type]
                output[f"{prefix}_max"] = float(dist.max)  # type: ignore[arg-type]
        return output


class _MetricAccumulator:
    def __init__(self) -> None:
        self.counters: dict[str, int] = {}
        self.distributions: dict[str, TITODistribution] = {}

    def increment(self, name: str, value: int = 1) -> None:
        self.counters[name] = self.counters.get(name, 0) + value

    def observe(self, name: str, value: float) -> None:
        observed = float(value)
        current = self.distributions.get(name)
        self.distributions[name] = (
            TITODistribution(count=1, sum=observed, min=observed, max=observed)
            if current is None
            else current.add(observed)
        )

    def snapshot(self) -> TITOMetricSummary:
        return TITOMetricSummary(
            counters=MappingProxyType(dict(self.counters)),
            distributions=MappingProxyType(dict(self.distributions)),
        )


@dataclass(frozen=True)
class TITOResponseAttempt:
    attempt_id: str
    turn_id: str
    emission: TITOEmission
    created_at: float


@dataclass(frozen=True)
class TITOCallRecord:
    call_id: str
    kind: TITOCallKind
    classification_source: str
    outcome: TITOCallOutcome
    started_at: float
    ended_at: float
    request_fingerprint: str | None = None
    prepared_prompt_hash: str | None = None
    turn_id: str | None = None
    logical_request_id: str | None = None
    upstream_response_id: str | None = None
    attempts: int = 0
    server_attempts: tuple[SampledServerAttempt, ...] = ()
    error_code: str | None = None


@dataclass(frozen=True)
class TITOTurn:
    turn_id: str
    request: TITOChatRequest
    assistant: TITOParsedAssistant
    exact_prompt_ids: tuple[int, ...]
    exact_completion_ids: tuple[int, ...]
    inference_logprobs: tuple[float, ...] | None
    sampling_logprobs: tuple[float | None, ...] | None
    routing_matrices: RoutingReferences | None
    response_id: str
    finish_reason: str
    prompt_disposition: TITOPromptDisposition
    prefix_match_tokens: int | None
    realign_from_token: int | None
    realigned_masked_tokens: int
    requested_output_tokens: int
    effective_output_tokens: int
    context_remaining_tokens: int
    server_metrics: ServerMetrics | None
    sampler_wall_seconds: float
    logical_request_id: str
    upstream_response_id: str | None
    upstream_attempts: int
    prompt_routing_start: int | None = None
    prompt_routing_matrices: RoutingReferences | None = None
    prompt_mode: TITOPromptMode = "full_history"
    incremental_contract_id: str | None = None
    incremental_junction_kind: str | None = None
    incremental_checkpoint_trim_tokens: int = 0
    incremental_fallback_reason: str | None = None
    server_attempts: tuple[SampledServerAttempt, ...] = ()
    parser_fallback: bool = False
    top_sampling_references: RoutingReferences | None = None
    sampling_mask_references: RoutingReferences | None = None
    sample_extra_references: RoutingReferences | None = None
    """Completion-only Parquet top-K sampling rows, one per ``exact_completion_ids`` token."""

    parent_turn_id: str | None = None

    @property
    def exact_checkpoint_ids(self) -> tuple[int, ...]:
        return self.exact_prompt_ids + self.exact_completion_ids


@dataclass(frozen=True)
class TITOSegmentResult:
    segment_id: str
    start_reason: str
    render_contract_id: str
    turns: tuple[TITOTurn, ...]
    closed_reason: str | None


@dataclass(frozen=True)
class TITOTrajectoryEndpoint:
    """Sidecar endpoint and credential for one independent trajectory."""

    trajectory_id: str
    openai_base_url: str
    api_key: str


# Only renderer rejections that identify a tool-call defect with a complete
# stop are eligible. Generic parse failures and length truncation stay failures.
_MALFORMED_TOOL_CALL_REASONS = frozenset(
    {
        "tool_missing_name",
        "tool_unknown_name",
        "tool_arguments_invalid_json",
        "tool_arguments_not_object",
    }
)


def _is_retained_tool_reason(failure: Mapping[str, Any]) -> bool:
    reason = failure.get("parser_reason_code")
    if failure.get("closed_tool_action") is False:
        return False
    return isinstance(reason, str) and (
        reason in _MALFORMED_TOOL_CALL_REASONS
        or (reason == "tool_invalid_argument" and failure.get("closed_tool_action") is True)
    )


def _has_exact_tool_sample(
    finish_reason: str, logprobs: Sequence[float | None] | None, completion_len: int
) -> bool:
    return (
        finish_reason in {"stop", "tool_calls"}
        and logprobs is not None
        and completion_len > 0
        and len(logprobs) == completion_len
        and all(isinstance(value, (int, float)) and math.isfinite(value) for value in logprobs)
    )


@dataclass(frozen=True)
class TITOMalformedToolCall:
    """A rejected terminal tool action with an exact retained policy turn."""

    turn_id: str
    reason_code: str


@dataclass(frozen=True)
class TITOTrajectoryArtifact:
    trajectory_id: str
    serving_affinity_key_hash: str
    metadata: Mapping[str, Any]
    status: Literal["completed", "abandoned", "failed"]
    terminal_reason: str | None
    segments: tuple[TITOSegmentResult, ...]
    calls: tuple[TITOCallRecord, ...]
    response_attempts: tuple[TITOResponseAttempt, ...]
    metrics: TITOMetricSummary
    started_at: float
    finished_at: float
    lineage_mode: Literal["tree"] = "tree"

    @property
    def malformed_tool_call(self) -> TITOMalformedToolCall | None:
        """Return the terminal malformed tool action, if its sample was retained."""
        if self.status != "failed" or self.terminal_reason != "tito_sdk_parse_error":
            return None
        failure = self.metadata.get("tito_failure")
        if not isinstance(failure, Mapping):
            return None
        reason = failure.get("parser_reason_code")
        if (
            failure.get("code") != "tito_sdk_parse_error"
            or failure.get("origin") != "sdk_parser"
            or failure.get("debug_storage_error") is not None
            or not isinstance(reason, str)
            or not _is_retained_tool_reason(failure)
        ):
            return None
        call_id = self.metadata.get("tito_malformed_tool_call_id")
        if not isinstance(call_id, str) or call_id != failure.get("call_id"):
            return None
        call = next(
            (item for item in self.calls if item.call_id == call_id),
            None,
        )
        if (
            call is None
            or call.kind != "policy"
            or call.classification_source == "fail_closed"
            or call.outcome != "model_malformed"
            or call.error_code != "tito_sdk_parse_error"
            or call.turn_id is None
        ):
            return None
        for segment in self.segments:
            if segment.closed_reason != "malformed_tool_call" or not segment.turns:
                continue
            turn = segment.turns[-1]
            if (
                turn.turn_id == call.turn_id
                and turn.assistant.output_kind == "malformed_tool_call"
                and _has_exact_tool_sample(turn.finish_reason, turn.sampling_logprobs, len(turn.exact_completion_ids))
            ):
                return TITOMalformedToolCall(turn_id=turn.turn_id, reason_code=reason)
        return None

    def continued_turn_ids(self) -> frozenset[str]:
        """Return assistant turns confirmed by a subsequent accepted request.

        Confirmation can cross a segment boundary. Response emission and
        harness acceptance are separate evidence for the caller to consider.
        Invalid tree parent links raise ValueError.
        """
        turns = tuple(turn for segment in self.segments for turn in segment.turns)
        by_id = {turn.turn_id: turn for turn in turns}
        if len(by_id) != len(turns):
            raise ValueError("tree trajectory contains duplicate turn IDs")
        continued = set()
        for segment in self.segments:
            prior = None
            for turn in segment.turns:
                if prior is not None and turn.parent_turn_id != prior.turn_id:
                    raise ValueError("tree turn does not continue its exact prior checkpoint")
                if turn.parent_turn_id is not None:
                    parent = by_id.get(turn.parent_turn_id)
                    if parent is None or not _request_continues_turn(parent, turn):
                        raise ValueError("tree parent does not match the accepted request history")
                    continued.add(parent.turn_id)
                prior = turn
        return frozenset(continued)

    def pack(self) -> bytes:
        """Encode this artifact as versioned compact bytes."""
        from fireworks.training.sdk.tito._artifact import pack_trajectory_artifact

        return pack_trajectory_artifact(self)

    @classmethod
    def unpack(cls, payload: bytes) -> "TITOTrajectoryArtifact":
        from fireworks.training.sdk.tito._artifact import unpack_trajectory_artifact

        return unpack_trajectory_artifact(payload)

    @classmethod
    def unpack_stream(
        cls,
        chunks: Iterable[bytes],
        *,
        expected_bytes: int,
        expected_sha256: str | None,
        max_expanded_bytes: int,
    ) -> "TITOTrajectoryArtifact":
        """Decode chunks with bounded expansion and full stream framing checks.

        Supply the manifest SHA-256 for untrusted input. Pass `None` only when
        the caller has already checked the digest and kept the bytes private
        and unchanged. Byte count, compression framing and decoded format are
        checked in either case.
        """
        from fireworks.training.sdk.tito._artifact import unpack_trajectory_stream

        return unpack_trajectory_stream(
            chunks,
            expected_bytes=expected_bytes,
            expected_sha256=expected_sha256,
            max_expanded_bytes=max_expanded_bytes,
        )


def _request_continues_turn(prior: TITOTurn, later: TITOTurn) -> bool:
    expected = (*prior.request.messages, prior.assistant.message)
    messages = later.request.messages
    return len(messages) >= len(expected) and all(actual == previous for actual, previous in zip(messages, expected))


@dataclass(frozen=True)
class TITOCallResult:
    response: Mapping[str, Any]
    call: TITOCallRecord
    turn_id: str | None
    replayed: bool = False


class TITOParseError(ValueError):
    """The renderer recognized malformed or protocol-unsafe sampled output."""

    def __init__(self, *args: object, reason_code: str = "unclassified") -> None:
        super().__init__(*args)
        self.reason_code = reason_code


class TITOError(RuntimeError):
    def __init__(
        self,
        code: str,
        status: int,
        message: str,
        *,
        should_retry: bool = False,
        origin: TITOErrorOrigin = "sdk",
        discard_trajectory: bool = False,
        context: Mapping[str, Any] | None = None,
    ) -> None:
        self.code = code
        self.status = status
        self.should_retry = should_retry
        self.origin = origin if origin in get_args(TITOErrorOrigin) else "unknown"
        self.discard_trajectory = discard_trajectory
        self.context = dict(context or {})
        super().__init__(message)

    def as_error_record(self) -> dict[str, Any]:
        if self.discard_trajectory:
            error_type = "trajectory_error"
        elif self.origin in {"server", "transport"}:
            error_type = "server_error"
        elif self.status >= 500:
            error_type = "sdk_error"
        else:
            error_type = "invalid_request_error"
        return {
            **self.context,
            "message": str(self),
            "type": error_type,
            "code": self.code,
            "origin": self.origin,
            "should_retry": self.should_retry,
            "discard_trajectory": self.discard_trajectory,
        }

    def openai_body(self) -> dict[str, Any]:
        return {"error": self.as_error_record()}

    def __reduce__(self) -> tuple:
        return type(self), (self.code, self.status, str(self)), self.__dict__
