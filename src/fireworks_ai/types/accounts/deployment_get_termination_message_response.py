# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["DeploymentGetTerminationMessageResponse"]


class DeploymentGetTerminationMessageResponse(BaseModel):
    message: Optional[str] = None
    """The termination message."""
