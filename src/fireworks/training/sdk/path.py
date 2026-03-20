"""Cloud-aware path utilities for training data and checkpoints.

Centralizes ``gs://`` and ``s3://`` handling so that recipe loops (cookbook)
and SDK internals share consistent logic instead of duplicating inline
fsspec checks and cloud-path concatenation.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import IO, Generator

_CLOUD_SCHEMES = ("gs://", "s3://")

try:
    import fsspec
    FSSPEC_AVAILABLE = True
except ImportError:
    fsspec = None  # type: ignore[assignment]
    FSSPEC_AVAILABLE = False


def is_cloud_path(path: str) -> bool:
    """Return ``True`` if *path* is a ``gs://`` or ``s3://`` URI."""
    return path.startswith(_CLOUD_SCHEMES)


def require_fsspec() -> None:
    """Raise ``ImportError`` with an actionable message when fsspec is absent."""
    if not FSSPEC_AVAILABLE:
        raise ImportError(
            "fsspec is required for cloud paths (gs://, s3://). "
            "Install with: pip install fsspec gcsfs s3fs"
        )


def cloud_join(base: str, *parts: str) -> str:
    """Join path segments, preserving cloud URI schemes.

    ``os.path.join`` mangles ``gs://bucket/dir`` into a local-looking path;
    this helper concatenates with ``/`` for cloud URIs and falls back to
    ``os.path.join`` for local paths.
    """
    if is_cloud_path(base):
        return base.rstrip("/") + "/" + "/".join(p.strip("/") for p in parts)
    return os.path.join(base, *parts)


@contextmanager
def open_path(path: str, mode: str = "r") -> Generator[IO, None, None]:
    """Open a local file **or** cloud URI (``gs://``, ``s3://``) transparently.

    Cloud paths are opened via :mod:`fsspec`; local paths use the built-in
    :func:`open`.  Raises :class:`ImportError` if fsspec is needed but not
    installed.
    """
    if is_cloud_path(path):
        require_fsspec()
        with fsspec.open(path, mode) as fh:
            yield fh
    else:
        with open(path, mode) as fh:
            yield fh
