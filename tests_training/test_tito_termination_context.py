"""Synthetic barrier-controlled lifecycle tests; no inferred backend causes."""

from __future__ import annotations

import pickle
import asyncio
import threading
from typing import Any

import httpx
import pytest

from fireworks.training.sdk import TITOError
from tests_training.test_tito import FakeSampler, _engine, _first_request


class _BlockingCloseObserver:
    def __init__(self) -> None:
        self.started = threading.Event()
        self.release = threading.Event()

    def record(self, *args: Any, **kwargs: Any) -> int:
        return 1

    def close_trajectory(self, *args: Any, **kwargs: Any) -> None:
        self.started.set()
        assert self.release.wait(5)


@pytest.mark.parametrize(
    "action,status,reason",
    [
        ("finish", "completed", None),
        ("fail", "failed", "whole_trial_bound"),
        ("abandon", "abandoned", "caller_abandoned"),
        ("shutdown", "abandoned", "sidecar_shutdown"),
    ],
)
@pytest.mark.parametrize("discarded", [False, True])
async def test_closing_and_terminal_errors_retain_intent(
    action: str,
    status: str,
    reason: str | None,
    discarded: bool,
) -> None:
    observer = _BlockingCloseObserver()
    engine = _engine(FakeSampler(), observer=observer)
    trajectory_id = engine.create_trajectory()
    if discarded:
        engine._require_active(trajectory_id).discard_error = TITOError(
            "tito_sdk_parse_error",
            422,
            "synthetic private output",
            origin="sdk_parser",
            discard_trajectory=True,
        )
    if action == "finish":
        closing = asyncio.create_task(engine.finish_async(trajectory_id))
    elif action == "shutdown":
        closing = asyncio.create_task(engine.close())
    else:
        closing = asyncio.create_task(engine._cancel_and_terminalize(trajectory_id, status, reason))
    try:
        assert await asyncio.to_thread(observer.started.wait, 5)
        with pytest.raises(TITOError) as pending:
            engine._require_active(trajectory_id)
        context = pending.value.as_error_record()
        assert pending.value.status == 410
        assert context["code"] == "tito_trajectory_closed"
        assert context["origin"] == "sdk"
        assert context["should_retry"] is False
        assert context["termination_phase"] == "closing"
        assert context["terminal_action"] == action
        assert context["requested_terminal_status"] == status
        assert context["terminal_status"] == ("failed" if discarded else status)
        assert context["terminal_reason"] == ("tito_sdk_parse_error" if discarded else reason)
        assert ("cause_error_code" in context) == discarded
        assert "synthetic private output" not in repr(context)
    finally:
        observer.release.set()
        await closing
    with pytest.raises(TITOError) as retired:
        engine._require_active(trajectory_id, count_terminal_request=True)
    terminal = retired.value.as_error_record()
    assert retired.value.status == 410
    assert terminal["termination_phase"] == "terminal"
    assert terminal["terminal_at"] >= context["terminal_started_at"]
    for name in ("terminal_action", "terminal_reason", "terminal_status", "terminal_started_at"):
        assert terminal[name] == context[name]


async def test_failed_close_restores_active_admission_and_clears_intent(caplog: Any) -> None:
    class FailingObserver:
        def record(self, *args: Any, **kwargs: Any) -> int:
            return 1

        def close_trajectory(self, *args: Any, **kwargs: Any) -> None:
            raise OSError("synthetic close failure")

    engine = _engine(FakeSampler(), observer=FailingObserver())
    trajectory_id = engine.create_trajectory()
    with pytest.raises(TITOError) as failure:
        await engine.finish_async(trajectory_id)
    assert failure.value.code == "tito_debug_storage_error"
    state = engine._require_active(trajectory_id)
    assert state.terminalizing is False
    assert state.termination_intent is None
    assert any(getattr(record, "tito_termination", {}).get("terminal_action") == "finish" for record in caplog.records)
    engine.observer = None
    assert (await engine.finish_async(trajectory_id)).status == "completed"


async def test_a_recovered_server_failure_is_not_a_normal_close_cause(monkeypatch: Any) -> None:
    sampler = FakeSampler()
    original = sampler.sample_with_prompt_tokens_result
    failed = False

    async def sample(*args: Any, **kwargs: Any) -> Any:
        nonlocal failed
        if not failed:
            failed = True
            response = httpx.Response(503, request=httpx.Request("POST", "https://example.invalid"))
            raise httpx.HTTPStatusError("synthetic", request=response.request, response=response)
        return await original(*args, **kwargs)

    monkeypatch.setattr(sampler, "sample_with_prompt_tokens_result", sample)
    engine = _engine(sampler)
    trajectory_id = engine.create_trajectory()
    with pytest.raises(TITOError) as failure:
        await engine.complete(trajectory_id, _first_request())
    assert failure.value.origin == "server"
    await engine.complete(trajectory_id, _first_request())
    assert (await engine.finish_async(trajectory_id)).status == "completed"
    with pytest.raises(TITOError) as terminal:
        engine._require_active(trajectory_id)
    assert "cause_error_code" not in terminal.value.context


def test_free_form_termination_reason_is_not_exposed_as_public_error_text() -> None:
    engine = _engine(FakeSampler())
    trajectory_id = engine.create_trajectory()
    engine.fail(trajectory_id, "private /tmp/path and model-generated text")
    with pytest.raises(TITOError) as terminal:
        engine._require_active(trajectory_id)
    assert terminal.value.context["terminal_reason"] == "caller_supplied_reason"
    assert "private" not in repr(terminal.value.as_error_record())


@pytest.mark.parametrize("finish", ["error", "cancelled", "unknown"])
async def test_custom_sampler_cannot_commit_unsuccessful_finishes(finish: str) -> None:
    engine = _engine(FakeSampler(finishes=[finish]))
    trajectory_id = engine.create_trajectory()
    with pytest.raises(TITOError) as failure:
        await engine.complete(trajectory_id, _first_request())
    assert failure.value.code == "tito_sdk_sampling_parse_error"
    assert failure.value.origin == "sdk_parser"
    artifact = await engine.finish_async(trajectory_id)
    assert not [turn for segment in artifact.segments for turn in segment.turns]


async def test_cancelled_finish_still_retires_before_reporting_cancellation() -> None:
    observer = _BlockingCloseObserver()
    engine = _engine(FakeSampler(), observer=observer)
    trajectory_id = engine.create_trajectory()
    closing = asyncio.create_task(engine.finish_async(trajectory_id))
    try:
        assert await asyncio.to_thread(observer.started.wait, 5)
        closing.cancel()
    finally:
        observer.release.set()
    with pytest.raises(asyncio.CancelledError):
        await closing
    with pytest.raises(TITOError) as terminal:
        engine._require_active(trajectory_id)
    assert terminal.value.context["terminal_status"] == "completed"
    assert terminal.value.context["terminal_action"] == "finish"
    assert "cause_error_code" not in terminal.value.context


async def test_cancelled_shutdown_drain_clears_unfinished_intent() -> None:
    engine = _engine(FakeSampler())
    trajectory_id = engine.create_trajectory()
    state = engine._require_active(trajectory_id)
    started = asyncio.Event()
    draining = asyncio.Event()

    async def auxiliary() -> None:
        started.set()
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            draining.set()
            await asyncio.Event().wait()

    child = asyncio.create_task(auxiliary())
    state.auxiliary_tasks.add(child)
    await started.wait()
    closing = asyncio.create_task(engine.close())
    await draining.wait()
    assert state.termination_intent.action == "shutdown"
    closing.cancel()
    with pytest.raises(asyncio.CancelledError):
        await closing
    assert child.done()
    assert state.termination_intent is None
    assert state.terminalizing is False
    await engine.close()


def test_tito_error_survives_worker_pickle() -> None:
    error = TITOError(
        "tito_server_stream_error", 503, "Model request failed", origin="server", should_retry=True,
        context={"wire_status": 200, "request_id": "request-1", "attempts": 2},
    )
    restored = pickle.loads(pickle.dumps(error))
    assert restored.as_error_record() == error.as_error_record()
    assert restored.status == 503


def test_terminalization_warning_omits_caller_reason(caplog: Any) -> None:
    engine = _engine(FakeSampler())
    trajectory_id = engine.create_trajectory()
    state = engine._require_active(trajectory_id)
    engine._begin_terminalization(state, "failed", "fw_synthetic-secret", action="fail")
    engine._clear_termination_intent(state)
    assert caplog.records
    assert "fw_synthetic-secret" not in repr([record.__dict__ for record in caplog.records])


@pytest.mark.parametrize("origin,expected", [("adapter", "adapter"), ("environment", "environment"), ("made-up", "unknown")])
def test_error_origin_and_closure_cause_are_canonical(origin: str, expected: str) -> None:
    engine = _engine(FakeSampler())
    state = engine._require_active(engine.create_trajectory())
    state.discard_error = TITOError("rejected", 422, "private", origin=origin, discard_trajectory=True)
    engine._begin_terminalization(state, "completed", None, action="finish")
    assert state.discard_error.as_error_record()["origin"] == expected
    assert state.termination_intent.as_context()["cause_origin"] == expected


async def test_shutdown_debug_failure_preserves_established_discard_cause() -> None:
    class FailingObserver:
        def record(self, *args: Any, **kwargs: Any) -> int:
            return 1

        def close_trajectory(self, *args: Any, **kwargs: Any) -> None:
            raise OSError("private debug sink failure")

    engine = _engine(FakeSampler(), observer=FailingObserver())
    trajectory_id = engine.create_trajectory()
    engine._require_active(trajectory_id).discard_error = TITOError(
        "tito_sdk_parse_error",
        422,
        "private",
        origin="sdk_parser",
        discard_trajectory=True,
    )
    await engine.close()
    with pytest.raises(TITOError) as terminal:
        engine._require_active(trajectory_id)
    assert terminal.value.context["terminal_status"] == "failed"
    assert terminal.value.context["terminal_reason"] == "tito_sdk_parse_error"
    assert terminal.value.context["cause_error_code"] == "tito_sdk_parse_error"
