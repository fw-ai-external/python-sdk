"""Optional local JSONL evidence for troubleshooting TITO trajectories.

The terminal ``.tito`` artifact is the authoritative training record.  This
module only preserves events that can be useful when a trajectory fails before
terminalization.  Its files are deliberately plain JSONL so operators can use
normal filesystem, ``rg``, and ``jq`` tooling; it is not a second trajectory
database or query API.
"""

from __future__ import annotations

import os
import re
import json
import time
import shutil
import hashlib
import secrets
import threading
from types import MappingProxyType
from typing import Any, Mapping, Sequence
from pathlib import Path
from dataclasses import field, dataclass


def _safe_component(value: str, *, field_name: str) -> str:
    if not value or not re.fullmatch(r"[A-Za-z0-9_.-]+", value):
        raise ValueError(f"{field_name} must contain only letters, digits, '.', '_' or '-'")
    return value


def _trajectory_storage_key(trajectory_id: str) -> str:
    return hashlib.sha256(trajectory_id.encode("utf-8")).hexdigest()


class TITODebugStorageFullError(OSError):
    """The configured local debug budget cannot accept another event."""

    storage_full = True


@dataclass(frozen=True)
class TITOLocalDebugConfig:
    """Bounds and privacy controls for an opt-in local event log."""

    root_dir: Path
    max_local_bytes: int
    min_free_bytes: int
    run_id: str | None = None
    writer_id: str | None = None
    redact_text: bool = False
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.root_dir.is_absolute():
            raise ValueError("TITO debug root_dir must be absolute")
        if self.max_local_bytes < 1:
            raise ValueError("max_local_bytes must be positive")
        if self.min_free_bytes < 0:
            raise ValueError("min_free_bytes must be non-negative")
        if self.run_id is not None:
            _safe_component(self.run_id, field_name="run_id")
        if self.writer_id is not None:
            _safe_component(self.writer_id, field_name="writer_id")
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(json.loads(json.dumps(dict(self.metadata)))),
        )


class TITOLocalDebugSink:
    """Append sidecar events to one searchable JSONL file per trajectory."""

    FORMAT = "fireworks-tito-debug-jsonl"
    SCHEMA_VERSION = 1
    _SECRET_KEY = re.compile(
        r"(?:authorization|cookie|api[-_]?key|bearer|access[-_]?token|secret)",
        re.IGNORECASE,
    )
    _TEXT_KEY = re.compile(
        r"^(?:content|text|reasoning_content|arguments|instruction|prompt|"
        r"problem_statement|completion_text|body|wire_request_body)$",
        re.IGNORECASE,
    )
    _SECRET_VALUE = re.compile(
        r"(bearer\s+)[A-Za-z0-9._~+/=-]+|"
        r"((?:api[-_]?key|token|secret)\s*[:=]\s*)[^\s,;]+",
        re.IGNORECASE,
    )

    def __init__(self, config: TITOLocalDebugConfig) -> None:
        self.config = config
        self.run_id = _safe_component(
            config.run_id or f"{int(time.time())}-{secrets.token_hex(6)}",
            field_name="run_id",
        )
        self.writer_id = _safe_component(
            config.writer_id or f"pid{os.getpid()}-{secrets.token_hex(6)}",
            field_name="writer_id",
        )
        self.run_dir = config.root_dir / f"run={self.run_id}"
        self.writer_dir = self.run_dir / f"writer={self.writer_id}"
        self.trajectories_dir = self.writer_dir / "trajectories"
        self.manifest_path = self.writer_dir / "manifest.json"
        self.tombstones_path = self.writer_dir / "tombstones.jsonl"
        self._lock = threading.Lock()
        self._closed = False
        self._bytes_written = 0
        self._sequences: dict[str, int] = {}

        self._mkdir(config.root_dir)
        self._mkdir(self.run_dir)
        # A writer directory is an immutable ownership boundary. Reusing one
        # would reset sequence and byte accounting while appending to old files.
        self.writer_dir.mkdir(mode=0o700, exist_ok=False)
        self._mkdir(self.trajectories_dir)
        self._write_manifest()

    @staticmethod
    def _mkdir(path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)
        path.chmod(0o700)

    def _write_manifest(self) -> None:
        value = {
            "format": self.FORMAT,
            "schema_version": self.SCHEMA_VERSION,
            "run_id": self.run_id,
            "writer_id": self.writer_id,
            "created_at": time.time(),
            "redact_text": self.config.redact_text,
            "metadata": dict(self.config.metadata),
        }
        encoded = self._encode(value)
        self._reserve(len(encoded))
        with self.manifest_path.open("wb") as stream:
            stream.write(encoded)
        self.manifest_path.chmod(0o600)
        self._bytes_written += len(encoded)

    @staticmethod
    def _encode(value: Mapping[str, Any]) -> bytes:
        return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")

    def _reserve(self, size: int) -> None:
        if self._bytes_written + size > self.config.max_local_bytes:
            raise TITODebugStorageFullError("TITO debug byte budget exhausted")
        free = shutil.disk_usage(self.config.root_dir).free
        if free - size < self.config.min_free_bytes:
            raise TITODebugStorageFullError("TITO debug free-space floor reached")

    @staticmethod
    def _text_digest(value: str) -> Mapping[str, Any]:
        encoded = value.encode("utf-8")
        return {
            "redacted": True,
            "bytes": len(encoded),
            "sha256": hashlib.sha256(encoded).hexdigest(),
        }

    def _redact(self, value: Any, *, key: str | None = None) -> Any:
        if key is not None and self._SECRET_KEY.search(key):
            return "<redacted>"
        if isinstance(value, Mapping):
            return {
                str(item_key): self._redact(item_value, key=str(item_key)) for item_key, item_value in value.items()
            }
        if isinstance(value, (list, tuple)):
            return [self._redact(item) for item in value]
        if isinstance(value, str):
            if self.config.redact_text and key is not None and self._TEXT_KEY.match(key):
                return self._text_digest(value)
            return self._SECRET_VALUE.sub(lambda match: f"{match.group(1) or match.group(2) or ''}<redacted>", value)
        return value

    def _trajectory_dir(self, trajectory_id: str) -> Path:
        return self.trajectories_dir / _trajectory_storage_key(trajectory_id)

    def _append(self, path: Path, value: Mapping[str, Any]) -> int:
        encoded = self._encode(value)
        self._reserve(len(encoded))
        self._mkdir(path.parent)
        with path.open("ab") as stream:
            stream.write(encoded)
            stream.flush()
        path.chmod(0o600)
        self._bytes_written += len(encoded)
        return len(encoded)

    def record(
        self,
        event: str,
        trajectory_id: str,
        payload: Mapping[str, Any],
        arrays: Mapping[str, Sequence[Any]] | None = None,
    ) -> int:
        with self._lock:
            if self._closed:
                raise RuntimeError("TITO debug sink is closed")
            sequence = self._sequences.get(trajectory_id, 0)
            value = {
                "event": event,
                "event_seq": sequence,
                "recorded_at": time.time(),
                "trajectory_id": trajectory_id,
                "payload": self._redact(dict(payload)),
            }
            if arrays:
                value["arrays"] = self._redact(dict(arrays))
            written = self._append(
                self._trajectory_dir(trajectory_id) / "events.jsonl",
                value,
            )
            self._sequences[trajectory_id] = sequence + 1
            return written

    def close_trajectory(
        self,
        trajectory_id: str,
        status: str,
        payload: Mapping[str, Any] | None = None,
    ) -> int:
        return self.record(
            "trajectory_terminal",
            trajectory_id,
            {"status": status, **dict(payload or {})},
        )

    def record_tombstone_event(
        self,
        event: str,
        trajectory_id: str,
        payload: Mapping[str, Any],
    ) -> int:
        with self._lock:
            if self._closed:
                return 0
            return self._append(
                self.tombstones_path,
                {
                    "event": event,
                    "recorded_at": time.time(),
                    "trajectory_id": trajectory_id,
                    "payload": self._redact(dict(payload)),
                },
            )

    def close(self) -> None:
        with self._lock:
            self._closed = True


__all__ = [
    "TITODebugStorageFullError",
    "TITOLocalDebugConfig",
    "TITOLocalDebugSink",
]
