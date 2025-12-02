# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from .._utils import PropertyInfo
from .shared_params.inference_parameters import InferenceParameters

__all__ = ["BatchInferenceJobCreateParams"]


class BatchInferenceJobCreateParams(TypedDict, total=False):
    account_id: str

    batch_inference_job_id: Annotated[str, PropertyInfo(alias="batchInferenceJobId")]
    """ID of the batch inference job."""

    continued_from_job_name: Annotated[str, PropertyInfo(alias="continuedFromJobName")]
    """
    The resource name of the batch inference job that this job continues from. Used
    for lineage tracking to understand job continuation chains.
    """

    display_name: Annotated[str, PropertyInfo(alias="displayName")]

    inference_parameters: Annotated[InferenceParameters, PropertyInfo(alias="inferenceParameters")]
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

    precision: Literal[
        "PRECISION_UNSPECIFIED",
        "FP16",
        "FP8",
        "FP8_MM",
        "FP8_AR",
        "FP8_MM_KV_ATTN",
        "FP8_KV",
        "FP8_MM_V2",
        "FP8_V2",
        "FP8_MM_KV_ATTN_V2",
        "NF4",
        "FP4",
        "BF16",
        "FP4_BLOCKSCALED_MM",
        "FP4_MX_MOE",
    ]
    """
    The precision with which the model should be served. If PRECISION_UNSPECIFIED, a
    default will be chosen based on the model.
    """
