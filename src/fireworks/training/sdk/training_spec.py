"""Shared LR-scheduler schema for Firetitan cookbook training."""

from __future__ import annotations

import math
from typing import Any, Union, Literal, Iterable, Annotated
from typing_extensions import TypeAlias

from pydantic import Field, BaseModel, ConfigDict, TypeAdapter, model_validator

__all__ = [
    "StrictSpec",
    "ConstantSchedule",
    "LinearSchedule",
    "CosineSchedule",
    "WSDSchedule",
    "LRSchedulerSpec",
    "default_constant_schedule",
    "parse_lr_scheduler_spec",
    "normalize_lr_scheduler_spec",
    "compute_lr",
    "has_v1_scheduler_fields",
]


class StrictSpec(BaseModel):
    """Pydantic base that rejects unknown fields."""

    model_config = ConfigDict(extra="forbid")


def _validate_warmup_exclusive(values: dict[str, Any]) -> dict[str, Any]:
    steps = values.get("warmup_steps") or 0
    ratio = values.get("warmup_ratio")
    if steps and ratio is not None:
        raise ValueError(
            "warmup_steps and warmup_ratio are mutually exclusive; "
            f"got warmup_steps={steps} and warmup_ratio={ratio}."
        )
    return values


class _ScheduleBase(StrictSpec):
    warmup_steps: int = Field(0, ge=0)
    warmup_ratio: float | None = Field(
        None,
        ge=0.0,
        lt=1.0,
        description="Fraction of total steps to warm up; mutually exclusive with warmup_steps.",
    )

    @model_validator(mode="before")
    @classmethod
    def _check_warmup_exclusive(cls, data: Any) -> Any:
        if isinstance(data, dict):
            return _validate_warmup_exclusive(data)
        return data


class ConstantSchedule(_ScheduleBase):
    """Constant LR with optional warmup."""

    type: Literal["constant"] = "constant"


class LinearSchedule(_ScheduleBase):
    """Linear decay after warmup."""

    type: Literal["linear"] = "linear"
    decay_ratio: float | None = Field(None, ge=0.0, le=1.0)
    min_lr_ratio: float = Field(0.0, ge=0.0, le=1.0)


class CosineSchedule(_ScheduleBase):
    """Cosine decay after warmup."""

    type: Literal["cosine"] = "cosine"
    decay_ratio: float | None = Field(None, ge=0.0, le=1.0)
    min_lr_ratio: float = Field(0.0, ge=0.0, le=1.0)


class WSDSchedule(_ScheduleBase):
    """Warmup-Stable-Decay schedule."""

    type: Literal["wsd"] = "wsd"
    decay_ratio: float = Field(0.1, gt=0.0, le=1.0)
    decay_type: Literal["linear", "cosine", "sqrt"] = "linear"
    min_lr_ratio: float = Field(0.0, ge=0.0, le=1.0)


LRSchedulerSpec: TypeAlias = Annotated[
    Union[ConstantSchedule, LinearSchedule, CosineSchedule, WSDSchedule],
    Field(discriminator="type"),
]

_SCHEDULER_ADAPTER = TypeAdapter(LRSchedulerSpec)

_V1_SCHEDULER_FIELDS = {
    "lr_schedule",
    "lr_warmup_steps",
    "warmup_steps",
    "warmup_ratio",
    "min_lr_ratio",
}


def default_constant_schedule() -> ConstantSchedule:
    """Return a no-warmup constant schedule."""

    return ConstantSchedule()


def parse_lr_scheduler_spec(data: Any) -> LRSchedulerSpec:
    """Validate a raw scheduler payload into an LRSchedulerSpec variant."""

    return _SCHEDULER_ADAPTER.validate_python(data)


def normalize_lr_scheduler_spec(
    data: Any = None,
    *,
    legacy_lr_schedule: str | None = None,
    legacy_warmup_steps: int | None = None,
    legacy_warmup_ratio: float | None = None,
    legacy_min_lr_ratio: float | None = None,
) -> LRSchedulerSpec:
    """Return a scheduler spec from nested data plus optional legacy knobs.

    Nested ``data`` wins. Legacy fields are used only when callers have not
    provided a meaningful nested scheduler, preserving old recipe configs such
    as ``warmup_steps=10`` and ``lr_schedule="cosine"``.
    """

    if data is None:
        spec = default_constant_schedule()
    elif isinstance(data, dict):
        spec = parse_lr_scheduler_spec(data)
    else:
        spec = data

    has_legacy = bool(legacy_warmup_steps) or (
        legacy_warmup_ratio is not None and legacy_warmup_ratio > 0
    ) or (
        legacy_lr_schedule is not None and legacy_lr_schedule != "constant"
    ) or (
        legacy_min_lr_ratio is not None and legacy_min_lr_ratio > 0
    )
    if not has_legacy:
        return spec

    is_default_nested = (
        isinstance(spec, ConstantSchedule)
        and spec.warmup_steps == 0
        and spec.warmup_ratio is None
    )
    if data is not None and not is_default_nested:
        return spec

    schedule_type = legacy_lr_schedule or spec.type
    payload: dict[str, Any] = {"type": schedule_type}
    if legacy_warmup_steps:
        payload["warmup_steps"] = legacy_warmup_steps
    elif legacy_warmup_ratio is not None and legacy_warmup_ratio > 0:
        payload["warmup_ratio"] = legacy_warmup_ratio
    if schedule_type != "constant" and legacy_min_lr_ratio is not None:
        payload["min_lr_ratio"] = legacy_min_lr_ratio
    return parse_lr_scheduler_spec(payload)


def has_v1_scheduler_fields(flat: Iterable[str]) -> bool:
    """Return True if any legacy flat scheduler key is present."""

    return bool(_V1_SCHEDULER_FIELDS & set(flat))


def _resolve_warmup_steps(
    spec: LRSchedulerSpec,
    *,
    total_steps: int | None,
) -> int:
    if spec.warmup_steps:
        return int(spec.warmup_steps)
    if spec.warmup_ratio is not None:
        if total_steps is None or total_steps <= 0:
            raise ValueError(
                "warmup_ratio requires a positive total_steps; "
                f"got total_steps={total_steps}."
            )
        return max(0, int(round(spec.warmup_ratio * total_steps)))
    return 0


def compute_lr(
    spec: LRSchedulerSpec,
    step: int,
    base_lr: float,
    *,
    total_steps: int | None = None,
) -> float:
    """Return the learning rate for 1-indexed optimizer step ``step``."""

    warmup = _resolve_warmup_steps(spec, total_steps=total_steps)

    if warmup > 0 and step <= warmup:
        return base_lr * (step / warmup)

    if isinstance(spec, ConstantSchedule):
        return base_lr

    if total_steps is None or total_steps <= 0:
        raise ValueError(
            f"{type(spec).__name__} requires total_steps; got total_steps={total_steps}."
        )

    decay_ratio = getattr(spec, "decay_ratio", None)
    if decay_ratio is None:
        decay_start = warmup
        decay_end = total_steps
    else:
        decay_window = max(1, int(round(decay_ratio * total_steps)))
        decay_start = max(warmup, total_steps - decay_window)
        decay_end = total_steps

    if step <= decay_start:
        return base_lr

    min_ratio = float(getattr(spec, "min_lr_ratio", 0.0))
    if step >= decay_end:
        return base_lr * min_ratio

    progress = (step - decay_start) / max(1, decay_end - decay_start)

    if isinstance(spec, LinearSchedule):
        factor = 1.0 - progress * (1.0 - min_ratio)
        return base_lr * factor
    if isinstance(spec, CosineSchedule):
        cosine = 0.5 * (1.0 + math.cos(math.pi * progress))
        factor = min_ratio + (1.0 - min_ratio) * cosine
        return base_lr * factor
    if isinstance(spec, WSDSchedule):
        if spec.decay_type == "linear":
            factor = 1.0 - progress * (1.0 - min_ratio)
        elif spec.decay_type == "cosine":
            cosine = 0.5 * (1.0 + math.cos(math.pi * progress))
            factor = min_ratio + (1.0 - min_ratio) * cosine
        elif spec.decay_type == "sqrt":
            factor = max(min_ratio, 1.0 - math.sqrt(progress) * (1.0 - min_ratio))
        else:  # pragma: no cover - guarded by Literal validation
            raise ValueError(f"unknown WSD decay_type: {spec.decay_type}")
        return base_lr * factor

    raise TypeError(f"Unsupported LRSchedulerSpec variant: {type(spec).__name__}")
