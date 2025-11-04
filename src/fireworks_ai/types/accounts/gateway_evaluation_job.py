# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .gateway_status import GatewayStatus
from .gateway_job_state import GatewayJobState

__all__ = ["GatewayEvaluationJob"]


class GatewayEvaluationJob(BaseModel):
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

    created_by: Optional[str] = FieldInfo(alias="createdBy", default=None)

    create_time: Optional[datetime] = FieldInfo(alias="createTime", default=None)

    display_name: Optional[str] = FieldInfo(alias="displayName", default=None)

    metrics: Optional[Dict[str, float]] = None

    name: Optional[str] = None

    output_stats: Optional[str] = FieldInfo(alias="outputStats", default=None)
    """The output dataset's aggregated stats for the evaluation job."""

    state: Optional[GatewayJobState] = None
    """JobState represents the state an asynchronous job can be in."""

    status: Optional[GatewayStatus] = None

    update_time: Optional[datetime] = FieldInfo(alias="updateTime", default=None)
    """The update time for the evaluation job."""
