# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .gateway_status import GatewayStatus
from .gateway_mcp_server_state import GatewayMcpServerState
from .mcp_server_authentication_type import McpServerAuthenticationType

__all__ = ["GatewayMcpServer"]


class GatewayMcpServer(BaseModel):
    annotations: Optional[Dict[str, str]] = None
    """
    Annotations to identify MCP properties. Key/value pairs may be used by external
    tools or other services.
    """

    api_key_secret: Optional[str] = FieldInfo(alias="apiKeySecret", default=None)
    """
    The resource name of the secret to use for authenticating with the MCP server.
    e.g. accounts/my-account/secrets/my-secret If provided for a remote-hosted MCP,
    the endpoint will be validated for connectivity during creation.
    """

    authentication_type: Optional[McpServerAuthenticationType] = FieldInfo(alias="authenticationType", default=None)
    """The authentication method required by this MCP server."""

    create_time: Optional[datetime] = FieldInfo(alias="createTime", default=None)
    """The creation time of the mcp."""

    description: Optional[str] = None
    """The description of the mcp. Must be fewer than 4000 characters long."""

    display_name: Optional[str] = FieldInfo(alias="displayName", default=None)
    """Human-readable display name of the mcp.

    e.g. "My Mcp" Must be fewer than 64 characters long.
    """

    endpoint_url: Optional[str] = FieldInfo(alias="endpointUrl", default=None)
    """The URL of the MCP server. Required if self_hosted is true.

    For managed MCPs, this will be populated after deployment.
    """

    max_qps: Optional[float] = FieldInfo(alias="maxQps", default=None)
    """Max QPS of this MCP server. 0 means no ratelimit."""

    name: Optional[str] = None

    public: Optional[bool] = None
    """
    Whether this MCP is publicly available to all Fireworks users. If false, only
    accessible to the account that created it.
    """

    remote_hosted: Optional[bool] = FieldInfo(alias="remoteHosted", default=None)
    """Whether this MCP is remote-hosted (true) or managed by Fireworks (false)."""

    simulated: Optional[bool] = None
    """Whether this is a simulated MCP server."""

    state: Optional[GatewayMcpServerState] = None
    """The state of the mcp."""

    status: Optional[GatewayStatus] = None
    """Contains detailed message when the last mcp operation fails."""

    update_time: Optional[datetime] = FieldInfo(alias="updateTime", default=None)
    """The update time for the mcp."""
