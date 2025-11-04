# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._types import SequenceNotStr
from ..._utils import PropertyInfo
from .gateway_oidc_config_param import GatewayOidcConfigParam
from .gateway_saml_config_param import GatewaySAMLConfigParam

__all__ = ["IdentityProviderUpdateParams"]


class IdentityProviderUpdateParams(TypedDict, total=False):
    account_id: Required[str]

    display_name: Annotated[str, PropertyInfo(alias="displayName")]

    oidc_config: Annotated[GatewayOidcConfigParam, PropertyInfo(alias="oidcConfig")]

    saml_config: Annotated[GatewaySAMLConfigParam, PropertyInfo(alias="samlConfig")]

    tenant_domains: Annotated[SequenceNotStr[str], PropertyInfo(alias="tenantDomains")]
