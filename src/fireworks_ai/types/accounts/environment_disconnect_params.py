# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["EnvironmentDisconnectParams"]


class EnvironmentDisconnectParams(TypedDict, total=False):
    account_id: Required[str]

    force: bool
    """Disconnect the environment even if snapshotting fails (e.g.

    due to pod failure). This flag should only be used if you are certain that the
    pod is gone.
    """

    reset_snapshots: Annotated[bool, PropertyInfo(alias="resetSnapshots")]
    """
    Forces snapshots to be rebuilt. This can be used when there are too many
    snapshot layers or when an unforeseen snapshotting logic error has occurred.
    """
