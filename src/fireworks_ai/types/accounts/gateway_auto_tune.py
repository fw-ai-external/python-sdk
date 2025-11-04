# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["GatewayAutoTune"]


class GatewayAutoTune(BaseModel):
    long_prompt: Optional[bool] = FieldInfo(alias="longPrompt", default=None)
    """If true, this deployment is optimized for long prompt lengths."""
