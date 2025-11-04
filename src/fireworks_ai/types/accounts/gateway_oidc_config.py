# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["GatewayOidcConfig"]


class GatewayOidcConfig(BaseModel):
    client_id: str = FieldInfo(alias="clientId")

    client_secret: str = FieldInfo(alias="clientSecret")

    issuer_url: str = FieldInfo(alias="issuerUrl")
