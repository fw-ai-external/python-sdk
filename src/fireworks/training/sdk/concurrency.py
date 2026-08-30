"""Concurrency controllers for DeploymentSampler completions (fixed + AIMD)."""

from __future__ import annotations

import time
import asyncio
import logging
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from fireworks.training.sdk.sampling import ServerMetrics

logger = logging.getLogger(__name__)


def _set_if_pending(fut: "asyncio.Future") -> None:
    if not fut.done():
        fut.set_result(None)


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
# Window-adjustment strategies
# =============================================================================
#
# The two deployment kinds expose different congestion signals and are kept
# strictly separate:
#
#   * Dedicated deployments report ``prefill_queue_duration``. That signal is
#     rich and well behaved, so its AIMD logic is untouched and never consults
#     HTTP status codes.
#   * Serverless reports no prefill queue at all; the only congestion evidence
#     is 429/503 and transport errors. That logic lives entirely in its own
#     strategy and never runs when a prefill queue is available.
#
# ``AdaptiveConcurrencyController`` routes each observation by asking whether
# the metrics carry a prefill queue, so neither strategy can perturb the other.


class _PrefillQueueStrategy:
    """AIMD on ``prefill_queue_duration`` (dedicated deployments).

    This is the original controller behaviour, unchanged: observations are
    averaged, smoothed into an EMA, and the window moves once per adjustment
    interval or per RL step. It reacts only at those boundaries.
    """

    _MAX_INCREASE_FACTOR = 4.0   # Cap proportional increase at 4x base rate.
    _MIN_PQ_FLOOR = 0.001        # Avoid division by zero in headroom calc.

    def __init__(
        self,
        prefill_queue_target: float,
        additive_increase: float,
        multiplicative_decrease: float,
        ema_alpha: float,
    ):
        self._target = prefill_queue_target
        self._additive_increase = additive_increase
        self._multiplicative_decrease = multiplicative_decrease
        self._ema_alpha = ema_alpha
        self._samples: list[float] = []
        self.ema: float | None = None

    def observe(self, metrics: "ServerMetrics") -> None:
        self._samples.append(metrics.prefill_queue_duration)

    @property
    def has_observations(self) -> bool:
        return bool(self._samples)

    def next_window(self, window: float) -> float:
        """AIMD adjustment based on the averaged prefill queue."""
        avg = sum(self._samples) / len(self._samples)
        if self.ema is None:
            self.ema = avg
        else:
            a = self._ema_alpha
            self.ema = a * avg + (1 - a) * self.ema

        if self.ema > self._target:
            return window * self._multiplicative_decrease
        # Proportional increase: grow faster when far below target.
        headroom = self._target / max(self.ema, self._MIN_PQ_FLOOR)
        increase = self._additive_increase * min(headroom, self._MAX_INCREASE_FACTOR)
        return window + increase

    def summary(self) -> dict[str, float]:
        out: dict[str, float] = {}
        if self._samples:
            out["avg_pq"] = sum(self._samples) / len(self._samples)
        if self.ema is not None:
            out["ema_pq"] = self.ema
        return out

    def reset(self) -> None:
        self._samples.clear()


class _StatusCodeStrategy:
    """Congestion from HTTP 429/503 and transport errors (serverless).

    Serverless sheds load rather than queueing, so the only evidence is the
    rejection itself. Three behaviours matter here that the prefill-queue
    strategy does not need:

    * React on the spot, because a storm can exhaust a request's whole retry
      budget inside a single adjustment interval.
    * Collapse a burst into one shrink via a cooldown, so N concurrent victims
      of one event do not shrink the window N times.
    * Shrink harder for deeper retries, since attempt 5 means the server is
      further past its limit than attempt 1.
    """

    _CONGESTION_STATUS_CODES = frozenset({429, 503})
    _DEEP_RETRY_ATTEMPT = 3

    def __init__(
        self,
        additive_increase: float,
        multiplicative_decrease: float,
        shrink_cooldown_s: float,
    ):
        self._additive_increase = additive_increase
        self._multiplicative_decrease = multiplicative_decrease
        self._shrink_cooldown_s = shrink_cooldown_s
        self._responses = 0
        self._congested = 0
        self.congestion_events = 0
        self.retry_exhaustions = 0
        self._last_shrink_at = float("-inf")

    @classmethod
    def is_congestion(cls, metrics: "ServerMetrics") -> bool:
        if getattr(metrics, "transport_error", False):
            return True
        code = getattr(metrics, "http_status_code", None)
        return code is not None and code in cls._CONGESTION_STATUS_CODES

    def observe(self, metrics: "ServerMetrics") -> bool:
        """Record one response; returns True when it signals congestion."""
        congested = self.is_congestion(metrics)
        code = getattr(metrics, "http_status_code", None)
        if congested:
            self._responses += 1
            self._congested += 1
        elif code is not None and 200 <= code < 300:
            # Other error codes are neither congestion nor evidence of
            # headroom, so they must not drive growth.
            self._responses += 1
        return congested

    def shrink_now(self, window: float, metrics: "ServerMetrics", now: float) -> float | None:
        """Immediate decrease, or None while inside the cooldown."""
        if now - self._last_shrink_at < self._shrink_cooldown_s:
            return None
        self._last_shrink_at = now
        self.congestion_events += 1
        attempt = getattr(metrics, "retry_attempt", 1) or 1
        factor = self._multiplicative_decrease
        if attempt >= self._DEEP_RETRY_ATTEMPT:
            factor *= self._multiplicative_decrease
        return window * factor

    def note_retry_exhausted(self) -> None:
        """Record that a congested serverless request exhausted its retries."""
        self.retry_exhaustions += 1

    @property
    def has_observations(self) -> bool:
        return self._responses > 0

    def next_window(self, window: float) -> float | None:
        # Congestion was already applied immediately; a clean interval grows.
        if self._congested:
            return None
        return window + self._additive_increase

    def summary(self) -> dict[str, float]:
        out: dict[str, float] = {}
        if self._responses:
            out["status_responses"] = float(self._responses)
            out["congestion_responses"] = float(self._congested)
            out["congestion_rate"] = self._congested / self._responses
        if self.congestion_events:
            out["congestion_events"] = float(self.congestion_events)
        if self.retry_exhaustions:
            out["retry_exhaustions"] = float(self.retry_exhaustions)
        return out

    def reset(self) -> None:
        self._responses = 0
        self._congested = 0

    def reset_step(self) -> None:
        self.congestion_events = 0
        self.retry_exhaustions = 0


# =============================================================================
# AdaptiveConcurrencyController — AIMD-based dynamic concurrency
# =============================================================================


class AdaptiveConcurrencyController(SamplingConcurrencyController):
    """AIMD concurrency controller with proportional increase.

    Owns the window and the admission gate; the adjustment policy lives in one
    of two isolated strategies, chosen per observation:

    * ``prefill_queue_duration`` present (dedicated) -> :class:`_PrefillQueueStrategy`,
      the original behaviour, which never looks at HTTP status codes.
    * absent (serverless) -> :class:`_StatusCodeStrategy`, driven by 429/503 and
      transport errors, which never runs when a prefill queue is available.

    Two mechanics are shared because they are correctness, not policy:

    * **Shrink debt.** A shrink can only reclaim slots that are free, and during
      a storm every slot is in flight. Unsatisfied shrink is carried as debt and
      paid off by later releases, so the window actually reaches target.
    * **Loop-agnostic waiting.** The controller is built on the trainer's event
      loop but acquired on the sampler's, so it holds no loop-bound primitive.
      An ``asyncio.Semaphore`` created in ``__init__`` raises "bound to a
      different event loop" on every acquire; a counter plus per-waiter futures
      does not.

    Compatible with ``DeploymentSampler`` -- pass as ``concurrency_controller``.
    """

    _DEFAULT_INITIAL_WINDOW = 8
    _DEFAULT_MIN_WINDOW = 1
    _DEFAULT_MAX_WINDOW = 256
    _DEFAULT_PQ_TARGET = 0.5     # Prefill queue target in seconds.
    _DEFAULT_ADDITIVE_INCREASE = 1.0
    _DEFAULT_MULTIPLICATIVE_DECREASE = 0.5
    _DEFAULT_EMA_ALPHA = 0.3
    _DEFAULT_ADJUSTMENT_INTERVAL = 32
    # One congestion event should shrink once, not once per concurrent victim.
    _DEFAULT_SHRINK_COOLDOWN_S = 1.0

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
        shrink_cooldown_s: float = _DEFAULT_SHRINK_COOLDOWN_S,
    ):
        if adjustment_interval < 0:
            raise ValueError("adjustment_interval must be non-negative")

        self._min_window = min_window
        self._max_window = max_window
        self._window: float = max(
            float(min_window), min(float(max_window), float(initial_window))
        )
        self._adjustment_interval = adjustment_interval

        self._prefill = _PrefillQueueStrategy(
            prefill_queue_target=prefill_queue_target,
            additive_increase=additive_increase,
            multiplicative_decrease=multiplicative_decrease,
            ema_alpha=ema_alpha,
        )
        self._status = _StatusCodeStrategy(
            additive_increase=additive_increase,
            multiplicative_decrease=multiplicative_decrease,
            shrink_cooldown_s=shrink_cooldown_s,
        )
        self._warned_missing_prefill_queue = False

        # Deliberately not an asyncio.Semaphore: see the class docstring.
        self._in_flight: int = 0
        self._waiters: list[asyncio.Future] = []
        self._pending_decrease: int = 0

        self._interval_requests: int = 0
        self._completed_requests: int = 0
        self._last_logged_window: int = int(self._window)
        self._step_metrics_count: int = 0
        self._step_cache_hits: int = 0
        self._step_cache_total: int = 0
        # Window/occupancy samples so a step can report averages, not just the
        # instantaneous window at the boundary.
        self._step_window_sum: float = 0.0
        self._step_window_samples: int = 0
        self._step_max_in_flight: int = 0

    # ------------------------------------------------------------------
    # Window accounting / admission
    # ------------------------------------------------------------------

    @property
    def window_size(self) -> int:
        return max(self._min_window, min(self._max_window, int(self._window)))

    @property
    def in_flight(self) -> int:
        return self._in_flight

    @property
    def ema_prefill_queue(self) -> float | None:
        """Smoothed prefill-queue signal, or None if never observed."""
        return self._prefill.ema

    def _now(self) -> float:
        try:
            return asyncio.get_running_loop().time()
        except RuntimeError:
            return time.monotonic()

    async def acquire(self) -> None:
        while True:
            if self._in_flight < self.window_size and self._pending_decrease == 0:
                self._in_flight += 1
                if self._in_flight > self._step_max_in_flight:
                    self._step_max_in_flight = self._in_flight
                return
            fut: asyncio.Future = asyncio.get_running_loop().create_future()
            self._waiters.append(fut)
            try:
                await fut
            except asyncio.CancelledError:
                if fut in self._waiters:
                    self._waiters.remove(fut)
                raise

    def _wake_waiters(self) -> None:
        """Hand a slot to a waiter. Safe to call from any event loop."""
        while self._waiters and self._in_flight < self.window_size and self._pending_decrease == 0:
            fut = self._waiters.pop(0)
            if fut.done():
                continue
            try:
                fut.get_loop().call_soon_threadsafe(_set_if_pending, fut)
            except RuntimeError:
                continue
            break

    # ------------------------------------------------------------------
    # Observation intake and dispatch
    # ------------------------------------------------------------------

    def release(self, metrics: "ServerMetrics | None" = None) -> None:
        """Release a slot, collect metrics, and optionally adjust the window.

        A positive ``adjustment_interval`` adjusts after that many completed
        requests. :meth:`step_completed` adjusts any remaining requests and
        starts a fresh interval for the next RL step.
        """
        # Free the slot before adjusting, matching the original ordering, so a
        # shrink can reclaim the slot this request just gave back.
        self._in_flight = max(0, self._in_flight - 1)
        if self._pending_decrease > 0:
            self._pending_decrease -= 1
        self._completed_requests += 1
        self._step_window_sum += float(self.window_size)
        self._step_window_samples += 1

        if metrics is not None:
            if metrics.prefill_queue_duration is not None:
                # Dedicated deployment: prefill-queue logic only.
                self._prefill.observe(metrics)
            else:
                # Serverless: status-code logic only.
                if not self._warned_missing_prefill_queue:
                    logger.warning(
                        "prefill_queue_duration is unavailable; "
                        "AdaptiveConcurrencyController is using HTTP 429/503 "
                        "and transport-error congestion signals instead"
                    )
                    self._warned_missing_prefill_queue = True
                if self._status.observe(metrics):
                    proposed = self._status.shrink_now(self._window, metrics, self._now())
                    if proposed is not None:
                        self._resize_window(proposed)
            self._step_metrics_count += 1
            if metrics.cached_prompt_tokens is not None:
                self._step_cache_hits += metrics.cached_prompt_tokens
            if metrics.prompt_tokens is not None:
                self._step_cache_total += metrics.prompt_tokens

        if self._adjustment_interval > 0:
            self._interval_requests += 1
            if self._interval_requests >= self._adjustment_interval:
                self._apply_interval_adjustment()
                self._interval_requests = 0

        self._wake_waiters()

    def note_retry_exhausted(self, metrics: "ServerMetrics | None") -> None:
        """Record exhausted serverless congestion after its final release."""
        if (
            metrics is not None
            and metrics.prefill_queue_duration is None
            and self._status.is_congestion(metrics)
        ):
            self._status.note_retry_exhausted()

    def _apply_interval_adjustment(self) -> None:
        """Ask whichever strategy has observations; prefill wins if both do."""
        if self._prefill.has_observations:
            self._resize_window(self._prefill.next_window(self._window))
        elif self._status.has_observations:
            proposed = self._status.next_window(self._window)
            if proposed is not None:
                self._resize_window(proposed)
        self._prefill.reset()
        self._status.reset()

    def step_completed(self) -> dict[str, float]:
        """Called between RL steps. Adjusts the window from the step's
        observations and returns a summary dict for logging."""
        summary: dict[str, float] = {
            "window": float(self.window_size),
            "requests": float(self._step_metrics_count),
        }
        prefill_mode = self._prefill.has_observations
        summary.update(self._prefill.summary() if prefill_mode else self._status.summary())
        if self._pending_decrease:
            summary["pending_decrease"] = float(self._pending_decrease)
        if self._step_window_samples:
            summary["avg_window"] = self._step_window_sum / self._step_window_samples
        summary["max_in_flight"] = float(self._step_max_in_flight)

        adjusted = self._prefill.has_observations or self._status.has_observations
        self._apply_interval_adjustment()
        if adjusted:
            summary["window_after"] = float(self.window_size)

        if self._step_cache_total > 0:
            summary["cache_hit_rate"] = self._step_cache_hits / self._step_cache_total

        if prefill_mode:
            logger.info(
                "AdaptiveConcurrency step: window=%d, reqs=%d, avg_pq=%.3fs, ema_pq=%s, cache=%.1f%%",
                self.window_size,
                self._step_metrics_count,
                summary.get("avg_pq", 0.0),
                f"{self.ema_prefill_queue:.3f}" if self.ema_prefill_queue is not None else "N/A",
                summary.get("cache_hit_rate", 0.0) * 100,
            )
        else:
            logger.info(
                "AdaptiveConcurrency step: window=%d, reqs=%d, congestion=%d/%d, events=%d, exhausted=%d",
                self.window_size,
                self._step_metrics_count,
                int(summary.get("congestion_responses", 0)),
                int(summary.get("status_responses", 0)),
                int(summary.get("congestion_events", 0)),
                int(summary.get("retry_exhaustions", 0)),
            )

        self._interval_requests = 0
        self._step_metrics_count = 0
        self._step_cache_hits = 0
        self._step_cache_total = 0
        self._step_window_sum = 0.0
        self._step_window_samples = 0
        self._step_max_in_flight = 0
        self._status.reset_step()

        return summary

    def _resize_window(self, new_window: float) -> None:
        old_int_window = self.window_size
        self._window = max(float(self._min_window), min(float(self._max_window), new_window))
        new_int_window = self.window_size
        delta = new_int_window - old_int_window

        if new_int_window != self._last_logged_window:
            # Steps are long, so log adjustments as they happen rather than only
            # at the step boundary -- otherwise the window is invisible for
            # exactly as long as it is adapting.
            logger.info(
                "AdaptiveConcurrency: window %d -> %d (in_flight=%d debt=%d)",
                self._last_logged_window,
                new_int_window,
                self._in_flight,
                self._pending_decrease,
            )
            self._last_logged_window = new_int_window

        if delta > 0:
            self._pending_decrease -= min(delta, self._pending_decrease)
        elif delta < 0:
            free = max(0, old_int_window - self._in_flight)
            self._pending_decrease += max(0, (-delta) - free)

        self._wake_waiters()
