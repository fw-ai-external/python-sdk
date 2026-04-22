"""Backwards compatibility shim for the old ``fireworks.client`` import path.

The 0.x SDK exported its public API from ``fireworks.client``.  The 1.x SDK
moved everything to the top-level ``fireworks`` package.  This module re-exports
the most commonly used symbols so that existing code such as::

    from fireworks.client import Fireworks, AsyncFireworks

continues to work without changes.

.. deprecated::
    Import directly from ``fireworks`` instead::

        from fireworks import Fireworks, AsyncFireworks
"""

from __future__ import annotations

import warnings as _warnings

from fireworks import (
    Fireworks,
    AsyncFireworks,
    __version__,
)

__all__ = [
    "__version__",
    "Fireworks",
    "AsyncFireworks",
]

_warnings.warn(
    "Importing from 'fireworks.client' is deprecated. "
    "Use 'from fireworks import Fireworks, AsyncFireworks' instead. "
    "The 'fireworks.client' shim will be removed in a future release.",
    DeprecationWarning,
    stacklevel=2,
)
