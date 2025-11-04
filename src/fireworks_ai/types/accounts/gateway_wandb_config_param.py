# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["GatewayWandbConfigParam"]


class GatewayWandbConfigParam(TypedDict, total=False):
    api_key: Annotated[str, PropertyInfo(alias="apiKey")]
    """The API key for the wandb service."""

    enabled: bool
    """Whether to enable wandb logging."""

    entity: str
    """The entity name for the wandb service."""

    project: str
    """The project name for the wandb service."""

    run_id: Annotated[str, PropertyInfo(alias="runId")]
    """The run ID for the wandb service."""
