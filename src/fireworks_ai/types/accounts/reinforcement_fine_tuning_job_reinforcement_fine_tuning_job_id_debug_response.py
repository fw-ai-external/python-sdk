# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["ReinforcementFineTuningJobReinforcementFineTuningJobIDDebugResponse"]


class ReinforcementFineTuningJobReinforcementFineTuningJobIDDebugResponse(BaseModel):
    name: str
    """The resource name of the reinforcement fine-tuning job."""

    failed_job_name: Optional[str] = FieldInfo(alias="failedJobName", default=None)
