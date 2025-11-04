# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["ConversationConfigParam"]


class ConversationConfigParam(TypedDict, total=False):
    style: Required[str]
    """The chat template to use."""

    system: str
    """The system prompt (if the chat style supports it)."""

    template: str
    """The Jinja template (if style is "jinja")."""
