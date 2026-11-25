"""Load the native core at the TITO rollout and artifact writing boundary."""

from __future__ import annotations

from types import ModuleType

_TITO_ABI_VERSION = 2

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
    if getattr(_native, "TITO_ABI_VERSION", None) != _TITO_ABI_VERSION:
        raise RuntimeError(
            "The installed TITO extension is incompatible with this SDK. "
            "Reinstall the platform wheel or rebuild the extension from this SDK checkout."
        )
    return _native
