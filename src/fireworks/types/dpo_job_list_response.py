# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .dpo_job import DpoJob
from .._models import BaseModel

__all__ = ["DpoJobListResponse"]


class DpoJobListResponse(BaseModel):
    dpo_jobs: Optional[List[DpoJob]] = FieldInfo(alias="dpoJobs", default=None)

    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)
    """
    A token, which can be sent as `page_token` to retrieve the next page. If this
    field is omitted, there are no subsequent pages.
    """

    total_size: Optional[int] = FieldInfo(alias="totalSize", default=None)
