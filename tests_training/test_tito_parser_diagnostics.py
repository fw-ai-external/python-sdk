from __future__ import annotations

import pickle
from typing import Any

import pytest

from fireworks.training.sdk import TITOError, TITOParseError
from tests_training.test_tito import FakeSampler, FakeRenderer, _engine, _first_request


@pytest.mark.parametrize("reason", ["reasoning_missing_close", "private text\n/tmp/secret", "x" * 129])
async def test_parser_diagnostics_do_not_expose_rejected_content(reason: str, monkeypatch: Any) -> None:
    renderer = FakeRenderer()
    renderer.certification_id = "native-renderer@pinned-revision-v1"

    def reject(*args: Any) -> None:
        raise TITOParseError("private sampled tool payload", reason_code=reason)

    monkeypatch.setattr(renderer, "parse_assistant", reject)
    engine = _engine(FakeSampler(), renderer=renderer)
    trajectory_id = engine.create_trajectory()
    with pytest.raises(TITOError) as failure:
        await engine.complete(trajectory_id, _first_request(max_tokens=12))
    record = failure.value.as_error_record()
    assert record["code"] == "tito_sdk_parse_error"
    assert record["origin"] == "sdk_parser"
    assert record["discard_trajectory"] is True
    assert record["parser_reason_code"] == (reason if reason == "reasoning_missing_close" else "unclassified")
    assert record["renderer_id"] == "fake-v1"
    assert record["renderer_certification_id"] == "native-renderer@pinned-revision-v1"
    assert record["wire_status"] == 200
    assert record.get("upstream_status") is None
    assert record["request_id"] == "request-1"
    assert record["upstream_response_id"] == "cmpl-upstream-1"
    assert record["attempts"] == 1
    assert record["requested_max_tokens"] == 12
    assert record["max_output_tokens"] == 32
    assert record["completion_tokens"] == 2
    assert record["prompt_tokens"] > 0
    assert "private" not in repr(record)
    assert "secret" not in repr(record)
    artifact = await engine.finish_async(trajectory_id)
    assert artifact.status == "failed"


def test_parse_error_legacy_constructor_and_pickle() -> None:
    legacy = TITOParseError("legacy")
    assert legacy.args == ("legacy",)
    assert legacy.reason_code == "unclassified"
    structured = TITOParseError("private", reason_code="tool_unparsed_boundary")
    restored = pickle.loads(pickle.dumps(structured))
    assert restored.args == structured.args
    assert restored.reason_code == structured.reason_code
