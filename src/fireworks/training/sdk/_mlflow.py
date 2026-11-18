"""Write-only MLflow ingest client and fail-fast enforcement for Training SDK runs.

Resolves credentials from ``MLFLOW_TRACKING_URI`` / ``MLFLOW_TRACKING_TOKEN`` or
``~/.config/mlflow/{tracking_uri,token}`` (so non-interactive agent shells that
do not source ``~/.bashrc`` still pick up host credentials). Fails fast at run
initialization whenever ``FIREWORKS_REQUIRE_MLFLOW`` is truthy, partial local
credentials exist, or the Fireworks backend marks the account as requiring
MLflow via ``x-fireworks-require-mlflow``—unless an explicit
``FIREWORKS_SKIP_MLFLOW_REASON`` breakglass reason is set.
"""

from __future__ import annotations

import os
import re
import sys
import math
import stat
import time
import queue
import atexit
import logging
import posixpath
import threading
import urllib.parse
from typing import Any
from numbers import Real
from pathlib import Path
from collections.abc import Mapping

import httpx

logger = logging.getLogger(__name__)

TRACKING_URI_ENV = "MLFLOW_TRACKING_URI"
TOKEN_ENV = "MLFLOW_TRACKING_TOKEN"
EXPERIMENT_ENV = "MLFLOW_EXPERIMENT_NAME"
RUN_NAME_ENV = "MLFLOW_RUN_NAME"
REQUIRE_MLFLOW_ENV = "FIREWORKS_REQUIRE_MLFLOW"
SKIP_REASON_ENV = "FIREWORKS_SKIP_MLFLOW_REASON"
CONFIG_DIR_ENV = "FIREWORKS_MLFLOW_CONFIG_DIR"
DEFAULT_EXPERIMENT = "fireworks-training"

REQUIRE_MLFLOW_HEADER = "x-fireworks-require-mlflow"

MAX_METRICS_PER_BATCH = 1000
MAX_ITEMS_PER_BATCH = 100
MAX_PARAM_VALUE_LEN = 500
_MAX_CONFIG_FILE_BYTES = 4096
_QUEUE_SIZE = 1024
_HTTP_TIMEOUT = httpx.Timeout(10.0, connect=3.0)
_FINISH_JOIN_TIMEOUT_S = 5.0
_MAX_RETRY_AFTER_S = 3.0
_RETRY_STATUSES = frozenset({429, 503})
_TRUTHY = frozenset({"1", "true", "yes", "on"})
_LOOPBACK_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})
_MLFLOW_NAME_RE = re.compile(r"[\w /:.-]+")
_SENSITIVE_KEY_RE = re.compile(
    r"(?:^|[._/-])(?:api[_-]?key|secret|passwd|password|authorization|bearer|credential"
    r"|auth[_-]?token|access[_-]?token|tracking[_-]?token|refresh[_-]?token|token)(?:$|[._/-])",
    re.IGNORECASE,
)
_SENSITIVE_VALUE_PREFIXES = ("fw_", "fwml1.", "sk-", "ghp_", "ghs_", "github_pat_", "Bearer ")
_SKIPPED_RECORD_KEYS = frozenset({"step", "session_id"})
_STOP = object()
_EXCEPTHOOK_LOCK = threading.Lock()
_excepthook_installed = False
_uncaught_terminal_status: str | None = None


def _ensure_excepthook() -> None:
    global _excepthook_installed
    with _EXCEPTHOOK_LOCK:
        if _excepthook_installed:
            return
        previous = sys.excepthook

        def _hook(exc_type: type[BaseException], exc: BaseException, tb: Any) -> None:
            global _uncaught_terminal_status
            _uncaught_terminal_status = "KILLED" if issubclass(exc_type, KeyboardInterrupt) else "FAILED"
            previous(exc_type, exc, tb)

        sys.excepthook = _hook
        _excepthook_installed = True


def _now_ms() -> int:
    return int(time.time() * 1000)


def _config_dir() -> Path:
    override = os.environ.get(CONFIG_DIR_ENV, "").strip()
    if override:
        return Path(override)
    xdg = os.environ.get("XDG_CONFIG_HOME", "").strip()
    base = Path(xdg) if xdg else (Path.home() / ".config")
    return base / "mlflow"


def _read_config_file(name: str) -> str:
    path = _config_dir() / name
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        if path.is_symlink():
            return ""
        fd = os.open(path, flags)
    except OSError:
        return ""
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            return ""
        data = os.read(fd, _MAX_CONFIG_FILE_BYTES + 1)
    except OSError:
        return ""
    finally:
        os.close(fd)
    if len(data) > _MAX_CONFIG_FILE_BYTES:
        return ""
    try:
        return data.decode("utf-8").strip()
    except UnicodeDecodeError:
        return ""


def _is_valid_tracking_uri(uri: str) -> bool:
    if not uri:
        return False
    parsed = urllib.parse.urlsplit(uri)
    if not parsed.hostname:
        return False
    if parsed.scheme == "https":
        return True
    return parsed.scheme == "http" and parsed.hostname.lower() in _LOOPBACK_HOSTS


def _sanitize_metadata_value(key: str, value: Any) -> str:
    text = str(value)
    if _SENSITIVE_KEY_RE.search(key) or text.startswith(_SENSITIVE_VALUE_PREFIXES):
        return "[REDACTED]"
    return text[:MAX_PARAM_VALUE_LEN]


def _finite_float(value: Any) -> float | None:
    if value is None or isinstance(value, (bool, str, bytes, Mapping, list, tuple, set)):
        return None
    if isinstance(value, Real):
        num = float(value)
        return num if math.isfinite(num) else None
    item_fn = getattr(value, "item", None)
    if callable(item_fn):
        try:
            scalar = item_fn()
        except Exception:
            return None
        if not isinstance(scalar, bool) and isinstance(scalar, Real) and math.isfinite(float(scalar)):
            return float(scalar)
    return None


def translate_mlflow_key(key: str) -> str | None:
    """Translate ``pass@k`` / ``pass^k`` to MLflow-valid names, or ``None`` if invalid."""
    if not isinstance(key, str) or not key:
        return None
    name = re.sub(r"(^|/)pass@(\d+)(?=_|$)", r"\1pass_at_\2", key)
    name = re.sub(r"(^|/)pass\^(\d+)(?=_|$)", r"\1pass_all_\2", name)
    if (
        not _MLFLOW_NAME_RE.fullmatch(name)
        or len(name) > 250
        or posixpath.normpath(name) != name
        or name.startswith(("/", "../"))
        or name in {".", ".."}
    ):
        return None
    return name


def translate_mlflow_metrics(data: Mapping[str, Any]) -> dict[str, float]:
    """Extract finite numeric metrics and translate keys to MLflow-safe names."""
    translated: dict[str, float] = {}
    for key, raw_value in data.items():
        if key in _SKIPPED_RECORD_KEYS:
            continue
        number = _finite_float(raw_value)
        name = translate_mlflow_key(str(key)) if number is not None else None
        if name is not None and number is not None and name not in translated:
            translated[name] = number
    return translated


def _flatten_params(config: Mapping[str, Any], *, prefix: str = "") -> dict[str, str]:
    flat: dict[str, str] = {}
    for raw_key, value in config.items():
        if value is None:
            continue
        key = f"{prefix}.{raw_key}" if prefix else str(raw_key)
        if translate_mlflow_key(key) is None:
            continue
        if isinstance(value, Mapping):
            flat.update(_flatten_params(value, prefix=key))
        else:
            flat[key] = _sanitize_metadata_value(key, value)
    return flat


class MlflowIngestClient:
    """Write-only background MLflow client targeting the Fireworks ingest proxy."""

    def __init__(
        self,
        tracking_uri: str,
        token: str,
        experiment_name: str,
        run_name: str,
        *,
        tags: Mapping[str, str] | None = None,
        params: Mapping[str, Any] | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._http = httpx.Client(
            base_url=tracking_uri.rstrip("/"),
            headers={"Authorization": f"Bearer {token}"},
            timeout=_HTTP_TIMEOUT,
            transport=transport,
        )
        self._pid = os.getpid()
        self._failed = threading.Event()
        self._finished = False
        self._finish_lock = threading.Lock()
        self._logged_params: set[str] = set()

        try:
            exp = self._post("/ingest/experiments", {"name": experiment_name})
            self.experiment_id = str(exp["experiment_id"])
            tag_list = [
                {"key": str(k), "value": _sanitize_metadata_value(str(k), v)}
                for k, v in (tags or {}).items()
                if v is not None and translate_mlflow_key(str(k)) is not None
            ]
            run = self._post(
                "/api/2.0/mlflow/runs/create",
                {"experiment_id": self.experiment_id, "start_time": _now_ms(), "run_name": run_name, "tags": tag_list},
            )
            self.run_id = str(run["run"]["info"]["run_id"])
        except Exception:
            self._http.close()
            raise

        self._queue: queue.Queue[Any] = queue.Queue(maxsize=_QUEUE_SIZE)
        self._sender = threading.Thread(target=self._send_loop, name="fw-mlflow-ingest", daemon=True)
        self._sender.start()
        _ensure_excepthook()
        atexit.register(self._atexit_finish)
        if params:
            self.log_params(params)

    def log(self, data: Mapping[str, Any], step: int) -> None:
        if os.getpid() != self._pid or self._finished or self._failed.is_set():
            return
        metrics = translate_mlflow_metrics(data)
        if metrics:
            ts = _now_ms()
            self._enqueue(
                "metrics", [{"key": k, "value": v, "timestamp": ts, "step": int(step)} for k, v in metrics.items()]
            )

    def log_params(self, params: Mapping[str, Any]) -> None:
        if os.getpid() != self._pid or self._finished or self._failed.is_set():
            return
        entries = []
        for k, v in _flatten_params(params).items():
            if k not in self._logged_params:
                self._logged_params.add(k)
                entries.append({"key": k, "value": v})
        if entries:
            self._enqueue("params", entries)

    def set_tags(self, tags: Mapping[str, str]) -> None:
        if os.getpid() != self._pid or self._finished or self._failed.is_set():
            return
        entries = [
            {"key": str(k), "value": _sanitize_metadata_value(str(k), v)}
            for k, v in tags.items()
            if v is not None and translate_mlflow_key(str(k)) is not None
        ]
        if entries:
            self._enqueue("tags", entries)

    def _enqueue(self, kind: str, entries: list[dict[str, Any]]) -> None:
        try:
            self._queue.put_nowait((kind, entries))
        except queue.Full:
            logger.warning("MLflow mirror queue full; dropping %s batch", kind)

    def _atexit_finish(self) -> None:
        self.finish(status=_uncaught_terminal_status or "FINISHED")

    def finish(self, *, status: str = "FINISHED") -> None:
        if os.getpid() != self._pid:
            return
        with self._finish_lock:
            if self._finished:
                return
            self._finished = True
        while True:
            try:
                self._queue.put_nowait((_STOP, status))
                break
            except queue.Full:
                try:
                    self._queue.get_nowait()
                except queue.Empty:
                    pass
        self._sender.join(timeout=_FINISH_JOIN_TIMEOUT_S)

    def _send_loop(self) -> None:
        try:
            while True:
                item = self._queue.get()
                kind, payload = item
                if kind is _STOP:
                    if not self._failed.is_set():
                        try:
                            self._post(
                                "/api/2.0/mlflow/runs/update",
                                {"run_id": self.run_id, "status": str(payload), "end_time": _now_ms()},
                            )
                        except Exception as exc:
                            logger.warning(
                                "MLflow mirror could not close run %s: %s: %s", self.run_id, type(exc).__name__, exc
                            )
                    return
                if self._failed.is_set():
                    continue
                limit = MAX_METRICS_PER_BATCH if kind == "metrics" else MAX_ITEMS_PER_BATCH
                try:
                    for start in range(0, len(payload), limit):
                        batch: dict[str, Any] = {"run_id": self.run_id, "metrics": [], "params": [], "tags": []}
                        batch[kind] = payload[start : start + limit]
                        self._post("/api/2.0/mlflow/runs/log-batch", batch)
                except Exception as exc:
                    self._failed.set()
                    logger.warning(
                        "MLflow mirror stopped after write error on run %s: %s: %s",
                        self.run_id,
                        type(exc).__name__,
                        exc,
                    )
        finally:
            self._http.close()

    def _post(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        for attempt in range(1, 4):
            resp = self._http.post(path, json=body)
            if resp.status_code in _RETRY_STATUSES and attempt < 3:
                hdr = resp.headers.get("retry-after", "")
                time.sleep(min(float(hdr) if hdr.isdecimal() else 1.0, _MAX_RETRY_AFTER_S))
                continue
            resp.raise_for_status()
            return resp.json() if resp.content else {}
        raise AssertionError("unreachable")


def resolve_mlflow_credentials() -> tuple[str, str, bool]:
    """Return ``(tracking_uri, token, configured)`` from env or ``~/.config/mlflow``."""
    env_uri = os.environ.get(TRACKING_URI_ENV, "").strip()
    env_token = os.environ.get(TOKEN_ENV, "").strip()
    disk_uri = _read_config_file("tracking_uri")
    disk_token = _read_config_file("token")
    uri = env_uri or disk_uri
    token = env_token or disk_token
    configured = bool(uri or token)
    return uri, token, configured


def client_from_env(
    *,
    project: str | None = None,
    run_name: str | None = None,
    server_required: bool = False,
    tags: Mapping[str, str] | None = None,
    params: Mapping[str, Any] | None = None,
    transport: httpx.BaseTransport | None = None,
) -> MlflowIngestClient | None:
    """Create an ``MlflowIngestClient`` or fail fast when MLflow is required."""
    skip_reason = os.environ.get(SKIP_REASON_ENV, "").strip()
    if skip_reason:
        logger.warning("Skipping MLflow reporting (%s=%r)", SKIP_REASON_ENV, skip_reason)
        return None

    uri, token, configured = resolve_mlflow_credentials()
    required = os.environ.get(REQUIRE_MLFLOW_ENV, "").strip().lower() in _TRUTHY or server_required
    if not configured and not required:
        return None
    must_succeed = required or configured
    if not token or not _is_valid_tracking_uri(uri):
        raise RuntimeError(
            f"MLflow reporting is required, but credentials are invalid or incomplete "
            f"(uri={'valid' if _is_valid_tracking_uri(uri) else 'missing/insecure'}, "
            f"token={'set' if token else 'missing'}). "
            f"Set an https {TRACKING_URI_ENV} and {TOKEN_ENV} "
            f"(or populate ~/.config/mlflow/{{tracking_uri,token}})."
        )
    exp_name = os.environ.get(EXPERIMENT_ENV, "").strip() or project or DEFAULT_EXPERIMENT
    resolved_run = (
        os.environ.get(RUN_NAME_ENV, "").strip()
        or run_name
        or os.environ.get("FIREWORKS_JOB_ID", "").strip()
        or time.strftime("fw-run-%Y%m%dT%H%M%SZ", time.gmtime())
    )
    try:
        client = MlflowIngestClient(
            uri,
            token,
            exp_name,
            resolved_run,
            tags={"fireworks.source": "training-sdk", **(tags or {})},
            params=params,
            transport=transport,
        )
    except Exception as exc:
        if must_succeed:
            raise RuntimeError(f"MLflow ingest initialization failed: {type(exc).__name__}: {exc}") from exc
        logger.warning("MLflow mirror setup failed: %s: %s", type(exc).__name__, exc)
        return None
    logger.info("MLflow mirror on: experiment=%s run=%s", client.experiment_id, client.run_id)
    return client


def is_server_mlflow_required(headers: Mapping[str, str] | None) -> bool:
    """Return whether Fireworks response headers require MLflow reporting for this account."""
    if not headers:
        return False
    for key, value in headers.items():
        if str(key).lower() == REQUIRE_MLFLOW_HEADER:
            return str(value).strip().lower() in _TRUTHY
    return False
