from typing_extensions import Literal

from fireworks.training.sdk._core._models import BaseModel

__all__ = ["TryAgainResponse"]


class TryAgainResponse(BaseModel):
    type: Literal["try_again"] = "try_again"

    request_id: str
    """Request ID that is still pending"""

    queue_state: Literal["active", "paused_capacity", "paused_rate_limit"]
