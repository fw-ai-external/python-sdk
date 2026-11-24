from __future__ import annotations

import asyncio

import pytest

from fireworks.training.sdk import TITORolloutPhaseMetrics


def test_rollout_wall_time_does_not_double_count_overlapping_model_and_tools() -> None:
    now = 0.0
    phases = TITORolloutPhaseMetrics(lambda: now)
    now = 1.0
    model = phases.begin("model")
    now = 2.0
    shell = phases.begin("tool")
    now = 3.0
    file = phases.begin("tool")
    now = 4.0
    phases.end("model", model)
    now = 5.0
    phases.end("tool", file, "failed")
    now = 6.0
    phases.end("tool", shell)
    now = 7.0
    local = phases.begin("other")
    now = 8.0
    phases.end("other", local)
    now = 9.0
    summary = phases.finish()
    assert summary["wall_seconds"] == 9.0
    assert summary["unattributed_wall_seconds"] == 3.0
    assert summary["model_only_wall_seconds"] == 1.0
    assert summary["tool_only_wall_seconds"] == 2.0
    assert summary["model_tool_overlap_wall_seconds"] == 2.0
    assert summary["other_wall_seconds"] == 1.0
    assert summary["model_work_seconds"] == 3.0
    assert summary["tool_work_seconds"] == 6.0
    assert summary["tool/succeeded"] == 1
    assert summary["tool/failed"] == 1


async def test_cancellation_closes_a_tool_span_without_counting_success() -> None:
    phases = TITORolloutPhaseMetrics()
    started = asyncio.Event()

    async def tool() -> None:
        with phases.measure("tool"):
            started.set()
            await asyncio.Future()

    task = asyncio.create_task(tool())
    await started.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    summary = phases.finish()
    assert summary["tool/cancelled"] == 1
    assert summary["tool/succeeded"] == 0
    assert summary["tool_work_seconds"] == summary["tool_only_wall_seconds"]
