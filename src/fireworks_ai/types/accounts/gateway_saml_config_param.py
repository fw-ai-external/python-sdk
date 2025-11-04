# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["GatewaySAMLConfigParam"]


class GatewaySAMLConfigParam(TypedDict, total=False):
    metadata_url: Required[Annotated[str, PropertyInfo(alias="metadataUrl")]]
