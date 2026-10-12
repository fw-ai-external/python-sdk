"""Tests for SDK checkpoint reference resolution behavior."""

import pytest

from fireworks.training.sdk.client import FiretitanTrainingClient

CROSS_JOB_CHECKPOINT_REF_PREFIX = "cross_job://"


@pytest.mark.parametrize(
    "checkpoint_ref",
    [
        "gs://bucket/path/step-4",
        "  gs://bucket/path/step-4",
        "GS://bucket/path/step-4",
        "tinker://run/weights/step-4",
        "s3://bucket/path/step-4",
        "https://example.test/step-4",
        "/tmp/step-4",
        "../step-4",
        "phase-1/step-4",
        "cross_job://old-job/../../step-4",
        "cross_job://old-job/phase-1/step-4",
    ],
)
def test_resolve_checkpoint_path_rejects_non_schema_ref(checkpoint_ref: str) -> None:
    client = object.__new__(FiretitanTrainingClient)
    with pytest.raises(ValueError, match="checkpoint"):
        client.resolve_checkpoint_path(checkpoint_ref)


def test_resolve_checkpoint_path_returns_name_for_same_job():
    client = object.__new__(FiretitanTrainingClient)
    assert client.resolve_checkpoint_path("step-4") == "step-4"


def test_resolve_checkpoint_path_returns_serverless_cross_run_ref():
    client = object.__new__(FiretitanTrainingClient)
    checkpoint_ref = "account/run-0123456789abcdef0123456789abcdef/phase-1/step-4"
    assert client.resolve_checkpoint_path(checkpoint_ref) == checkpoint_ref


def test_resolve_checkpoint_path_returns_opaque_ref_for_cross_job():
    client = object.__new__(FiretitanTrainingClient)
    checkpoint_ref = client.resolve_checkpoint_path("step-4", source_job_id="old-job")
    assert checkpoint_ref == f"{CROSS_JOB_CHECKPOINT_REF_PREFIX}old-job/step-4"
