# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from .._utils import PropertyInfo
from .._models import BaseModel
from .response_char_location_citation import ResponseCharLocationCitation
from .response_page_location_citation import ResponsePageLocationCitation
from .response_content_block_location_citation import ResponseContentBlockLocationCitation
from .response_search_result_location_citation import ResponseSearchResultLocationCitation
from .response_web_search_result_location_citation import ResponseWebSearchResultLocationCitation

__all__ = ["ResponseTextBlock", "Citation"]

Citation: TypeAlias = Annotated[
    Union[
        ResponseCharLocationCitation,
        ResponsePageLocationCitation,
        ResponseContentBlockLocationCitation,
        ResponseWebSearchResultLocationCitation,
        ResponseSearchResultLocationCitation,
    ],
    PropertyInfo(discriminator="type"),
]


class ResponseTextBlock(BaseModel):
    citations: Optional[List[Citation]] = None
    """Citations supporting the text block.

    The type of citation returned will depend on the type of document being cited.
    Citing a PDF results in `page_location`, plain text results in `char_location`,
    and content document results in `content_block_location`.
    """

    text: str

    type: Literal["text"]
