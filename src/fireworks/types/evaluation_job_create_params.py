# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._types import SequenceNotStr
from .._utils import PropertyInfo

__all__ = ["EvaluationJobCreateParams", "EvaluationJob"]


class EvaluationJobCreateParams(TypedDict, total=False):
    account_id: str

    evaluation_job: Required[Annotated[EvaluationJob, PropertyInfo(alias="evaluationJob")]]

    evaluation_job_id: Annotated[str, PropertyInfo(alias="evaluationJobId")]

    leaderboard_ids: Annotated[SequenceNotStr[str], PropertyInfo(alias="leaderboardIds")]
    """Optional leaderboards to attach this job to upon creation."""


class EvaluationJob(TypedDict, total=False):
    evaluator: Required[str]
    """The fully-qualified resource name of the Evaluation used by this job.

    Format: accounts/{account_id}/evaluators/{evaluator_id}
    """

    input_dataset: Required[Annotated[str, PropertyInfo(alias="inputDataset")]]
    """The fully-qualified resource name of the input Dataset used by this job.

    Format: accounts/{account_id}/datasets/{dataset_id}
    """

    output_dataset: Required[Annotated[str, PropertyInfo(alias="outputDataset")]]
    """The fully-qualified resource name of the output Dataset created by this job.

    Format: accounts/{account_id}/datasets/{output_dataset_id}
    """

    display_name: Annotated[str, PropertyInfo(alias="displayName")]

    output_stats: Annotated[str, PropertyInfo(alias="outputStats")]
    """The output dataset's aggregated stats for the evaluation job."""
