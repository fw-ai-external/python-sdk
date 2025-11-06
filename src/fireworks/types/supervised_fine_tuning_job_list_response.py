# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .supervised_fine_tuning_job import SupervisedFineTuningJob

__all__ = ["SupervisedFineTuningJobListResponse"]


class SupervisedFineTuningJobListResponse(BaseModel):
    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)
    """
    A token, which can be sent as `page_token` to retrieve the next page. If this
    field is omitted, there are no subsequent pages.
    """

    supervised_fine_tuning_jobs: Optional[List[SupervisedFineTuningJob]] = FieldInfo(
        alias="supervisedFineTuningJobs", default=None
    )

    total_size: Optional[int] = FieldInfo(alias="totalSize", default=None)
