# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from ...._models import BaseModel

__all__ = ["LedgerRetrieveResponse", "Ledger"]


class Ledger(BaseModel):
    timestamp: Optional[datetime] = None
    """The timestamp of the entry."""

    value: Optional[str] = None
    """The contents of the entry."""


class LedgerRetrieveResponse(BaseModel):
    ledger: Optional[List[Ledger]] = None
    """The contents of the ledger."""
