"""Load the native core at the TITO rollout and artifact writing boundary."""

from __future__ import annotations

from types import ModuleType

try:
    from . import _native
except ImportError as error:
    _native = None
    _load_error: ImportError | None = error
else:
    _load_error = None


def require_native() -> ModuleType:
    if _native is None:
        raise RuntimeError(
            "TITO rollouts and artifact writing require the native Training SDK extension. "
            "Install a supported platform wheel or build the TITO extension from source."
        ) from _load_error
    return _native
