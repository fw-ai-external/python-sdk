# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._types import SequenceNotStr
from ..._utils import PropertyInfo
from .gateway_evaluation_job_param import GatewayEvaluationJobParam

__all__ = ["EvaluationJobCreateParams"]


class EvaluationJobCreateParams(TypedDict, total=False):
    evaluation_job: Required[Annotated[GatewayEvaluationJobParam, PropertyInfo(alias="evaluationJob")]]

    evaluation_job_id: Annotated[str, PropertyInfo(alias="evaluationJobId")]

    leaderboard_ids: Annotated[SequenceNotStr[str], PropertyInfo(alias="leaderboardIds")]
    """Optional leaderboards to attach this job to upon creation."""
