# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .gateway_shell_executor import GatewayShellExecutor
from .gateway_batch_job_state import GatewayBatchJobState
from .gateway_python_executor import GatewayPythonExecutor
from .gateway_notebook_executor import GatewayNotebookExecutor

__all__ = ["GatewayBatchJob"]


class GatewayBatchJob(BaseModel):
    node_pool_id: str = FieldInfo(alias="nodePoolId")

    annotations: Optional[Dict[str, str]] = None
    """
    Arbitrary, user-specified metadata. Keys and values must adhere to Kubernetes
    constraints:
    https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/#syntax-and-character-set
    Additionally, the "fireworks.ai/" prefix is reserved.
    """

    created_by: Optional[str] = FieldInfo(alias="createdBy", default=None)
    """The email address of the user who created this batch job."""

    create_time: Optional[datetime] = FieldInfo(alias="createTime", default=None)
    """The creation time of the batch job."""

    display_name: Optional[str] = FieldInfo(alias="displayName", default=None)
    """Human-readable display name of the batch job.

    e.g. "My Batch Job" Must be fewer than 64 characters long.
    """

    end_time: Optional[datetime] = FieldInfo(alias="endTime", default=None)
    """The time when the batch job completed, failed, or was cancelled."""

    environment_id: Optional[str] = FieldInfo(alias="environmentId", default=None)
    """The ID of the environment that this batch job should use.

    e.g. my-env If specified, image_ref must not be specified.
    """

    env_vars: Optional[Dict[str, str]] = FieldInfo(alias="envVars", default=None)
    """Environment variables to be passed during this job's execution."""

    image_ref: Optional[str] = FieldInfo(alias="imageRef", default=None)
    """The container image used by this job.

    If specified, environment_id and snapshot_id must not be specified.
    """

    name: Optional[str] = None

    notebook_executor: Optional[GatewayNotebookExecutor] = FieldInfo(alias="notebookExecutor", default=None)
    """Execute a notebook file."""

    num_ranks: Optional[int] = FieldInfo(alias="numRanks", default=None)
    """
    For GPU node pools: one GPU per rank w/ host packing, for CPU node pools: one
    host per rank.
    """

    python_executor: Optional[GatewayPythonExecutor] = FieldInfo(alias="pythonExecutor", default=None)
    """Execute a Python process."""

    role: Optional[str] = None
    """
    The ARN of the AWS IAM role that the batch job should assume. If not specified,
    the connection will fall back to the node pool's node_role.
    """

    shared: Optional[bool] = None
    """
    Whether the batch job is shared with all users in the account. This allows all
    users to update, delete, clone, and create environments using the batch job.
    """

    shell_executor: Optional[GatewayShellExecutor] = FieldInfo(alias="shellExecutor", default=None)
    """Execute a shell script."""

    snapshot_id: Optional[str] = FieldInfo(alias="snapshotId", default=None)
    """
    The ID of the snapshot used by this batch job. If specified, environment_id must
    be specified and image_ref must not be specified.
    """

    start_time: Optional[datetime] = FieldInfo(alias="startTime", default=None)
    """The time when the batch job started running."""

    state: Optional[GatewayBatchJobState] = None
    """The current state of the batch job."""

    status: Optional[str] = None
    """Detailed information about the current status of the batch job."""

    update_time: Optional[datetime] = FieldInfo(alias="updateTime", default=None)
    """The update time for the batch job."""
