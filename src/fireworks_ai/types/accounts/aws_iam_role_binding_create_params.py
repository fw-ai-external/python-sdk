# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["AwsIamRoleBindingCreateParams"]


class AwsIamRoleBindingCreateParams(TypedDict, total=False):
    principal: Required[str]
    """The principal that is allowed to assume the AWS IAM role.

    This must be the email address of the user.
    """

    role: Required[str]
    """The AWS IAM role ARN that is allowed to be assumed by the principal."""
