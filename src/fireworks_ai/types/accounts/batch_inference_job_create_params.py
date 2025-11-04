# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ..._utils import PropertyInfo
from .deployment_precision import DeploymentPrecision
from .gateway_inference_parameters_param import GatewayInferenceParametersParam

__all__ = ["BatchInferenceJobCreateParams"]


class BatchInferenceJobCreateParams(TypedDict, total=False):
    batch_inference_job_id: Annotated[str, PropertyInfo(alias="batchInferenceJobId")]
    """ID of the batch inference job."""

    continued_from_job_name: Annotated[str, PropertyInfo(alias="continuedFromJobName")]
    """
    The resource name of the batch inference job that this job continues from. Used
    for lineage tracking to understand job continuation chains.
    """

    display_name: Annotated[str, PropertyInfo(alias="displayName")]

    inference_parameters: Annotated[GatewayInferenceParametersParam, PropertyInfo(alias="inferenceParameters")]
    """Parameters controlling the inference process."""

    input_dataset_id: Annotated[str, PropertyInfo(alias="inputDatasetId")]
    """The name of the dataset used for inference.

    This is required, except when continued_from_job_name is specified.
    """

    model: str
    """The name of the model to use for inference.

    This is required, except when continued_from_job_name is specified.
    """

    output_dataset_id: Annotated[str, PropertyInfo(alias="outputDatasetId")]
    """The name of the dataset used for storing the results.

    This will also contain the error file.
    """

    precision: DeploymentPrecision
    """
    The precision with which the model should be served. If PRECISION_UNSPECIFIED, a
    default will be chosen based on the model.
    """
