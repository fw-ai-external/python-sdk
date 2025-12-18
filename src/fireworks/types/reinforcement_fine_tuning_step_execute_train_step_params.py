# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["ReinforcementFineTuningStepExecuteTrainStepParams"]


class ReinforcementFineTuningStepExecuteTrainStepParams(TypedDict, total=False):
    account_id: str

    dataset: Required[str]
    """Dataset to process for this iteration."""

    output_model: Required[Annotated[str, PropertyInfo(alias="outputModel")]]
    """Output model to materialize when training completes."""
