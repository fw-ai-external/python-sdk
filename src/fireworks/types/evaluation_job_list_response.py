# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .shared.status import Status

__all__ = ["EvaluationJobListResponse", "AwsS3Config"]


class AwsS3Config(BaseModel):
    """The AWS configuration for S3 dataset access."""

    credentials_secret: Optional[str] = FieldInfo(alias="credentialsSecret", default=None)

    iam_role_arn: Optional[str] = FieldInfo(alias="iamRoleArn", default=None)


class EvaluationJobListResponse(BaseModel):
    evaluator: str
    """The fully-qualified resource name of the Evaluation used by this job.

    Format: accounts/{account_id}/evaluators/{evaluator_id}
    """

    input_dataset: str = FieldInfo(alias="inputDataset")
    """The fully-qualified resource name of the input Dataset used by this job.

    Format: accounts/{account_id}/datasets/{dataset_id}
    """

    output_dataset: str = FieldInfo(alias="outputDataset")
    """The fully-qualified resource name of the output Dataset created by this job.

    Format: accounts/{account_id}/datasets/{output_dataset_id}
    """

    aws_s3_config: Optional[AwsS3Config] = FieldInfo(alias="awsS3Config", default=None)
    """The AWS configuration for S3 dataset access."""

    created_by: Optional[str] = FieldInfo(alias="createdBy", default=None)

    create_time: Optional[datetime] = FieldInfo(alias="createTime", default=None)

    display_name: Optional[str] = FieldInfo(alias="displayName", default=None)

    metrics: Optional[Dict[str, float]] = None

    name: Optional[str] = None

    output_stats: Optional[str] = FieldInfo(alias="outputStats", default=None)
    """The output dataset's aggregated stats for the evaluation job."""

    state: Optional[
        Literal[
            "JOB_STATE_UNSPECIFIED",
            "JOB_STATE_CREATING",
            "JOB_STATE_RUNNING",
            "JOB_STATE_COMPLETED",
            "JOB_STATE_FAILED",
            "JOB_STATE_CANCELLED",
            "JOB_STATE_DELETING",
            "JOB_STATE_WRITING_RESULTS",
            "JOB_STATE_VALIDATING",
            "JOB_STATE_DELETING_CLEANING_UP",
            "JOB_STATE_PENDING",
            "JOB_STATE_EXPIRED",
            "JOB_STATE_RE_QUEUEING",
            "JOB_STATE_CREATING_INPUT_DATASET",
            "JOB_STATE_IDLE",
            "JOB_STATE_CANCELLING",
            "JOB_STATE_EARLY_STOPPED",
            "JOB_STATE_PAUSED",
        ]
    ] = None
    """JobState represents the state an asynchronous job can be in.

    - JOB_STATE_PAUSED: Job is paused, typically due to account suspension or manual
      intervention.
    """

    status: Optional[Status] = None

    update_time: Optional[datetime] = FieldInfo(alias="updateTime", default=None)
    """The update time for the evaluation job."""
