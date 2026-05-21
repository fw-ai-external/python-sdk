from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["EvaluationResult"]


class EvaluationResult(BaseModel):
    evaluation_job_id: str = FieldInfo(alias="evaluationJobId")
