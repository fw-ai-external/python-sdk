"""Unit tests for the session-scoped checkpoint methods on FireworksClient.

These cover promote_session_checkpoint + list_training_session_checkpoints —
the serverless analogs of promote_checkpoint / list_checkpoints used by the
cookbook sft_loop serverless mode. They mock the HTTP layer so they assert the
exact request path/body/parsing without a live gateway.
"""
# Strict pyright flags the loosely-typed HTTP mocks below (untyped dict bodies,
# fake _post/_get stubs, bare-dict method returns). Relax those report
# categories for this mock-only unit test, mirroring
# tests/test_downstream_compat_unit.py.
# pyright: reportUnknownVariableType=false, reportUnknownMemberType=false
# pyright: reportUnknownArgumentType=false, reportUnknownParameterType=false
# pyright: reportMissingParameterType=false, reportMissingTypeArgument=false
from __future__ import annotations

import pytest

try:
    from fireworks.training.sdk.fireworks_client import FireworksClient
except ImportError as exc:  # the SDK package __init__ pulls in tinker (absent in this CI env)
    pytest.skip(f"fireworks.training.sdk requires tinker: {exc}", allow_module_level=True)


class _FakeResp:
    def __init__(self, *, ok: bool = True, status: int = 200, payload: dict | None = None):
        self.is_success = ok
        self.status_code = status
        self._payload = payload or {}

    def json(self):
        return self._payload


def _client() -> FireworksClient:
    return FireworksClient(api_key="fw_test", base_url="https://api.example")


def test_promote_session_checkpoint_builds_request():
    c = _client()
    captured: dict = {}

    def fake_post(path, *, json, **_kwargs):
        captured["path"] = path
        captured["body"] = json
        return _FakeResp(payload={"model": {"state": "READY", "kind": "HF_PEFT_ADDON"}})

    c._post = fake_post  # type: ignore[assignment]
    name = "accounts/acct1/trainingSessions/ts-abcdef/checkpoints/step-5-1a2b3c4d"
    model = c.promote_session_checkpoint(
        name=name,
        output_model_id="my-out",
        base_model="accounts/fireworks/models/qwen3-8b",
    )

    assert captured["path"] == f"/v1/{name}:promote"
    assert captured["body"] == {
        "output_model": "accounts/acct1/models/my-out",
        "base_model": "accounts/fireworks/models/qwen3-8b",
    }
    # Session promote carries neither the job-scoped trainer_job_id nor a
    # hot_load_deployment_id (the gateway resolves the bucket from the session).
    assert "trainer_job_id" not in captured["body"]
    assert "hot_load_deployment_id" not in captured["body"]
    assert model["state"] == "READY"


@pytest.mark.parametrize(
    "bad_name",
    [
        "accounts/a/rlorTrainerJobs/j/checkpoints/c",  # job form, not a session
        "accounts/a/trainingSessions/s",               # missing /checkpoints/<c>
        "trainingSessions/s/checkpoints/c",            # missing account
    ],
)
def test_promote_session_checkpoint_rejects_bad_name(bad_name):
    with pytest.raises(ValueError):
        _client().promote_session_checkpoint(
            name=bad_name, output_model_id="x", base_model="b"
        )


def test_promote_session_checkpoint_rejects_bad_output_model_id():
    with pytest.raises(ValueError):
        _client().promote_session_checkpoint(
            name="accounts/a/trainingSessions/s/checkpoints/c",
            output_model_id="Bad_ID",  # uppercase + underscore are invalid
            base_model="b",
        )


def test_list_training_session_checkpoints_paginates_and_parses():
    c = _client()
    calls: list[str] = []
    pages = [
        {
            "trainingSessionCheckpoints": [{"name": "n1", "promotable": True}],
            "nextPageToken": "tok",
        },
        {"trainingSessionCheckpoints": [{"name": "n2", "promotable": False}]},
    ]

    def fake_get(path, **_kwargs):
        calls.append(path)
        return _FakeResp(payload=pages[len(calls) - 1])

    c._get = fake_get  # type: ignore[assignment]
    name = "accounts/acct1/trainingSessions/ts-abcdef"
    rows = c.list_training_session_checkpoints(name, page_size=50)

    assert calls[0] == f"/v1/{name}/checkpoints?pageSize=50"
    assert "pageToken=tok" in calls[1]
    assert [r["name"] for r in rows] == ["n1", "n2"]


def test_list_training_session_checkpoints_raises_on_http_error():
    c = _client()

    def fake_get(*_args, **_kwargs):
        return _FakeResp(ok=False, status=404, payload={"error": {"message": "not found"}})

    c._get = fake_get  # type: ignore[assignment]
    with pytest.raises(RuntimeError):
        c.list_training_session_checkpoints("accounts/a/trainingSessions/s")
