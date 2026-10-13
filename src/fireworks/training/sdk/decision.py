"""Decision checkpoint calibration.

``SamplerCheckpointMetadata`` rides on ``save_weights_for_sampler`` and carries the held-out
temperatures the trainer writes into the checkpoint's ``decision.json``. The models
below validate the calibration metadata supplied with a sampler checkpoint.
"""

from __future__ import annotations

import math
from typing import Literal, Optional, Annotated

from pydantic import Field, BaseModel, ConfigDict, AfterValidator, model_validator

# The serving prompt and readout contract a checkpoint was trained against.
DEFAULT_DECISION_CONTRACT = "systemone-letter-v1"

QuestionType = Literal["noul", "choice", "score"]

_IDENTIFIER = r"^[a-z0-9][a-z0-9._-]{0,63}$"
_MAX_METRIC_GROUPS = 16
_MAX_METRICS_PER_GROUP = 32


def _finite(value: float) -> float:
    if not math.isfinite(value):
        raise ValueError("must be finite")
    return value


FiniteFloat = Annotated[float, AfterValidator(_finite)]
PositiveTemperature = Annotated[float, Field(gt=0.0, le=100.0), AfterValidator(_finite)]


class DecisionCalibration(BaseModel):
    """Post-hoc temperatures fit on held-out rows, per question type (absent: T = 1)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    contract: str = Field(default=DEFAULT_DECISION_CONTRACT, pattern=_IDENTIFIER)
    objective: Literal["nll"] = "nll"
    temperature: dict[QuestionType, PositiveTemperature]
    fit_rows: dict[QuestionType, Annotated[int, Field(ge=0)]] = Field(default_factory=dict)
    metrics: dict[
        Annotated[str, Field(min_length=1, max_length=64)],
        dict[Annotated[str, Field(min_length=1, max_length=64)], FiniteFloat],
    ] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _bounded_metrics(self) -> "DecisionCalibration":
        if len(self.metrics) > _MAX_METRIC_GROUPS or any(
            len(group) > _MAX_METRICS_PER_GROUP for group in self.metrics.values()
        ):
            raise ValueError(f"metrics allows at most {_MAX_METRIC_GROUPS} groups of {_MAX_METRICS_PER_GROUP} values")
        return self


class SamplerCheckpointMetadata(BaseModel):
    """Typed metadata attached to one ``save_weights_for_sampler`` call."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    decision_calibration: Optional[DecisionCalibration] = None
