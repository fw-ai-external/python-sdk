# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["GatewayFakeNodePoolParam"]


class GatewayFakeNodePoolParam(TypedDict, total=False):
    machine_type: Annotated[str, PropertyInfo(alias="machineType")]

    num_nodes: Annotated[int, PropertyInfo(alias="numNodes")]

    service_account: Annotated[str, PropertyInfo(alias="serviceAccount")]
