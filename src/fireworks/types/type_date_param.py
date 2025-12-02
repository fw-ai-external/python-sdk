# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["TypeDateParam"]


class TypeDateParam(TypedDict, total=False):
    day: int
    """Day of a month.

    Must be from 1 to 31 and valid for the year and month, or 0 to specify a year by
    itself or a year and month where the day isn't significant.
    """

    month: int
    """Month of a year.

    Must be from 1 to 12, or 0 to specify a year without a month and day.
    """

    year: int
    """Year of the date.

    Must be from 1 to 9999, or 0 to specify a date without a year.
    """
