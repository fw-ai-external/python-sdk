"""R3 (Router Replay) side-channel for official tinker compatibility.

Official tinker's ModelInput uses StrictBase(extra="forbid"), so routing
matrices cannot be added as a Pydantic field. This module attaches them
as a non-Pydantic attribute via object.__setattr__ (bypassing frozen=True)
and provides helpers to retrieve them for injection into HTTP requests.
"""

from __future__ import annotations

from typing import List, Optional

from tinker.types import ModelInput

_R3_ATTR = "_r3_routing_matrices"


def make_r3_model_input(
    tokens: List[int],
    routing_matrices: Optional[List[str]] = None,
) -> ModelInput:
    """Create a ModelInput with optional R3 routing matrices attached.

    Routing matrices are stored as a non-Pydantic attribute so they survive
    the object being reused across forward and backward passes in
    forward_backward_custom, but are invisible to Pydantic validation.
    """
    mi = ModelInput.from_ints(tokens)
    if routing_matrices is not None:
        object.__setattr__(mi, _R3_ATTR, routing_matrices)
    return mi


def get_r3_routing_matrices(model_input: ModelInput) -> Optional[List[str]]:
    """Retrieve routing matrices previously attached by make_r3_model_input."""
    return getattr(model_input, _R3_ATTR, None)
