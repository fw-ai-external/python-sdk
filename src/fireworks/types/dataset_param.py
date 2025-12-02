# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from .._utils import PropertyInfo
from .splitted_param import SplittedParam
from .transformed_param import TransformedParam
from .evaluation_result_param import EvaluationResultParam

__all__ = ["DatasetParam"]


class DatasetParam(TypedDict, total=False):
    display_name: Annotated[str, PropertyInfo(alias="displayName")]

    eval_protocol: Annotated[object, PropertyInfo(alias="evalProtocol")]

    evaluation_result: Annotated[EvaluationResultParam, PropertyInfo(alias="evaluationResult")]

    example_count: Annotated[str, PropertyInfo(alias="exampleCount")]

    external_url: Annotated[str, PropertyInfo(alias="externalUrl")]

    format: Literal["FORMAT_UNSPECIFIED", "CHAT", "COMPLETION", "RL"]

    source_job_name: Annotated[str, PropertyInfo(alias="sourceJobName")]
    """
    The resource name of the job that created this dataset (e.g., batch inference
    job). Used for lineage tracking to understand dataset provenance.
    """

    splitted: SplittedParam

    transformed: TransformedParam

    user_uploaded: Annotated[object, PropertyInfo(alias="userUploaded")]
