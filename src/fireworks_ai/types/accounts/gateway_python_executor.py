# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["GatewayPythonExecutor"]


class GatewayPythonExecutor(BaseModel):
    target: str
    """A Python module or filename depending on TargetType."""

    target_type: Literal["TARGET_TYPE_UNSPECIFIED", "MODULE", "FILENAME"] = FieldInfo(alias="targetType")
    """The type of Python target to run."""

    args: Optional[List[str]] = None
    """Command line arguments to pass to the Python process."""
