# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["DeployedModelRef"]


class DeployedModelRef(BaseModel):
    default: Optional[bool] = None
    """
    If true, this is the default target when querying this model without the
    `#<deployment>` suffix. The first deployment a model is deployed to will have
    this field set to true automatically.
    """

    deployment: Optional[str] = None
    """The resource name of the base deployment the model is deployed to."""

    name: Optional[str] = None

    public: Optional[bool] = None
    """If true, the deployed model will be publicly reachable."""

    state: Optional[Literal["STATE_UNSPECIFIED", "UNDEPLOYING", "DEPLOYING", "DEPLOYED", "UPDATING"]] = None
    """The state of the deployed model."""
