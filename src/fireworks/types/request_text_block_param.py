# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .cache_control_ephemeral_param import CacheControlEphemeralParam
from .request_char_location_citation_param import RequestCharLocationCitationParam
from .request_page_location_citation_param import RequestPageLocationCitationParam
from .request_content_block_location_citation_param import RequestContentBlockLocationCitationParam
from .request_search_result_location_citation_param import RequestSearchResultLocationCitationParam
from .request_web_search_result_location_citation_param import RequestWebSearchResultLocationCitationParam

__all__ = ["RequestTextBlockParam", "Citation"]

Citation: TypeAlias = Union[
    RequestCharLocationCitationParam,
    RequestPageLocationCitationParam,
    RequestContentBlockLocationCitationParam,
    RequestWebSearchResultLocationCitationParam,
    RequestSearchResultLocationCitationParam,
]


class RequestTextBlockParam(TypedDict, total=False):
    text: Required[str]

    type: Required[Literal["text"]]

    cache_control: Optional[CacheControlEphemeralParam]
    """Create a cache control breakpoint at this content block."""

    citations: Optional[Iterable[Citation]]
