# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .gateway_status import GatewayStatus
from .gateway_environment_state import GatewayEnvironmentState
from .gateway_environment_connection import GatewayEnvironmentConnection

__all__ = ["GatewayEnvironment"]


class GatewayEnvironment(BaseModel):
    annotations: Optional[Dict[str, str]] = None
    """
    Arbitrary, user-specified metadata. Keys and values must adhere to Kubernetes
    constraints:
    https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/#syntax-and-character-set
    Additionally, the "fireworks.ai/" prefix is reserved.
    """

    base_image_ref: Optional[str] = FieldInfo(alias="baseImageRef", default=None)
    """The URI of the base container image used for this environment."""

    connection: Optional[GatewayEnvironmentConnection] = None
    """Information about the current environment connection."""

    created_by: Optional[str] = FieldInfo(alias="createdBy", default=None)
    """The email address of the user who created this environment."""

    create_time: Optional[datetime] = FieldInfo(alias="createTime", default=None)
    """The creation time of the environment."""

    display_name: Optional[str] = FieldInfo(alias="displayName", default=None)

    image_ref: Optional[str] = FieldInfo(alias="imageRef", default=None)
    """The URI of the container image used for this environment.

    This is a image is an immutable snapshot of the base_image_ref when the
    environment was created.
    """

    name: Optional[str] = None

    shared: Optional[bool] = None
    """
    Whether the environment is shared with all users in the account. This allows all
    users to connect, disconnect, update, delete, clone, and create batch jobs using
    the environment.
    """

    snapshot_image_ref: Optional[str] = FieldInfo(alias="snapshotImageRef", default=None)
    """The URI of the latest container image snapshot for this environment."""

    state: Optional[GatewayEnvironmentState] = None
    """The current state of the environment."""

    status: Optional[GatewayStatus] = None
    """The current error status of the environment."""

    update_time: Optional[datetime] = FieldInfo(alias="updateTime", default=None)
    """The update time for the environment."""
