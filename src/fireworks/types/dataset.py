# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .splitted import Splitted
from .transformed import Transformed
from .shared.status import Status
from .evaluation_result import EvaluationResult

__all__ = ["Dataset"]


class Dataset(BaseModel):
    average_turn_count: Optional[float] = FieldInfo(alias="averageTurnCount", default=None)
    """An estimate of the average number of turns per sample in the dataset."""

    created_by: Optional[str] = FieldInfo(alias="createdBy", default=None)
    """The email address of the user who initiated this fine-tuning job."""

    create_time: Optional[datetime] = FieldInfo(alias="createTime", default=None)

    display_name: Optional[str] = FieldInfo(alias="displayName", default=None)

    estimated_token_count: Optional[str] = FieldInfo(alias="estimatedTokenCount", default=None)
    """The estimated number of tokens in the dataset."""

    eval_protocol: Optional[object] = FieldInfo(alias="evalProtocol", default=None)

    evaluation_result: Optional[EvaluationResult] = FieldInfo(alias="evaluationResult", default=None)

    example_count: Optional[str] = FieldInfo(alias="exampleCount", default=None)

    external_url: Optional[str] = FieldInfo(alias="externalUrl", default=None)

    format: Optional[Literal["FORMAT_UNSPECIFIED", "CHAT", "COMPLETION", "RL"]] = None

    name: Optional[str] = None

    source_job_name: Optional[str] = FieldInfo(alias="sourceJobName", default=None)
    """
    The resource name of the job that created this dataset (e.g., batch inference
    job). Used for lineage tracking to understand dataset provenance.
    """

    splitted: Optional[Splitted] = None

    state: Optional[Literal["STATE_UNSPECIFIED", "UPLOADING", "READY"]] = None

    status: Optional[Status] = None

    transformed: Optional[Transformed] = None

    update_time: Optional[datetime] = FieldInfo(alias="updateTime", default=None)
    """The update time for the dataset."""

    user_uploaded: Optional[object] = FieldInfo(alias="userUploaded", default=None)
