"""Linear exact-token trajectory state machine."""

from __future__ import annotations

import time
import uuid
import asyncio
import hashlib
import secrets
from types import MappingProxyType
from typing import Any, Literal, Mapping, Callable, Protocol, Sequence
from functools import partial
from dataclasses import field, dataclass
from concurrent.futures import ThreadPoolExecutor

from fireworks.training.sdk.sampling import (
    ServerMetrics,
    SampledCompletion,
    SampledRequestResult,
    SampledServerAttempt,
)
from fireworks.training.sdk.tito._types import (
    TITOTurn,
    TITOError,
    TITOCallKind,
    TITOEmission,
    TITORenderer,
    TITOCallRecord,
    TITOCallResult,
    TITOPromptMode,
    TITOCallOutcome,
    TITOChatRequest,
    TITOSegmentResult,
    TITOClassification,
    TITOParsedAssistant,
    TITOResponseAttempt,
    TITOTrajectoryStatus,
    TITOIncrementalPrompt,
    TrajectoryDriftPolicy,
    TITOTrajectoryArtifact,
    TITOIncrementalRenderer,
    _hash_json,
    _plain_json,
    _freeze_json,
    _hash_tokens,
    _MetricAccumulator,
    _server_attempt_value,
)

# Rendering and durable debug writes are deliberately bounded and separated.
# One render worker preserves the renderer/tokenizer's existing serialized
# execution contract while allowing HTTP keepalives and other trajectories to
# keep making progress on the asyncio loop.
_TITO_RENDER_EXECUTOR = ThreadPoolExecutor(max_workers=1, thread_name_prefix="tito-render")
_TITO_OBSERVER_EXECUTOR = ThreadPoolExecutor(max_workers=1, thread_name_prefix="tito-observer")


@dataclass
class _Segment:
    segment_id: str
    start_reason: str
    render_contract_id: str
    turns: list[TITOTurn] = field(default_factory=list)
    closed_reason: str | None = None


@dataclass(frozen=True)
class _LastCall:
    idempotency_key: str
    request_fingerprint: str
    prepared_prompt_hash: str
    turn_id: str
    response: Mapping[str, Any]


@dataclass
class _TrajectoryState:
    trajectory_id: str
    serving_affinity_key: str
    metadata: Mapping[str, Any]
    drift_policy: TrajectoryDriftPolicy
    started_at: float
    segments: list[_Segment] = field(default_factory=list)
    calls: list[TITOCallRecord] = field(default_factory=list)
    response_attempts: list[TITOResponseAttempt] = field(default_factory=list)
    last_call: _LastCall | None = None
    policy_lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    policy_waiters: set[asyncio.Task[Any]] = field(default_factory=set)
    policy_in_flight: bool = False
    policy_task: asyncio.Task[Any] | None = None
    auxiliary_tasks: set[asyncio.Task[Any]] = field(default_factory=set)
    transport_tasks: set[asyncio.Task[Any]] = field(default_factory=set)
    terminalizing: bool = False
    last_policy_commit_at: float | None = None
    sampler_calls: int = 0
    metrics: _MetricAccumulator = field(default_factory=_MetricAccumulator)

    @property
    def active_segment(self) -> _Segment | None:
        if not self.segments or self.segments[-1].closed_reason is not None:
            return None
        return self.segments[-1]


@dataclass
class _Tombstone:
    status: TITOTrajectoryStatus
    reason: str | None
    terminal_at: float
    metrics: _MetricAccumulator


@dataclass(frozen=True)
class _TurnPlan:
    request: TITOChatRequest
    render_contract_id: str
    request_fingerprint: str
    prepared_prompt_ids: tuple[int, ...]
    prepared_prompt_hash: str
    prompt_disposition: Literal["append", "realign", "new_segment"]
    prefix_match_tokens: int | None
    realign_from_token: int | None
    realigned_masked_tokens: int
    prompt_mode: TITOPromptMode
    incremental_contract_id: str | None
    incremental_junction_kind: str | None
    incremental_checkpoint_trim_tokens: int
    incremental_fallback_reason: str | None
    segment: _Segment | None
    start_reason: str | None
    close_reason: str | None
    requested_output_tokens: int
    effective_output_tokens: int
    context_remaining_tokens: int


class TITOEventObserver(Protocol):
    def record(
        self,
        event: str,
        trajectory_id: str,
        payload: Mapping[str, Any],
        arrays: Mapping[str, Sequence[Any]] | None = None,
    ) -> int | None: ...

    def close_trajectory(
        self,
        trajectory_id: str,
        status: str,
        payload: Mapping[str, Any] | None = None,
    ) -> int | None: ...

    def record_tombstone_event(
        self,
        event: str,
        trajectory_id: str,
        payload: Mapping[str, Any],
    ) -> int | None: ...


class _ExactTokenSampler(Protocol):
    """Small sampling boundary required by the TITO transaction core."""

    model: str

    async def sample_with_prompt_tokens_result(
        self,
        prompt_token_ids: list[int],
        **kwargs: Any,
    ) -> SampledRequestResult: ...


class _LinearTrajectoryCore:
    """Serialized exact-token transaction core for exactly one trajectory."""

    def __init__(
        self,
        sampler: _ExactTokenSampler,
        renderer: TITORenderer,
        *,
        max_context_tokens: int,
        max_output_tokens: int,
        call_classifier: Callable[[TITOChatRequest], TITOClassification] | None = None,
        sampling_defaults: Mapping[str, Any] | None = None,
        backend_headers_snapshot: Mapping[str, str] | None = None,
        observer: TITOEventObserver | None = None,
        default_drift_policy: TrajectoryDriftPolicy | None = None,
        prompt_mode: TITOPromptMode = "full_history",
    ) -> None:
        if max_context_tokens < 2 or max_output_tokens < 1:
            raise ValueError("invalid context/output token limits")
        if not isinstance(renderer, TITORenderer):
            raise TypeError("renderer does not implement the TITO renderer protocol")
        if prompt_mode not in {"full_history", "incremental"}:
            raise ValueError(f"unknown TITO prompt mode: {prompt_mode!r}")
        if prompt_mode == "incremental" and not isinstance(renderer, TITOIncrementalRenderer):
            raise TypeError("experimental incremental prompt mode requires an incremental renderer")
        self.sampler = sampler
        self.renderer = renderer
        self.prompt_mode = prompt_mode
        self.max_context_tokens = max_context_tokens
        self.max_output_tokens = max_output_tokens
        self.call_classifier = call_classifier
        defaults = dict(sampling_defaults or {})
        default_temperature = defaults.pop("temperature", None)
        self.default_temperature = None if default_temperature is None else float(default_temperature)
        reserved_defaults = sorted(
            name
            for name in (
                "prompt_cache_key",
                "prompt_cache_isolation_key",
                "user",
                "additional_headers_snapshot",
                "logical_request_id",
            )
            if name in defaults
        )
        if reserved_defaults:
            raise ValueError("sampling_defaults cannot set sidecar-owned fields: " + ", ".join(reserved_defaults))
        for name in ("max_seq_len", "max_tokens", "n", "echo", "stop"):
            defaults.pop(name, None)
        defaults["logprobs"] = True
        self.sampling_defaults = MappingProxyType(_freeze_json(defaults))
        self._backend_headers_snapshot = MappingProxyType(dict(backend_headers_snapshot or {}))
        self.observer = observer
        self.default_drift_policy = default_drift_policy or TrajectoryDriftPolicy()
        self._state: _TrajectoryState | None = None
        self._tombstone: _Tombstone | None = None
        self._trajectory_id: str | None = None
        self._closing = False

    def _allocate_trajectory(
        self,
        *,
        trajectory_id: str | None = None,
        serving_affinity_key: str | None = None,
        metadata: Mapping[str, Any] | None = None,
        drift_policy: TrajectoryDriftPolicy | None = None,
    ) -> _TrajectoryState:
        if self._closing:
            raise TITOError("tito_sidecar_closed", 503, "sidecar is shutting down")
        trajectory_id = trajectory_id or uuid.uuid4().hex
        if self._trajectory_id is not None:
            raise RuntimeError("trajectory engine is already bound")
        state = _TrajectoryState(
            trajectory_id=trajectory_id,
            serving_affinity_key=serving_affinity_key or secrets.token_urlsafe(24),
            metadata=MappingProxyType(_freeze_json(metadata or {})),
            drift_policy=drift_policy or self.default_drift_policy,
            started_at=time.time(),
        )
        state.metrics.increment("cache/affinity_bound")
        self._state = state
        self._trajectory_id = trajectory_id
        return state

    def _trajectory_open_payload(self, state: _TrajectoryState) -> Mapping[str, Any]:
        return {
            "metadata": dict(state.metadata),
            "renderer_id": self.renderer.renderer_id,
            "model": str(getattr(self.sampler, "model", "policy")),
            "max_context_tokens": self.max_context_tokens,
            "max_output_tokens": self.max_output_tokens,
            "prompt_mode": self.prompt_mode,
            "serving_affinity_key_hash": hashlib.sha256(state.serving_affinity_key.encode("utf-8")).hexdigest(),
            "drift_policy": {
                "max_masked_tokens": state.drift_policy.max_masked_tokens,
                "on_other_mismatch": state.drift_policy.on_other_mismatch,
            },
        }

    def create_trajectory(
        self,
        *,
        trajectory_id: str | None = None,
        serving_affinity_key: str | None = None,
        metadata: Mapping[str, Any] | None = None,
        drift_policy: TrajectoryDriftPolicy | None = None,
    ) -> str:
        state = self._allocate_trajectory(
            trajectory_id=trajectory_id,
            serving_affinity_key=serving_affinity_key,
            metadata=metadata,
            drift_policy=drift_policy,
        )
        try:
            self._record(state, "trajectory_open", self._trajectory_open_payload(state))
        except Exception:
            self._state = None
            self._trajectory_id = None
            raise
        return state.trajectory_id

    async def create_trajectory_async(
        self,
        *,
        trajectory_id: str | None = None,
        serving_affinity_key: str | None = None,
        metadata: Mapping[str, Any] | None = None,
        drift_policy: TrajectoryDriftPolicy | None = None,
    ) -> str:
        state = self._allocate_trajectory(
            trajectory_id=trajectory_id,
            serving_affinity_key=serving_affinity_key,
            metadata=metadata,
            drift_policy=drift_policy,
        )
        try:
            await self._record_async(state, "trajectory_open", self._trajectory_open_payload(state))
        except BaseException:
            self._state = None
            self._trajectory_id = None
            raise
        return state.trajectory_id

    def _record(
        self,
        state: _TrajectoryState,
        event: str,
        payload: Mapping[str, Any],
        arrays: Mapping[str, Sequence[Any]] | None = None,
    ) -> None:
        if self.observer is not None:
            started = time.monotonic()
            try:
                bytes_written = self.observer.record(event, state.trajectory_id, payload, arrays)
            except Exception as exc:
                if getattr(exc, "storage_full", False):
                    state.metrics.increment("debug/storage_full")
                state.metrics.increment("debug/write_failed")
                raise TITOError(
                    "tito_debug_storage_error",
                    507,
                    f"local TITO debug write failed: {exc}",
                ) from exc
            state.metrics.increment("debug/events_written")
            state.metrics.observe("debug/write_seconds", time.monotonic() - started)
            if bytes_written is not None:
                state.metrics.observe("debug/bytes_written", bytes_written)

    async def _record_async(
        self,
        state: _TrajectoryState,
        event: str,
        payload: Mapping[str, Any],
        arrays: Mapping[str, Sequence[Any]] | None = None,
    ) -> None:
        observer = self.observer
        if observer is None:
            return
        started = time.monotonic()
        cancelled: asyncio.CancelledError | None = None
        operation = asyncio.get_running_loop().run_in_executor(
            _TITO_OBSERVER_EXECUTOR,
            partial(observer.record, event, state.trajectory_id, payload, arrays),
        )
        try:
            # Cancellation must not split the debug barrier from the state
            # transition it guards. The writer operation cannot be cancelled
            # once its worker has started, so finish observing its result before
            # propagating cancellation to the caller.
            while True:
                try:
                    bytes_written = await asyncio.shield(operation)
                    break
                except asyncio.CancelledError as exc:
                    cancelled = exc
        except Exception as exc:
            if getattr(exc, "storage_full", False):
                state.metrics.increment("debug/storage_full")
            state.metrics.increment("debug/write_failed")
            raise TITOError(
                "tito_debug_storage_error",
                507,
                f"local TITO debug write failed: {exc}",
            ) from exc
        state.metrics.increment("debug/events_written")
        state.metrics.observe("debug/write_seconds", time.monotonic() - started)
        if bytes_written is not None:
            state.metrics.observe("debug/bytes_written", bytes_written)
        if cancelled is not None:
            raise cancelled

    async def _record_and_apply_async(
        self,
        state: _TrajectoryState,
        event: str,
        payload: Mapping[str, Any],
        arrays: Mapping[str, Sequence[Any]] | None,
        apply: Callable[[], Any],
        *,
        return_after_cancelled_commit: bool = False,
    ) -> Any:
        """Keep one durable event and its in-memory transition cancellation-atomic."""

        async def operation() -> Any:
            await self._record_async(state, event, payload, arrays)
            return apply()

        task = asyncio.create_task(operation())
        cancelled: asyncio.CancelledError | None = None
        while True:
            try:
                result = await asyncio.shield(task)
                break
            except asyncio.CancelledError as exc:
                cancelled = exc
        if cancelled is not None and not return_after_cancelled_commit:
            raise cancelled
        return result

    async def _render_full(
        self,
        state: _TrajectoryState,
        request: TITOChatRequest,
    ) -> tuple[int, ...]:
        submitted_at = time.monotonic()
        queue_seconds: list[float] = []
        render_seconds: list[float] = []

        def render() -> Sequence[int]:
            queue_seconds.append(time.monotonic() - submitted_at)
            started_at = time.monotonic()
            try:
                return self.renderer.render_conversation_tokens(request)
            finally:
                render_seconds.append(time.monotonic() - started_at)

        try:
            rendered = await asyncio.get_running_loop().run_in_executor(
                _TITO_RENDER_EXECUTOR,
                render,
            )
            return tuple(int(token) for token in rendered)
        finally:
            if queue_seconds:
                state.metrics.observe("renderer/render_queue_seconds", queue_seconds[0])
            if render_seconds:
                state.metrics.observe("renderer/full_render_seconds", render_seconds[0])

    async def _render_incremental(
        self,
        state: _TrajectoryState,
        request: TITOChatRequest,
        stored_messages: Sequence[Mapping[str, Any]],
        appended_messages: Sequence[Mapping[str, Any]],
        exact_checkpoint_ids: Sequence[int],
    ) -> TITOIncrementalPrompt | None:
        renderer = self.renderer
        if not isinstance(renderer, TITOIncrementalRenderer):
            raise RuntimeError("incremental renderer capability disappeared")
        submitted_at = time.monotonic()
        queue_seconds: list[float] = []
        render_seconds: list[float] = []

        def render() -> TITOIncrementalPrompt | None:
            queue_seconds.append(time.monotonic() - submitted_at)
            started_at = time.monotonic()
            try:
                return renderer.prepare_incremental_prompt(
                    request,
                    stored_messages,
                    appended_messages,
                    exact_checkpoint_ids,
                )
            finally:
                render_seconds.append(time.monotonic() - started_at)

        try:
            return await asyncio.get_running_loop().run_in_executor(
                _TITO_RENDER_EXECUTOR,
                render,
            )
        finally:
            if queue_seconds:
                state.metrics.observe("renderer/render_queue_seconds", queue_seconds[0])
            if render_seconds:
                state.metrics.observe("renderer/incremental_render_seconds", render_seconds[0])

    def _record_tombstone_event(
        self,
        trajectory_id: str,
        tombstone: _Tombstone,
        event: str,
        payload: Mapping[str, Any],
    ) -> None:
        if self.observer is None:
            return
        record = getattr(self.observer, "record_tombstone_event", None)
        if record is None:
            # Completed trajectory evidence is immutable. Observers predating
            # the writer-level tombstone channel therefore omit this optional
            # event instead of reopening a terminal trajectory artifact.
            return
        started = time.monotonic()
        try:
            bytes_written = record(event, trajectory_id, payload)
        except Exception as exc:
            if getattr(exc, "storage_full", False):
                tombstone.metrics.increment("debug/storage_full")
            tombstone.metrics.increment("debug/write_failed")
            # The lifecycle contract wins after terminalization: a late call
            # must remain the exact non-retryable 410 and can never resurrect
            # or replace the completed trajectory. The failed optional
            # writer-level audit is visible in the retained debug counters.
            return
        tombstone.metrics.increment("debug/events_written")
        tombstone.metrics.observe("debug/write_seconds", time.monotonic() - started)
        if bytes_written is not None:
            tombstone.metrics.observe("debug/bytes_written", bytes_written)

    def _require_active(
        self,
        trajectory_id: str,
        *,
        count_terminal_request: bool = False,
        request_started_at: float | None = None,
    ) -> _TrajectoryState:
        state = self._state
        if state is not None and state.trajectory_id == trajectory_id:
            if state.terminalizing:
                raise TITOError(
                    "tito_trajectory_closed",
                    410,
                    "trajectory terminalization is in progress",
                )
            return state
        tombstone = self._tombstone
        if tombstone is not None and self._trajectory_id == trajectory_id:
            if count_terminal_request:
                tombstone.metrics.increment("calls/total")
                tombstone.metrics.increment("calls/policy")
                tombstone.metrics.increment("calls/rejected")
                tombstone.metrics.increment("admission/trajectory_closed")
                tombstone.metrics.observe(
                    "calls/request_wall_seconds",
                    max(0.0, time.time() - (request_started_at or time.time())),
                )
                self._record_tombstone_event(
                    trajectory_id,
                    tombstone,
                    "request_rejected",
                    {
                        "call_kind": "policy",
                        "outcome": "rejected",
                        "error_code": "tito_trajectory_closed",
                        "terminal_status": tombstone.status,
                    },
                )
            raise TITOError(
                "tito_trajectory_closed",
                410,
                f"trajectory is already {tombstone.status}",
            )
        raise TITOError("tito_trajectory_not_found", 404, "unknown trajectory")

    def _account_normalization_reject(
        self,
        trajectory_id: str,
        *,
        started_at: float,
        error: BaseException,
        wire_request: Any = None,
        wire_request_body: str | None = None,
    ) -> tuple[_TrajectoryState, Mapping[str, Any]]:
        state = self._require_active(
            trajectory_id,
            count_terminal_request=True,
            request_started_at=started_at,
        )
        state.metrics.increment("calls/total")
        state.metrics.increment("calls/policy")
        state.metrics.increment("calls/rejected")
        state.metrics.increment("admission/normalization_reject")
        state.metrics.observe("calls/request_wall_seconds", max(0.0, time.time() - started_at))
        return state, {
            "call_kind": "policy",
            "classification_source": "normalization_fail_closed",
            "outcome": "rejected",
            "error_code": "tito_invalid_request",
            "phase": "normalization",
            "error": {
                "type": type(error).__name__,
                "message": str(error)[:2000],
            },
            "wire_request": _plain_json(wire_request),
            "wire_request_body": wire_request_body,
        }

    def record_normalization_reject(
        self,
        trajectory_id: str,
        *,
        started_at: float,
        error: BaseException,
        wire_request: Any = None,
        wire_request_body: str | None = None,
    ) -> None:
        """Account for an authenticated wire request that cannot normalize."""
        state, payload = self._account_normalization_reject(
            trajectory_id,
            started_at=started_at,
            error=error,
            wire_request=wire_request,
            wire_request_body=wire_request_body,
        )
        self._record(state, "request_rejected", payload)

    async def record_normalization_reject_async(
        self,
        trajectory_id: str,
        *,
        started_at: float,
        error: BaseException,
        wire_request: Any = None,
        wire_request_body: str | None = None,
    ) -> None:
        """Async transport path for a request that cannot normalize."""
        state, payload = self._account_normalization_reject(
            trajectory_id,
            started_at=started_at,
            error=error,
            wire_request=wire_request,
            wire_request_body=wire_request_body,
        )
        await self._record_async(state, "request_rejected", payload)

    def _classify(
        self,
        request: TITOChatRequest,
    ) -> tuple[TITOCallKind, str, Mapping[str, str] | None]:
        if self.call_classifier is None:
            return "policy", "default", None
        try:
            classified = self.call_classifier(request)
            if isinstance(classified, tuple):
                value, source = classified
            else:
                value, source = classified, "adapter"
            if value not in {"policy", "auxiliary"}:
                raise ValueError(f"unknown classifier result {value!r}")
            if not source:
                raise ValueError("classifier source must not be empty")
            return value, str(source), None
        except Exception as error:
            return (
                "policy",
                "fail_closed",
                {
                    "type": type(error).__name__,
                    "message": str(error)[:2000],
                },
            )

    @staticmethod
    def _request_fingerprint(request: TITOChatRequest, contract: str) -> str:
        return _hash_json(
            {
                "render_contract_id": contract,
                "request": request.canonical_value(),
                "sampling": request.sampling_value(),
            }
        )

    @staticmethod
    def _history_for_segment(segment: _Segment) -> tuple[Mapping[str, Any], ...]:
        if not segment.turns:
            return ()
        last = segment.turns[-1]
        return last.request.messages + (last.assistant.message,)

    @staticmethod
    def _history_extends(
        stored: Sequence[Mapping[str, Any]],
        incoming: Sequence[Mapping[str, Any]],
    ) -> bool:
        return len(incoming) >= len(stored) and tuple(incoming[: len(stored)]) == tuple(stored)

    @staticmethod
    def _history_rewrite_kind(
        stored: Sequence[Mapping[str, Any]],
        incoming: Sequence[Mapping[str, Any]],
    ) -> Literal["prior_context", "assistant_roundtrip", "truncated"]:
        """Classify the first canonical message-level lineage discontinuity."""

        for index, (stored_message, incoming_message) in enumerate(zip(stored, incoming)):
            if stored_message != incoming_message:
                if index == len(stored) - 1:
                    return "assistant_roundtrip"
                return "prior_context"
        return "truncated"

    @staticmethod
    def _common_prefix_tokens(left: Sequence[int], right: Sequence[int]) -> int:
        matched = 0
        limit = min(len(left), len(right))
        while matched < limit and left[matched] == right[matched]:
            matched += 1
        return matched

    def _turn_plan(
        self,
        state: _TrajectoryState,
        request: TITOChatRequest,
        contract: str,
        fingerprint: str,
        prompt: Sequence[int],
        *,
        prompt_disposition: Literal["append", "realign", "new_segment"],
        prefix_match_tokens: int | None,
        realign_from_token: int | None,
        realigned_masked_tokens: int,
        prompt_mode: TITOPromptMode = "full_history",
        incremental_contract_id: str | None = None,
        incremental_junction_kind: str | None = None,
        incremental_checkpoint_trim_tokens: int = 0,
        incremental_fallback_reason: str | None = None,
        segment: _Segment | None,
        start_reason: str | None,
        close_reason: str | None,
    ) -> _TurnPlan:
        prompt_ids = tuple(int(token) for token in prompt)
        requested, effective, remaining = self._budget(state, request, len(prompt_ids))
        return _TurnPlan(
            request=request,
            render_contract_id=contract,
            request_fingerprint=fingerprint,
            prepared_prompt_ids=prompt_ids,
            prepared_prompt_hash=_hash_tokens(prompt_ids),
            prompt_disposition=prompt_disposition,
            prefix_match_tokens=prefix_match_tokens,
            realign_from_token=realign_from_token,
            realigned_masked_tokens=realigned_masked_tokens,
            prompt_mode=prompt_mode,
            incremental_contract_id=incremental_contract_id,
            incremental_junction_kind=incremental_junction_kind,
            incremental_checkpoint_trim_tokens=incremental_checkpoint_trim_tokens,
            incremental_fallback_reason=incremental_fallback_reason,
            segment=segment,
            start_reason=start_reason,
            close_reason=close_reason,
            requested_output_tokens=requested,
            effective_output_tokens=effective,
            context_remaining_tokens=remaining,
        )

    def _budget(self, state: _TrajectoryState, request: TITOChatRequest, prompt_tokens: int) -> tuple[int, int, int]:
        requested = self.max_output_tokens if request.max_tokens is None else request.max_tokens
        client_capped = min(requested, self.max_output_tokens)
        remaining = self.max_context_tokens - prompt_tokens
        if remaining <= 0:
            state.metrics.increment("budget/context_overflow")
            raise TITOError(
                "tito_context_overflow",
                400,
                "prepared prompt exhausts the model context",
            )
        effective = min(client_capped, remaining)
        if effective < requested and client_capped < requested:
            state.metrics.increment("budget/output_capped_by_sidecar_limit")
        if effective < client_capped:
            state.metrics.increment("budget/output_capped_by_context_limit")
        return requested, effective, remaining

    async def _prepare_policy(
        self,
        state: _TrajectoryState,
        request: TITOChatRequest,
        contract: str,
        fingerprint: str,
    ) -> _TurnPlan:
        # Preserve the original full-history admission path exactly: render the
        # complete request before inspecting lineage state. Incremental mode is
        # the only mode allowed to defer that render and construct a suffix.
        full_prompt = await self._render_full(state, request) if self.prompt_mode == "full_history" else None
        active = state.active_segment
        if active is None:
            start_reason = "initial"
            if state.segments:
                start_reason = state.segments[-1].closed_reason or "closed_segment"
            if full_prompt is None:
                full_prompt = await self._render_full(state, request)
            return self._turn_plan(
                state,
                request,
                contract,
                fingerprint,
                full_prompt,
                prompt_disposition="new_segment",
                prefix_match_tokens=None,
                realign_from_token=None,
                realigned_masked_tokens=0,
                segment=None,
                start_reason=start_reason,
                close_reason=None,
            )

        if active.render_contract_id != contract:
            state.metrics.increment("lineage/boundary_reason_contract_change")
            if state.drift_policy.on_other_mismatch == "reject":
                state.metrics.increment("lineage/reject")
                raise TITOError(
                    "tito_lineage_divergence",
                    409,
                    "incoming request changes the active render contract",
                )
            if full_prompt is None:
                full_prompt = await self._render_full(state, request)
            return self._turn_plan(
                state,
                request,
                contract,
                fingerprint,
                full_prompt,
                prompt_disposition="new_segment",
                prefix_match_tokens=None,
                realign_from_token=None,
                realigned_masked_tokens=0,
                incremental_fallback_reason=("contract_change" if self.prompt_mode == "incremental" else None),
                segment=None,
                start_reason="contract_change",
                close_reason="contract_change",
            )

        last = active.turns[-1]
        stored_history = self._history_for_segment(active)
        if not self._history_extends(stored_history, request.messages):
            state.metrics.increment("lineage/boundary_reason_history_rewrite")
            rewrite_kind = self._history_rewrite_kind(stored_history, request.messages)
            state.metrics.increment(f"lineage/history_rewrite_{rewrite_kind}")
            if state.drift_policy.on_other_mismatch == "reject":
                state.metrics.increment("lineage/reject")
                raise TITOError(
                    "tito_lineage_divergence",
                    409,
                    "incoming history does not extend the active segment",
                )
            if full_prompt is None:
                full_prompt = await self._render_full(state, request)
            return self._turn_plan(
                state,
                request,
                contract,
                fingerprint,
                full_prompt,
                prompt_disposition="new_segment",
                prefix_match_tokens=None,
                realign_from_token=None,
                realigned_masked_tokens=0,
                incremental_fallback_reason=("history_rewrite" if self.prompt_mode == "incremental" else None),
                segment=None,
                start_reason="history_rewrite",
                close_reason="history_rewrite",
            )

        exact_checkpoint = last.exact_checkpoint_ids
        if self.prompt_mode == "incremental":
            appended_messages = request.messages[len(stored_history) :]
            prepared = await self._render_incremental(
                state,
                request,
                stored_history,
                appended_messages,
                exact_checkpoint,
            )
            if prepared is None:
                state.metrics.increment("lineage/boundary_reason_incremental_unsupported")
                if state.drift_policy.on_other_mismatch == "reject":
                    state.metrics.increment("lineage/reject")
                    raise TITOError(
                        "tito_lineage_divergence",
                        409,
                        "experimental incremental renderer cannot join this request",
                    )
                full_prompt = await self._render_full(state, request)
                return self._turn_plan(
                    state,
                    request,
                    contract,
                    fingerprint,
                    full_prompt,
                    prompt_disposition="new_segment",
                    prefix_match_tokens=None,
                    realign_from_token=None,
                    realigned_masked_tokens=0,
                    incremental_fallback_reason="unsupported_incremental_join",
                    segment=None,
                    start_reason="incremental_unsupported",
                    close_reason="incremental_unsupported",
                )

            # Miles Session v2 is the mechanism reference for this experimental
            # path: construct a suffix under a synthetic assistant anchor, then
            # let the model renderer own one bounded junction edit. Fireworks
            # intentionally retains only linear lineage, not Miles's tree.
            prompt = prepared.prompt_ids
            trim_tokens = prepared.checkpoint_trim_tokens
            checkpoint_length = len(exact_checkpoint)
            if trim_tokens > checkpoint_length or trim_tokens > len(last.exact_completion_ids):
                state.metrics.increment("renderer/incremental_contract_error")
                raise TITOError(
                    "tito_renderer_contract_error",
                    500,
                    "incremental renderer trimmed beyond the prior completion boundary",
                )
            retained_length = checkpoint_length - trim_tokens
            if len(prompt) <= retained_length or prompt[:retained_length] != exact_checkpoint[:retained_length]:
                state.metrics.increment("renderer/incremental_contract_error")
                raise TITOError(
                    "tito_renderer_contract_error",
                    500,
                    "incremental renderer exceeded its declared checkpoint junction",
                )
            prefix_match_tokens = self._common_prefix_tokens(exact_checkpoint, prompt)
            state.metrics.increment("lineage/prefix_check")
            return self._turn_plan(
                state,
                request,
                contract,
                fingerprint,
                prompt,
                prompt_disposition="append",
                prefix_match_tokens=prefix_match_tokens,
                realign_from_token=None,
                realigned_masked_tokens=0,
                prompt_mode="incremental",
                incremental_contract_id=prepared.contract_id,
                incremental_junction_kind=prepared.junction_kind,
                incremental_checkpoint_trim_tokens=trim_tokens,
                segment=active,
                start_reason=None,
                close_reason=None,
            )

        if full_prompt is None:
            raise RuntimeError("full-history prompt was not prepared")
        state.metrics.increment("lineage/prefix_check")
        prefix_match_tokens = self._common_prefix_tokens(exact_checkpoint, full_prompt)
        if prefix_match_tokens == len(exact_checkpoint):
            return self._turn_plan(
                state,
                request,
                contract,
                fingerprint,
                full_prompt,
                prompt_disposition="append",
                prefix_match_tokens=prefix_match_tokens,
                realign_from_token=None,
                realigned_masked_tokens=0,
                segment=active,
                start_reason=None,
                close_reason=None,
            )

        state.metrics.increment("lineage/prefix_mismatch")
        response_start = len(last.exact_prompt_ids)
        masked_tokens = len(full_prompt) - response_start
        can_realign = prefix_match_tokens >= response_start and masked_tokens < state.drift_policy.max_masked_tokens
        if can_realign:
            return self._turn_plan(
                state,
                request,
                contract,
                fingerprint,
                full_prompt,
                prompt_disposition="realign",
                prefix_match_tokens=prefix_match_tokens,
                realign_from_token=response_start,
                realigned_masked_tokens=masked_tokens,
                segment=active,
                start_reason=None,
                close_reason=None,
            )

        state.metrics.increment("lineage/boundary_reason_unbounded_or_ambiguous_drift")
        if state.drift_policy.on_other_mismatch == "reject":
            state.metrics.increment("lineage/reject")
            raise TITOError(
                "tito_lineage_divergence",
                409,
                "full-rendered prompt does not safely extend the active segment",
            )
        return self._turn_plan(
            state,
            request,
            contract,
            fingerprint,
            full_prompt,
            prompt_disposition="new_segment",
            prefix_match_tokens=prefix_match_tokens,
            realign_from_token=None,
            realigned_masked_tokens=0,
            segment=None,
            start_reason="token_drift",
            close_reason="token_drift",
        )

    def _validate_completion(
        self,
        plan: _TurnPlan,
        result: SampledRequestResult,
        include_routing_matrix: bool,
    ) -> SampledCompletion:
        if len(result.completions) != 1:
            raise TITOError(
                "tito_sampler_contract_error",
                502,
                f"expected one completion, got {len(result.completions)}",
            )
        completion = result.completions[0]
        prompt = tuple(completion.full_tokens[: completion.prompt_len])
        output = tuple(completion.full_tokens[completion.prompt_len :])
        if prompt != plan.prepared_prompt_ids:
            raise TITOError(
                "tito_prompt_mismatch",
                502,
                "deployment returned prompt IDs that differ from the prepared prompt",
            )
        if len(output) != completion.completion_len:
            raise TITOError(
                "tito_completion_alignment_error",
                502,
                "completion token count is inconsistent",
            )
        if not output:
            raise TITOError(
                "tito_completion_alignment_error",
                502,
                "deployment returned an empty completion",
            )
        if len(output) > plan.effective_output_tokens:
            raise TITOError(
                "tito_completion_alignment_error",
                502,
                "deployment returned more completion IDs than the effective output budget",
            )
        if len(prompt) + len(output) > self.max_context_tokens:
            raise TITOError(
                "tito_completion_alignment_error",
                502,
                "deployment response exceeds the sidecar context budget",
            )
        for name, values in (
            ("inference_logprobs", completion.inference_logprobs),
            ("sampling_logprobs", completion.sampling_logprobs),
        ):
            if values is not None and len(values) != len(output):
                raise TITOError(
                    "tito_completion_alignment_error",
                    502,
                    f"{name} is not aligned with completion token IDs",
                )
        if include_routing_matrix and (
            completion.routing_matrices is None or len(completion.routing_matrices) != len(output)
        ):
            raise TITOError(
                "tito_completion_alignment_error",
                502,
                "completion-only routing matrices are not aligned with completion IDs",
            )
        return completion

    def _parse(self, request: TITOChatRequest, completion: SampledCompletion) -> TITOParsedAssistant:
        completion_ids = completion.full_tokens[completion.prompt_len :]
        try:
            return self.renderer.parse_assistant(
                request,
                completion_ids,
                completion.text,
                completion.finish_reason,
            )
        except Exception as parser_error:
            fallback = self.renderer.fallback_assistant_text(
                request,
                completion_ids,
                completion.finish_reason,
                parser_error,
            )
            if fallback is None:
                raise TITOError(
                    "tito_model_malformed_output",
                    502,
                    "assistant output cannot be represented losslessly on this protocol",
                ) from parser_error
            return TITOParsedAssistant(
                message={"role": "assistant", "content": fallback},
                output_kind="text",
                parser_fallback=True,
            )

    @staticmethod
    def _response(
        turn_id: str,
        parsed: TITOParsedAssistant,
        finish_reason: str,
        model: str,
    ) -> dict[str, Any]:
        return {
            "id": f"chatcmpl-{turn_id}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": dict(parsed.message),
                    "finish_reason": finish_reason,
                }
            ],
        }

    def _call_record(
        self,
        state: _TrajectoryState,
        *,
        call_id: str,
        kind: TITOCallKind,
        classification_source: str,
        outcome: TITOCallOutcome,
        started_at: float,
        fingerprint: str | None = None,
        prompt_hash: str | None = None,
        turn_id: str | None = None,
        sampled: SampledRequestResult | None = None,
        sampler_wall_seconds: float | None = None,
        logical_request_id: str | None = None,
        attempts: int | None = None,
        server_attempts: Sequence[SampledServerAttempt] | None = None,
        error_code: str | None = None,
    ) -> TITOCallRecord:
        record = TITOCallRecord(
            call_id=call_id,
            kind=kind,
            classification_source=classification_source,
            outcome=outcome,
            started_at=started_at,
            ended_at=time.time(),
            request_fingerprint=fingerprint,
            prepared_prompt_hash=prompt_hash,
            turn_id=turn_id,
            logical_request_id=sampled.logical_request_id if sampled else logical_request_id,
            upstream_response_id=sampled.upstream_response_id if sampled else None,
            attempts=sampled.attempts if sampled else int(attempts or 0),
            server_attempts=(sampled.server_attempts if sampled is not None else tuple(server_attempts or ())),
            error_code=error_code,
        )
        state.calls.append(record)
        state.metrics.increment(f"calls/{outcome}")
        state.metrics.observe("calls/request_wall_seconds", record.ended_at - started_at)
        if sampled is not None:
            state.metrics.observe("calls/sampler_wall_seconds", sampled.wall_seconds)
            state.metrics.increment("calls/upstream_retry_attempts", sampled.attempts - 1)
        elif sampler_wall_seconds is not None:
            state.metrics.observe("calls/sampler_wall_seconds", sampler_wall_seconds)
            if attempts is not None:
                state.metrics.increment("calls/upstream_retry_attempts", max(0, attempts - 1))
        return record

    async def _record_call_terminal(
        self,
        state: _TrajectoryState,
        *,
        event: str,
        call_id: str,
        kind: TITOCallKind,
        classification_source: str,
        outcome: TITOCallOutcome,
        started_at: float,
        fingerprint: str | None,
        prompt_hash: str | None,
        sampled: SampledRequestResult | None,
        sampler_wall_seconds: float | None,
        error_code: str,
        error: BaseException,
        phase: str,
        request: TITOChatRequest | None = None,
        logical_request_id: str | None = None,
        attempts: int | None = None,
        server_attempts: Sequence[SampledServerAttempt] | None = None,
    ) -> TITOCallRecord:
        logical_request_id = (
            sampled.logical_request_id
            if sampled is not None
            else getattr(error, "logical_request_id", None) or logical_request_id
        )
        attempts = sampled.attempts if sampled is not None else getattr(error, "attempts", None) or attempts
        server_attempts = (
            sampled.server_attempts
            if sampled is not None
            else getattr(error, "server_attempts", None) or server_attempts
        )
        error_record = getattr(error, "as_error_record", None)
        details = error_record() if callable(error_record) else {"type": type(error).__name__, "message": str(error)}
        sampled_payload: dict[str, Any] = {}
        sampled_arrays: dict[str, Sequence[Any]] = {}
        if sampled is not None:
            sampled_payload = {
                "sampled_completion_count": len(sampled.completions),
                "sampled_completions": [
                    {
                        "index": index,
                        "text": completion.text,
                        "prompt_len": completion.prompt_len,
                        "completion_len": completion.completion_len,
                        "finish_reason": completion.finish_reason,
                        "full_tokens_hash": _hash_tokens(completion.full_tokens),
                    }
                    for index, completion in enumerate(sampled.completions)
                ],
                "server_metrics": (vars(sampled.server_metrics) if sampled.server_metrics is not None else None),
            }
            for index, completion in enumerate(sampled.completions):
                prefix = f"completion_{index}"
                sampled_arrays[f"{prefix}_full_tokens"] = completion.full_tokens
                if completion.inference_logprobs is not None:
                    sampled_arrays[f"{prefix}_inference_logprobs"] = completion.inference_logprobs
                if completion.sampling_logprobs is not None:
                    sampled_arrays[f"{prefix}_sampling_logprobs"] = completion.sampling_logprobs
                if completion.routing_matrices is not None:
                    sampled_arrays[f"{prefix}_routing_matrices"] = completion.routing_matrices
        try:
            await self._record_async(
                state,
                event,
                {
                    "call_id": call_id,
                    "call_kind": kind,
                    "classification_source": classification_source,
                    "outcome": outcome,
                    "error_code": error_code,
                    "phase": phase,
                    "request_fingerprint": fingerprint,
                    "prompt_hash": prompt_hash,
                    "logical_request_id": logical_request_id,
                    "upstream_attempts": attempts,
                    "server_attempts": [_server_attempt_value(attempt) for attempt in server_attempts or ()],
                    "error": details,
                    **(
                        {
                            "request": request.canonical_value(),
                            "wire_request": request.wire_value(),
                            "wire_request_body": request.wire_request_body,
                            "normalization_steps": list(request.normalization_steps),
                            "sampling": request.sampling_value(),
                            "adapter_metadata": dict(request.adapter_metadata),
                        }
                        if request is not None
                        else {}
                    ),
                    **sampled_payload,
                },
                sampled_arrays,
            )
        except TITOError:
            self._call_record(
                state,
                call_id=call_id,
                kind=kind,
                classification_source=classification_source,
                outcome="failed",
                started_at=started_at,
                fingerprint=fingerprint,
                prompt_hash=prompt_hash,
                sampled=sampled,
                sampler_wall_seconds=sampler_wall_seconds,
                logical_request_id=logical_request_id,
                attempts=attempts,
                server_attempts=server_attempts,
                error_code="tito_debug_storage_error",
            )
            raise
        return self._call_record(
            state,
            call_id=call_id,
            kind=kind,
            classification_source=classification_source,
            outcome=outcome,
            started_at=started_at,
            fingerprint=fingerprint,
            prompt_hash=prompt_hash,
            sampled=sampled,
            sampler_wall_seconds=sampler_wall_seconds,
            logical_request_id=logical_request_id,
            attempts=attempts,
            server_attempts=server_attempts,
            error_code=error_code,
        )

    def _observe_server_metrics(self, state: _TrajectoryState, metrics: ServerMetrics | None) -> None:
        if metrics is None:
            return
        mapping = {
            "server/processing_seconds": metrics.server_processing_time,
            "server/upstream_ttft_seconds": metrics.server_ttft,
            "server/tokenizer_queue_seconds": metrics.tokenizer_queue_duration,
            "server/tokenizer_seconds": metrics.tokenizer_duration,
            "server/prefill_queue_seconds": metrics.prefill_queue_duration,
            "server/prefill_seconds": metrics.prefill_duration,
            "server/generation_queue_seconds": metrics.generation_queue_duration,
            "server/generation_seconds": metrics.generation_duration,
        }
        for name, value in mapping.items():
            if value is not None:
                state.metrics.observe(name, value)
        if metrics.prefill_duration is not None and metrics.generation_duration is not None:
            state.metrics.observe(
                "server/model_compute_seconds",
                metrics.prefill_duration + metrics.generation_duration,
            )
        if metrics.cached_prompt_tokens is not None and metrics.prompt_tokens is not None:
            state.metrics.observe("cache/cached_prompt_tokens", metrics.cached_prompt_tokens)
            state.metrics.increment("cache/eligible_prompt_tokens_total", metrics.prompt_tokens)

    def _sampling_kwargs(self, state: _TrajectoryState, request: TITOChatRequest) -> dict[str, Any]:
        values = dict(request.sampling_fields)
        # Serving affinity belongs exclusively to the trajectory. Opaque
        # provider fields cannot introduce or override another cache identity.
        affinity_fields = (
            "prompt_cache_key",
            "prompt_cache_isolation_key",
            "user",
        )
        conflicts = sorted(name for name in affinity_fields if name in values)
        if conflicts:
            state.metrics.increment("cache/affinity_conflict")
            raise TITOError(
                "tito_affinity_override",
                400,
                "request cannot override trajectory serving affinity via: " + ", ".join(conflicts),
            )
        internal_fields = (
            "additional_headers_snapshot",
            "logical_request_id",
            "max_seq_len",
            "n",
            "echo",
            "stop",
            "prompt",
            "stream",
            "raw_output",
            "perf_metrics_in_response",
        )
        internal_conflicts = sorted(name for name in internal_fields if name in values)
        if internal_conflicts:
            raise TITOError(
                "tito_invalid_sampling_field",
                400,
                "request cannot set SDK-internal sampling fields: " + ", ".join(internal_conflicts),
            )
        values.pop("temperature", None)
        values.update(self.sampling_defaults)
        values["logprobs"] = True
        return values

    def _renderer_stop_sequences(self, request: TITOChatRequest) -> list[str] | None:
        """Validate the renderer's text-stop contract before sampling."""

        values = list(self.renderer.stop_sequences(request) or ())
        if any(not isinstance(value, str) for value in values):
            raise TITOError(
                "tito_renderer_contract_error",
                500,
                "renderer stop sequences must be strings",
            )
        return values or None

    def _backend_headers_for_call(self, state: _TrajectoryState) -> Mapping[str, str]:
        """Return the immutable construction-time backend header snapshot."""
        del state
        return self._backend_headers_snapshot

    async def complete(
        self,
        trajectory_id: str,
        request: TITOChatRequest,
        *,
        idempotency_key: str | None = None,
        prepared_event: asyncio.Event | None = None,
    ) -> TITOCallResult:
        started_at = time.time()
        call_id = uuid.uuid4().hex
        state = self._require_active(
            trajectory_id,
            count_terminal_request=True,
            request_started_at=started_at,
        )
        kind, classification_source, classifier_error = self._classify(request)
        current_task = asyncio.current_task()
        policy_lock_acquired = False
        if kind == "auxiliary":
            if current_task is not None:
                state.auxiliary_tasks.add(current_task)
        else:
            # asyncio.Lock admits waiters in arrival order. Register this task
            # before the first await so terminalization can cancel both the
            # executing policy call and callers queued behind it.
            waited = state.policy_lock.locked()
            wait_started_at = time.monotonic()
            if waited:
                state.metrics.increment("queue/policy_waited")
            if current_task is not None:
                state.policy_waiters.add(current_task)
            try:
                await state.policy_lock.acquire()
                policy_lock_acquired = True
            except asyncio.CancelledError:
                if waited:
                    state.metrics.increment("queue/policy_wait_cancelled")
                    state.metrics.observe(
                        "queue/policy_wait_seconds",
                        time.monotonic() - wait_started_at,
                    )
                raise
            finally:
                if current_task is not None:
                    state.policy_waiters.discard(current_task)
            if waited:
                state.metrics.observe(
                    "queue/policy_wait_seconds",
                    time.monotonic() - wait_started_at,
                )
            try:
                # A queued caller observed no trajectory or replay state while
                # waiting. Revalidate the lifecycle after it owns the cursor;
                # semantic history and idempotency are revalidated below.
                state = self._require_active(
                    trajectory_id,
                    count_terminal_request=True,
                    request_started_at=started_at,
                )
            except BaseException:
                state.policy_lock.release()
                raise
            state.policy_in_flight = True
            state.policy_task = current_task
        state.metrics.increment("calls/total")
        state.metrics.increment(f"calls/{kind}")
        if classifier_error is not None:
            state.metrics.increment("admission/classifier_failed")
        try:
            await self._record_async(
                state,
                "request_normalized",
                {
                    "call_id": call_id,
                    "call_kind": kind,
                    "classification_source": classification_source,
                    "classifier_error": classifier_error,
                    "wire_request": request.wire_value(),
                    "wire_request_body": request.wire_request_body,
                    "canonical_request": request.canonical_value(),
                    "sampling": request.sampling_value(),
                    "adapter_metadata": dict(request.adapter_metadata),
                    "normalization_steps": list(request.normalization_steps),
                },
            )
        except asyncio.CancelledError:
            self._call_record(
                state,
                call_id=call_id,
                kind=kind,
                classification_source=classification_source,
                outcome="cancelled",
                started_at=started_at,
            )
            if kind == "auxiliary":
                if current_task is not None:
                    state.auxiliary_tasks.discard(current_task)
            else:
                state.policy_in_flight = False
                state.policy_task = None
                if policy_lock_acquired:
                    state.policy_lock.release()
            raise
        except TITOError:
            self._call_record(
                state,
                call_id=call_id,
                kind=kind,
                classification_source=classification_source,
                outcome="failed",
                started_at=started_at,
                error_code="tito_debug_storage_error",
            )
            if kind == "auxiliary":
                if current_task is not None:
                    state.auxiliary_tasks.discard(current_task)
            else:
                state.policy_in_flight = False
                state.policy_task = None
                if policy_lock_acquired:
                    state.policy_lock.release()
            raise
        except BaseException:
            if kind == "auxiliary":
                if current_task is not None:
                    state.auxiliary_tasks.discard(current_task)
            else:
                state.policy_in_flight = False
                state.policy_task = None
                if policy_lock_acquired:
                    state.policy_lock.release()
            raise

        if kind == "auxiliary":
            try:
                return await self._complete_auxiliary(
                    state,
                    request,
                    call_id=call_id,
                    classification_source=classification_source,
                    started_at=started_at,
                    prepared_event=prepared_event,
                )
            finally:
                if current_task is not None:
                    state.auxiliary_tasks.discard(current_task)

        sampled: SampledRequestResult | None = None
        sampler_started_at: float | None = None
        logical_request_id: str | None = None
        fingerprint: str | None = None
        prompt_hash: str | None = None
        phase = "render_contract"
        inter_call_gap = max(0.0, started_at - (state.last_policy_commit_at or state.started_at))
        try:
            contract = self.renderer.render_contract_id(request)
            fingerprint = self._request_fingerprint(request, contract)
            phase = "idempotency"
            if idempotency_key is not None and state.last_call is not None:
                if idempotency_key == state.last_call.idempotency_key:
                    prompt_matches = True
                    if fingerprint == state.last_call.request_fingerprint:
                        last_turn = self._last_policy_turn(state)
                        if (
                            last_turn is None
                            or last_turn.turn_id != state.last_call.turn_id
                            or _hash_tokens(last_turn.exact_prompt_ids) != state.last_call.prepared_prompt_hash
                        ):
                            raise TITOError(
                                "tito_replay_state_error",
                                500,
                                "last-call replay record is not bound to the current cursor",
                            )
                        if last_turn.prompt_mode == "full_history":
                            phase = "idempotency_render"
                            retry_prompt = await self._render_full(state, request)
                            prompt_matches = _hash_tokens(retry_prompt) == state.last_call.prepared_prompt_hash
                        else:
                            segment = state.segments[-1]
                            if len(segment.turns) < 2 or segment.turns[-1].turn_id != last_turn.turn_id:
                                raise TITOError(
                                    "tito_replay_state_error",
                                    500,
                                    "incremental replay has no prior exact checkpoint",
                                )
                            prior_turn = segment.turns[-2]
                            stored_history = prior_turn.request.messages + (prior_turn.assistant.message,)
                            phase = "idempotency_incremental_render"
                            retry_prompt = await self._render_incremental(
                                state,
                                request,
                                stored_history,
                                request.messages[len(stored_history) :],
                                prior_turn.exact_checkpoint_ids,
                            )
                            prompt_matches = (
                                retry_prompt is not None
                                and _hash_tokens(retry_prompt.prompt_ids) == state.last_call.prepared_prompt_hash
                            )
                    if fingerprint != state.last_call.request_fingerprint or not prompt_matches:
                        state.metrics.increment("admission/idempotency_conflict")
                        await self._record_async(
                            state,
                            "request_rejected",
                            {
                                "call_id": call_id,
                                "call_kind": kind,
                                "classification_source": classification_source,
                                "outcome": "rejected",
                                "error_code": "idempotency_key_reused",
                                "request_fingerprint": fingerprint,
                            },
                        )
                        self._call_record(
                            state,
                            call_id=call_id,
                            kind=kind,
                            classification_source=classification_source,
                            outcome="rejected",
                            started_at=started_at,
                            fingerprint=fingerprint,
                            error_code="idempotency_key_reused",
                        )
                        raise TITOError(
                            "idempotency_key_reused",
                            409,
                            "Idempotency-Key was reused with a different request",
                        )
                    await self._record_async(
                        state,
                        "replay",
                        {"call_id": call_id, "turn_id": state.last_call.turn_id},
                    )
                    record = self._call_record(
                        state,
                        call_id=call_id,
                        kind=kind,
                        classification_source=classification_source,
                        outcome="replayed",
                        started_at=started_at,
                        fingerprint=fingerprint,
                        prompt_hash=state.last_call.prepared_prompt_hash,
                        turn_id=state.last_call.turn_id,
                    )
                    if prepared_event is not None:
                        prepared_event.set()
                    return TITOCallResult(
                        response=MappingProxyType(_freeze_json(state.last_call.response)),
                        call=record,
                        turn_id=state.last_call.turn_id,
                        replayed=True,
                    )

            phase = "prepare"
            plan = await self._prepare_policy(state, request, contract, fingerprint)
            prompt_hash = plan.prepared_prompt_hash
            active_before_commit = state.active_segment
            prepare_arrays: Mapping[str, Sequence[Any]] = {
                "prepared_prompt_ids": plan.prepared_prompt_ids,
            }
            phase = "debug_prepare"
            await self._record_async(
                state,
                "prepare",
                {
                    "call_id": call_id,
                    "call_kind": kind,
                    "classification_source": classification_source,
                    "request_fingerprint": fingerprint,
                    "render_contract_id": contract,
                    "prompt_hash": prompt_hash,
                    "prompt_tokens": len(plan.prepared_prompt_ids),
                    "disposition": plan.prompt_disposition,
                    "prefix_match_tokens": plan.prefix_match_tokens,
                    "realign_from_token": plan.realign_from_token,
                    "realigned_masked_tokens": plan.realigned_masked_tokens,
                    "prompt_mode": plan.prompt_mode,
                    "incremental_contract_id": plan.incremental_contract_id,
                    "incremental_junction_kind": plan.incremental_junction_kind,
                    "incremental_checkpoint_trim_tokens": plan.incremental_checkpoint_trim_tokens,
                    "incremental_fallback_reason": (plan.incremental_fallback_reason),
                    "segment_id": plan.segment.segment_id if plan.segment is not None else None,
                    "start_reason": plan.start_reason,
                    "close_reason": plan.close_reason,
                    "prior_checkpoint_hash": (
                        _hash_tokens(active_before_commit.turns[-1].exact_checkpoint_ids)
                        if active_before_commit is not None and active_before_commit.turns
                        else None
                    ),
                    "requested_output_tokens": plan.requested_output_tokens,
                    "effective_output_tokens": plan.effective_output_tokens,
                    "context_remaining_tokens": plan.context_remaining_tokens,
                    "request": request.canonical_value(),
                    "sampling": request.sampling_value(),
                    "adapter_metadata": dict(request.adapter_metadata),
                },
                prepare_arrays,
            )
            phase = "sampling_admission"
            sampling_kwargs = self._sampling_kwargs(state, request)
            include_routing = bool(sampling_kwargs.get("include_routing_matrix", False))
            if state.sampler_calls:
                state.metrics.increment("cache/affinity_reused")
            state.sampler_calls += 1
            logical_request_id = uuid.uuid4().hex
            stop_sequences = self._renderer_stop_sequences(request)
            await self._record_async(
                state,
                "inference_start",
                {
                    "call_id": call_id,
                    "prompt_hash": plan.prepared_prompt_hash,
                    "model": str(getattr(self.sampler, "model", request.model)),
                    "max_tokens": plan.effective_output_tokens,
                    "temperature": (
                        self.default_temperature if self.default_temperature is not None else request.temperature
                    ),
                    "stop": stop_sequences,
                    "sampling": sampling_kwargs,
                    "logical_request_id": logical_request_id,
                    "serving_affinity_key_hash": hashlib.sha256(state.serving_affinity_key.encode("utf-8")).hexdigest(),
                },
            )
            # The HTTP sidecar may commit a streamed 200 as soon as this event
            # fires. Keep it after every deterministic admission/preparation
            # step so an invalid request is still returned as a normal JSON
            # error rather than an error event inside a successful stream.
            if prepared_event is not None:
                prepared_event.set()
            phase = "inference"
            sampler_started_at = time.monotonic()
            sampled = await self.sampler.sample_with_prompt_tokens_result(
                list(plan.prepared_prompt_ids),
                max_tokens=plan.effective_output_tokens,
                temperature=(self.default_temperature if self.default_temperature is not None else request.temperature),
                stop=stop_sequences,
                prompt_cache_key=state.serving_affinity_key,
                additional_headers_snapshot=self._backend_headers_for_call(state),
                logical_request_id=logical_request_id,
                **sampling_kwargs,
            )
            phase = "completion_validation"
            completion = self._validate_completion(plan, sampled, include_routing)
            phase = "parser"
            parsed = self._parse(request, completion)
            if parsed.parser_fallback:
                state.metrics.increment("parser/fallback")
            else:
                state.metrics.increment("parser/success")

            prior_segment = state.active_segment if plan.close_reason is not None else None
            is_new_segment = plan.segment is None
            segment = plan.segment or _Segment(
                segment_id=uuid.uuid4().hex,
                start_reason=plan.start_reason or "new_segment",
                render_contract_id=plan.render_contract_id,
            )
            output_ids = tuple(completion.full_tokens[completion.prompt_len :])
            turn_id = uuid.uuid4().hex
            response = self._response(
                turn_id,
                parsed,
                completion.finish_reason,
                str(getattr(self.sampler, "model", request.model)),
            )
            turn = TITOTurn(
                turn_id=turn_id,
                request=request,
                assistant=parsed,
                exact_prompt_ids=plan.prepared_prompt_ids,
                exact_completion_ids=output_ids,
                inference_logprobs=(
                    tuple(completion.inference_logprobs) if completion.inference_logprobs is not None else None
                ),
                sampling_logprobs=(
                    tuple(completion.sampling_logprobs) if completion.sampling_logprobs is not None else None
                ),
                routing_matrices=(
                    tuple(completion.routing_matrices) if completion.routing_matrices is not None else None
                ),
                response_id=str(response["id"]),
                finish_reason=completion.finish_reason,
                prompt_disposition=plan.prompt_disposition,
                prefix_match_tokens=plan.prefix_match_tokens,
                realign_from_token=plan.realign_from_token,
                realigned_masked_tokens=plan.realigned_masked_tokens,
                prompt_mode=plan.prompt_mode,
                incremental_contract_id=plan.incremental_contract_id,
                incremental_junction_kind=plan.incremental_junction_kind,
                incremental_checkpoint_trim_tokens=plan.incremental_checkpoint_trim_tokens,
                incremental_fallback_reason=plan.incremental_fallback_reason,
                requested_output_tokens=plan.requested_output_tokens,
                effective_output_tokens=plan.effective_output_tokens,
                context_remaining_tokens=plan.context_remaining_tokens,
                server_metrics=sampled.server_metrics,
                sampler_wall_seconds=sampled.wall_seconds,
                logical_request_id=sampled.logical_request_id,
                upstream_response_id=sampled.upstream_response_id,
                upstream_attempts=sampled.attempts,
                server_attempts=sampled.server_attempts,
                parser_fallback=parsed.parser_fallback,
            )
            commit_payload = {
                "call_id": call_id,
                "turn_id": turn_id,
                "segment_id": segment.segment_id,
                "segment_start_reason": segment.start_reason if is_new_segment else None,
                "prior_segment_id": prior_segment.segment_id if prior_segment is not None else None,
                "prior_segment_close_reason": plan.close_reason,
                "segment_close_reason": ("length_truncation" if completion.finish_reason == "length" else None),
                "prompt_disposition": plan.prompt_disposition,
                "prefix_match_tokens": plan.prefix_match_tokens,
                "realign_from_token": plan.realign_from_token,
                "realigned_masked_tokens": plan.realigned_masked_tokens,
                "prompt_mode": plan.prompt_mode,
                "incremental_contract_id": plan.incremental_contract_id,
                "incremental_junction_kind": plan.incremental_junction_kind,
                "incremental_checkpoint_trim_tokens": plan.incremental_checkpoint_trim_tokens,
                "incremental_fallback_reason": plan.incremental_fallback_reason,
                "finish_reason": completion.finish_reason,
                "completion_tokens": len(output_ids),
                "logical_request_id": sampled.logical_request_id,
                "upstream_response_id": sampled.upstream_response_id,
                "upstream_attempts": sampled.attempts,
                "server_attempts": [_server_attempt_value(attempt) for attempt in sampled.server_attempts],
                "sampler_wall_seconds": sampled.wall_seconds,
                "server_metrics": vars(sampled.server_metrics) if sampled.server_metrics is not None else None,
                "assistant": dict(parsed.message),
                "parser_fallback": parsed.parser_fallback,
                "output_kind": parsed.output_kind,
                "completion_text": completion.text,
                "response": response,
            }
            commit_arrays = {
                "completion_ids": output_ids,
                **(
                    {"inference_logprobs": completion.inference_logprobs}
                    if completion.inference_logprobs is not None
                    else {}
                ),
                **(
                    {"sampling_logprobs": completion.sampling_logprobs}
                    if completion.sampling_logprobs is not None
                    else {}
                ),
                **(
                    {"routing_matrices": completion.routing_matrices} if completion.routing_matrices is not None else {}
                ),
            }

            def apply_commit() -> TITOCallResult:
                if prior_segment is not None:
                    prior_segment.closed_reason = plan.close_reason
                if is_new_segment:
                    state.segments.append(segment)
                segment.turns.append(turn)
                state.metrics.increment(f"lineage/{plan.prompt_disposition}")
                state.metrics.increment(f"prompt_construction/{plan.prompt_mode}")
                if plan.incremental_fallback_reason is not None:
                    state.metrics.increment("prompt_construction/incremental_fallback")
                if plan.incremental_checkpoint_trim_tokens:
                    state.metrics.increment(
                        "prompt_construction/incremental_checkpoint_trim_tokens",
                        plan.incremental_checkpoint_trim_tokens,
                    )
                if plan.prompt_disposition == "realign":
                    state.metrics.increment(
                        "lineage/realigned_masked_tokens",
                        plan.realigned_masked_tokens,
                    )
                if completion.finish_reason == "length":
                    segment.closed_reason = "length_truncation"
                    state.metrics.increment("lineage/boundary_reason_length_closed")
                state.last_policy_commit_at = time.time()
                state.metrics.observe("turn/prompt_tokens", len(plan.prepared_prompt_ids))
                state.metrics.observe("turn/completion_tokens", len(output_ids))
                state.metrics.observe("turn/model_tokens", len(plan.prepared_prompt_ids) + len(output_ids))
                state.metrics.observe("turn/context_remaining_tokens", plan.context_remaining_tokens)
                state.metrics.observe("turn/requested_output_tokens", plan.requested_output_tokens)
                state.metrics.observe("turn/effective_output_tokens", plan.effective_output_tokens)
                state.metrics.observe("turn/inter_call_gap_seconds", inter_call_gap)
                finish_reason_label = (
                    completion.finish_reason
                    if completion.finish_reason in {"stop", "length", "tool_calls", "content_filter"}
                    else "other"
                )
                state.metrics.increment(f"calls/finish_reason_{finish_reason_label}")
                self._observe_server_metrics(state, sampled.server_metrics)
                if idempotency_key is not None:
                    state.last_call = _LastCall(
                        idempotency_key=idempotency_key,
                        request_fingerprint=fingerprint,
                        prepared_prompt_hash=plan.prepared_prompt_hash,
                        turn_id=turn_id,
                        response=_freeze_json(response),
                    )
                else:
                    state.last_call = None
                record = self._call_record(
                    state,
                    call_id=call_id,
                    kind=kind,
                    classification_source=classification_source,
                    outcome="succeeded",
                    started_at=started_at,
                    fingerprint=fingerprint,
                    prompt_hash=plan.prepared_prompt_hash,
                    turn_id=turn_id,
                    sampled=sampled,
                )
                state.metrics.observe(
                    "turn/request_wall_seconds",
                    record.ended_at - record.started_at,
                )
                return TITOCallResult(
                    response=MappingProxyType(_freeze_json(response)),
                    call=record,
                    turn_id=turn_id,
                )

            # The strict debug barrier and cursor advance are one shielded
            # operation. A cancellation is propagated only after both have
            # completed, so durable evidence and in-memory state cannot split.
            phase = "debug_commit"
            return await self._record_and_apply_async(
                state,
                "commit",
                commit_payload,
                commit_arrays,
                apply_commit,
                # Once both the durable commit record and cursor transition
                # exist, the caller needs the committed turn ID even if a
                # transport cancellation raced the barrier. The HTTP sidecar
                # then records the response as ambiguous instead of silently
                # dropping a trainable action.
                return_after_cancelled_commit=True,
            )
        except asyncio.CancelledError as exc:
            if not any(record.call_id == call_id for record in state.calls):
                self._call_record(
                    state,
                    call_id=call_id,
                    kind=kind,
                    classification_source=classification_source,
                    outcome="cancelled",
                    started_at=started_at,
                    fingerprint=fingerprint,
                    prompt_hash=prompt_hash,
                    sampled=sampled,
                    sampler_wall_seconds=(
                        time.monotonic() - sampler_started_at
                        if sampled is None and sampler_started_at is not None
                        else None
                    ),
                    logical_request_id=(getattr(exc, "logical_request_id", None) or logical_request_id),
                    attempts=getattr(exc, "attempts", None) or (1 if sampler_started_at is not None else None),
                    server_attempts=getattr(exc, "server_attempts", None),
                )
            raise
        except TITOError as exc:
            if not any(record.call_id == call_id for record in state.calls):
                if exc.code == "tito_model_malformed_output":
                    state.metrics.increment("parser/model_malformed")
                # Wire status and accounting disposition are deliberately
                # separate. A protocol-unsafe sampled action remains a 502 so
                # the harness may resample, but it is a model outcome rather
                # than a sidecar failure or a deterministic request rejection.
                outcome: TITOCallOutcome = (
                    "model_malformed"
                    if exc.code == "tito_model_malformed_output"
                    else "rejected"
                    if exc.status < 500
                    else "failed"
                )
                sampler_wall_seconds = (
                    time.monotonic() - sampler_started_at
                    if sampled is None and sampler_started_at is not None
                    else None
                )
                if exc.code == "tito_debug_storage_error":
                    self._call_record(
                        state,
                        call_id=call_id,
                        kind=kind,
                        classification_source=classification_source,
                        outcome="failed",
                        started_at=started_at,
                        fingerprint=fingerprint,
                        prompt_hash=prompt_hash,
                        sampled=sampled,
                        sampler_wall_seconds=sampler_wall_seconds,
                        logical_request_id=logical_request_id,
                        attempts=(1 if sampler_started_at is not None else None),
                        error_code=exc.code,
                    )
                else:
                    await self._record_call_terminal(
                        state,
                        event="call_terminal",
                        call_id=call_id,
                        kind=kind,
                        classification_source=classification_source,
                        outcome=outcome,
                        started_at=started_at,
                        fingerprint=fingerprint,
                        prompt_hash=prompt_hash,
                        sampled=sampled,
                        sampler_wall_seconds=sampler_wall_seconds,
                        error_code=exc.code,
                        error=exc,
                        phase=phase,
                        request=request,
                        logical_request_id=logical_request_id,
                        attempts=(1 if sampler_started_at is not None else None),
                    )
            raise
        except Exception as exc:
            await self._record_call_terminal(
                state,
                event="call_terminal",
                call_id=call_id,
                kind=kind,
                classification_source=classification_source,
                outcome="failed",
                started_at=started_at,
                fingerprint=fingerprint,
                prompt_hash=prompt_hash,
                sampled=sampled,
                sampler_wall_seconds=(
                    time.monotonic() - sampler_started_at
                    if sampled is None and sampler_started_at is not None
                    else None
                ),
                error_code="tito_internal_error",
                error=exc,
                phase=phase,
                request=request,
                logical_request_id=logical_request_id,
                attempts=(1 if sampler_started_at is not None else None),
            )
            raise
        finally:
            state.policy_in_flight = False
            state.policy_task = None
            if policy_lock_acquired:
                state.policy_lock.release()

    async def _complete_auxiliary(
        self,
        state: _TrajectoryState,
        request: TITOChatRequest,
        *,
        call_id: str,
        classification_source: str,
        started_at: float,
        prepared_event: asyncio.Event | None,
    ) -> TITOCallResult:
        sampled: SampledRequestResult | None = None
        sampler_started_at: float | None = None
        logical_request_id: str | None = None
        phase = "full_render"
        try:
            prompt = await self._render_full(state, request)
            phase = "budget"
            _requested, effective, _remaining = self._budget(state, request, len(prompt))
            contract = self.renderer.render_contract_id(request)
            prompt_hash = _hash_tokens(prompt)
            phase = "debug_prepare"
            await self._record_async(
                state,
                "auxiliary_prepare",
                {
                    "call_id": call_id,
                    "call_kind": "auxiliary",
                    "classification_source": classification_source,
                    "render_contract_id": contract,
                    "prompt_hash": prompt_hash,
                    "prompt_tokens": len(prompt),
                    "requested_output_tokens": _requested,
                    "effective_output_tokens": effective,
                    "context_remaining_tokens": _remaining,
                    "request": request.canonical_value(),
                    "sampling": request.sampling_value(),
                    "adapter_metadata": dict(request.adapter_metadata),
                },
                {"prepared_prompt_ids": prompt},
            )
            phase = "sampling_admission"
            sampling_kwargs = self._sampling_kwargs(state, request)
            if state.sampler_calls:
                state.metrics.increment("cache/affinity_reused")
            state.sampler_calls += 1
            logical_request_id = uuid.uuid4().hex
            stop_sequences = self._renderer_stop_sequences(request)
            await self._record_async(
                state,
                "auxiliary_inference_start",
                {
                    "call_id": call_id,
                    "prompt_hash": prompt_hash,
                    "model": str(getattr(self.sampler, "model", request.model)),
                    "max_tokens": effective,
                    "temperature": (
                        self.default_temperature if self.default_temperature is not None else request.temperature
                    ),
                    "stop": stop_sequences,
                    "sampling": sampling_kwargs,
                    "logical_request_id": logical_request_id,
                },
            )
            if prepared_event is not None:
                prepared_event.set()
            phase = "inference"
            sampler_started_at = time.monotonic()
            sampled = await self.sampler.sample_with_prompt_tokens_result(
                list(prompt),
                max_tokens=effective,
                temperature=(self.default_temperature if self.default_temperature is not None else request.temperature),
                stop=stop_sequences,
                prompt_cache_key=state.serving_affinity_key,
                additional_headers_snapshot=self._backend_headers_for_call(state),
                logical_request_id=logical_request_id,
                **sampling_kwargs,
            )
            phase = "completion_validation"
            completion = self._validate_completion(
                _TurnPlan(
                    request=request,
                    render_contract_id=contract,
                    request_fingerprint="",
                    prepared_prompt_ids=prompt,
                    prepared_prompt_hash=prompt_hash,
                    prompt_disposition="new_segment",
                    prefix_match_tokens=None,
                    realign_from_token=None,
                    realigned_masked_tokens=0,
                    prompt_mode="full_history",
                    incremental_contract_id=None,
                    incremental_junction_kind=None,
                    incremental_checkpoint_trim_tokens=0,
                    incremental_fallback_reason=None,
                    segment=None,
                    start_reason=None,
                    close_reason=None,
                    requested_output_tokens=_requested,
                    effective_output_tokens=effective,
                    context_remaining_tokens=_remaining,
                ),
                sampled,
                bool(sampling_kwargs.get("include_routing_matrix", False)),
            )
            phase = "parser"
            parsed = self._parse(request, completion)
            state.metrics.increment("parser/fallback" if parsed.parser_fallback else "parser/success")
            response = self._response(
                uuid.uuid4().hex,
                parsed,
                completion.finish_reason,
                str(getattr(self.sampler, "model", request.model)),
            )
            output_ids = tuple(completion.full_tokens[completion.prompt_len :])
            phase = "debug_complete"
            await self._record_async(
                state,
                "auxiliary_complete",
                {
                    "call_id": call_id,
                    "finish_reason": completion.finish_reason,
                    "logical_request_id": sampled.logical_request_id,
                    "upstream_response_id": sampled.upstream_response_id,
                    "upstream_attempts": sampled.attempts,
                    "server_attempts": [_server_attempt_value(attempt) for attempt in sampled.server_attempts],
                    "sampler_wall_seconds": sampled.wall_seconds,
                    "server_metrics": vars(sampled.server_metrics) if sampled.server_metrics is not None else None,
                    "assistant": dict(parsed.message),
                    "parser_fallback": parsed.parser_fallback,
                    "output_kind": parsed.output_kind,
                    "completion_text": completion.text,
                    "response": response,
                },
                {
                    "completion_ids": output_ids,
                    **(
                        {"inference_logprobs": completion.inference_logprobs}
                        if completion.inference_logprobs is not None
                        else {}
                    ),
                    **(
                        {"sampling_logprobs": completion.sampling_logprobs}
                        if completion.sampling_logprobs is not None
                        else {}
                    ),
                    **(
                        {"routing_matrices": completion.routing_matrices}
                        if completion.routing_matrices is not None
                        else {}
                    ),
                },
            )
            finish_reason_label = (
                completion.finish_reason
                if completion.finish_reason in {"stop", "length", "tool_calls", "content_filter"}
                else "other"
            )
            state.metrics.increment(f"calls/finish_reason_{finish_reason_label}")
            record = self._call_record(
                state,
                call_id=call_id,
                kind="auxiliary",
                classification_source=classification_source,
                outcome="succeeded",
                started_at=started_at,
                sampled=sampled,
                sampler_wall_seconds=(
                    time.monotonic() - sampler_started_at
                    if sampled is None and sampler_started_at is not None
                    else None
                ),
            )
            self._observe_server_metrics(state, sampled.server_metrics)
            return TITOCallResult(response=MappingProxyType(response), call=record, turn_id=None)
        except asyncio.CancelledError as exc:
            self._call_record(
                state,
                call_id=call_id,
                kind="auxiliary",
                classification_source=classification_source,
                outcome="cancelled",
                started_at=started_at,
                sampled=sampled,
                sampler_wall_seconds=(
                    time.monotonic() - sampler_started_at
                    if sampled is None and sampler_started_at is not None
                    else None
                ),
                logical_request_id=(getattr(exc, "logical_request_id", None) or logical_request_id),
                attempts=getattr(exc, "attempts", None) or (1 if sampler_started_at is not None else None),
                server_attempts=getattr(exc, "server_attempts", None),
            )
            raise
        except TITOError as exc:
            if exc.code == "tito_model_malformed_output":
                state.metrics.increment("parser/model_malformed")
            outcome: TITOCallOutcome = (
                "model_malformed"
                if exc.code == "tito_model_malformed_output"
                else "rejected"
                if exc.status < 500
                else "failed"
            )
            sampler_wall_seconds = (
                time.monotonic() - sampler_started_at if sampled is None and sampler_started_at is not None else None
            )
            if exc.code == "tito_debug_storage_error":
                self._call_record(
                    state,
                    call_id=call_id,
                    kind="auxiliary",
                    classification_source=classification_source,
                    outcome="failed",
                    started_at=started_at,
                    sampled=sampled,
                    sampler_wall_seconds=sampler_wall_seconds,
                    logical_request_id=logical_request_id,
                    attempts=(1 if sampler_started_at is not None else None),
                    error_code=exc.code,
                )
            else:
                await self._record_call_terminal(
                    state,
                    event="auxiliary_terminal",
                    call_id=call_id,
                    kind="auxiliary",
                    classification_source=classification_source,
                    outcome=outcome,
                    started_at=started_at,
                    fingerprint=None,
                    prompt_hash=None,
                    sampled=sampled,
                    sampler_wall_seconds=sampler_wall_seconds,
                    error_code=exc.code,
                    error=exc,
                    phase=phase,
                    request=request,
                    logical_request_id=logical_request_id,
                    attempts=(1 if sampler_started_at is not None else None),
                )
            raise
        except Exception as exc:
            await self._record_call_terminal(
                state,
                event="auxiliary_terminal",
                call_id=call_id,
                kind="auxiliary",
                classification_source=classification_source,
                outcome="failed",
                started_at=started_at,
                sampled=sampled,
                sampler_wall_seconds=(
                    time.monotonic() - sampler_started_at
                    if sampled is None and sampler_started_at is not None
                    else None
                ),
                error_code="tito_internal_error",
                fingerprint=None,
                prompt_hash=None,
                error=exc,
                phase=phase,
                request=request,
                logical_request_id=logical_request_id,
                attempts=(1 if sampler_started_at is not None else None),
            )
            raise

    @staticmethod
    def _last_policy_turn(state: _TrajectoryState) -> TITOTurn | None:
        for segment in reversed(state.segments):
            if segment.turns:
                return segment.turns[-1]
        return None

    def record_response_emission(
        self,
        trajectory_id: str,
        turn_id: str,
        emission: TITOEmission,
        *,
        wire_evidence: Mapping[str, Any] | None = None,
    ) -> TITOResponseAttempt:
        # A rollout may start abandonment after the policy commit but while
        # the HTTP handler is still writing the response. The terminalizer
        # cancels and awaits that handler; its cancellation path must be able
        # to record the honest ambiguous emission before the terminal marker.
        state = self._state
        if state is None or state.trajectory_id != trajectory_id:
            state = self._require_active(trajectory_id)
        if not any(turn.turn_id == turn_id for segment in state.segments for turn in segment.turns):
            raise ValueError(f"unknown committed turn: {turn_id}")
        attempt = TITOResponseAttempt(
            attempt_id=uuid.uuid4().hex,
            turn_id=turn_id,
            emission=emission,
            created_at=time.time(),
        )
        self._record(
            state,
            "response_emission",
            {
                "attempt_id": attempt.attempt_id,
                "turn_id": turn_id,
                "emission": emission,
                "wire": dict(wire_evidence or {}),
            },
        )
        state.response_attempts.append(attempt)
        state.metrics.increment(f"transport/response_emission_{emission}")
        return attempt

    async def record_response_emission_async(
        self,
        trajectory_id: str,
        turn_id: str,
        emission: TITOEmission,
        *,
        wire_evidence: Mapping[str, Any] | None = None,
    ) -> TITOResponseAttempt:
        state = self._state
        if state is None or state.trajectory_id != trajectory_id:
            state = self._require_active(trajectory_id)
        if not any(turn.turn_id == turn_id for segment in state.segments for turn in segment.turns):
            raise ValueError(f"unknown committed turn: {turn_id}")
        attempt = TITOResponseAttempt(
            attempt_id=uuid.uuid4().hex,
            turn_id=turn_id,
            emission=emission,
            created_at=time.time(),
        )
        payload = {
            "attempt_id": attempt.attempt_id,
            "turn_id": turn_id,
            "emission": emission,
            "wire": dict(wire_evidence or {}),
        }

        def apply_emission() -> TITOResponseAttempt:
            state.response_attempts.append(attempt)
            state.metrics.increment(f"transport/response_emission_{emission}")
            return attempt

        return await self._record_and_apply_async(
            state,
            "response_emission",
            payload,
            None,
            apply_emission,
        )

    def observe_agent_wall(self, trajectory_id: str, seconds: float) -> None:
        """Attach the cookbook-owned exact harness lifecycle bracket."""
        if seconds < 0:
            raise ValueError("agent wall time must be non-negative")
        state = self._require_active(trajectory_id)
        state.metrics.observe("agent/wall_seconds", seconds)
        self._record(state, "agent_wall", {"seconds": seconds})

    async def observe_agent_wall_async(self, trajectory_id: str, seconds: float) -> None:
        if seconds < 0:
            raise ValueError("agent wall time must be non-negative")
        state = self._require_active(trajectory_id)
        state.metrics.observe("agent/wall_seconds", seconds)
        await self._record_async(state, "agent_wall", {"seconds": seconds})

    @staticmethod
    def _terminal_closed_reason(status: TITOTrajectoryStatus) -> str:
        return {
            "completed": "trajectory_completed",
            "abandoned": "trajectory_abandoned",
            "failed": "trajectory_failed",
            "active": "trajectory_terminal",
        }[status]

    @staticmethod
    def _ensure_no_in_flight(state: _TrajectoryState) -> None:
        state.policy_waiters.difference_update({task for task in state.policy_waiters if task.done()})
        state.auxiliary_tasks.difference_update({task for task in state.auxiliary_tasks if task.done()})
        state.transport_tasks.difference_update({task for task in state.transport_tasks if task.done()})
        if state.policy_in_flight or state.policy_waiters or state.auxiliary_tasks or state.transport_tasks:
            raise TITOError(
                "tito_call_in_flight",
                409,
                "cannot terminalize while a sidecar call is in flight",
            )

    def _terminal_payload(
        self,
        state: _TrajectoryState,
        status: TITOTrajectoryStatus,
        reason: str | None,
    ) -> Mapping[str, Any]:
        active = state.active_segment
        terminal_reason = self._terminal_closed_reason(status)
        return {
            "reason": reason,
            "metrics": state.metrics.snapshot().flattened(),
            "segments": [
                {
                    "segment_id": segment.segment_id,
                    "start_reason": segment.start_reason,
                    "closed_reason": terminal_reason if segment is active else segment.closed_reason,
                    "turns": len(segment.turns),
                }
                for segment in state.segments
            ],
        }

    def _retire_state(
        self,
        state: _TrajectoryState,
        status: TITOTrajectoryStatus,
        reason: str | None,
    ) -> _Tombstone:
        active = state.active_segment
        if active is not None:
            active.closed_reason = self._terminal_closed_reason(status)
        tombstone = _Tombstone(
            status=status,
            reason=reason,
            terminal_at=time.time(),
            metrics=state.metrics,
        )
        self._state = None
        self._tombstone = tombstone
        return tombstone

    def _terminalize(
        self,
        state: _TrajectoryState,
        status: TITOTrajectoryStatus,
        reason: str | None,
        write_observer: bool = True,
    ) -> _Tombstone:
        self._ensure_no_in_flight(state)
        if write_observer and self.observer is not None:
            started = time.monotonic()
            try:
                bytes_written = self.observer.close_trajectory(
                    state.trajectory_id,
                    status,
                    self._terminal_payload(state, status, reason),
                )
            except Exception as exc:
                if getattr(exc, "storage_full", False):
                    state.metrics.increment("debug/storage_full")
                state.metrics.increment("debug/write_failed")
                raise TITOError(
                    "tito_debug_storage_error",
                    507,
                    f"local TITO debug close failed: {exc}",
                ) from exc
            state.metrics.increment("debug/trajectories_written")
            state.metrics.observe("debug/write_seconds", time.monotonic() - started)
            if bytes_written is not None:
                state.metrics.observe("debug/bytes_written", bytes_written)
        return self._retire_state(state, status, reason)

    async def _terminalize_async(
        self,
        state: _TrajectoryState,
        status: TITOTrajectoryStatus,
        reason: str | None,
        write_observer: bool = True,
    ) -> _Tombstone:
        async def operation() -> _Tombstone:
            self._ensure_no_in_flight(state)
            observer = self.observer
            if write_observer and observer is not None:
                started = time.monotonic()
                try:
                    bytes_written = await asyncio.get_running_loop().run_in_executor(
                        _TITO_OBSERVER_EXECUTOR,
                        observer.close_trajectory,
                        state.trajectory_id,
                        status,
                        self._terminal_payload(state, status, reason),
                    )
                except Exception as exc:
                    if getattr(exc, "storage_full", False):
                        state.metrics.increment("debug/storage_full")
                    state.metrics.increment("debug/write_failed")
                    raise TITOError(
                        "tito_debug_storage_error",
                        507,
                        f"local TITO debug close failed: {exc}",
                    ) from exc
                state.metrics.increment("debug/trajectories_written")
                state.metrics.observe("debug/write_seconds", time.monotonic() - started)
                if bytes_written is not None:
                    state.metrics.observe("debug/bytes_written", bytes_written)
            return self._retire_state(state, status, reason)

        task = asyncio.create_task(operation())
        cancelled: asyncio.CancelledError | None = None
        while True:
            try:
                tombstone = await asyncio.shield(task)
                break
            except asyncio.CancelledError as exc:
                cancelled = exc
        if cancelled is not None:
            raise cancelled
        return tombstone

    async def _cancel_and_terminalize(
        self,
        trajectory_id: str,
        status: Literal["abandoned", "failed"],
        reason: str,
    ) -> TITOTrajectoryArtifact:
        state = self._require_active(trajectory_id)
        current = asyncio.current_task()
        if (
            current is state.policy_task
            or current in state.policy_waiters
            or current in state.auxiliary_tasks
            or current in state.transport_tasks
        ):
            raise TITOError(
                "tito_call_in_flight",
                409,
                "a sidecar call cannot terminalize its own trajectory",
            )
        state.terminalizing = True
        finished_at = time.time()
        prior_summary = {name: state.metrics.distributions.get(name) for name in self._trajectory_summary_names()}
        try:
            tasks = {
                task
                for task in ({state.policy_task} | state.policy_waiters | state.auxiliary_tasks | state.transport_tasks)
                if task is not None and task is not current and not task.done()
            }
            for task in tasks:
                task.cancel()
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
                state.policy_waiters.difference_update(tasks)
                state.auxiliary_tasks.difference_update(tasks)
                state.transport_tasks.difference_update(tasks)
            self._observe_trajectory_summary(state, finished_at)
            try:
                await self._terminalize_async(state, status, reason)
            except BaseException as exc:
                if self._state is state:
                    if isinstance(exc, TITOError) and exc.code == "tito_debug_storage_error":
                        # Debug closure remains fail-closed, but a failed sink
                        # must not strand live token arrays after cancellation.
                        await self._terminalize_async(
                            state,
                            status,
                            f"{reason}_debug_failure",
                            False,
                        )
                    else:
                        self._restore_trajectory_summary(state, prior_summary)
                raise
            return self._trajectory_result(state, finished_at, status=status, reason=reason)
        finally:
            if self._state is state:
                state.terminalizing = False

    async def _wait_for_transport(self, trajectory_id: str) -> None:
        state = self._require_active(trajectory_id)
        state.transport_tasks.difference_update({task for task in state.transport_tasks if task.done()})
        current = asyncio.current_task()
        if current in state.transport_tasks:
            raise TITOError(
                "tito_call_in_flight",
                409,
                "a sidecar response task cannot finish its own trajectory",
            )
        tasks = {task for task in state.transport_tasks if task is not current and not task.done()}
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
            state.transport_tasks.difference_update(tasks)

    def _observe_trajectory_summary(self, state: _TrajectoryState, finished_at: float) -> None:
        policy_turns = sum(len(segment.turns) for segment in state.segments)
        state.metrics.observe("trajectory/policy_turns", policy_turns)
        state.metrics.observe("trajectory/segments", len(state.segments))
        state.metrics.observe("trajectory/wall_seconds", finished_at - state.started_at)
        model_input = sum(len(turn.exact_prompt_ids) for segment in state.segments for turn in segment.turns)
        sampled_output = sum(len(turn.exact_completion_ids) for segment in state.segments for turn in segment.turns)
        state.metrics.observe("trajectory/model_input_tokens", model_input)
        state.metrics.observe("trajectory/sampled_output_tokens", sampled_output)
        state.metrics.observe("trajectory/model_tokens_processed", model_input + sampled_output)
        state.metrics.observe(
            "trajectory/pre_retention_segment_tokens",
            sum(len(segment.turns[-1].exact_checkpoint_ids) for segment in state.segments if segment.turns),
        )
        last = self._last_policy_turn(state)
        state.metrics.observe(
            "trajectory/final_context_tokens",
            len(last.exact_checkpoint_ids) if last is not None else 0,
        )

    @staticmethod
    def _trajectory_summary_names() -> tuple[str, ...]:
        return (
            "trajectory/policy_turns",
            "trajectory/segments",
            "trajectory/wall_seconds",
            "trajectory/model_input_tokens",
            "trajectory/sampled_output_tokens",
            "trajectory/model_tokens_processed",
            "trajectory/pre_retention_segment_tokens",
            "trajectory/final_context_tokens",
        )

    def _restore_trajectory_summary(
        self,
        state: _TrajectoryState,
        prior: Mapping[str, Any],
    ) -> None:
        for name in self._trajectory_summary_names():
            value = prior.get(name)
            if value is None:
                state.metrics.distributions.pop(name, None)
            else:
                state.metrics.distributions[name] = value

    @staticmethod
    def _trajectory_result(
        state: _TrajectoryState,
        finished_at: float,
        *,
        status: Literal["completed", "abandoned", "failed"] = "completed",
        reason: str | None = None,
    ) -> TITOTrajectoryArtifact:
        return TITOTrajectoryArtifact(
            trajectory_id=state.trajectory_id,
            serving_affinity_key_hash=hashlib.sha256(state.serving_affinity_key.encode("utf-8")).hexdigest(),
            metadata=state.metadata,
            status=status,
            terminal_reason=reason,
            segments=tuple(
                TITOSegmentResult(
                    segment_id=segment.segment_id,
                    start_reason=segment.start_reason,
                    render_contract_id=segment.render_contract_id,
                    turns=tuple(segment.turns),
                    closed_reason=segment.closed_reason,
                )
                for segment in state.segments
            ),
            calls=tuple(state.calls),
            response_attempts=tuple(state.response_attempts),
            metrics=state.metrics.snapshot(),
            started_at=state.started_at,
            finished_at=finished_at,
        )

    def _terminalize_sync_result(
        self,
        trajectory_id: str,
        status: Literal["completed", "abandoned", "failed"],
        reason: str | None,
    ) -> TITOTrajectoryArtifact:
        state = self._require_active(trajectory_id)
        state.transport_tasks.difference_update({task for task in state.transport_tasks if task.done()})
        self._ensure_no_in_flight(state)
        finished_at = time.time()
        prior_summary = {name: state.metrics.distributions.get(name) for name in self._trajectory_summary_names()}
        try:
            self._observe_trajectory_summary(state, finished_at)
            self._terminalize(state, status, reason)
        except BaseException:
            self._restore_trajectory_summary(state, prior_summary)
            raise
        return self._trajectory_result(
            state,
            finished_at,
            status=status,
            reason=reason,
        )

    def finish(self, trajectory_id: str) -> TITOTrajectoryArtifact:
        return self._terminalize_sync_result(trajectory_id, "completed", None)

    async def finish_async(self, trajectory_id: str) -> TITOTrajectoryArtifact:
        state = self._require_active(trajectory_id)
        state.terminalizing = True
        try:
            self._ensure_no_in_flight(state)
            finished_at = time.time()
            prior_summary = {name: state.metrics.distributions.get(name) for name in self._trajectory_summary_names()}
            try:
                self._observe_trajectory_summary(state, finished_at)
                await self._terminalize_async(state, "completed", None)
            except BaseException:
                if self._state is state:
                    self._restore_trajectory_summary(state, prior_summary)
                raise
            return self._trajectory_result(state, finished_at)
        finally:
            if self._state is state:
                state.terminalizing = False

    def abandon(self, trajectory_id: str, reason: str) -> TITOTrajectoryArtifact:
        return self._terminalize_sync_result(trajectory_id, "abandoned", reason)

    def fail(self, trajectory_id: str, reason: str) -> TITOTrajectoryArtifact:
        return self._terminalize_sync_result(trajectory_id, "failed", reason)

    async def close(self) -> None:
        self._closing = True
        current = asyncio.current_task()
        state = self._state
        if state is not None:
            state.terminalizing = True
        tasks = {
            task
            for state in (() if state is None else (state,))
            for task in ({state.policy_task} | state.policy_waiters | state.auxiliary_tasks | state.transport_tasks)
            if task is not None and task is not current and not task.done()
        }
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        terminalization_error: TITOError | None = None
        if state is not None:
            try:
                await self._terminalize_async(state, "abandoned", "sidecar_shutdown")
            except TITOError as exc:
                if exc.code != "tito_debug_storage_error":
                    raise
                terminalization_error = exc
                # Durable debug closure is fail-closed, but shutdown must still
                # retire the in-memory trajectory and release its token arrays.
                await self._terminalize_async(
                    state,
                    "abandoned",
                    "sidecar_shutdown_debug_failure",
                    False,
                )
        if terminalization_error is not None:
            raise TITOError(
                "tito_debug_storage_error",
                507,
                f"failed to close debug evidence for the trajectory: {terminalization_error}",
            ) from terminalization_error


class TITOTrajectoryEngine:
    """Internal state machine for exactly one independent trajectory.

    ``_LinearTrajectoryCore`` retains the proven token transaction while this
    object fixes its cardinality to one. The environment sidecar owns the only
    table of these engines; no ancestry or cross-engine state is represented.
    """

    def __init__(
        self,
        engine: _LinearTrajectoryCore,
        trajectory_id: str,
    ) -> None:
        self._core = engine
        self.trajectory_id = trajectory_id
        self._terminal = False

    @property
    def sampler(self) -> _ExactTokenSampler:
        return self._core.sampler

    @property
    def is_terminal(self) -> bool:
        return self._terminal

    def require_active(
        self,
        *,
        count_terminal_request: bool = False,
        request_started_at: float | None = None,
    ) -> _TrajectoryState:
        return self._core._require_active(
            self.trajectory_id,
            count_terminal_request=count_terminal_request,
            request_started_at=request_started_at,
        )

    async def record_normalization_reject_async(
        self,
        *,
        started_at: float,
        error: BaseException,
        wire_request: Mapping[str, Any] | None,
        wire_request_body: str | None,
    ) -> None:
        await self._core.record_normalization_reject_async(
            self.trajectory_id,
            started_at=started_at,
            error=error,
            wire_request=wire_request,
            wire_request_body=wire_request_body,
        )

    async def complete(
        self,
        request: TITOChatRequest | Mapping[str, Any],
        *,
        idempotency_key: str | None = None,
        prepared_event: asyncio.Event | None = None,
    ) -> TITOCallResult:
        normalized = request if isinstance(request, TITOChatRequest) else TITOChatRequest.from_openai(request)
        return await self._core.complete(
            self.trajectory_id,
            normalized,
            idempotency_key=idempotency_key,
            prepared_event=prepared_event,
        )

    async def record_response_emission_async(
        self,
        turn_id: str,
        emission: TITOEmission,
        *,
        wire_evidence: Mapping[str, Any] | None = None,
    ) -> TITOResponseAttempt:
        return await self._core.record_response_emission_async(
            self.trajectory_id,
            turn_id,
            emission,
            wire_evidence=wire_evidence,
        )

    async def finish(self) -> TITOTrajectoryArtifact:
        await self._core._wait_for_transport(self.trajectory_id)
        result = await self._core.finish_async(self.trajectory_id)
        self._terminal = True
        return result

    def observe_agent_wall(self, seconds: float) -> None:
        self._core.observe_agent_wall(self.trajectory_id, seconds)

    async def observe_agent_wall_async(self, seconds: float) -> None:
        await self._core.observe_agent_wall_async(self.trajectory_id, seconds)

    async def abandon(self, reason: str = "caller_abandoned") -> TITOTrajectoryArtifact | None:
        if not self._terminal:
            try:
                return await self._core._cancel_and_terminalize(
                    self.trajectory_id,
                    "abandoned",
                    reason,
                )
            finally:
                self._terminal = self._core._state is None
        return None

    async def fail(self, reason: str) -> TITOTrajectoryArtifact | None:
        if not self._terminal:
            try:
                return await self._core._cancel_and_terminalize(
                    self.trajectory_id,
                    "failed",
                    reason,
                )
            finally:
                self._terminal = self._core._state is None
        return None

    async def close(self) -> TITOTrajectoryArtifact | None:
        if self._terminal:
            return None
        return await self.abandon("sidecar_shutdown")

    async def __aenter__(self) -> "TITOTrajectoryEngine":
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        if not self._terminal:
            await asyncio.shield(self.abandon("trajectory_scope_exit"))
