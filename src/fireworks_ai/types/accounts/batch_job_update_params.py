# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo
from .gateway_shell_executor_param import GatewayShellExecutorParam
from .gateway_python_executor_param import GatewayPythonExecutorParam
from .gateway_notebook_executor_param import GatewayNotebookExecutorParam

__all__ = ["BatchJobUpdateParams"]


class BatchJobUpdateParams(TypedDict, total=False):
    account_id: Required[str]

    node_pool_id: Required[Annotated[str, PropertyInfo(alias="nodePoolId")]]

    annotations: Dict[str, str]
    """
    Arbitrary, user-specified metadata. Keys and values must adhere to Kubernetes
    constraints:
    https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/#syntax-and-character-set
    Additionally, the "fireworks.ai/" prefix is reserved.
    """

    display_name: Annotated[str, PropertyInfo(alias="displayName")]
    """Human-readable display name of the batch job.

    e.g. "My Batch Job" Must be fewer than 64 characters long.
    """

    environment_id: Annotated[str, PropertyInfo(alias="environmentId")]
    """The ID of the environment that this batch job should use.

    e.g. my-env If specified, image_ref must not be specified.
    """

    env_vars: Annotated[Dict[str, str], PropertyInfo(alias="envVars")]
    """Environment variables to be passed during this job's execution."""

    image_ref: Annotated[str, PropertyInfo(alias="imageRef")]
    """The container image used by this job.

    If specified, environment_id and snapshot_id must not be specified.
    """

    notebook_executor: Annotated[GatewayNotebookExecutorParam, PropertyInfo(alias="notebookExecutor")]
    """Execute a notebook file."""

    num_ranks: Annotated[int, PropertyInfo(alias="numRanks")]
    """
    For GPU node pools: one GPU per rank w/ host packing, for CPU node pools: one
    host per rank.
    """

    python_executor: Annotated[GatewayPythonExecutorParam, PropertyInfo(alias="pythonExecutor")]
    """Execute a Python process."""

    role: str
    """
    The ARN of the AWS IAM role that the batch job should assume. If not specified,
    the connection will fall back to the node pool's node_role.
    """

    shared: bool
    """
    Whether the batch job is shared with all users in the account. This allows all
    users to update, delete, clone, and create environments using the batch job.
    """

    shell_executor: Annotated[GatewayShellExecutorParam, PropertyInfo(alias="shellExecutor")]
    """Execute a shell script."""

    snapshot_id: Annotated[str, PropertyInfo(alias="snapshotId")]
    """
    The ID of the snapshot used by this batch job. If specified, environment_id must
    be specified and image_ref must not be specified.
    """
