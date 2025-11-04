# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .gateway_reinforcement_fine_tuning_job import GatewayReinforcementFineTuningJob

__all__ = ["ReinforcementFineTuningJobRetrieveReinforcementFineTuningJobsResponse"]


class ReinforcementFineTuningJobRetrieveReinforcementFineTuningJobsResponse(BaseModel):
    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)
    """
    A token, which can be sent as `page_token` to retrieve the next page. If this
    field is omitted, there are no subsequent pages.
    """

    reinforcement_fine_tuning_jobs: Optional[List[GatewayReinforcementFineTuningJob]] = FieldInfo(
        alias="reinforcementFineTuningJobs", default=None
    )

    total_size: Optional[int] = FieldInfo(alias="totalSize", default=None)
