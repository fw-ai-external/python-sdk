"""Exclusive wall-time accounting within one agentic rollout clock domain."""

from __future__ import annotations

import time
import asyncio
from typing import Literal
from collections.abc import Callable

Phase = Literal["model", "tool", "other"]
Outcome = Literal["succeeded", "failed", "cancelled"]

_PHASES = ("model", "tool", "other")
_OUTCOMES = ("succeeded", "failed", "cancelled")
_PHASE_INDEX = {name: index for index, name in enumerate(_PHASES)}
_OUTCOME_INDEX = {name: index for index, name in enumerate(_OUTCOMES)}
_WALL_PHASES = ("unattributed", "model_only", "tool_only", "model_tool_overlap", "other")
# Model and tool spans take precedence over concurrent other operations.
_WALL_INDEX = (0, 1, 2, 3, 4, 1, 2, 3)


class _MeasuredPhase:
    __slots__ = ("metrics", "index", "started_at")

    def __init__(self, metrics: TITORolloutPhaseMetrics, index: int) -> None:
        self.metrics = metrics
        self.index = index

    def __enter__(self) -> None:
        self.started_at = self.metrics._begin(self.index)

    def __exit__(self, exc_type, exc, traceback) -> None:
        outcome = 0 if exc_type is None else 2 if isinstance(exc, asyncio.CancelledError) else 1
        self.metrics._end(self.index, self.started_at, outcome)


class TITORolloutPhaseMetrics:
    """Opt-in wall breakdown for a local agentic rollout on one clock.

    Construct one per rollout and wrap actual client model calls and tool
    execution with `measure`. Report `finish()` once the operations settle.
    Server decode durations belong to the separately reported serving metrics.
    """

    __slots__ = ("_clock", "_last", "_started", "_active", "_mask", "_wall", "_work", "_counts", "_finished")

    def __init__(self, clock: Callable[[], float] = time.monotonic) -> None:
        self._clock = clock
        self._last = self._started = clock()
        self._active = [0, 0, 0]
        self._mask = 0
        self._wall = [0.0] * len(_WALL_PHASES)
        self._work = [0.0, 0.0, 0.0]
        self._counts = [0] * (len(_PHASES) * len(_OUTCOMES))
        self._finished = False

    def _begin(self, index: int) -> float:
        if self._finished:
            raise RuntimeError("rollout phase metrics are closed")
        now = self._clock()
        self._wall[_WALL_INDEX[self._mask]] += now - self._last
        self._last = now
        self._active[index] += 1
        self._mask |= 1 << index
        return now

    def _end(self, index: int, started_at: float, outcome: int) -> None:
        if self._active[index] <= 0:
            raise RuntimeError(f"no active rollout phase {_PHASES[index]!r}")
        now = self._clock()
        self._wall[_WALL_INDEX[self._mask]] += now - self._last
        self._last = now
        self._active[index] -= 1
        if not self._active[index]:
            self._mask &= ~(1 << index)
        self._work[index] += now - started_at
        self._counts[index * 3 + outcome] += 1

    def begin(self, phase: Phase) -> float:
        return self._begin(_PHASE_INDEX[phase])

    def end(self, phase: Phase, started_at: float, outcome: Outcome = "succeeded") -> None:
        self._end(_PHASE_INDEX[phase], started_at, _OUTCOME_INDEX[outcome])

    def measure(self, phase: Phase) -> _MeasuredPhase:
        """Ensure synchronous and async callers account for all exits."""
        return _MeasuredPhase(self, _PHASE_INDEX[phase])

    def finish(self) -> dict[str, float]:
        if self._mask:
            raise RuntimeError("rollout phases must be closed before publishing metrics")
        if not self._finished:
            now = self._clock()
            self._wall[0] += now - self._last
            self._last = now
            self._finished = True
        return {
            "wall_seconds": self._last - self._started,
            **{f"{phase}_wall_seconds": self._wall[i] for i, phase in enumerate(_WALL_PHASES)},
            **{f"{phase}_work_seconds": self._work[i] for i, phase in enumerate(_PHASES)},
            **{
                f"{phase}/{outcome}": float(self._counts[i * 3 + j])
                for i, phase in enumerate(_PHASES)
                for j, outcome in enumerate(_OUTCOMES)
            },
        }
