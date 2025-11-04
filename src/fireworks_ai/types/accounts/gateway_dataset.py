# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .dataset_format import DatasetFormat
from .gateway_status import GatewayStatus
from .gateway_splitted import GatewaySplitted
from .gateway_transformed import GatewayTransformed
from .gateway_dataset_state import GatewayDatasetState
from .gateway_evaluation_result import GatewayEvaluationResult

__all__ = ["GatewayDataset"]


class GatewayDataset(BaseModel):
    created_by: Optional[str] = FieldInfo(alias="createdBy", default=None)
    """The email address of the user who initiated this fine-tuning job."""

    create_time: Optional[datetime] = FieldInfo(alias="createTime", default=None)

    display_name: Optional[str] = FieldInfo(alias="displayName", default=None)

    estimated_token_count: Optional[str] = FieldInfo(alias="estimatedTokenCount", default=None)
    """The estimated number of tokens in the dataset."""

    eval_protocol: Optional[object] = FieldInfo(alias="evalProtocol", default=None)

    evaluation_result: Optional[GatewayEvaluationResult] = FieldInfo(alias="evaluationResult", default=None)

    example_count: Optional[str] = FieldInfo(alias="exampleCount", default=None)

    external_url: Optional[str] = FieldInfo(alias="externalUrl", default=None)

    format: Optional[DatasetFormat] = None

    name: Optional[str] = None

    source_job_name: Optional[str] = FieldInfo(alias="sourceJobName", default=None)
    """
    The resource name of the job that created this dataset (e.g., batch inference
    job). Used for lineage tracking to understand dataset provenance.
    """

    splitted: Optional[GatewaySplitted] = None

    state: Optional[GatewayDatasetState] = None

    status: Optional[GatewayStatus] = None

    transformed: Optional[GatewayTransformed] = None

    update_time: Optional[datetime] = FieldInfo(alias="updateTime", default=None)
    """The update time for the dataset."""

    user_uploaded: Optional[object] = FieldInfo(alias="userUploaded", default=None)
