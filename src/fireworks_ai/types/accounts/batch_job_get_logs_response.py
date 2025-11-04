# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["BatchJobGetLogsResponse", "Entry"]


class Entry(BaseModel):
    log_time: Optional[datetime] = FieldInfo(alias="logTime", default=None)
    """The timestamp of the log entry."""

    message: Optional[str] = None
    """The log messsage."""

    rank: Optional[int] = None
    """The rank which produced the log entry."""


class BatchJobGetLogsResponse(BaseModel):
    entries: Optional[List[Entry]] = None

    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)
    """
    A token, which can be sent as `page_token` to retrieve the next page. If this
    field is omitted, there are no subsequent pages.
    """
