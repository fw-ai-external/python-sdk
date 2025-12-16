# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["RollupSettings"]


class RollupSettings(BaseModel):
    criteria_weights: Optional[Dict[str, float]] = FieldInfo(alias="criteriaWeights", default=None)

    python_code: Optional[str] = FieldInfo(alias="pythonCode", default=None)

    skip_rollup: Optional[bool] = FieldInfo(alias="skipRollup", default=None)

    success_threshold: Optional[float] = FieldInfo(alias="successThreshold", default=None)
