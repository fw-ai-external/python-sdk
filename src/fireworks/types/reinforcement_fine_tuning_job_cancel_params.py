from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["ReinforcementFineTuningJobCancelParams"]


class ReinforcementFineTuningJobCancelParams(TypedDict, total=False):
    account_id: str

    body: Required[object]
