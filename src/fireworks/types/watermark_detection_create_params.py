# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Required, TypedDict

__all__ = ["WatermarkDetectionCreateParams"]


class WatermarkDetectionCreateParams(TypedDict, total=False):
    text: Required[str]
