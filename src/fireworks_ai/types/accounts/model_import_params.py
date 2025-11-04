# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["ModelImportParams", "AwsS3Source"]


class ModelImportParams(TypedDict, total=False):
    account_id: Required[str]

    aws_s3_source: Annotated[AwsS3Source, PropertyInfo(alias="awsS3Source")]
    """AWS S3 source details. Must be set when importing from AWS S3."""


class AwsS3Source(TypedDict, total=False):
    s3_bucket: Required[Annotated[str, PropertyInfo(alias="s3Bucket")]]
    """The S3 bucket name."""

    access_key_id: Annotated[str, PropertyInfo(alias="accessKeyId")]

    access_secret: Annotated[str, PropertyInfo(alias="accessSecret")]

    role_arn: Annotated[str, PropertyInfo(alias="roleArn")]

    s3_path: Annotated[str, PropertyInfo(alias="s3Path")]
    """The S3 path prefix."""
