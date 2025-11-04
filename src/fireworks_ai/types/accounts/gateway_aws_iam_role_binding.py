# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["GatewayAwsIamRoleBinding"]


class GatewayAwsIamRoleBinding(BaseModel):
    principal: str
    """The principal that is allowed to assume the AWS IAM role.

    This must be the email address of the user.
    """

    role: str
    """The AWS IAM role ARN that is allowed to be assumed by the principal."""

    account_id: Optional[str] = FieldInfo(alias="accountId", default=None)
    """The account ID that this binding is associated with."""

    create_time: Optional[datetime] = FieldInfo(alias="createTime", default=None)
    """The creation time of the AWS IAM role binding."""
