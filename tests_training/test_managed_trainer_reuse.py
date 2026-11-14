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
        _ManagedTinkerConfig(
            base_model="accounts/fireworks/models/qwen3p5-9b",
            trainer_job_id="sft-job-1",
            use_reservation=True,
        ),
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


def test_create_managed_multi_model_handle_defers_create_model(monkeypatch):
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
            self.create_training_client = MagicMock()

        def _attach_sampler_backend(self, _backend):
            return self

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
            max_lora_rank=256,
            trainer_job_id="sft-job-1",
            create_deployment=False,
        ),
    )

    assert handle.training_client is None
    assert handle.training_clients == []
    handle.service_client.create_training_client.assert_not_called()


def _bare_training_client():
    """A FiretitanTrainingClient with __init__ bypassed for unit testing
    (same construction as tests_training/test_client.py's helper)."""
    from types import SimpleNamespace

    from fireworks.training.sdk._core import TrainingClient as CoreTrainingClient
    from fireworks.training.sdk.client import FiretitanTrainingClient

    client = FiretitanTrainingClient.__new__(FiretitanTrainingClient)
    CoreTrainingClient.__init__(client, SimpleNamespace(_client_config=None), 0, "model-test")
    client.routing_matrix_format, client.r3_store_id = "base64_inline", None
    client._http_admissions = {}
    client._http_admission_slots = None
    client._sampler_backend = None
    client._tokenizer_model = None
    client._lora_rank = 0
    client._sampler_checkpoint_saved = False
    client._first_sampler_checkpoint_type = "base"
    return client


def _drive_no_rpc_managed_client(monkeypatch, *, base_model: str, tokenizer_model: str):
    """Drive the managed no-RPC create branch (max_lora_rank is None) with the
    existing reuse-style fakes; returns handle.training_client (a real client)."""
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
            return _bare_training_client()

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
            base_model=base_model,
            trainer_job_id="sft-job-1",
            create_deployment=False,
            cleanup_trainer_on_close=True,
            tokenizer_model=tokenizer_model,
        ),
    )
    return handle.training_client


def test_no_rpc_managed_client_carries_base_model_for_tokenizer_gate(monkeypatch):
    """G4: the no-RPC managed branch must carry config.base_model onto the
    client, so get_tokenizer's family gate sees the independently selected
    model instead of falling back to artifact-only recognition.

    This is a context-carriage assertion, not an RCE claim: on the pinned
    Transformers the ungated default load ignores auto_map; what the gate
    restores is the explicit code-free contract pinned by the caller's model
    selection."""
    from unittest.mock import patch

    client = _drive_no_rpc_managed_client(
        monkeypatch,
        base_model="accounts/fireworks/models/deepseek-v4-flash-0731",
        tokenizer_model="acme/renamed-tokenizer",
    )
    assert client._tokenizer_model == "acme/renamed-tokenizer"
    assert getattr(client, "_tokenizer_base_model", None) == "accounts/fireworks/models/deepseek-v4-flash-0731"
    with patch("transformers.AutoTokenizer.from_pretrained", return_value="tok") as load:
        assert client.get_tokenizer() == "tok"
    load.assert_called_once_with("acme/renamed-tokenizer", trust_remote_code=False)


def test_no_rpc_managed_client_standard_family_forces_code_free_tokenizer_call(monkeypatch):
    """Independently selected standard-family context forces code-free loading."""
    from unittest.mock import patch

    client = _drive_no_rpc_managed_client(
        monkeypatch,
        base_model="accounts/fireworks/models/qwen3p5-9b",
        tokenizer_model="Qwen/Qwen3-8B",
    )
    with patch("transformers.AutoTokenizer.from_pretrained", return_value="tok") as load:
        assert client.get_tokenizer() == "tok"
    load.assert_called_once_with("Qwen/Qwen3-8B", trust_remote_code=False)
