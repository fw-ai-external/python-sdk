"""Request admission must recover from transient congestion without an RL-step clock."""

from __future__ import annotations

import time

import pytest

from fireworks.training.sdk.sampling import ServerMetrics
from fireworks.training.sdk.concurrency import AdaptiveConcurrencyController
from tests_training.profile_concurrency import feedback_trace, small_window_recovery


def test_clean_queue_recovers_after_a_large_transient_without_a_step_boundary() -> None:
    controller = AdaptiveConcurrencyController(initial_window=32)
    for _ in range(32):
        controller.release(ServerMetrics(prefill_queue_duration=200.0))
    reduced = controller.window_size
    assert reduced == 16

    # The stall is over. An old EMA must not cause another multiplicative cut.
    for _ in range(reduced):
        controller.release(ServerMetrics(prefill_queue_duration=0.05))

    assert controller.window_size > reduced
    assert controller.ema_prefill_queue == pytest.approx(0.05)


def test_inflight_requests_from_before_a_cut_cannot_keep_reducing_the_window(monkeypatch: pytest.MonkeyPatch) -> None:
    clock = [100.0]
    monkeypatch.setattr("fireworks.training.sdk.concurrency.time.monotonic", lambda: clock[0])
    controller = AdaptiveConcurrencyController(initial_window=32)

    def old_response() -> ServerMetrics:
        return ServerMetrics(prefill_queue_duration=200.0, client_request_started_at=1.0)

    for _ in range(32):
        controller.release(old_response())
    assert controller.window_size == 16

    # These completions all describe the load before the first reduction.
    clock[0] = 101.0
    for _ in range(128):
        controller.release(old_response())
    assert controller.window_size == 16

    for _ in range(16):
        controller.release(ServerMetrics(prefill_queue_duration=0.05, client_request_started_at=100.5))
    assert controller.window_size > 16
    summary = controller.step_completed()
    assert summary["stale_prefill_observations"] == 128
    assert controller.step_completed()["stale_prefill_observations"] == 0


@pytest.mark.parametrize("initial_window", [1, 2, 4])
def test_small_windows_adjust_after_one_window_of_fresh_responses(initial_window: int) -> None:
    controller = AdaptiveConcurrencyController(initial_window=initial_window)
    for _ in range(initial_window):
        controller.release(ServerMetrics(prefill_queue_duration=0.05))
    assert controller.window_size > initial_window


def test_newly_admitted_requests_still_reduce_under_persistent_queue_pressure(monkeypatch: pytest.MonkeyPatch) -> None:
    clock = [1.0]
    monkeypatch.setattr("fireworks.training.sdk.concurrency.time.monotonic", lambda: clock[0])
    controller = AdaptiveConcurrencyController(initial_window=32)
    for _ in range(5):
        admitted_at = clock[0] + 1.0
        clock[0] += 2.0
        for _ in range(controller.window_size):
            controller.release(ServerMetrics(prefill_queue_duration=5.0, client_request_started_at=admitted_at))
    assert controller.window_size == 1


def test_explicit_step_only_adjustment_remains_step_only() -> None:
    controller = AdaptiveConcurrencyController(initial_window=1, adjustment_interval=0)
    for _ in range(32):
        controller.release(ServerMetrics(prefill_queue_duration=0.05))
    assert controller.window_size == 1
    controller.step_completed()
    assert controller.window_size > 1


def test_custom_metrics_without_admission_time_still_report_real_congestion() -> None:
    controller = AdaptiveConcurrencyController(initial_window=8, adjustment_interval=1)
    for _ in range(3):
        controller.release(ServerMetrics(prefill_queue_duration=5.0))
    assert controller.window_size == 1


def test_stale_prefill_observations_do_not_disable_transport_congestion(monkeypatch: pytest.MonkeyPatch) -> None:
    clock = [100.0]
    monkeypatch.setattr("fireworks.training.sdk.concurrency.time.monotonic", lambda: clock[0])
    controller = AdaptiveConcurrencyController(initial_window=32, adjustment_interval=1)
    controller.release(ServerMetrics(prefill_queue_duration=200.0, client_request_started_at=1.0))
    assert controller.window_size == 16
    controller.release(ServerMetrics(prefill_queue_duration=200.0, client_request_started_at=1.0))
    controller.release(ServerMetrics(http_status_code=503))
    assert controller.window_size == 8


@pytest.mark.asyncio
@pytest.mark.parametrize("congestion", ["503", "transport"])
@pytest.mark.parametrize("adjustment_interval", [0, 32])
async def test_transport_cut_discards_pre_cut_healthy_feedback(
    monkeypatch: pytest.MonkeyPatch, congestion: str, adjustment_interval: int
) -> None:
    clock = [100.0]
    monkeypatch.setattr("fireworks.training.sdk.concurrency.time.monotonic", lambda: clock[0])
    controller = AdaptiveConcurrencyController(initial_window=8, adjustment_interval=adjustment_interval)
    for _ in range(8):
        await controller.acquire()
    for _ in range(5):
        controller.release(ServerMetrics(prefill_queue_duration=0.05, client_request_started_at=1.0))
    assert controller.window_size == 8

    controller.release(
        ServerMetrics(http_status_code=503) if congestion == "503" else ServerMetrics(transport_error=True)
    )
    assert controller.window_size == 4
    assert controller.step_completed()["window_after"] == 4

    # Remaining responses were admitted before the transport-driven cut.
    for _ in range(2):
        controller.release(ServerMetrics(prefill_queue_duration=0.05, client_request_started_at=1.0))
    assert controller.window_size == 4
    assert controller.step_completed()["stale_prefill_observations"] == 2

    clock[0] = 101.0
    for _ in range(4):
        await controller.acquire()
        controller.release(ServerMetrics(prefill_queue_duration=0.05, client_request_started_at=101.0))
    controller.step_completed()
    assert controller.window_size > 4
    assert controller.in_flight == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("congestion", ["503", "transport"])
@pytest.mark.parametrize("successes_before_cut", [0, 4])
async def test_status_burst_cannot_count_toward_fresh_prefill_recovery(
    congestion: str, successes_before_cut: int
) -> None:
    controller = AdaptiveConcurrencyController(initial_window=8)
    controller._now = lambda: 100.0  # All congestion responses belong to one cooldown burst.
    for _ in range(8):
        await controller.acquire()
    for index in range(8):
        if index < successes_before_cut:
            metrics = ServerMetrics(http_status_code=200)
        else:
            metrics = (
                ServerMetrics(http_status_code=503) if congestion == "503" else ServerMetrics(transport_error=True)
            )
        controller.release(metrics)
    assert controller.window_size == 4
    assert controller.in_flight == 0

    # Recovery needs four fresh queue samples, not one sample plus old statuses.
    for completed in range(1, 5):
        await controller.acquire()
        controller.release(ServerMetrics(prefill_queue_duration=0.05, client_request_started_at=time.monotonic()))
        assert controller.window_size == (4 if completed < 4 else 8)
    summary = controller.step_completed()
    assert summary["requests"] == 12
    assert summary["congestion_events"] == 1
    assert controller.in_flight == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("adjustment_interval", [2, 32])
@pytest.mark.parametrize("other_feedback", [None, 200])
async def test_status_and_metricless_completions_do_not_advance_prefill_interval(
    adjustment_interval: int, other_feedback: int | None
) -> None:
    controller = AdaptiveConcurrencyController(initial_window=4, adjustment_interval=adjustment_interval)
    await controller.acquire()
    controller.release(ServerMetrics(prefill_queue_duration=0.05))
    for _ in range(32):
        await controller.acquire()
        controller.release(None if other_feedback is None else ServerMetrics(http_status_code=other_feedback))
        assert controller.window_size == 4

    required = min(adjustment_interval, 4)
    for completed in range(2, required + 1):
        await controller.acquire()
        controller.release(ServerMetrics(prefill_queue_duration=0.05))
        assert controller.window_size == (4 if completed < required else 8)
    assert controller.in_flight == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("congestion", ["503", "transport"])
async def test_transport_cut_at_minimum_discards_pre_cut_healthy_feedback(congestion: str) -> None:
    controller = AdaptiveConcurrencyController(initial_window=1, adjustment_interval=0)
    await controller.acquire()
    controller.release(ServerMetrics(prefill_queue_duration=0.05))
    await controller.acquire()
    controller.release(
        ServerMetrics(http_status_code=503) if congestion == "503" else ServerMetrics(transport_error=True)
    )
    assert controller.window_size == 1
    assert controller.step_completed()["window_after"] == 1

    await controller.acquire()
    controller.release(ServerMetrics(prefill_queue_duration=0.05))
    controller.step_completed()
    assert controller.window_size > 1
    assert controller.in_flight == 0


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "scenario, final_window", [("healthy", 64), ("transient", 64), ("persistent", 1), ("serverless", 48)]
)
async def test_profiled_request_feedback_preserves_capacity_and_recovers(scenario: str, final_window: int) -> None:
    trace = await feedback_trace(AdaptiveConcurrencyController, scenario)
    assert len(trace["windows"]) == 577  # Initial state + all 576 acquired/released requests.
    assert trace["windows"][-1] == final_window
    if scenario == "transient":
        assert trace["windows"][64] == 32
        assert sum(trace["ignored_prefill_feedback"]) == 32
        assert trace["ema_prefill_queue_seconds"][-1] == pytest.approx(0.05)


@pytest.mark.asyncio
async def test_profiled_window_one_recovers_after_one_fresh_response() -> None:
    assert await small_window_recovery(AdaptiveConcurrencyController) == 1
