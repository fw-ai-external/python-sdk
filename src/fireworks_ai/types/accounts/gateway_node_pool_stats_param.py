# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["GatewayNodePoolStatsParam"]


class GatewayNodePoolStatsParam(TypedDict, total=False):
    batch_job_count: Annotated[Dict[str, int], PropertyInfo(alias="batchJobCount")]
    """The key is the string representation of BatchJob.State (e.g.

    "RUNNING"). The value is the number of batch jobs in that state allocated to
    this node pool.
    """

    batch_job_ranks: Annotated[Dict[str, int], PropertyInfo(alias="batchJobRanks")]
    """The key is the string representation of BatchJob.State (e.g.

    "RUNNING"). The value is the number of ranks allocated to batch jobs in that
    state in this node pool.
    """

    environment_count: Annotated[int, PropertyInfo(alias="environmentCount")]
    """The number of environments connected to this node pool."""

    environment_ranks: Annotated[int, PropertyInfo(alias="environmentRanks")]
    """
    The number of ranks in this node pool that are currently allocated to
    environment connections.
    """

    node_count: Annotated[int, PropertyInfo(alias="nodeCount")]
    """The number of nodes currently available in this pool."""

    ranks_per_node: Annotated[int, PropertyInfo(alias="ranksPerNode")]
    """The number of ranks available per node.

    This is determined by the machine type of the nodes in this node pool.
    """
