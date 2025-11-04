# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo
from .provider_param import ProviderParam
from .assertion_param import AssertionParam

__all__ = ["EvaluationParam"]


class EvaluationParam(TypedDict, total=False):
    assertions: Required[Iterable[AssertionParam]]

    evaluation_type: Required[Annotated[str, PropertyInfo(alias="evaluationType")]]

    providers: Required[Iterable[ProviderParam]]

    description: str
