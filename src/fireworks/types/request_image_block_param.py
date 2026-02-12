# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from .._types import Base64FileInput
from .._utils import PropertyInfo
from .._models import set_pydantic_config
from .cache_control_ephemeral_param import CacheControlEphemeralParam

__all__ = ["RequestImageBlockParam", "Source", "SourceAnthropicBase64ImageSource", "SourceAnthropicURLImageSource"]


class SourceAnthropicBase64ImageSource(TypedDict, total=False):
    data: Required[Annotated[Union[str, Base64FileInput], PropertyInfo(format="base64")]]

    media_type: Required[Literal["image/jpeg", "image/png", "image/gif", "image/webp"]]

    type: Required[Literal["base64"]]


set_pydantic_config(SourceAnthropicBase64ImageSource, {"arbitrary_types_allowed": True})


class SourceAnthropicURLImageSource(TypedDict, total=False):
    type: Required[Literal["url"]]

    url: Required[str]


Source: TypeAlias = Union[SourceAnthropicBase64ImageSource, SourceAnthropicURLImageSource]


class RequestImageBlockParam(TypedDict, total=False):
    source: Required[Source]

    type: Required[Literal["image"]]

    cache_control: Optional[CacheControlEphemeralParam]
    """Create a cache control breakpoint at this content block."""
