# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["TypeDateParam"]


class TypeDateParam(TypedDict, total=False):
    """
    * A full date, with non-zero year, month, and day values
    * A month and day value, with a zero year, such as an anniversary
    * A year on its own, with zero month and day values
    * A year and month value, with a zero day, such as a credit card expiration
    date

    Related types are [google.type.TimeOfDay][google.type.TimeOfDay] and
    `google.protobuf.Timestamp`.
    """

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
