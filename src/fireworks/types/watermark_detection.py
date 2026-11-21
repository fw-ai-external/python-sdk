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
    """Token positions scored under the tokenizer that decided the result.

    When no tokenizer could score enough of the text, this is the largest count
    any tokenizer reached, and 0 when none could score it.
    """
