# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["WatermarkDetection"]


class WatermarkDetection(BaseModel):
    object: Literal["watermark.detection"]

    result: Literal["detected", "not_detected"]
    """
    `detected` when the Fireworks watermark was found; otherwise `not_detected`,
    including text too short to score. Text watermarked before the last key
    rotation is scored like unwatermarked text. `not_detected` does not prove
    human authorship.
    """
