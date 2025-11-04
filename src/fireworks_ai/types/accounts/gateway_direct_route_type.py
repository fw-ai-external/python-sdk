# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal, TypeAlias

__all__ = ["GatewayDirectRouteType"]

GatewayDirectRouteType: TypeAlias = Literal[
    "DIRECT_ROUTE_TYPE_UNSPECIFIED", "INTERNET", "GCP_PRIVATE_SERVICE_CONNECT", "AWS_PRIVATELINK"
]
