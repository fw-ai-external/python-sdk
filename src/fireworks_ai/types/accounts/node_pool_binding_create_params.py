# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["NodePoolBindingCreateParams"]


class NodePoolBindingCreateParams(TypedDict, total=False):
    principal: Required[str]
    """The principal that is allowed use the node pool.

    This must be the email address of the user.
    """
