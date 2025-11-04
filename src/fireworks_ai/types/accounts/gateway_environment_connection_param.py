# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["GatewayEnvironmentConnectionParam"]


class GatewayEnvironmentConnectionParam(TypedDict, total=False):
    node_pool_id: Required[Annotated[str, PropertyInfo(alias="nodePoolId")]]
    """The resource id of the node pool the environment is connected to."""

    num_ranks: Annotated[int, PropertyInfo(alias="numRanks")]
    """
    For GPU node pools: one GPU per rank w/ host packing, for CPU node pools: one
    host per rank. If not specified, the default is 1.
    """

    role: str
    """
    The ARN of the AWS IAM role that the connection should assume. If not specified,
    the connection will fall back to the node pool's node_role.
    """

    use_local_storage: Annotated[bool, PropertyInfo(alias="useLocalStorage")]
    """If true, the node's local storage will be mounted on /tmp.

    This flag has no effect if the node does not have local storage.
    """
