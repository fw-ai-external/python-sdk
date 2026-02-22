"""Tests for SDK checkpoint reference resolution behavior."""

from fireworks.training.sdk.client import FiretitanTrainingClient

CROSS_JOB_CHECKPOINT_REF_PREFIX = "cross_job://"


def test_resolve_checkpoint_path_keeps_full_paths_unchanged():
    client = object.__new__(FiretitanTrainingClient)
    full_path = "gs://bucket/path/step-4"
    assert client.resolve_checkpoint_path(full_path) == full_path


def test_resolve_checkpoint_path_returns_name_for_same_job():
    client = object.__new__(FiretitanTrainingClient)
    assert client.resolve_checkpoint_path("step-4") == "step-4"


def test_resolve_checkpoint_path_returns_opaque_ref_for_cross_job():
    client = object.__new__(FiretitanTrainingClient)
    checkpoint_ref = client.resolve_checkpoint_path("step-4", source_job_id="old-job")
    assert checkpoint_ref == f"{CROSS_JOB_CHECKPOINT_REF_PREFIX}old-job/step-4"
