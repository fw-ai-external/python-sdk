"""Unit tests for write-only MLflow ingest, security hardening, and fail-fast checks."""

from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest

from fireworks.training.sdk import _mlflow


class _FakeIngest:
    def __init__(self, *, retry_once: bool = False) -> None:
        self.requests: list[tuple[str, dict]] = []
        self._retry_once = retry_once
        self.transport = httpx.MockTransport(self._handle)

    def _handle(self, request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.headers.get("authorization") == "Bearer fwml1.user.k.secret"
        body = json.loads(request.content.decode("utf-8"))
        self.requests.append((request.url.path, body))
        if request.url.path == "/ingest/experiments":
            return httpx.Response(200, json={"experiment_id": "exp-1"})
        if request.url.path == "/api/2.0/mlflow/runs/create":
            return httpx.Response(200, json={"run": {"info": {"run_id": "run-1"}}})
        if request.url.path == "/api/2.0/mlflow/runs/log-batch" and self._retry_once:
            self._retry_once = False
            return httpx.Response(429, headers={"Retry-After": "0"}, json={})
        return httpx.Response(200, json={})


def test_translate_mlflow_metrics_handles_pass_rates_and_tinker_suffixes() -> None:
    translated = _mlflow.translate_mlflow_metrics(
        {
            "step": 2,
            "rollout/pass@1": 0.5,
            "rollout/pass@4_lower": 0.75,
            "eval/pass^2": 0.25,
            "train/clip_frac:mean": 0.125,
            "nan_val": float("nan"),
            "flag": True,
            "../bad": 1.0,
        }
    )
    assert translated == {
        "rollout/pass_at_1": 0.5,
        "rollout/pass_at_4_lower": 0.75,
        "eval/pass_all_2": 0.25,
        "train/clip_frac:mean": 0.125,
    }


def test_disk_config_fallback_and_secret_redaction(monkeypatch, tmp_path: Path) -> None:
    cfg_dir = tmp_path / "mlflow"
    cfg_dir.mkdir()
    (cfg_dir / "token").write_text("fwml1.user.k.secret\n", encoding="utf-8")
    monkeypatch.setenv(_mlflow.CONFIG_DIR_ENV, str(cfg_dir))

    # A token file without any URI fails fast instead of silently skipping MLflow.
    with pytest.raises(RuntimeError, match="MLflow reporting is required"):
        _mlflow.client_from_env()

    (cfg_dir / "tracking_uri").write_text("https://mlflow-ingest.invalid\n", encoding="utf-8")
    fake = _FakeIngest(retry_once=True)
    client = _mlflow.client_from_env(
        project="rl-exp",
        run_name="run-a",
        params={
            "lr": 1e-4,
            "max_tokens": 512,
            "api_key": "fw_live_secret_value",
            "nested": {"custom_field": "sk-proj-12345"},
        },
        transport=fake.transport,
    )
    assert client is not None
    client.log({"rollout/pass@2": 0.6, "train/loss:sum": 1.5}, step=3)
    client.set_tags({"fireworks.trainer_job_id": "job-1", "auth_token": "leak"})
    client.finish()

    metric_batches = [b["metrics"] for p, b in fake.requests if p == "/api/2.0/mlflow/runs/log-batch" and b["metrics"]]
    assert {m["key"]: (m["value"], m["step"]) for m in metric_batches[0]} == {
        "rollout/pass_at_2": (0.6, 3),
        "train/loss:sum": (1.5, 3),
    }

    params = {
        p["key"]: p["value"]
        for path, b in fake.requests
        if path == "/api/2.0/mlflow/runs/log-batch"
        for p in b["params"]
    }
    assert params["lr"] == "0.0001"
    assert params["max_tokens"] == "512"
    assert params["api_key"] == "[REDACTED]"
    assert params["nested.custom_field"] == "[REDACTED]"

    tags = {
        t["key"]: t["value"] for path, b in fake.requests if path == "/api/2.0/mlflow/runs/log-batch" for t in b["tags"]
    }
    assert tags["fireworks.trainer_job_id"] == "job-1"
    assert tags["auth_token"] == "[REDACTED]"
    assert fake.requests[-1][0] == "/api/2.0/mlflow/runs/update"
    assert fake.requests[-1][1]["status"] == "FINISHED"


def test_rejects_cleartext_remote_http_and_symlinks(monkeypatch, tmp_path: Path) -> None:
    # Remote cleartext http:// is rejected so bearer tokens never cross the network unencrypted;
    # loopback http://127.0.0.1 remains allowed for local testing.
    monkeypatch.setenv(_mlflow.TOKEN_ENV, "fwml1.user.k.secret")
    monkeypatch.setenv(_mlflow.TRACKING_URI_ENV, "http://mlflow-ingest.invalid")
    with pytest.raises(RuntimeError, match="missing/insecure"):
        _mlflow.client_from_env()

    fake = _FakeIngest()
    monkeypatch.setenv(_mlflow.TRACKING_URI_ENV, "http://127.0.0.1:5000")
    local_client = _mlflow.client_from_env(transport=fake.transport)
    assert local_client is not None
    local_client.finish()

    # Symlinked config files are ignored (O_NOFOLLOW).
    monkeypatch.delenv(_mlflow.TOKEN_ENV)
    monkeypatch.delenv(_mlflow.TRACKING_URI_ENV)
    cfg_dir = tmp_path / "symlink-cfg"
    cfg_dir.mkdir()
    outside = tmp_path / "outside-token"
    outside.write_text("fwml1.user.k.secret", encoding="utf-8")
    (cfg_dir / "token").symlink_to(outside)
    monkeypatch.setenv(_mlflow.CONFIG_DIR_ENV, str(cfg_dir))
    assert _mlflow.client_from_env() is None


def test_unconfigured_external_returns_none_while_server_required_fails_fast(monkeypatch) -> None:
    assert _mlflow.is_server_mlflow_required({"X-Fireworks-Require-Mlflow": "1"}) is True
    assert _mlflow.is_server_mlflow_required({}) is False
    assert _mlflow.client_from_env(server_required=False) is None

    with pytest.raises(RuntimeError, match="MLflow reporting is required"):
        _mlflow.client_from_env(server_required=True)

    monkeypatch.setenv(_mlflow.SKIP_REASON_ENV, "offline unit smoke")
    assert _mlflow.client_from_env(server_required=True) is None


def test_large_batch_chunks_and_atexit_marks_uncaught_exception_failed(monkeypatch) -> None:
    fake = _FakeIngest()
    monkeypatch.setenv(_mlflow.TRACKING_URI_ENV, "https://mlflow-ingest.invalid")
    monkeypatch.setenv(_mlflow.TOKEN_ENV, "fwml1.user.k.secret")
    monkeypatch.setattr(_mlflow, "_uncaught_terminal_status", None)

    client = _mlflow.client_from_env(transport=fake.transport)
    assert client is not None
    client.log({f"m/{i}": float(i) for i in range(1250)}, step=1)

    try:
        raise RuntimeError("boom")
    except RuntimeError as exc:
        _mlflow.sys.excepthook(type(exc), exc, exc.__traceback__)

    client._atexit_finish()
    monkeypatch.setattr(_mlflow, "_uncaught_terminal_status", None)

    sizes = [len(b["metrics"]) for p, b in fake.requests if p == "/api/2.0/mlflow/runs/log-batch" and b["metrics"]]
    assert sizes == [1000, 250]
    assert fake.requests[-1][0] == "/api/2.0/mlflow/runs/update"
    assert fake.requests[-1][1]["status"] == "FAILED"
