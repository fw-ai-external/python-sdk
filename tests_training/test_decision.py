"""The SDK's decision models match the trainer's authoritative schema."""

from __future__ import annotations

import sys
import importlib.util
from pathlib import Path
from unittest.mock import patch

import pytest

# Monorepo checkout only; the published SDK has no trainer sources beside it.
_TRAINER_SCHEMA = next(
    (
        parent / "train-firetitan-py" / "firetitan" / "train" / "rlor" / "decision_artifact.py"
        for parent in Path(__file__).resolve().parents
        if (parent / "train-firetitan-py").is_dir()
    ),
    None,
)


def _wire(schema):
    """A JSON schema without prose, which the two copies word differently."""
    if isinstance(schema, dict):
        return {k: _wire(v) for k, v in schema.items() if k != "description"}
    if isinstance(schema, list):
        return [_wire(v) for v in schema]
    return schema


@pytest.mark.skipif(_TRAINER_SCHEMA is None, reason="trainer sources are not beside this SDK checkout")
@pytest.mark.parametrize("name", ["DecisionCalibration", "SamplerCheckpointMetadata"])
def test_sdk_decision_schema_matches_trainer(name: str) -> None:
    spec = importlib.util.spec_from_file_location("_trainer_decision_artifact", _TRAINER_SCHEMA)
    trainer = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {spec.name: trainer}):
        spec.loader.exec_module(trainer)
    sdk = importlib.import_module("fireworks.training.sdk.decision")

    assert _wire(getattr(sdk, name).model_json_schema()) == _wire(getattr(trainer, name).model_json_schema())
