"""Tests for managed trainer reuse vs create-with-stable-id."""

from __future__ import annotations

from unittest.mock import MagicMock

from fireworks.training.sdk.managed import (
    _ManagedTinkerConfig,
    _start_or_reuse_trainer,
    _wait_for_started_trainer,
    _create_managed_tinker_client,
)
from fireworks.training.sdk.trainer import CreatedTrainerJob, TrainerJobManager, TrainerServiceEndpoint


def test_start_or_reuse_trainer_reuses_existing_job():
    trainer_mgr = MagicMock(spec=TrainerJobManager)
    trainer_mgr.account_id = "acct"
    trainer_mgr.try_get.return_value = {"state": "JOB_STATE_RUNNING"}

    started = _start_or_reuse_trainer(
        trainer_mgr,
        _ManagedTinkerConfig(base_model="accounts/fireworks/models/qwen3p5-9b", trainer_job_id="sft-job-1"),
        max_context_length=200_000,
        profile_training_shape="accounts/fireworks/trainingShapes/qwen3p5-9b/versions/1",
    )

    assert started.job == CreatedTrainerJob(
        job_name="accounts/acct/rlorTrainerJobs/sft-job-1",
        job_id="sft-job-1",
    )
    assert started.created is False
    trainer_mgr.create.assert_not_called()


def test_start_or_reuse_trainer_creates_when_stable_id_missing():
    trainer_mgr = MagicMock(spec=TrainerJobManager)
    trainer_mgr.account_id = "acct"
    trainer_mgr.try_get.return_value = None
    trainer_mgr.create.return_value = CreatedTrainerJob(
        job_name="accounts/acct/rlorTrainerJobs/sft-job-1",
        job_id="sft-job-1",
    )

    started = _start_or_reuse_trainer(
        trainer_mgr,
        _ManagedTinkerConfig(
            base_model="accounts/fireworks/models/qwen3p5-9b",
            trainer_job_id="sft-job-1",
            managed_by="parent-job",
        ),
        max_context_length=200_000,
        profile_training_shape="accounts/fireworks/trainingShapes/qwen3p5-9b/versions/1",
    )

    assert started.job.job_id == "sft-job-1"
    assert started.created is True
    trainer_mgr.create.assert_called_once()
    trainer_config = trainer_mgr.create.call_args.args[0]
    assert trainer_config.requested_job_id == "sft-job-1"
    assert trainer_config.managed_by == "parent-job"


def test_wait_for_started_trainer_resumes_failed_job():
    trainer_mgr = MagicMock(spec=TrainerJobManager)
    trainer_mgr.try_get.return_value = {"state": "JOB_STATE_FAILED"}
    trainer_mgr.resume_and_wait.return_value = TrainerServiceEndpoint(
        job_name="accounts/acct/rlorTrainerJobs/sft-job-1",
        job_id="sft-job-1",
        base_url="https://api.example.com/training/v1/rlorTrainerJobs/acct/sft-job-1",
    )

    endpoint = _wait_for_started_trainer(
        trainer_mgr,
        CreatedTrainerJob(
            job_name="accounts/acct/rlorTrainerJobs/sft-job-1",
            job_id="sft-job-1",
        ),
        _ManagedTinkerConfig(
            base_model="accounts/fireworks/models/qwen3p5-9b",
            trainer_pending_timeout_s=12345.0,
        ),
    )

    assert endpoint.job_id == "sft-job-1"
    trainer_mgr.resume_and_wait.assert_called_once_with(
        "sft-job-1",
        timeout_s=3600.0,
        pending_timeout_s=12345.0,
    )
    trainer_mgr.wait_for_ready.assert_not_called()


def test_create_managed_client_does_not_cleanup_reused_stable_trainer(monkeypatch):
    trainer_mgr = MagicMock(spec=TrainerJobManager)
    trainer_mgr.account_id = "acct"
    trainer_mgr.try_get.return_value = {"state": "JOB_STATE_RUNNING"}
    trainer_mgr.wait_for_ready.return_value = TrainerServiceEndpoint(
        job_name="accounts/acct/rlorTrainerJobs/sft-job-1",
        job_id="sft-job-1",
        base_url="https://api.example.com/training/v1/rlorTrainerJobs/acct/sft-job-1",
    )

    class FakeServiceClient:
        def __init__(self, **_kwargs):
            pass

        def create_training_client(self, **_kwargs):
            return type("FakeTrainingClient", (), {})()

    monkeypatch.setattr(
        "fireworks.training.sdk.managed._build_resource_managers",
        lambda **_kwargs: (trainer_mgr, object()),
    )
    monkeypatch.setattr(
        "fireworks.training.sdk.managed.FiretitanServiceClient",
        FakeServiceClient,
    )

    handle = _create_managed_tinker_client(
        api_key="fw-key",
        config=_ManagedTinkerConfig(
            base_model="accounts/fireworks/models/qwen3p5-9b",
            trainer_job_id="sft-job-1",
            create_deployment=False,
            cleanup_trainer_on_close=True,
        ),
    )

    assert handle.cleanup_trainer_on_close is False


def test_create_managed_client_cleans_created_stable_trainer(monkeypatch):
    trainer_mgr = MagicMock(spec=TrainerJobManager)
    trainer_mgr.account_id = "acct"
    trainer_mgr.try_get.return_value = None
    trainer_mgr.create.return_value = CreatedTrainerJob(
        job_name="accounts/acct/rlorTrainerJobs/sft-job-1",
        job_id="sft-job-1",
    )
    trainer_mgr.wait_for_ready.return_value = TrainerServiceEndpoint(
        job_name="accounts/acct/rlorTrainerJobs/sft-job-1",
        job_id="sft-job-1",
        base_url="https://api.example.com/training/v1/rlorTrainerJobs/acct/sft-job-1",
    )

    class FakeServiceClient:
        def __init__(self, **_kwargs):
            pass

        def create_training_client(self, **_kwargs):
            return type("FakeTrainingClient", (), {})()

    monkeypatch.setattr(
        "fireworks.training.sdk.managed._build_resource_managers",
        lambda **_kwargs: (trainer_mgr, object()),
    )
    monkeypatch.setattr(
        "fireworks.training.sdk.managed.FiretitanServiceClient",
        FakeServiceClient,
    )

    handle = _create_managed_tinker_client(
        api_key="fw-key",
        config=_ManagedTinkerConfig(
            base_model="accounts/fireworks/models/qwen3p5-9b",
            trainer_job_id="sft-job-1",
            create_deployment=False,
            cleanup_trainer_on_close=True,
        ),
    )

    assert handle.cleanup_trainer_on_close is True
