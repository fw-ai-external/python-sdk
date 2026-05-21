from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["ReinforcementFineTuningStepResumeParams"]


class ReinforcementFineTuningStepResumeParams(TypedDict, total=False):
    account_id: str

    body: Required[object]
