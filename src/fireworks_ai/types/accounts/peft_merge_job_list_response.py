# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .gateway_peft_merge_job import GatewayPeftMergeJob

__all__ = ["PeftMergeJobListResponse"]


class PeftMergeJobListResponse(BaseModel):
    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)
    """
    A token, which can be sent as `page_token` to retrieve the next page. If this
    field is omitted, there are no subsequent pages.
    """

    peft_merge_jobs: Optional[List[GatewayPeftMergeJob]] = FieldInfo(alias="peftMergeJobs", default=None)

    total_size: Optional[int] = FieldInfo(alias="totalSize", default=None)
    """The total number of peft merge jobs."""
