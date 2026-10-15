from typing_extensions import Literal

from fireworks.training.sdk._core._models import BaseModel

__all__ = ["TelemetryResponse"]


class TelemetryResponse(BaseModel):
    status: Literal["accepted"]
