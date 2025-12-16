# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["RollupSettingsParam"]


class RollupSettingsParam(TypedDict, total=False):
    criteria_weights: Annotated[Dict[str, float], PropertyInfo(alias="criteriaWeights")]

    python_code: Annotated[str, PropertyInfo(alias="pythonCode")]

    skip_rollup: Annotated[bool, PropertyInfo(alias="skipRollup")]

    success_threshold: Annotated[float, PropertyInfo(alias="successThreshold")]
