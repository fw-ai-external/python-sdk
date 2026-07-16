"""Concurrency controllers for DeploymentSampler completions (fixed + AIMD)."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from fireworks.training.sdk.sampling import ServerMetrics

logger = logging.getLogger(__name__)


@runtime_checkable
class SamplingConcurrencyController(Protocol):
    """Interface for controlling concurrent deployment sampling requests."""

    @property
    def window_size(self) -> int: ...

    async def acquire(self) -> None: ...

    def release(self, metrics: "ServerMetrics | None" = None) -> None: ...

    def step_completed(self) -> dict[str, float]: ...


# =============================================================================
# FixedConcurrencyController — static semaphore
# =============================================================================


class FixedConcurrencyController(SamplingConcurrencyController):
    """Fixed concurrency controller backed by an asyncio.Semaphore.

    Implements ``SamplingConcurrencyController`` with a static window.
    """

    def __init__(self, max_concurrency: int):
        self._max_concurrency = max_concurrency
        self._semaphore = asyncio.Semaphore(max_concurrency)

    @property
    def window_size(self) -> int:
        return self._max_concurrency

    async def acquire(self) -> None:
        await self._semaphore.acquire()

    def release(self, metrics: "ServerMetrics | None" = None) -> None:
        self._semaphore.release()

    def step_completed(self) -> dict[str, float]:
        return {"window": float(self._max_concurrency)}


# =============================================================================
# AdaptiveConcurrencyController — AIMD-based dynamic concurrency
# =============================================================================


class AdaptiveConcurrencyController(SamplingConcurrencyController):
    """AIMD concurrency controller with proportional increase.

    Uses ``prefill_queue_duration`` from server response headers as the
    congestion signal.  When the prefill queue is above the target, the
    window shrinks (multiplicative decrease).  When below, the window
    grows proportionally to the headroom (further below target = faster
    growth), capped at ``_MAX_INCREASE_FACTOR``.

    Compatible with ``DeploymentSampler`` -- pass as ``concurrency_controller``.
    """

    # -- Internal constants (not user-configurable) --
    _MAX_INCREASE_FACTOR = 4.0   # Cap proportional increase at 4x base rate.
    _MIN_PQ_FLOOR = 0.001        # Avoid division by zero in headroom calc.
    _DEFAULT_INITIAL_WINDOW = 16
    _DEFAULT_MIN_WINDOW = 1
    _DEFAULT_MAX_WINDOW = 256
    _DEFAULT_PQ_TARGET = 0.5     # Prefill queue target in seconds.
    _DEFAULT_ADDITIVE_INCREASE = 1.0
    _DEFAULT_MULTIPLICATIVE_DECREASE = 0.5
    _DEFAULT_EMA_ALPHA = 0.3
    _DEFAULT_ADJUSTMENT_INTERVAL = 32

    def __init__(
        self,
        initial_window: int = _DEFAULT_INITIAL_WINDOW,
        min_window: int = _DEFAULT_MIN_WINDOW,
        max_window: int = _DEFAULT_MAX_WINDOW,
        prefill_queue_target: float = _DEFAULT_PQ_TARGET,
        additive_increase: float = _DEFAULT_ADDITIVE_INCREASE,
        multiplicative_decrease: float = _DEFAULT_MULTIPLICATIVE_DECREASE,
        ema_alpha: float = _DEFAULT_EMA_ALPHA,
        adjustment_interval: int = _DEFAULT_ADJUSTMENT_INTERVAL,
    ):
        if adjustment_interval < 0:
            raise ValueError("adjustment_interval must be non-negative")

        self._window: float = float(initial_window)
        self._min_window = min_window
        self._max_window = max_window
        self._prefill_queue_target = prefill_queue_target
        self._additive_increase = additive_increase
        self._multiplicative_decrease = multiplicative_decrease
        self._ema_alpha = ema_alpha
        self._adjustment_interval = adjustment_interval

        self._ema_prefill_queue: float | None = None
        self._semaphore = asyncio.Semaphore(initial_window)
        self._interval_requests: int = 0

        self._completed_requests: int = 0
        self._last_logged_window: int = initial_window

        # Batch-level metrics: collected per-request, aggregated at step boundary.
        self._prefill_queues: list[float] = []
        self._step_metrics_count: int = 0
        self._step_cache_hits: int = 0
        self._step_cache_total: int = 0

    @property
    def window_size(self) -> int:
        return max(self._min_window, min(self._max_window, int(self._window)))

    @property
    def ema_prefill_queue(self) -> float | None:
        return self._ema_prefill_queue

    async def acquire(self) -> None:
        await self._semaphore.acquire()

    def release(self, metrics: ServerMetrics | None = None) -> None:
        """Release a slot, collect metrics, and optionally adjust the window.

        A positive ``adjustment_interval`` adjusts after that many completed
        requests. :meth:`step_completed` adjusts any remaining requests and
        starts a fresh interval for the next RL step.
        """
        self._semaphore.release()
        self._completed_requests += 1
        if metrics is not None:
            if metrics.prefill_queue_duration is not None:
                self._prefill_queues.append(metrics.prefill_queue_duration)
            self._step_metrics_count += 1
            if metrics.cached_prompt_tokens is not None:
                self._step_cache_hits += metrics.cached_prompt_tokens
            if metrics.prompt_tokens is not None:
                self._step_cache_total += metrics.prompt_tokens

        if self._adjustment_interval > 0:
            self._interval_requests += 1
            if self._interval_requests >= self._adjustment_interval:
                if self._prefill_queues:
                    avg_pq = sum(self._prefill_queues) / len(
                        self._prefill_queues
                    )
                    self._update_window(avg_pq)
                self._prefill_queues.clear()
                self._interval_requests = 0

    def step_completed(self) -> dict[str, float]:
        """Called between RL steps.  Adjusts window based on the step's
        average prefill queue duration and returns a summary dict for logging.

        Returns:
            Dict with step-level metrics (``avg_pq``, ``window``, ``cache_hit_rate``, etc.).
        """
        summary: dict[str, float] = {
            "window": float(self.window_size),
            "requests": float(self._step_metrics_count),
        }

        # Compute the average since the last adjustment.
        if self._prefill_queues:
            avg_pq = sum(self._prefill_queues) / len(self._prefill_queues)
            summary["avg_pq"] = avg_pq
            self._update_window(avg_pq)
            summary["window_after"] = float(self.window_size)

        if self._step_cache_total > 0:
            summary["cache_hit_rate"] = self._step_cache_hits / self._step_cache_total

        if self._ema_prefill_queue is not None:
            summary["ema_pq"] = self._ema_prefill_queue

        logger.info(
            "AdaptiveConcurrency step: window=%d, reqs=%d, avg_pq=%.3fs, ema_pq=%s, cache=%.1f%%",
            self.window_size,
            self._step_metrics_count,
            summary.get("avg_pq", 0.0),
            f"{self._ema_prefill_queue:.3f}" if self._ema_prefill_queue is not None else "N/A",
            summary.get("cache_hit_rate", 0.0) * 100,
        )

        # Reset per-step accumulators.
        self._prefill_queues.clear()
        self._interval_requests = 0
        self._step_metrics_count = 0
        self._step_cache_hits = 0
        self._step_cache_total = 0

        return summary

    def _update_window(self, avg_prefill_queue: float) -> None:
        """AIMD adjustment based on the averaged prefill queue."""
        if self._ema_prefill_queue is None:
            self._ema_prefill_queue = avg_prefill_queue
        else:
            a = self._ema_alpha
            self._ema_prefill_queue = a * avg_prefill_queue + (1 - a) * self._ema_prefill_queue

        old_int_window = self.window_size

        if self._ema_prefill_queue > self._prefill_queue_target:
            self._window *= self._multiplicative_decrease
        else:
            # Proportional increase: grow faster when far below target.
            headroom = self._prefill_queue_target / max(self._ema_prefill_queue, self._MIN_PQ_FLOOR)
            increase = self._additive_increase * min(headroom, self._MAX_INCREASE_FACTOR)
            self._window += increase

        self._window = max(float(self._min_window), min(float(self._max_window), self._window))
        new_int_window = self.window_size

        if new_int_window != old_int_window:
            resized_window = self._resize_semaphore(old_int_window, new_int_window)
            if resized_window != new_int_window:
                self._window = float(resized_window)

    def _resize_semaphore(self, old_size: int, new_size: int) -> int:
        delta = new_size - old_size
        if delta > 0:
            for _ in range(delta):
                self._semaphore.release()
            return new_size
        elif delta < 0:
            resized_size = old_size
            for _ in range(-delta):
                if self._semaphore._value > 0:
                    self._semaphore._value -= 1
                    resized_size -= 1
                else:
                    break
            return resized_size
        return old_size
