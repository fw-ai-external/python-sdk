# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .reinforcement_fine_tuning_step import ReinforcementFineTuningStep

__all__ = ["ReinforcementFineTuningStepListResponse"]


class ReinforcementFineTuningStepListResponse(BaseModel):
    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)
    """
    A token, which can be sent as `page_token` to retrieve the next page. If this
    field is omitted, there are no subsequent pages.
    """

    rlor_trainer_jobs: Optional[List[ReinforcementFineTuningStep]] = FieldInfo(alias="rlorTrainerJobs", default=None)

    total_size: Optional[int] = FieldInfo(alias="totalSize", default=None)
