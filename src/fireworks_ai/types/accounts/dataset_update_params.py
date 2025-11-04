# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo
from .dataset_format import DatasetFormat
from .gateway_splitted_param import GatewaySplittedParam
from .gateway_transformed_param import GatewayTransformedParam
from .gateway_evaluation_result_param import GatewayEvaluationResultParam

__all__ = ["DatasetUpdateParams"]


class DatasetUpdateParams(TypedDict, total=False):
    account_id: Required[str]

    display_name: Annotated[str, PropertyInfo(alias="displayName")]

    eval_protocol: Annotated[object, PropertyInfo(alias="evalProtocol")]

    evaluation_result: Annotated[GatewayEvaluationResultParam, PropertyInfo(alias="evaluationResult")]

    example_count: Annotated[str, PropertyInfo(alias="exampleCount")]

    external_url: Annotated[str, PropertyInfo(alias="externalUrl")]

    format: DatasetFormat

    source_job_name: Annotated[str, PropertyInfo(alias="sourceJobName")]
    """
    The resource name of the job that created this dataset (e.g., batch inference
    job). Used for lineage tracking to understand dataset provenance.
    """

    splitted: GatewaySplittedParam

    transformed: GatewayTransformedParam

    user_uploaded: Annotated[object, PropertyInfo(alias="userUploaded")]
