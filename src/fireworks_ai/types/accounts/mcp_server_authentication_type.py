# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal, TypeAlias

__all__ = ["McpServerAuthenticationType"]

McpServerAuthenticationType: TypeAlias = Literal[
    "AUTHENTICATION_TYPE_UNSPECIFIED", "OPEN", "API_KEY", "OAUTH2", "BEARER_TOKEN"
]
