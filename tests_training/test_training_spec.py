from __future__ import annotations

import pytest

from fireworks.training.sdk.training_spec import (
    CosineSchedule,
    LinearSchedule,
    ConstantSchedule,
    compute_lr,
    parse_lr_scheduler_spec,
    normalize_lr_scheduler_spec,
)


def test_constant_schedule_warmup() -> None:
    sched = ConstantSchedule(warmup_steps=4)

    assert compute_lr(sched, step=1, base_lr=1e-4) == pytest.approx(2.5e-5)
    assert compute_lr(sched, step=4, base_lr=1e-4) == pytest.approx(1e-4)
    assert compute_lr(sched, step=5, base_lr=1e-4) == pytest.approx(1e-4)


def test_cosine_schedule_decays_to_min_ratio() -> None:
    sched = CosineSchedule(warmup_steps=2, min_lr_ratio=0.1)

    assert compute_lr(sched, step=1, base_lr=1.0, total_steps=10) == pytest.approx(0.5)
    assert compute_lr(sched, step=2, base_lr=1.0, total_steps=10) == pytest.approx(1.0)
    assert compute_lr(sched, step=10, base_lr=1.0, total_steps=10) == pytest.approx(0.1)


def test_linear_schedule_requires_total_steps() -> None:
    with pytest.raises(ValueError, match="requires total_steps"):
        compute_lr(LinearSchedule(), step=1, base_lr=1.0)


def test_parse_rejects_constant_min_lr_ratio() -> None:
    with pytest.raises(ValueError):
        parse_lr_scheduler_spec({
            "type": "constant",
            "min_lr_ratio": 0.1,
        })


def test_normalize_legacy_cosine_fields() -> None:
    sched = normalize_lr_scheduler_spec(
        legacy_lr_schedule="cosine",
        legacy_warmup_ratio=0.2,
        legacy_min_lr_ratio=0.1,
    )

    assert isinstance(sched, CosineSchedule)
    assert sched.warmup_ratio == pytest.approx(0.2)
    assert sched.min_lr_ratio == pytest.approx(0.1)
