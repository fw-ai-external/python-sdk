# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["AccountValidateEvaluationAssertionsResponse", "MetricToErrors"]


class MetricToErrors(BaseModel):
    error_messages: Optional[List[str]] = FieldInfo(alias="errorMessages", default=None)


class AccountValidateEvaluationAssertionsResponse(BaseModel):
    metric_to_errors: Optional[Dict[str, MetricToErrors]] = FieldInfo(alias="metricToErrors", default=None)

    status: Optional[str] = None
