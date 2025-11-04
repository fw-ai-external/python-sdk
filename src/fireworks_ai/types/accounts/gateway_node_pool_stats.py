# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["GatewayNodePoolStats"]


class GatewayNodePoolStats(BaseModel):
    batch_job_count: Optional[Dict[str, int]] = FieldInfo(alias="batchJobCount", default=None)
    """The key is the string representation of BatchJob.State (e.g.

    "RUNNING"). The value is the number of batch jobs in that state allocated to
    this node pool.
    """

    batch_job_ranks: Optional[Dict[str, int]] = FieldInfo(alias="batchJobRanks", default=None)
    """The key is the string representation of BatchJob.State (e.g.

    "RUNNING"). The value is the number of ranks allocated to batch jobs in that
    state in this node pool.
    """

    environment_count: Optional[int] = FieldInfo(alias="environmentCount", default=None)
    """The number of environments connected to this node pool."""

    environment_ranks: Optional[int] = FieldInfo(alias="environmentRanks", default=None)
    """
    The number of ranks in this node pool that are currently allocated to
    environment connections.
    """

    node_count: Optional[int] = FieldInfo(alias="nodeCount", default=None)
    """The number of nodes currently available in this pool."""

    ranks_per_node: Optional[int] = FieldInfo(alias="ranksPerNode", default=None)
    """The number of ranks available per node.

    This is determined by the machine type of the nodes in this node pool.
    """
