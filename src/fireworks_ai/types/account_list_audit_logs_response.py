# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .accounts.gateway_status import GatewayStatus

__all__ = ["AccountListAuditLogsResponse", "AuditLog"]


class AuditLog(BaseModel):
    id: Optional[str] = None
    """Audit log entry id."""

    is_admin_action: Optional[bool] = FieldInfo(alias="isAdminAction", default=None)

    message: Optional[str] = None

    method: Optional[str] = None
    """The gRPC method name."""

    payload: Optional[object] = None
    """The payload as JSON."""

    principal: Optional[str] = None
    """The email of the principal user who performed this action."""

    resource: Optional[str] = None

    status: Optional[GatewayStatus] = None
    """The response status."""

    timestamp: Optional[datetime] = None
    """The timestamp when the request was received."""


class AccountListAuditLogsResponse(BaseModel):
    audit_logs: Optional[List[AuditLog]] = FieldInfo(alias="auditLogs", default=None)

    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)
    """
    A token, which can be sent as `page_token` to retrieve the next page. If this
    field is omitted, there are no subsequent pages.
    """

    total_size: Optional[int] = FieldInfo(alias="totalSize", default=None)
    """The total number of request logs matching the request."""
