# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .type_money import TypeMoney

__all__ = ["BillingGetSummaryResponse", "LineItem"]


class LineItem(BaseModel):
    category: Optional[str] = None

    grouping_key: Optional[str] = FieldInfo(alias="groupingKey", default=None)

    grouping_value: Optional[str] = FieldInfo(alias="groupingValue", default=None)

    quantity: Optional[float] = None

    secondary_grouping_key: Optional[str] = FieldInfo(alias="secondaryGroupingKey", default=None)

    secondary_grouping_value: Optional[str] = FieldInfo(alias="secondaryGroupingValue", default=None)

    total_cost: Optional[TypeMoney] = FieldInfo(alias="totalCost", default=None)
    """Represents an amount of money with its currency type."""

    unit_amount: Optional[TypeMoney] = FieldInfo(alias="unitAmount", default=None)
    """Represents an amount of money with its currency type."""


class BillingGetSummaryResponse(BaseModel):
    line_items: Optional[List[LineItem]] = FieldInfo(alias="lineItems", default=None)
