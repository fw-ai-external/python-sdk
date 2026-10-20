"""Synthetic CPU/loopback regressions; no customer replay or live generation."""

from __future__ import annotations

import json
import stat
from pathlib import Path
from dataclasses import replace

import httpx
import pytest

from fireworks.training.sdk import TITOSidecar, TITOFailureTraceConfig
from tests_training.test_tito import FakeSampler, FakeRenderer
from fireworks.training.sdk.tito._failure_trace import _FailureTraceRecorder


def _config(path: Path, **overrides) -> TITOFailureTraceConfig:
    return TITOFailureTraceConfig(root_dir=path.resolve(), min_free_bytes=0, **overrides)


@pytest.mark.parametrize("stream", [False, True])
async def test_failed_parse_retains_raw_trajectory_and_next_trajectory_succeeds(tmp_path, stream, caplog):
    renderer = FakeRenderer()
    sampler = FakeSampler()
    sidecar = TITOSidecar.from_deployment_sampler(
        sampler,
        renderer=renderer,
        max_context_tokens=4096,
        max_output_tokens=128,
        failure_trace_config=_config(tmp_path),
    )
    await sidecar.start()
    try:
        endpoint = await sidecar.create_trajectory_async()
        headers = {"authorization": "Bearer " + endpoint.api_key}
        url = endpoint.openai_base_url + "/chat/completions"
        async with httpx.AsyncClient(trust_env=False) as client:
            messages = [{"role": "user", "content": "q"}]
            first = await client.post(url, headers=headers, json={"messages": messages})
            assert first.status_code == 200
            assert list(tmp_path.rglob("pending/*.jsonl"))
            renderer.fail_parse = True
            messages.extend([first.json()["choices"][0]["message"], {"role": "user", "content": "next"}])
            failed = await client.post(url, headers=headers, json={"messages": messages, "stream": stream})
            if stream:
                assert failed.status_code == 200  # Headers were already committed.
                event = next(line[6:] for line in failed.text.splitlines() if line.startswith("data: {"))
                error = json.loads(event)["error"]
                assert "event: error" in failed.text
            else:
                assert failed.status_code == 422
                assert failed.headers["x-should-retry"] == "false"
                error = failed.json()["error"]
            assert error["code"] == "tito_sdk_parse_error"
            assert error["origin"] == "sdk_parser"
            assert error["discard_trajectory"] is True
            assert error["should_retry"] is False
            trace_path = Path(error["trace_path"])
            events = [json.loads(line) for line in trace_path.read_text().splitlines()]
            assert events[0]["event"] == "trajectory_open"
            terminal = events[-1]
            assert terminal["payload"]["wire_request"]["messages"] == messages
            assert terminal["arrays"]["completion_0_full_tokens"][-2:] == [197, 3]
            assert "TITOParseError: parser failed" in "".join(terminal["payload"]["error"]["exception_chain"])
            assert any(item["event"] == "commit" for item in events)  # Earlier successful turn retained.
            assert stat.S_IMODE(trace_path.stat().st_mode) == 0o600
            assert str(trace_path) in caplog.text
            assert endpoint.api_key not in trace_path.read_text()
            count = len(sampler.calls)
            retried = await client.post(url, headers=headers, json={"messages": messages})
            assert retried.status_code == 422
            assert len(sampler.calls) == count

            artifact = await sidecar.finish_trajectory(endpoint.trajectory_id)
            assert artifact.status == "failed"
            assert artifact.metadata["tito_failure"]["trace_path"] == str(trace_path)
            assert trace_path.is_file()

            renderer.fail_parse = False
            next_endpoint = await sidecar.create_trajectory_async()
            success = await client.post(
                next_endpoint.openai_base_url + "/chat/completions",
                headers={"authorization": "Bearer " + next_endpoint.api_key},
                json={"messages": [{"role": "user", "content": "healthy"}]},
            )
            assert success.status_code == 200
            await sidecar.finish_trajectory(next_endpoint.trajectory_id)
            assert not list(tmp_path.rglob("pending/*.jsonl"))
    finally:
        await sidecar.close()


@pytest.mark.parametrize(
    "kind,code,origin,status",
    [
        ("parser_bug", "tito_sdk_parser_internal_error", "sdk_parser", 422),
        ("server", "tito_server_http_error", "server", 503),
        ("transport", "tito_transport_error", "transport", 504),
        ("decoding", "tito_transport_error", "transport", 502),
    ],
)
async def test_error_origin_is_preserved(tmp_path, kind, code, origin, status):
    class Renderer(FakeRenderer):
        def parse_assistant(self, *args):
            if kind == "parser_bug":
                raise TypeError("synthetic implementation bug")
            return super().parse_assistant(*args)

    class Sampler(FakeSampler):
        async def sample_with_prompt_tokens_result(self, *args, **kwargs):
            if kind == "server":
                response = httpx.Response(
                    503,
                    request=httpx.Request("POST", "https://example.invalid"),
                    headers={"x-request-id": "upstream-123"},
                )
                raise httpx.HTTPStatusError("unavailable", request=response.request, response=response)
            if kind == "transport":
                raise httpx.ReadTimeout("synthetic timeout")
            if kind == "decoding":
                raise httpx.DecodingError("synthetic corrupt compressed HTTP body")
            return await super().sample_with_prompt_tokens_result(*args, **kwargs)

    sidecar = TITOSidecar.from_deployment_sampler(
        Sampler(),
        renderer=Renderer(),
        max_context_tokens=4096,
        max_output_tokens=128,
        failure_trace_config=_config(tmp_path),
    )
    await sidecar.start()
    try:
        endpoint = await sidecar.create_trajectory_async()
        async with httpx.AsyncClient(trust_env=False) as client:
            response = await client.post(
                endpoint.openai_base_url + "/chat/completions",
                headers={"authorization": "Bearer " + endpoint.api_key},
                json={"messages": [{"role": "user", "content": "q"}]},
            )
        assert response.status_code == status
        error = response.json()["error"]
        assert error["code"] == code
        assert error["origin"] == origin
        assert error["discard_trajectory"] is (kind == "parser_bug")
        assert Path(error["trace_path"]).is_file()
        if kind == "server":
            assert error["upstream_request_id"] == "upstream-123"
    finally:
        await sidecar.close()


async def test_unwritable_trace_storage_never_replaces_the_parse_failure(tmp_path):
    root = tmp_path / "file"
    root.write_text("cannot create a directory here")
    sidecar = TITOSidecar.from_deployment_sampler(
        FakeSampler(),
        renderer=FakeRenderer(fail_parse=True),
        max_context_tokens=4096,
        max_output_tokens=128,
        failure_trace_config=_config(root),
    )
    await sidecar.start()
    try:
        endpoint = await sidecar.create_trajectory_async()
        async with httpx.AsyncClient(trust_env=False) as client:
            response = await client.post(
                endpoint.openai_base_url + "/chat/completions",
                headers={"authorization": "Bearer " + endpoint.api_key},
                json={"messages": [{"role": "user", "content": "q"}]},
            )
        error = response.json()["error"]
        assert error["code"] == "tito_sdk_parse_error"
        assert error["trace_storage_error"]
        assert not error.get("trace_path")
        assert (await sidecar.finish_trajectory(endpoint.trajectory_id)).status == "failed"
    finally:
        await sidecar.close()


def test_trace_retention_is_bounded_and_explicit_about_missing_history(tmp_path):
    recorder = _FailureTraceRecorder(
        _config(tmp_path, max_local_bytes=6000, max_trajectory_bytes=2000, max_failed_traces=1)
    )
    recorder.record("trajectory_open", "../outside", {"authorization": "secret"})
    for _ in range(4):
        recorder.record("prepare", "../outside", {"content": "x" * 500})
    recorder.record("call_terminal", "../outside", {"error": "first failure"})
    first = Path(recorder.evidence("../outside")["trace_path"])
    assert recorder.evidence("../outside")["trace_history_truncated"] is True
    assert first.is_relative_to(tmp_path)
    recorder.record("call_terminal", "second", {"error": "second failure"})
    second = Path(recorder.evidence("second")["trace_path"])
    assert not first.exists()
    assert second.is_file()
    assert sum(path.stat().st_size for path in tmp_path.rglob("*.jsonl")) <= 6000


def test_later_bookkeeping_cannot_erase_retained_failure(tmp_path):
    recorder = _FailureTraceRecorder(_config(tmp_path, max_local_bytes=2000, max_trajectory_bytes=1000))
    recorder.record("call_terminal", "failed", {"error": "preserve this failure", "raw": [123, 456]})
    path = Path(recorder.evidence("failed")["trace_path"])
    original = path.read_bytes()
    for _ in range(10):
        recorder.record("prepare", "failed", {"prompt": "x" * 500})
    recorder.close_trajectory("failed", "completed")
    assert path.read_bytes() == original


def test_abandoned_clean_trace_does_not_evict_a_failure(tmp_path):
    recorder = _FailureTraceRecorder(_config(tmp_path, max_failed_traces=1))
    recorder.record("call_terminal", "failed", {"error": "retain"})
    path = Path(recorder.evidence("failed")["trace_path"])
    recorder.record("trajectory_open", "abandoned", {"prompt": "ordinary cancellation"})
    recorder.close_trajectory("abandoned", "abandoned")
    assert path.is_file()
    assert not list(tmp_path.rglob("pending/*.jsonl"))


def test_rejected_call_does_not_evict_a_diagnosed_failure(tmp_path):
    recorder = _FailureTraceRecorder(_config(tmp_path, max_failed_traces=1))
    recorder.record("call_terminal", "failed", {"error": "retain"})
    retained = Path(recorder.evidence("failed")["trace_path"])
    recorder.record("call_terminal", "rejected", {"outcome": "rejected", "error_code": "tito_context_overflow"})
    recorder.close_trajectory("rejected", "completed")
    assert retained.is_file()
    assert not list(tmp_path.rglob("pending/*.jsonl"))


@pytest.mark.parametrize("kind", ["symlink", "permissions", "owner"])
def test_unsafe_trace_root_is_rejected_without_writing(tmp_path, monkeypatch, kind):
    import os

    root = tmp_path / "root"
    if kind == "symlink":
        target = tmp_path / "outside"
        target.mkdir(mode=0o700)
        root.symlink_to(target, target_is_directory=True)
    else:
        root.mkdir(mode=0o700)
        if kind == "permissions":
            root.chmod(0o755)
        else:
            monkeypatch.setattr(os, "geteuid", lambda: root.stat().st_uid + 1)
    recorder = _FailureTraceRecorder(TITOFailureTraceConfig(root_dir=root.absolute(), min_free_bytes=0))
    recorder.record("trajectory_open", "unsafe", {})
    assert recorder.evidence("unsafe")["trace_storage_error"]
    assert not list(root.iterdir())


@pytest.mark.parametrize("stream,prepared", [(False, False), (True, False), (True, True)])
async def test_sidecar_boundary_failure_discards_an_existing_prefix(tmp_path, stream, prepared):
    sidecar = TITOSidecar.from_deployment_sampler(
        FakeSampler(),
        renderer=FakeRenderer(),
        max_context_tokens=4096,
        max_output_tokens=128,
        failure_trace_config=_config(tmp_path),
    )
    await sidecar.start()
    try:
        endpoint = await sidecar.create_trajectory_async()
        async with httpx.AsyncClient(trust_env=False) as client:
            url = endpoint.openai_base_url + "/chat/completions"
            headers = {"authorization": "Bearer " + endpoint.api_key}
            messages = [{"role": "user", "content": "healthy prefix"}]
            first = await client.post(url, headers=headers, json={"messages": messages})
            assert first.status_code == 200

            async def broken_complete(*args, prepared_event=None, **kwargs):
                if prepared and prepared_event is not None:
                    prepared_event.set()
                raise RuntimeError("sidecar boundary regression")

            sidecar._engines[endpoint.trajectory_id].complete = broken_complete
            messages.extend([first.json()["choices"][0]["message"], {"role": "user", "content": "next"}])
            response = await client.post(url, headers=headers, json={"messages": messages, "stream": stream})
            if stream and prepared:
                assert response.status_code == 200
                payload = next(line[6:] for line in response.text.splitlines() if line.startswith("data: {"))
                error = json.loads(payload)["error"]
            else:
                assert response.status_code == 500
                error = response.json()["error"]
            assert error["code"] == "tito_sdk_internal_error"
            assert error["discard_trajectory"] is True
            artifact = await sidecar.finish_trajectory(endpoint.trajectory_id)
            assert artifact.status == "failed"
            assert sum(len(segment.turns) for segment in artifact.segments) == 1
            assert artifact.metadata["tito_failure"]["code"] == error["code"]
            assert "sidecar boundary regression" in Path(error["trace_path"]).read_text()
    finally:
        await sidecar.close()


def test_capture_can_be_disabled_without_creating_files(tmp_path):
    recorder = _FailureTraceRecorder(_config(tmp_path, enabled=False))
    recorder.record("trajectory_open", "disabled", {})
    assert not list(tmp_path.iterdir())
    assert "disabled" in recorder.evidence("disabled")["trace_storage_error"]


def test_only_old_dead_same_host_writers_are_reclaimed(tmp_path, monkeypatch):
    import os
    import time
    import socket

    if os.name != "posix":
        pytest.skip("orphan sweep uses POSIX process liveness")
    for name, pid, hostname, age in [
        ("dead", 99999999, socket.gethostname(), 100),
        ("live", os.getpid(), socket.gethostname(), 100),
        ("fresh", 99999999, socket.gethostname(), 0),
        ("foreign", 99999999, "another-host", 100),
    ]:
        directory = tmp_path / f"writer-{name}"
        directory.mkdir()
        (directory / "owner.json").write_text(
            json.dumps({"pid": pid, "hostname": hostname, "created": time.time() - age})
        )
    (tmp_path / "writer-unmarked").mkdir()
    real_kill = os.kill

    def check_pid(pid, signal):
        if pid == 99999999:
            raise ProcessLookupError
        return real_kill(pid, signal)

    monkeypatch.setattr(os, "kill", check_pid)
    recorder = _FailureTraceRecorder(_config(tmp_path, stale_writer_age_seconds=10))
    recorder.record("trajectory_open", "new", {})
    assert not (tmp_path / "writer-dead").exists()
    assert all((tmp_path / f"writer-{name}").exists() for name in ("live", "fresh", "foreign", "unmarked"))


@pytest.mark.parametrize("pack_fails", [False, True])
def test_collected_trace_survives_oversized_or_invalid_artifact(tmp_path, monkeypatch, pack_fails):
    from fireworks.training.sdk.tito import _failure_trace

    class Artifact:
        trajectory_id = "large-harbor-artifact"

        def pack(self):
            if pack_fails:
                raise ValueError("synthetic invalid artifact")
            return b"x" * 3000

    recorder = _FailureTraceRecorder(_config(tmp_path / "retained", max_local_bytes=4000, max_trajectory_bytes=2000))
    monkeypatch.setattr(_failure_trace, "_default_recorder", recorder)
    source = tmp_path / "collected.jsonl"
    body = json.dumps({"event": "call_terminal", "payload": {"error": "raw failure", "tokens": [123]}}) + "\n"
    source.write_text(body)
    path = _failure_trace.dump_tito_failure_trace(
        Artifact(), ValueError("parse"), code="tito_sdk_parse_error", source_trace=source
    )
    source.unlink()
    assert path is not None
    assert Path(path).read_text() == body
    assert stat.S_IMODE(Path(path).stat().st_mode) == 0o600
    assert sum(p.stat().st_size for p in (tmp_path / "retained").rglob("*.jsonl")) <= 4000


def test_http_decoding_failure_is_not_relabelled_as_sdk_parsing():
    from fireworks.training.sdk.sampling import _sampling_response_evidence

    error = httpx.DecodingError("corrupt compressed HTTP body")
    with pytest.raises(httpx.DecodingError) as failure, _sampling_response_evidence(httpx.Response(200), [1]):
        raise error
    assert failure.value is error
    assert not hasattr(error, "_fireworks_http_status")


@pytest.mark.parametrize("link_kind", ["file", "directory", "collection_root"])
@pytest.mark.parametrize("with_artifact", [False, True])
def test_collected_trace_links_cannot_read_outside_trial(tmp_path, monkeypatch, link_kind, with_artifact):
    from fireworks.training.sdk.tito import _failure_trace

    class Artifact:
        trajectory_id = "symlink-trial"

        def pack(self):
            return b"valid artifact bytes"

    trial = tmp_path / "trial"
    trial.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    secret = "host-file-must-not-enter-diagnostics"
    (outside / "evidence.jsonl").write_text(secret)
    root = trial / "artifacts/tito/failures"
    root.parent.mkdir(parents=True)
    if link_kind == "collection_root":
        root.symlink_to(outside, target_is_directory=True)
        source = root / "evidence.jsonl"
    elif link_kind == "directory":
        root.mkdir()
        (root / "failed").symlink_to(outside, target_is_directory=True)
        source = root / "failed/evidence.jsonl"
    else:
        root.mkdir()
        source = root / "evidence.jsonl"
        source.symlink_to(outside / "evidence.jsonl")
    recorder = _FailureTraceRecorder(_config(tmp_path / "retained", max_active_traces=1))
    monkeypatch.setattr(_failure_trace, "_default_recorder", recorder)
    path = _failure_trace.dump_tito_failure_trace(
        Artifact() if with_artifact else None,
        ValueError("artifact error"),
        code="tito_cookbook_artifact_error",
        source_trace=source,
        source_trace_root=trial,
    )
    if path is not None:
        payload = json.loads(Path(path).read_text().splitlines()[-1])["payload"]
        assert "collected_trace_error" in payload
        assert "collected_trace_jsonl" not in payload
    else:
        assert not with_artifact
    assert all(secret not in p.read_text() for p in (tmp_path / "retained").rglob("*.jsonl"))
    # Invalid imported traces must not exhaust active slots for later failures.
    recorder.record("call_terminal", "subsequent-valid-failure", {"error": "retained"})
    assert recorder.evidence("subsequent-valid-failure")["trace_path"]


@pytest.mark.parametrize("failure_kind", ["alignment", "empty", "sdk_internal"])
async def test_completion_contract_failure_poisoning_retains_successful_prefix(tmp_path, failure_kind):
    class Sampler(FakeSampler):
        async def sample_with_prompt_tokens_result(self, *args, **kwargs):
            result = await super().sample_with_prompt_tokens_result(*args, **kwargs)
            if len(self.calls) == 2:
                if failure_kind == "sdk_internal":
                    raise RuntimeError("synthetic SDK operation failure")
                completions = (
                    []
                    if failure_kind == "empty"
                    else [replace(result.completions[0], completion_len=result.completions[0].completion_len + 1)]
                )
                return replace(result, completions=completions)
            return result

    sampler = Sampler()
    sidecar = TITOSidecar.from_deployment_sampler(
        sampler,
        renderer=FakeRenderer(),
        max_context_tokens=4096,
        max_output_tokens=128,
        failure_trace_config=_config(tmp_path),
    )
    await sidecar.start()
    try:
        endpoint = await sidecar.create_trajectory_async()
        async with httpx.AsyncClient(trust_env=False) as client:
            messages = [{"role": "user", "content": "first"}]
            headers = {"authorization": "Bearer " + endpoint.api_key}
            url = endpoint.openai_base_url + "/chat/completions"
            first = await client.post(url, headers=headers, json={"messages": messages})
            assert first.status_code == 200
            messages.extend([first.json()["choices"][0]["message"], {"role": "user", "content": "next"}])
            response = await client.post(url, headers=headers, json={"messages": messages})
            error = response.json()["error"]
            internal = failure_kind == "sdk_internal"
            code = "tito_sdk_internal_error" if internal else "tito_sdk_sampling_parse_error"
            assert response.status_code == (500 if internal else 422)
            assert error["code"] == code
            assert error["origin"] == ("sdk" if internal else "sdk_parser")
            assert error["discard_trajectory"] is True
            assert Path(error["trace_path"]).is_file()
            await client.post(url, headers=headers, json={"messages": messages})
            assert len(sampler.calls) == 2
        artifact = await sidecar.finish_trajectory(endpoint.trajectory_id)
        assert artifact.status == "failed"
        assert artifact.segments  # Must discard the entire artifact, including this valid prefix.
        assert artifact.metadata["tito_failure"]["code"] == code
    finally:
        await sidecar.close()


async def test_sampler_decode_failure_has_its_own_code_and_raw_evidence(tmp_path):
    from fireworks.training.sdk.sampling import ServerMetrics, DeploymentSampler

    sampler = DeploymentSampler(inference_url="https://example.invalid", model="test", api_key="test-key")
    raw_response = {"id": "raw-response-id", "choices": [{"text": "raw malformed completion"}]}

    async def stream(**kwargs):
        return raw_response, ServerMetrics(response_request_id="server-request-id")

    def decode(*args, **kwargs):
        raise ValueError("synthetic raw response contract mismatch")

    sampler.async_completions_stream = stream
    sampler._parse_completions_result = decode
    sidecar = TITOSidecar.from_deployment_sampler(
        sampler,
        renderer=FakeRenderer(),
        max_context_tokens=4096,
        max_output_tokens=128,
        failure_trace_config=_config(tmp_path),
    )
    await sidecar.start()
    try:
        endpoint = await sidecar.create_trajectory_async()
        async with httpx.AsyncClient(trust_env=False) as client:
            response = await client.post(
                endpoint.openai_base_url + "/chat/completions",
                headers={"authorization": "Bearer " + endpoint.api_key},
                json={"messages": [{"role": "user", "content": "q"}]},
            )
        assert response.status_code == 422
        error = response.json()["error"]
        assert error["code"] == "tito_sdk_sampling_parse_error"
        assert error["upstream_attempts"] == 1
        assert error["server_attempts"][0]["response_request_id"] == "server-request-id"
        terminal = json.loads(Path(error["trace_path"]).read_text().splitlines()[-1])
        assert terminal["payload"]["upstream_completion"] == raw_response
        assert terminal["arrays"]["prompt_ids"]
        artifact = await sidecar.finish_trajectory(endpoint.trajectory_id)
        assert artifact.status == "failed"
        assert artifact.calls[0].server_attempts[0].status_code == 200
    finally:
        await sidecar.close()
        sampler.close()


@pytest.mark.parametrize("chunk", [{"choices": [0]}, {"usage": 3}])
async def test_malformed_http_200_sse_retains_wire_body_and_discards_trajectory(tmp_path, chunk):
    from fireworks.training.sdk.sampling import DeploymentSampler

    wire_body = f"data: {json.dumps(chunk)}\n\ndata: [DONE]\n\n"
    sampler = DeploymentSampler(inference_url="https://example.invalid", model="test", api_key="test-key")
    sampler._async_client = httpx.AsyncClient(
        transport=httpx.MockTransport(
            lambda _request: httpx.Response(200, text=wire_body, headers={"x-request-id": "bad-sse"})
        )
    )
    sidecar = TITOSidecar.from_deployment_sampler(
        sampler,
        renderer=FakeRenderer(),
        max_context_tokens=4096,
        max_output_tokens=128,
        failure_trace_config=_config(tmp_path),
    )
    await sidecar.start()
    try:
        endpoint = await sidecar.create_trajectory_async()
        async with httpx.AsyncClient(trust_env=False) as client:
            response = await client.post(
                endpoint.openai_base_url + "/chat/completions",
                headers={"authorization": "Bearer " + endpoint.api_key},
                json={"messages": [{"role": "user", "content": "q"}]},
            )
        assert response.status_code == 422
        error = response.json()["error"]
        assert error["code"] == "tito_sdk_sampling_parse_error"
        assert error["discard_trajectory"] is True
        assert error["server_attempts"][-1]["status_code"] == 200
        assert error["server_attempts"][-1]["response_request_id"] == "bad-sse"
        terminal = json.loads(Path(error["trace_path"]).read_text().splitlines()[-1])
        assert terminal["payload"]["upstream_completion"]["sse_body"] == wire_body
        assert terminal["payload"]["upstream_completion"]["body_truncated"] is False
        assert (await sidecar.finish_trajectory(endpoint.trajectory_id)).status == "failed"
    finally:
        await sidecar.close()
        await sampler._async_client.aclose()
        sampler.close()


@pytest.mark.parametrize("async_finish", [False, True])
async def test_debug_write_error_does_not_mask_original_parser_error(tmp_path, async_finish):
    from fireworks.training.sdk import TITOError
    from tests_training.test_tito import _first_request
    from fireworks.training.sdk.tito._engine import _LinearTrajectoryCore

    class Observer:
        def record(self, event, *args):
            if event == "call_terminal":
                raise OSError("synthetic debug disk failure")

        def close_trajectory(self, *args):
            raise OSError("synthetic debug close failure")

    core = _LinearTrajectoryCore(
        FakeSampler(),
        FakeRenderer(fail_parse=True),
        max_context_tokens=4096,
        max_output_tokens=128,
        observer=Observer(),
        failure_recorder=_FailureTraceRecorder(_config(tmp_path)),
    )
    trajectory_id = core.create_trajectory()
    with pytest.raises(TITOError) as failure:
        await core.complete(trajectory_id, _first_request())
    assert failure.value.code == "tito_sdk_parse_error"
    assert "debug disk failure" in failure.value.context["debug_storage_error"]
    assert Path(failure.value.context["trace_path"]).is_file()
    artifact = await core.finish_async(trajectory_id) if async_finish else core.finish(trajectory_id)
    assert artifact.status == "failed"
    assert artifact.metadata["tito_failure"]["code"] == "tito_sdk_parse_error"
    assert "debug close failure" in artifact.metadata["tito_failure"]["debug_storage_error"]


async def test_openai_stream_client_receives_parser_code_and_trace_pointer(tmp_path):
    from openai import APIError, AsyncOpenAI

    sidecar = TITOSidecar.from_deployment_sampler(
        FakeSampler(),
        renderer=FakeRenderer(fail_parse=True),
        max_context_tokens=4096,
        max_output_tokens=128,
        failure_trace_config=_config(tmp_path),
    )
    await sidecar.start()
    try:
        endpoint = await sidecar.create_trajectory_async()
        async with AsyncOpenAI(base_url=endpoint.openai_base_url, api_key=endpoint.api_key) as client:
            stream = await client.chat.completions.create(
                model="policy",
                messages=[{"role": "user", "content": "q"}],
                stream=True,
            )
            with pytest.raises(APIError) as failure:
                async for _chunk in stream:
                    pass
            assert failure.value.code == "tito_sdk_parse_error"
            assert Path(failure.value.body["trace_path"]).is_file()
    finally:
        await sidecar.close()


async def test_cancellation_during_failure_recording_cannot_leave_a_trainable_prefix(tmp_path):
    import asyncio
    import threading

    from tests_training.test_tito import _first_request, _second_request
    from fireworks.training.sdk.tito._engine import _LinearTrajectoryCore

    entered = asyncio.Event()
    release = threading.Event()
    loop = asyncio.get_running_loop()

    class Observer:
        def record(self, event, *args):
            if event == "call_terminal":
                loop.call_soon_threadsafe(entered.set)
                assert release.wait(timeout=2), "test did not release the diagnostic barrier"

        def close_trajectory(self, *args):
            pass

    renderer = FakeRenderer()
    core = _LinearTrajectoryCore(
        FakeSampler(),
        renderer,
        max_context_tokens=4096,
        max_output_tokens=128,
        observer=Observer(),
        failure_recorder=_FailureTraceRecorder(_config(tmp_path)),
    )
    trajectory_id = core.create_trajectory()
    await core.complete(trajectory_id, _first_request())
    renderer.fail_parse = True
    task = asyncio.create_task(core.complete(trajectory_id, _second_request()))
    try:
        await asyncio.wait_for(entered.wait(), timeout=2)
        task.cancel()
    finally:
        release.set()
    with pytest.raises(asyncio.CancelledError):
        await task
    artifact = await core.finish_async(trajectory_id)
    assert artifact.segments  # The earlier valid turn must still be discarded.
    assert artifact.status == "failed"
    failure = artifact.metadata["tito_failure"]
    assert failure["code"] == "tito_sdk_parse_error"
    assert Path(failure["trace_path"]).is_file()


@pytest.mark.parametrize("async_create", [False, True])
async def test_failed_create_releases_trace_slot_for_next_real_failure(tmp_path, async_create):
    from fireworks.training.sdk import TITOError
    from tests_training.test_tito import _engine, _first_request

    class FailOpenObserver:
        def record(self, event, *args):
            if event == "trajectory_open":
                raise OSError("synthetic open failure")

    recorder = _FailureTraceRecorder(_config(tmp_path, max_active_traces=1))
    core = _engine(FakeSampler(), FakeRenderer(fail_parse=True), observer=FailOpenObserver(), failure_recorder=recorder)
    for _ in range(3):
        with pytest.raises(TITOError, match="synthetic open failure"):
            if async_create:
                await core.create_trajectory_async()
            else:
                core.create_trajectory()
        assert not list(tmp_path.rglob("pending/*.jsonl"))
    core.observer = None
    trajectory_id = await core.create_trajectory_async() if async_create else core.create_trajectory()
    with pytest.raises(TITOError) as failure:
        await core.complete(trajectory_id, _first_request())
    assert failure.value.code == "tito_sdk_parse_error"
    assert Path(failure.value.context["trace_path"]).is_file()
    await core.finish_async(trajectory_id)


async def test_cancelled_create_releases_trace_slot(tmp_path):
    import asyncio
    import threading

    from tests_training.test_tito import _engine

    entered = threading.Event()
    release = threading.Event()

    class BlockingOpenObserver:
        def record(self, event, *args):
            if event == "trajectory_open":
                entered.set()
                assert release.wait(2)

    core = _engine(
        FakeSampler(),
        observer=BlockingOpenObserver(),
        failure_recorder=_FailureTraceRecorder(_config(tmp_path, max_active_traces=1)),
    )
    task = asyncio.create_task(core.create_trajectory_async())
    try:
        assert await asyncio.to_thread(entered.wait, 2)
        task.cancel()
    finally:
        release.set()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert not list(tmp_path.rglob("pending/*.jsonl"))
    core.observer = None
    trajectory_id = await core.create_trajectory_async()
    assert list(tmp_path.rglob("pending/*.jsonl"))
    await core.finish_async(trajectory_id)


def test_failure_trace_omits_both_sampling_reference_channels(tmp_path):
    recorder = _FailureTraceRecorder(_config(tmp_path))
    arrays = {
        "completion_0_full_tokens": [1, 2],
        "completion_0_top_sampling_references": [{"spans": [1] * 500}],
        "completion_0_sampling_mask_references": [{"spans": [2] * 500}],
    }
    recorder.record("call_terminal", "failed", {"error": "parse failure"}, arrays=arrays)
    path = Path(recorder.evidence("failed")["trace_path"])
    event = json.loads(path.read_text().splitlines()[-1])
    assert event["arrays"] == {"completion_0_full_tokens": [1, 2]}
    assert event["omitted_arrays"] == sorted(set(arrays) - {"completion_0_full_tokens"})
