# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["AccountDeleteAwsIamRoleBindingParams"]


class AccountDeleteAwsIamRoleBindingParams(TypedDict, total=False):
    principal: str
    """The principal that is allowed to assume the AWS IAM role.

    This must be the email address of the user.
    """

    role: str
    """The AWS IAM role ARN that is allowed to be assumed by the principal."""
