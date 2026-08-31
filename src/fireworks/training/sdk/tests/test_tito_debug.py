from __future__ import annotations

import json
import hashlib

import pytest

from fireworks.training.sdk.tito import TITOError
from fireworks.training.sdk.tito_debug import (
    TITOLocalDebugSink,
    TITOLocalDebugConfig,
    TITODebugStorageFullError,
)
from fireworks.training.sdk.tito._engine import _LinearTrajectoryCore


def _config(tmp_path, **kwargs):
    return TITOLocalDebugConfig(
        root_dir=tmp_path.resolve(),
        run_id=kwargs.pop("run_id", "debug-test"),
        writer_id=kwargs.pop("writer_id", "writer-test"),
        max_local_bytes=kwargs.pop("max_local_bytes", 1_000_000),
        min_free_bytes=kwargs.pop("min_free_bytes", 0),
        **kwargs,
    )


def _events(sink: TITOLocalDebugSink, trajectory_id: str):
    key = hashlib.sha256(trajectory_id.encode()).hexdigest()
    path = sink.trajectories_dir / key / "events.jsonl"
    return [json.loads(line) for line in path.read_text().splitlines()]


def test_writes_plain_searchable_events_and_exact_arrays(tmp_path) -> None:
    sink = TITOLocalDebugSink(_config(tmp_path))
    sink.record(
        "prepare",
        "trajectory-1",
        {"call_id": "call-1", "disposition": "append"},
        {"prepared_prompt_ids": [1, 2, 3], "sampling_logprobs": [None, -0.2]},
    )
    sink.close_trajectory("trajectory-1", "completed", {"reason": "test"})
    sink.close()

    events = _events(sink, "trajectory-1")
    assert [event["event"] for event in events] == [
        "prepare",
        "trajectory_terminal",
    ]
    assert events[0]["arrays"]["prepared_prompt_ids"] == [1, 2, 3]
    assert events[1]["payload"]["status"] == "completed"
    assert json.loads(sink.manifest_path.read_text())["format"] == ("fireworks-tito-debug-jsonl")


def test_trajectory_id_is_hashed_before_it_reaches_a_path(tmp_path) -> None:
    sink = TITOLocalDebugSink(_config(tmp_path, run_id="path-boundary"))
    trajectory_id = "../../outside/nested"
    sink.record("prepare", trajectory_id, {}, {"prepared_prompt_ids": [1]})
    sink.close()

    assert _events(sink, trajectory_id)[0]["trajectory_id"] == trajectory_id
    assert trajectory_id not in str(sink.trajectories_dir)
    assert not (sink.writer_dir.parent / "outside").exists()


def test_writer_directory_cannot_be_reused(tmp_path) -> None:
    config = _config(tmp_path)
    first = TITOLocalDebugSink(config)
    first.record("prepare", "trajectory-1", {})
    first.close()

    with pytest.raises(FileExistsError):
        TITOLocalDebugSink(config)

    assert [event["event_seq"] for event in _events(first, "trajectory-1")] == [0]


def test_redaction_happens_before_persistence(tmp_path) -> None:
    sink = TITOLocalDebugSink(_config(tmp_path, redact_text=True))
    sink.record(
        "request_normalized",
        "trajectory-redacted",
        {
            "authorization": "Bearer top-secret",
            "content": "ordinary private text",
            "diagnostic": "token=also-secret",
        },
    )
    sink.close()

    serialized = json.dumps(_events(sink, "trajectory-redacted"))
    assert "top-secret" not in serialized
    assert "also-secret" not in serialized
    assert "ordinary private text" not in serialized
    assert "<redacted>" in serialized


def test_quota_failure_does_not_advance_event_sequence(tmp_path) -> None:
    sink = TITOLocalDebugSink(_config(tmp_path, max_local_bytes=300))
    with pytest.raises(TITODebugStorageFullError):
        sink.record("prepare", "trajectory-full", {"value": "x" * 500})
    assert sink._sequences == {}  # noqa: SLF001
    sink.close()


async def test_engine_fails_loudly_when_enabled_debug_storage_is_full(
    tmp_path,
) -> None:
    from fireworks.training.sdk.tests.test_tito import FakeSampler, FakeRenderer

    sink = TITOLocalDebugSink(_config(tmp_path, max_local_bytes=300))
    engine = _LinearTrajectoryCore(
        FakeSampler(),  # type: ignore[arg-type]
        FakeRenderer(),
        max_context_tokens=256,
        max_output_tokens=32,
        observer=sink,
    )

    with pytest.raises(TITOError) as exc_info:
        await engine.create_trajectory_async(metadata={"large": "x" * 500})
    assert exc_info.value.code == "tito_debug_storage_error"
    assert engine._state is None  # noqa: SLF001
    sink.close()


def test_tombstone_events_are_separate_from_trajectory_history(tmp_path) -> None:
    sink = TITOLocalDebugSink(_config(tmp_path))
    sink.record("trajectory_open", "trajectory-1", {})
    sink.close_trajectory("trajectory-1", "completed")
    sink.record_tombstone_event("request_after_terminal", "trajectory-1", {})
    sink.close()

    assert [item["event"] for item in _events(sink, "trajectory-1")] == [
        "trajectory_open",
        "trajectory_terminal",
    ]
    tombstones = [json.loads(line) for line in sink.tombstones_path.read_text().splitlines()]
    assert tombstones[0]["event"] == "request_after_terminal"


@pytest.mark.parametrize("value", ["../bad", "has space", ""])
def test_run_and_writer_ids_are_path_safe(tmp_path, value) -> None:
    with pytest.raises(ValueError):
        TITOLocalDebugConfig(
            root_dir=tmp_path.resolve(),
            run_id=value,
            max_local_bytes=1_000,
            min_free_bytes=0,
        )
