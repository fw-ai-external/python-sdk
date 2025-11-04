# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._types import SequenceNotStr
from ..._utils import PropertyInfo

__all__ = ["GatewayPythonExecutorParam"]


class GatewayPythonExecutorParam(TypedDict, total=False):
    target: Required[str]
    """A Python module or filename depending on TargetType."""

    target_type: Required[
        Annotated[Literal["TARGET_TYPE_UNSPECIFIED", "MODULE", "FILENAME"], PropertyInfo(alias="targetType")]
    ]
    """The type of Python target to run."""

    args: SequenceNotStr[str]
    """Command line arguments to pass to the Python process."""
