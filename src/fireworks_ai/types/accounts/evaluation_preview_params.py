# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["EvaluationPreviewParams"]


class EvaluationPreviewParams(TypedDict, total=False):
    account_id: Required[str]

    sample_data: Required[Annotated[str, PropertyInfo(alias="sampleData")]]

    max_samples: Annotated[int, PropertyInfo(alias="maxSamples")]
