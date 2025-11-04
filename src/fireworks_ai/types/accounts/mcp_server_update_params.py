# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo
from .mcp_server_authentication_type import McpServerAuthenticationType

__all__ = ["McpServerUpdateParams"]


class McpServerUpdateParams(TypedDict, total=False):
    account_id: Required[str]

    annotations: Dict[str, str]
    """
    Annotations to identify MCP properties. Key/value pairs may be used by external
    tools or other services.
    """

    api_key_secret: Annotated[str, PropertyInfo(alias="apiKeySecret")]
    """
    The resource name of the secret to use for authenticating with the MCP server.
    e.g. accounts/my-account/secrets/my-secret If provided for a remote-hosted MCP,
    the endpoint will be validated for connectivity during creation.
    """

    authentication_type: Annotated[McpServerAuthenticationType, PropertyInfo(alias="authenticationType")]
    """The authentication method required by this MCP server."""

    description: str
    """The description of the mcp. Must be fewer than 4000 characters long."""

    display_name: Annotated[str, PropertyInfo(alias="displayName")]
    """Human-readable display name of the mcp.

    e.g. "My Mcp" Must be fewer than 64 characters long.
    """

    endpoint_url: Annotated[str, PropertyInfo(alias="endpointUrl")]
    """The URL of the MCP server. Required if self_hosted is true.

    For managed MCPs, this will be populated after deployment.
    """

    max_qps: Annotated[float, PropertyInfo(alias="maxQps")]
    """Max QPS of this MCP server. 0 means no ratelimit."""

    public: bool
    """
    Whether this MCP is publicly available to all Fireworks users. If false, only
    accessible to the account that created it.
    """

    remote_hosted: Annotated[bool, PropertyInfo(alias="remoteHosted")]
    """Whether this MCP is remote-hosted (true) or managed by Fireworks (false)."""

    simulated: bool
    """Whether this is a simulated MCP server."""
