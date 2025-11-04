# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["TypeMoney"]


class TypeMoney(BaseModel):
    currency_code: Optional[str] = FieldInfo(alias="currencyCode", default=None)
    """The three-letter currency code defined in ISO 4217."""

    nanos: Optional[int] = None
    """
    Number of nano (10^-9) units of the amount. The value must be between
    -999,999,999 and +999,999,999 inclusive. If `units` is positive, `nanos` must be
    positive or zero. If `units` is zero, `nanos` can be positive, zero, or
    negative. If `units` is negative, `nanos` must be negative or zero. For example
    $-1.75 is represented as `units`=-1 and `nanos`=-750,000,000.
    """

    units: Optional[str] = None
    """
    The whole units of the amount. For example if `currencyCode` is `"USD"`, then 1
    unit is one US dollar.
    """
