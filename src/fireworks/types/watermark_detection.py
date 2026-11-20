# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["WatermarkDetection"]


class WatermarkDetection(BaseModel):
    id: str
    object: Literal["watermark.detection"]
    detector_version: str
    result: Literal["detected", "not_detected", "uncertain"]
    scored_tokens: int
    """Token positions that contributed to the decision.

    When the text is evaluated more than one way, this is the smallest such count.
    0 when nothing could be scored.
    """
