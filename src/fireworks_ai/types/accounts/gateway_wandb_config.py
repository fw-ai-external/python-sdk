# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["GatewayWandbConfig"]


class GatewayWandbConfig(BaseModel):
    api_key: Optional[str] = FieldInfo(alias="apiKey", default=None)
    """The API key for the wandb service."""

    enabled: Optional[bool] = None
    """Whether to enable wandb logging."""

    entity: Optional[str] = None
    """The entity name for the wandb service."""

    project: Optional[str] = None
    """The project name for the wandb service."""

    run_id: Optional[str] = FieldInfo(alias="runId", default=None)
    """The run ID for the wandb service."""

    url: Optional[str] = None
    """The URL for the wandb service."""
