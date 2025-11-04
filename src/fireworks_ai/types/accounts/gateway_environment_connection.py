# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["GatewayEnvironmentConnection"]


class GatewayEnvironmentConnection(BaseModel):
    node_pool_id: str = FieldInfo(alias="nodePoolId")
    """The resource id of the node pool the environment is connected to."""

    num_ranks: Optional[int] = FieldInfo(alias="numRanks", default=None)
    """
    For GPU node pools: one GPU per rank w/ host packing, for CPU node pools: one
    host per rank. If not specified, the default is 1.
    """

    role: Optional[str] = None
    """
    The ARN of the AWS IAM role that the connection should assume. If not specified,
    the connection will fall back to the node pool's node_role.
    """

    use_local_storage: Optional[bool] = FieldInfo(alias="useLocalStorage", default=None)
    """If true, the node's local storage will be mounted on /tmp.

    This flag has no effect if the node does not have local storage.
    """

    zone: Optional[str] = None
    """Current for the last zone that this environment is connected to.

    We want to warn the users about cross zone migration latency when they are
    connecting to node pool in a different zone as their persistent volume.
    """
