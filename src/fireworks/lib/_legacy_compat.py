"""Backwards-compatibility shims for the 0.x SDK API surface.

The old ``fireworks-ai`` (0.x) SDK exposed ``acreate()`` on async completion
resources. The new Stainless-generated 1.x SDK uses ``create()`` for both sync
and async (the async version is a coroutine).  Downstream packages like
``langchain-fireworks`` and ``instructor`` call ``acreate()``, so we add it as
a deprecated alias.

This module is loaded at import time via ``fireworks/__init__.py``.
"""

from __future__ import annotations

import warnings
from typing import Any


def _patch_acreate_aliases() -> None:  # pyright: ignore[reportUnusedFunction]
    """Add ``acreate`` as a deprecated alias for ``create`` on async resources."""
    from fireworks.resources.completions import (
        AsyncCompletionsResource as AsyncCompletions,
    )
    from fireworks.resources.chat.completions import (
        AsyncCompletionsResource as AsyncChatCompletions,
    )

    for cls in (AsyncChatCompletions, AsyncCompletions):
        if hasattr(cls, "acreate"):
            continue

        original_create = cls.create

        async def _acreate(self: Any, *args: Any, _orig: Any = original_create, **kwargs: Any) -> Any:
            warnings.warn(
                "acreate() is deprecated, use create() instead. "
                "The async client's create() is already a coroutine.",
                DeprecationWarning,
                stacklevel=2,
            )
            return await _orig(self, *args, **kwargs)

        cls.acreate = _acreate  # type: ignore[attr-defined, union-attr]
