# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from .._utils import PropertyInfo
from .placement_param import PlacementParam

__all__ = ["BatchInferenceJobCreateParams", "InferenceParameters"]


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

    max_job_duration: Annotated[str, PropertyInfo(alias="maxJobDuration")]
    """
    The customer-requested wall-clock run window for the job: how long it may run
    before it is expired. This is the single public input that controls the job's
    lifetime. The server bounds it to [12h, 72h]; if unset it defaults to 24h. The
    resulting concrete deadline is surfaced as expire_time (= create_time + the
    bounded window) and the job is expired once that deadline passes. A duration
    (relative) is used rather than an absolute timestamp because the client does not
    know create_time at submit time. Customer-visible input.
    """

    model: str
    """The name of the model to use for inference.

    This is required, except when continued_from_job_name is specified.
    """

    output_dataset_id: Annotated[str, PropertyInfo(alias="outputDatasetId")]
    """The name of the dataset used for storing the results.

    This will also contain the error file.
    """

    placement: PlacementParam
    """
    The desired geographic region where the batch inference job runs. Set
    `multi_region` to limit the job to a region group (US, EUROPE, APAC, or GLOBAL).
    If unspecified, the job runs in any supported region.
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

    system_prompt: Annotated[str, PropertyInfo(alias="systemPrompt")]
    """Optional job-level system prompt.

    When set, it is injected as a leading system message into every input row that
    does NOT already begin with a system message (a row's own leading system message
    takes precedence). This lets callers avoid repeating a large, static system
    prompt on every row of the input dataset, shrinking the upload. Because the
    injected prefix is byte-identical across rows, prompt caching still applies.
    """


class InferenceParameters(TypedDict, total=False):
    """Parameters controlling the inference process."""

    extra_body: Annotated[str, PropertyInfo(alias="extraBody")]
    """
    Additional parameters for the inference request as a JSON string. For example:
    "{\"stop\": [\"\\n\"]}".
    """

    max_tokens: Annotated[int, PropertyInfo(alias="maxTokens")]
    """Maximum number of tokens to generate per response."""

    n: int
    """Number of response candidates to generate per input."""

    temperature: float
    """Sampling temperature, typically between 0 and 2."""

    top_k: Annotated[int, PropertyInfo(alias="topK")]
    """Top-k sampling parameter, limits the token selection to the top k tokens."""

    top_p: Annotated[float, PropertyInfo(alias="topP")]
    """Top-p sampling parameter, typically between 0 and 1."""
