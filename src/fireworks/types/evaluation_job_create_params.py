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

    evaluator_version: Annotated[str, PropertyInfo(alias="evaluatorVersion")]
    """The evaluator version ID used for this job.

    If specified in the request, this version is used instead of the evaluator's
    current version. If not specified, the evaluator's current_version_id is used
    and stored here for auditing purposes.

    Format: The version ID only (not the full resource name), e.g. "v1.0.0" or
    "abc123"
    """

    output_stats: Annotated[str, PropertyInfo(alias="outputStats")]
    """The output dataset's aggregated stats for the evaluation job."""
