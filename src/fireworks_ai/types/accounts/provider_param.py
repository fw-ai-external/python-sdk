# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import TypedDict

__all__ = ["ProviderParam"]


class ProviderParam(TypedDict, total=False):
    id: str

    config: Dict[str, str]

    label: str
