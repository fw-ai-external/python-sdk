"""Bounded, best-effort local evidence independent of opt-in debug storage."""

from __future__ import annotations

import os
import json
import stat
import time
import base64
import shutil
import socket
import hashlib
import logging
import secrets
import tempfile
import threading
import traceback
from typing import TYPE_CHECKING, Any, Mapping, BinaryIO, Iterator, Sequence
from pathlib import Path
from contextlib import contextmanager
from collections import OrderedDict
from dataclasses import field, dataclass

from fireworks.training.sdk.tito_debug import TITOLocalDebugSink

if TYPE_CHECKING:
    from fireworks.training.sdk.tito._types import TITOTrajectoryArtifact

logger = logging.getLogger(__name__)


@contextmanager
def _open_collected_trace(source: Path, trusted_root: Path | None) -> Iterator[BinaryIO]:
    """Read an untrusted collected file without following directory or file links."""
    if os.open not in os.supports_dir_fd or not hasattr(os, "O_NOFOLLOW"):
        raise OSError("secure collected trace reads require no-follow directory access")
    if trusted_root is None:
        # An explicit standalone caller trusts its chosen parent directory.
        root = source.parent.resolve(strict=True)
        relative = Path(source.name)
    else:
        relative = source.absolute().relative_to(trusted_root.absolute())
        root = trusted_root.resolve(strict=True)
    if not relative.parts or any(part == ".." for part in relative.parts):
        raise OSError("collected trace is outside the trusted directory")
    directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    parent_fd = os.open(root, directory_flags)
    try:
        for component in relative.parts[:-1]:
            child_fd = os.open(component, directory_flags, dir_fd=parent_fd)
            os.close(parent_fd)
            parent_fd = child_fd
        fd = os.open(relative.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent_fd)
        with os.fdopen(fd, "rb") as stream:
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise OSError("collected trace must be a regular file")
            yield stream
    finally:
        os.close(parent_fd)


@dataclass(frozen=True)
class TITOFailureTraceConfig:
    """Local-only temporary traces, removed after successful terminalization.

    Failed traces survive shutdown within these per-writer retention bounds.
    They contain raw requests and tokens; do not upload them automatically.
    """

    root_dir: Path = field(default_factory=lambda: Path(tempfile.gettempdir()) / "fireworks-tito-traces")
    max_local_bytes: int = 256 * 1024 * 1024
    max_trajectory_bytes: int = 32 * 1024 * 1024
    max_failed_traces: int = 32
    max_active_traces: int = 128
    min_free_bytes: int = 64 * 1024 * 1024
    enabled: bool = True
    stale_writer_age_seconds: float = 7 * 24 * 60 * 60

    def __post_init__(self) -> None:
        if not self.root_dir.is_absolute():
            raise ValueError("TITO failure trace root_dir must be absolute")
        for name in ("max_local_bytes", "max_trajectory_bytes", "max_failed_traces", "max_active_traces"):
            if getattr(self, name) < 1:
                raise ValueError(f"{name} must be positive")
        if self.max_trajectory_bytes > self.max_local_bytes or self.min_free_bytes < 0:
            raise ValueError("invalid TITO failure trace byte limits")
        if self.stale_writer_age_seconds <= 0:
            raise ValueError("stale_writer_age_seconds must be positive")


@dataclass
class _Trace:
    path: Path
    size: int = 0
    sequence: int = 0
    failed: bool = False
    truncated: bool = False
    storage_error: str | None = None


class _FailureTraceRecorder:
    def __init__(self, config: TITOFailureTraceConfig) -> None:
        self.config = config
        self._writer_dir: Path | None = None
        self._traces: dict[str, _Trace] = {}
        self._failed: OrderedDict[str, None] = OrderedDict()
        self._bytes = 0
        self._lock = threading.Lock()
        self._storage_error: str | None = None

    def _delete(self, trajectory_id: str) -> None:
        trace = self._traces[trajectory_id]
        trace.path.unlink(missing_ok=True)
        self._bytes -= trace.size
        self._traces.pop(trajectory_id)
        self._failed.pop(trajectory_id, None)

    def _trace(self, trajectory_id: str) -> _Trace:
        if trajectory_id in self._traces:
            return self._traces[trajectory_id]
        active = len(self._traces) - len(self._failed)
        if active >= self.config.max_active_traces:
            raise OSError("TITO active trace limit reached")
        if self._writer_dir is None:
            self.config.root_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
            root = self.config.root_dir.lstat()
            if not stat.S_ISDIR(root.st_mode):
                raise OSError("TITO trace root must be a directory, not a symlink")
            if os.name == "posix" and (root.st_uid != os.geteuid() or root.st_mode & 0o077):
                raise OSError("TITO trace root must be owned by this user with private permissions")
            self._sweep_stale_writers()
            self._writer_dir = Path(tempfile.mkdtemp(prefix="writer-", dir=self.config.root_dir))
            owner = self._writer_dir / "owner.json"
            owner.write_text(json.dumps({"pid": os.getpid(), "hostname": socket.gethostname(), "created": time.time()}))
            owner.chmod(0o600)
            (self._writer_dir / "pending").mkdir(mode=0o700)
            (self._writer_dir / "failed").mkdir(mode=0o700)
        key = hashlib.sha256(trajectory_id.encode()).hexdigest()
        trace = _Trace(self._writer_dir / "pending" / f"{key}.jsonl")
        self._traces[trajectory_id] = trace
        return trace

    def _sweep_stale_writers(self) -> None:
        # Only reclaim this host's dead POSIX processes. PID reuse keeps a
        # stale directory longer rather than risking a live writer's evidence.
        if os.name != "posix":
            return
        for directory in self.config.root_dir.glob("writer-*"):
            if directory.is_symlink() or not directory.is_dir():
                continue
            try:
                owner = json.loads((directory / "owner.json").read_text())
                if (
                    owner["hostname"] != socket.gethostname()
                    or time.time() - owner["created"] < self.config.stale_writer_age_seconds
                ):
                    continue
                pid = owner["pid"]
                if type(pid) is not int or pid <= 0:
                    continue
                try:
                    os.kill(pid, 0)
                except ProcessLookupError:
                    shutil.rmtree(directory)
            except (OSError, ValueError, KeyError, TypeError):
                continue  # Unmarked, foreign and live writers are never removed.

    def _make_room(self, trajectory_id: str, delta: int, incoming: int) -> None:
        while self._bytes + delta > self.config.max_local_bytes:
            victim = next((key for key in self._failed if key != trajectory_id), None)
            if victim is None:
                raise OSError("TITO local trace byte budget exhausted")
            self._delete(victim)
        if shutil.disk_usage(self.config.root_dir).free - incoming < self.config.min_free_bytes:
            raise OSError("TITO trace free-space floor reached")

    def _retain(self, trajectory_id: str, trace: _Trace) -> None:
        if not trace.failed:
            destination = trace.path.parent.parent / "failed" / trace.path.name
            trace.path.replace(destination)
            trace.path = destination
            trace.failed = True
            self._failed[trajectory_id] = None
        while len(self._failed) > self.config.max_failed_traces:
            self._delete(next(iter(self._failed)))

    def record(
        self,
        event: str,
        trajectory_id: str,
        payload: Mapping[str, Any],
        arrays: Mapping[str, Sequence[Any]] | None = None,
    ) -> None:
        if not self.config.enabled:
            return
        with self._lock:
            trace = None
            try:
                trace = self._trace(trajectory_id)
                if trace.failed and event not in {"call_terminal", "auxiliary_terminal"}:
                    return  # Later bookkeeping must never overwrite the failure.
                # Inline MoE routing/top-k arrays can dwarf the model tokens.
                # Preserve parser replay inputs by default; full debug storage
                # and the terminal artifact retain the other training arrays.
                selected_arrays = {
                    key: value
                    for key, value in (arrays or {}).items()
                    if "routing" not in key
                    and "topk" not in key
                    and "top_sampling" not in key
                    and "sampling_mask" not in key
                }
                value = {
                    "event": event,
                    "event_seq": trace.sequence,
                    "recorded_at": time.time(),
                    "trajectory_id": trajectory_id,
                    "history_truncated": trace.truncated,
                    "payload": dict(payload),
                    "arrays": selected_arrays,
                    "omitted_arrays": sorted(set(arrays or {}) - selected_arrays.keys()),
                }
                value = TITOLocalDebugSink.sanitize(value)
                encoded = TITOLocalDebugSink._encode(value)
                if len(encoded) > self.config.max_trajectory_bytes:
                    raise OSError("TITO trace event exceeds the per-trajectory byte limit")
                mode = "ab"
                if trace.size + len(encoded) > self.config.max_trajectory_bytes:
                    # Retain the latest complete event rather than a partial
                    # token/request record. Terminal events include the failed
                    # request and sampled completion, so they remain replayable.
                    trace.truncated = True
                    value["history_truncated"] = True
                    encoded = TITOLocalDebugSink._encode(value)
                    mode = "wb"
                replacement_size = trace.size if mode == "wb" else 0
                self._make_room(trajectory_id, len(encoded) - replacement_size, len(encoded))
                with trace.path.open(mode) as stream:
                    trace.path.chmod(0o600)
                    stream.write(encoded)
                    stream.flush()
                self._bytes += len(encoded) - replacement_size
                trace.size += len(encoded) - replacement_size
                trace.sequence += 1
                if event in {"call_terminal", "auxiliary_terminal"} and payload.get("outcome") != "rejected":
                    self._retain(trajectory_id, trace)
            except Exception as exc:
                # Diagnostics must never replace the actual sampling/parsing
                # failure or prevent the next trajectory from running.
                message = f"{type(exc).__name__}: {exc}"
                if trace is not None:
                    trace.storage_error = message
                if self._storage_error != message:
                    logger.warning("TITO failure trace unavailable: %s", message)
                self._storage_error = message

    def evidence(self, trajectory_id: str) -> dict[str, Any]:
        if not self.config.enabled:
            return {"trace_storage_error": "failure capture disabled by configuration"}
        with self._lock:
            trace = self._traces.get(trajectory_id)
            if trace is None:
                return {"trace_storage_error": self._storage_error or "trace not recorded"}
            try:
                exists = trace.path.is_file()
            except OSError:
                exists = False
            return {
                "trace_path": str(trace.path) if exists else None,
                "trace_history_truncated": trace.truncated,
                "trace_storage_error": trace.storage_error,
            }

    def close_trajectory(self, trajectory_id: str, status: str) -> None:
        with self._lock:
            trace = self._traces.get(trajectory_id)
            if trace is None:
                return
            try:
                if status in {"completed", "abandoned"} and not trace.failed:
                    self._delete(trajectory_id)
                elif trace.path.exists():
                    self._retain(trajectory_id, trace)
                else:
                    self._delete(trajectory_id)
            except OSError as exc:
                logger.warning("TITO trace cleanup failed: %s", type(exc).__name__)

    def retain_collected_trace(self, trajectory_id: str, source: Path, trusted_root: Path | None = None) -> str | None:
        """Retain raw JSONL separately when a combined artifact cannot fit."""
        if not self.config.enabled:
            return None
        with self._lock:
            temporary = None
            trace = None
            try:
                trace = self._trace(trajectory_id)
                with _open_collected_trace(source, trusted_root) as incoming:
                    size = os.fstat(incoming.fileno()).st_size
                    if size > self.config.max_trajectory_bytes:
                        raise OSError("collected trace exceeds the per-trajectory byte limit")
                    self._make_room(trajectory_id, size - trace.size, size)
                    temporary = trace.path.with_suffix(".importing")
                    # Copy at most the reserved size, even if the source changes.
                    with temporary.open("wb") as outgoing:
                        temporary.chmod(0o600)
                        remaining = size
                        while remaining:
                            chunk = incoming.read(min(remaining, 1024 * 1024))
                            if not chunk:
                                raise OSError("collected trace changed during copy")
                            outgoing.write(chunk)
                            remaining -= len(chunk)
                temporary.replace(trace.path)
                self._bytes += size - trace.size
                trace.size = size
                trace.storage_error = None
                self._retain(trajectory_id, trace)
                return str(trace.path)
            except Exception as exc:
                logger.warning("TITO collected trace unavailable: %s", type(exc).__name__)
                return None
            finally:
                if temporary is not None:
                    try:
                        temporary.unlink(missing_ok=True)
                    except OSError:
                        pass
                if trace is not None and not trace.failed:
                    try:
                        self._delete(trajectory_id)
                    except OSError:
                        pass


_default_recorder = _FailureTraceRecorder(TITOFailureTraceConfig())


def dump_tito_failure_trace(
    artifact: TITOTrajectoryArtifact | None,
    error: BaseException,
    *,
    code: str,
    source_trace: Path | None = None,
    source_trace_root: Path | None = None,
) -> str | None:
    """Persist a completed artifact rejected by cookbook validation, locally.

    ``source_trace`` may be a failure trace collected from an isolated agent
    environment. Copy it before temporary trial directories are removed.
    ``artifact=None`` retains that trace when compact finalization failed.
    Collection callers must supply their trusted ``source_trace_root``; reads
    reject symlinks in every path component below it and non-regular files.
    Returns an existing path, or None if local storage could not accept it.
    """
    return _dump_failure_trace(
        _default_recorder, artifact, error, code=code, source_trace=source_trace, source_trace_root=source_trace_root
    )


def _dump_failure_trace(
    recorder: _FailureTraceRecorder,
    artifact: TITOTrajectoryArtifact | None,
    error: BaseException,
    *,
    code: str,
    source_trace: Path | None = None,
    source_trace_root: Path | None = None,
) -> str | None:
    if not recorder.config.enabled:
        return None
    if artifact is None:
        if source_trace is None:
            return None
        key = "collected-" + source_trace.stem + "-" + secrets.token_hex(8)
        return recorder.retain_collected_trace(key, source_trace, source_trace_root)
    key = "artifact-" + artifact.trajectory_id + "-" + secrets.token_hex(8)
    try:
        payload = {
            "code": code,
            "exception_chain": traceback.format_exception(type(error), error, error.__traceback__),
            "artifact_encoding": "base64",
            "artifact_base64": base64.b64encode(artifact.pack()).decode("ascii"),
        }
        if source_trace is not None:
            try:
                with _open_collected_trace(source_trace, source_trace_root) as incoming:
                    limit = recorder.config.max_trajectory_bytes
                    if os.fstat(incoming.fileno()).st_size <= limit:
                        payload["collected_trace_jsonl"] = incoming.read(limit).decode("utf-8")
            except (OSError, ValueError, UnicodeError) as exc:
                payload["collected_trace_error"] = type(exc).__name__
        recorder.record("call_terminal", key, payload)
        evidence = recorder.evidence(key)
        if evidence.get("trace_storage_error") and source_trace is not None:
            path = recorder.retain_collected_trace(key, source_trace, source_trace_root)
            if path is not None:
                logger.warning("TITO retained collected trace without oversized artifact: %s", path)
                return path
        return evidence.get("trace_path")
    except Exception as exc:
        logger.warning("TITO artifact failure trace unavailable: %s", type(exc).__name__)
        if source_trace is not None:
            return recorder.retain_collected_trace(key, source_trace, source_trace_root)
        return None
    finally:
        recorder.close_trajectory(key, "completed")


__all__ = ["TITOFailureTraceConfig", "dump_tito_failure_trace"]
