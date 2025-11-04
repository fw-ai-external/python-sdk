# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["GatewayEksCluster"]


class GatewayEksCluster(BaseModel):
    aws_account_id: str = FieldInfo(alias="awsAccountId")
    """The 12-digit AWS account ID where this cluster lives."""

    region: str
    """The AWS region where this cluster lives.

    See
    https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.RegionsAndAvailabilityZones.html
    for a list of available regions.
    """

    cluster_name: Optional[str] = FieldInfo(alias="clusterName", default=None)
    """The EKS cluster name."""

    fireworks_manager_role: Optional[str] = FieldInfo(alias="fireworksManagerRole", default=None)

    inference_role: Optional[str] = FieldInfo(alias="inferenceRole", default=None)
    """The IAM role ARN used by the inference pods on the cluster."""

    load_balancer_controller_role: Optional[str] = FieldInfo(alias="loadBalancerControllerRole", default=None)
    """The IAM role ARN used by the EKS load balancer controller (i.e.

    the load balancer automatically created for the k8s gateway resource). If not
    specified, no gateway will be created.
    """

    metric_writer_role: Optional[str] = FieldInfo(alias="metricWriterRole", default=None)
    """
    The IAM role ARN used by Google Managed Prometheus role that will write metrics
    to Fireworks managed Prometheus. The role must be assumable by the
    `system:serviceaccount:gmp-system:collector` service account on the EKS cluster.
    If not specified, no metrics will be written to GCP.
    """

    storage_bucket_name: Optional[str] = FieldInfo(alias="storageBucketName", default=None)
    """The S3 bucket name."""

    workload_identity_pool_provider_id: Optional[str] = FieldInfo(alias="workloadIdentityPoolProviderId", default=None)
