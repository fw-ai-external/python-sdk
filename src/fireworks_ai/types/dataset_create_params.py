# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["DatasetCreateParams", "Dataset", "DatasetEvaluationResult", "DatasetSplitted", "DatasetTransformed"]


class DatasetCreateParams(TypedDict, total=False):
    dataset: Required[Dataset]

    dataset_id: Required[Annotated[str, PropertyInfo(alias="datasetId")]]

    filter: str

    source_dataset_id: Annotated[str, PropertyInfo(alias="sourceDatasetId")]


class DatasetEvaluationResult(TypedDict, total=False):
    evaluation_job_id: Required[Annotated[str, PropertyInfo(alias="evaluationJobId")]]


class DatasetSplitted(TypedDict, total=False):
    source_dataset_id: Required[Annotated[str, PropertyInfo(alias="sourceDatasetId")]]


class DatasetTransformed(TypedDict, total=False):
    source_dataset_id: Required[Annotated[str, PropertyInfo(alias="sourceDatasetId")]]

    filter: str

    original_format: Annotated[
        Literal["FORMAT_UNSPECIFIED", "CHAT", "COMPLETION", "RL"], PropertyInfo(alias="originalFormat")
    ]


class Dataset(TypedDict, total=False):
    display_name: Annotated[str, PropertyInfo(alias="displayName")]

    eval_protocol: Annotated[object, PropertyInfo(alias="evalProtocol")]

    evaluation_result: Annotated[DatasetEvaluationResult, PropertyInfo(alias="evaluationResult")]

    example_count: Annotated[str, PropertyInfo(alias="exampleCount")]

    external_url: Annotated[str, PropertyInfo(alias="externalUrl")]

    format: Literal["FORMAT_UNSPECIFIED", "CHAT", "COMPLETION", "RL"]

    source_job_name: Annotated[str, PropertyInfo(alias="sourceJobName")]
    """
    The resource name of the job that created this dataset (e.g., batch inference
    job). Used for lineage tracking to understand dataset provenance.
    """

    splitted: DatasetSplitted

    transformed: DatasetTransformed

    user_uploaded: Annotated[object, PropertyInfo(alias="userUploaded")]
