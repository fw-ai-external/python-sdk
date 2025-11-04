# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .evaluation import Evaluation

__all__ = ["EvaluationListResponse"]


class EvaluationListResponse(BaseModel):
    evaluations: Optional[List[Evaluation]] = None

    next_page_token: Optional[str] = FieldInfo(alias="nextPageToken", default=None)

    total_size: Optional[int] = FieldInfo(alias="totalSize", default=None)
