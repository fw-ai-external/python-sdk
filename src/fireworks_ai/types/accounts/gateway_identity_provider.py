# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .gateway_status import GatewayStatus
from .gateway_oidc_config import GatewayOidcConfig
from .gateway_saml_config import GatewaySAMLConfig
from .gateway_identity_provider_state import GatewayIdentityProviderState

__all__ = ["GatewayIdentityProvider"]


class GatewayIdentityProvider(BaseModel):
    client_id: Optional[str] = FieldInfo(alias="clientId", default=None)
    """The OIDC client ID."""

    create_time: Optional[datetime] = FieldInfo(alias="createTime", default=None)

    display_name: Optional[str] = FieldInfo(alias="displayName", default=None)

    domain_url: Optional[str] = FieldInfo(alias="domainUrl", default=None)
    """The domain URL."""

    issuer_url: Optional[str] = FieldInfo(alias="issuerUrl", default=None)
    """The OIDC issuer URL."""

    name: Optional[str] = None

    oidc_config: Optional[GatewayOidcConfig] = FieldInfo(alias="oidcConfig", default=None)

    saml_config: Optional[GatewaySAMLConfig] = FieldInfo(alias="samlConfig", default=None)

    state: Optional[GatewayIdentityProviderState] = None

    status: Optional[GatewayStatus] = None
    """Contains information about the identity provider status."""

    tenant_domains: Optional[List[str]] = FieldInfo(alias="tenantDomains", default=None)

    update_time: Optional[datetime] = FieldInfo(alias="updateTime", default=None)
