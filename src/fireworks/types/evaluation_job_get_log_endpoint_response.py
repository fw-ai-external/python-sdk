# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["EvaluationJobGetLogEndpointResponse"]


class EvaluationJobGetLogEndpointResponse(BaseModel):
    """Response carries the stream log URL (for VirtualizedLogViewer).

    Next ID: 4
    """

    content_type: Optional[str] = FieldInfo(alias="contentType", default=None)
    """Content type for the log file (e.g.

    "text/plain"). Only set when execution_log_signed_uri is present.
    """

    execution_log_signed_uri: Optional[str] = FieldInfo(alias="executionLogSignedUri", default=None)
    """
    Short-lived signed URL for the execution log file. Empty if the log file has not
    been created yet (e.g. job not started or still initializing).
    """

    expire_time: Optional[datetime] = FieldInfo(alias="expireTime", default=None)
    """
    Expiration time of the signed URL. Only set when execution_log_signed_uri is
    present.
    """
