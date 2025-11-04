# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["GatewayFakeNodePool"]


class GatewayFakeNodePool(BaseModel):
    machine_type: Optional[str] = FieldInfo(alias="machineType", default=None)

    num_nodes: Optional[int] = FieldInfo(alias="numNodes", default=None)

    service_account: Optional[str] = FieldInfo(alias="serviceAccount", default=None)
