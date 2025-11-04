# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, TypedDict

from .accounts.assertion_param import AssertionParam

__all__ = ["AccountValidateEvaluationAssertionsParams"]


class AccountValidateEvaluationAssertionsParams(TypedDict, total=False):
    assertions: Required[Iterable[AssertionParam]]
