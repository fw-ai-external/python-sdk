# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["ConversationConfig"]


class ConversationConfig(BaseModel):
    style: str
    """The chat template to use."""

    system: Optional[str] = None
    """The system prompt (if the chat style supports it)."""

    template: Optional[str] = None
    """The Jinja template (if style is "jinja")."""
