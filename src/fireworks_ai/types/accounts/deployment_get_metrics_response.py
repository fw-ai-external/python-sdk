# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional

from ..._models import BaseModel

__all__ = ["DeploymentGetMetricsResponse"]


class DeploymentGetMetricsResponse(BaseModel):
    metrics: Optional[Dict[str, float]] = None
