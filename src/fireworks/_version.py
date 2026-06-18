# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

import re as _re
from typing import Optional as _Optional
from pathlib import Path as _Path
from importlib import metadata as _metadata

__title__ = "fireworks"


def _fireworks_version(version: str) -> str:
    match = _re.fullmatch(r"(\d+\.\d+\.\d+)(a|b|rc)(\d+)", version)
    if not match:
        return version

    base, channel, counter = match.groups()
    channel_name = {"a": "alpha", "b": "beta", "rc": "rc"}[channel]
    return f"{base}-{channel_name}.{counter}"


def _version_from_package_metadata() -> _Optional[str]:
    try:
        return _fireworks_version(_metadata.version("fireworks-ai"))
    except _metadata.PackageNotFoundError:
        return None


def _version_from_pyproject() -> _Optional[str]:
    try:
        text = (_Path(__file__).resolve().parents[2] / "pyproject.toml").read_text(encoding="utf-8")
    except OSError:
        return None

    match = _re.search(r'(?m)^version\s*=\s*"([^"]+)"', text)
    if match:
        return match.group(1)
    return None


__version__ = _version_from_pyproject() or _version_from_package_metadata() or "0+unknown"
