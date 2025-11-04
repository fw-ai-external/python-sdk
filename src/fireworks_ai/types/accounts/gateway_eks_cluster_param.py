# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["GatewayEksClusterParam"]


class GatewayEksClusterParam(TypedDict, total=False):
    aws_account_id: Required[Annotated[str, PropertyInfo(alias="awsAccountId")]]
    """The 12-digit AWS account ID where this cluster lives."""

    region: Required[str]
    """The AWS region where this cluster lives.

    See
    https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.RegionsAndAvailabilityZones.html
    for a list of available regions.
    """

    cluster_name: Annotated[str, PropertyInfo(alias="clusterName")]
    """The EKS cluster name."""

    fireworks_manager_role: Annotated[str, PropertyInfo(alias="fireworksManagerRole")]

    inference_role: Annotated[str, PropertyInfo(alias="inferenceRole")]
    """The IAM role ARN used by the inference pods on the cluster."""

    load_balancer_controller_role: Annotated[str, PropertyInfo(alias="loadBalancerControllerRole")]
    """The IAM role ARN used by the EKS load balancer controller (i.e.

    the load balancer automatically created for the k8s gateway resource). If not
    specified, no gateway will be created.
    """

    metric_writer_role: Annotated[str, PropertyInfo(alias="metricWriterRole")]
    """
    The IAM role ARN used by Google Managed Prometheus role that will write metrics
    to Fireworks managed Prometheus. The role must be assumable by the
    `system:serviceaccount:gmp-system:collector` service account on the EKS cluster.
    If not specified, no metrics will be written to GCP.
    """

    storage_bucket_name: Annotated[str, PropertyInfo(alias="storageBucketName")]
    """The S3 bucket name."""

    workload_identity_pool_provider_id: Annotated[str, PropertyInfo(alias="workloadIdentityPoolProviderId")]
