"""Tests for the SDK-owned KL/DPO reference decision (single source of truth).

The shared-vs-separate-trainer choice for the reference model lives entirely in
``managed.py`` so every recipe and ``service.create_reference_client`` caller
gets the same behavior:

* LoRA policy without an explicit reference shape/job -> reuse the policy session.
* Full-parameter, an explicit ``reference_training_shape_id``, or an explicit
  ``reference_trainer_job_id`` -> a separate forward-only reference trainer.

These tests cover the decision predicate and the derived reference config; the
recipe-facing wrapper is tested in the cookbook suite.
"""

from __future__ import annotations

import threading
from types import SimpleNamespace

import fireworks.training.sdk.managed as managed_module
from fireworks.training.sdk.managed import (
    _ManagedTinkerConfig,
    _ManagedTinkerHandle,
    _reference_managed_config,
    _use_shared_base_reference,
)
from fireworks.training.sdk.trainer import CreatedTrainerJob, TrainerServiceEndpoint

BASE_MODEL = "accounts/acct/models/base"


def _policy_config(**overrides) -> _ManagedTinkerConfig:
    # _ManagedTinkerConfig is frozen, so build with overrides rather than setattr.
    fields = dict(
        base_model=BASE_MODEL,
        training_shape_id="ts-policy",
        region="US_OHIO_1",
        deployment_id="dep-1",
        trainer_job_id="policy-job",
        create_deployment=True,
    )
    fields.update(overrides)
    return _ManagedTinkerConfig(**fields)


class TestUseSharedBaseReference:
    """Only LoRA without an explicit reference shape reuses the policy session."""

    def test_lora_without_reference_shape_shares(self):
        config = _policy_config(reference_training_shape_id=None)
        assert _use_shared_base_reference(config, policy_lora_rank=16) is True

    def test_full_param_does_not_share(self):
        config = _policy_config(reference_training_shape_id=None)
        assert _use_shared_base_reference(config, policy_lora_rank=0) is False

    def test_explicit_reference_shape_disables_sharing_even_for_lora(self):
        config = _policy_config(reference_training_shape_id="ts-ref")
        assert _use_shared_base_reference(config, policy_lora_rank=16) is False

    def test_explicit_reference_job_disables_sharing_even_for_lora(self):
        config = _policy_config(reference_trainer_job_id="ref-job")
        assert _use_shared_base_reference(config, policy_lora_rank=16) is False


class TestReferenceManagedConfig:
    """The separate reference trainer is forward-only and deployment-free."""

    def test_full_param_uses_policy_shape_forward_only_base(self):
        config = _policy_config(reference_training_shape_id=None)
        reference = _reference_managed_config(config, policy_lora_rank=0)
        assert reference.training_shape_id == "ts-policy"
        assert reference.lora_rank == 0
        assert reference.forward_only is True
        assert reference.create_deployment is False
        assert reference.cleanup_trainer_on_close is True

    def test_fresh_trainer_and_no_deployment_reattach(self):
        # A fresh reference must never reattach the policy trainer or deployment.
        config = _policy_config(reference_training_shape_id="ts-ref")
        reference = _reference_managed_config(config, policy_lora_rank=0)
        assert reference.trainer_job_id is None
        assert reference.deployment_id is None

    def test_explicit_reference_job_reattaches_without_cleanup(self):
        config = _policy_config(reference_trainer_job_id="ref-job")
        reference = _reference_managed_config(config, policy_lora_rank=0)
        assert reference.trainer_job_id == "ref-job"
        assert reference.deployment_id is None
        assert reference.cleanup_trainer_on_close is False

    def test_fresh_reference_can_be_kept_for_later_reattach(self):
        config = _policy_config(cleanup_reference_trainer_on_close=False)
        reference = _reference_managed_config(config, policy_lora_rank=0)
        assert reference.trainer_job_id is None
        assert reference.cleanup_trainer_on_close is False

    def test_explicit_reference_shape_with_lora_loads_adapter(self):
        config = _policy_config(reference_training_shape_id="ts-ref")
        reference = _reference_managed_config(config, policy_lora_rank=16)
        assert reference.training_shape_id == "ts-ref"
        assert reference.lora_rank == 16

    def test_reference_inherits_policy_region(self):
        config = _policy_config(reference_training_shape_id="ts-ref")
        reference = _reference_managed_config(config, policy_lora_rank=0)
        assert reference.region == "US_OHIO_1"


class TestManagedProvisioning:
    def test_policy_reference_and_deployment_provision_in_parallel(self, monkeypatch):
        events: list[str] = []
        deployment_started = threading.Event()
        reference_started = threading.Event()

        class FakeTrainerManager:
            account_id = "acct"

            def resolve_training_profile(self, training_shape_id):
                events.append(f"resolve:{training_shape_id}")
                return SimpleNamespace(
                    training_shape_version="ts-policy/versions/v1",
                    deployment_shape="deployment-shape/versions/v1",
                    max_supported_context_length=32768,
                )

            def create(self, config):
                if config.forward_only:
                    events.append("reference_create")
                    reference_started.set()
                    return CreatedTrainerJob(
                        job_name="accounts/acct/rlorTrainerJobs/reference-job",
                        job_id="reference-job",
                    )
                events.append("policy_create")
                return CreatedTrainerJob(
                    job_name="accounts/acct/rlorTrainerJobs/policy-job",
                    job_id="policy-job",
                )

            def wait_for_ready(self, job_id, *, job_name, timeout_s):
                if job_id == "reference-job":
                    events.append("reference_wait")
                    return TrainerServiceEndpoint(
                        job_name=job_name,
                        job_id=job_id,
                        base_url="https://reference.test",
                    )

                events.append("policy_wait_start")
                if not deployment_started.wait(timeout=1):
                    raise AssertionError("deployment did not start while trainer was waiting")
                if not reference_started.wait(timeout=1):
                    raise AssertionError("reference did not start while trainer was waiting")
                events.append("policy_wait_done")
                return TrainerServiceEndpoint(
                    job_name=job_name,
                    job_id=job_id,
                    base_url="https://trainer.test",
                )

        class FakeTrainingClient:
            def _attach_sampler_backend(self, sampler_backend):
                events.append("training_attach_sampler")

        class FakeServiceClient:
            def __init__(self, *, base_url, api_key):
                events.append(f"service:{base_url}:{api_key}")

            def create_training_client(self, *, base_model, lora_rank, user_metadata):
                events.append(f"create_training_client:{base_model}:{lora_rank}")
                return FakeTrainingClient()

            def _attach_sampler_backend(self, sampler_backend):
                events.append("service_attach_sampler")

        def fake_build_resource_managers(**_kwargs):
            return FakeTrainerManager(), object()

        def fake_attach_deployment(
            _deploy_mgr,
            _config,
            *,
            trainer_job_name,
            deployment_shape,
        ):
            events.append(f"deployment_start:{trainer_job_name}:{deployment_shape}")
            deployment_started.set()
            return SimpleNamespace(deployment_id="deployment-1"), object()

        monkeypatch.setattr(
            managed_module,
            "_build_resource_managers",
            fake_build_resource_managers,
        )
        monkeypatch.setattr(
            managed_module,
            "_attach_managed_deployment",
            fake_attach_deployment,
        )
        monkeypatch.setattr(managed_module, "FiretitanServiceClient", FakeServiceClient)

        handle = managed_module._create_managed_tinker_client(
            api_key="fw-key",
            config=_policy_config(
                trainer_job_id=None,
                reference_training_shape_id="ts-reference",
                reference_required=True,
            ),
        )

        assert events.index("policy_wait_start") < events.index(
            "deployment_start:accounts/acct/rlorTrainerJobs/policy-job:deployment-shape/versions/v1"
        )
        assert events.index("policy_wait_start") < events.index("reference_create")
        assert events.index(
            "deployment_start:accounts/acct/rlorTrainerJobs/policy-job:deployment-shape/versions/v1"
        ) < events.index("policy_wait_done")
        assert events.index("reference_create") < events.index("policy_wait_done")
        assert handle.trainer_endpoint.job_id == "policy-job"
        assert handle.reference_handle.trainer_endpoint.job_id == "reference-job"
        assert handle.deployment.deployment_id == "deployment-1"


class TestManagedTinkerHandleCleanup:
    def test_close_stops_tinker_holder_before_deleting_trainer(self):
        events: list[str] = []

        class FakeFuture:
            def result(self, timeout=None):
                events.append(f"holder_cleanup_result:{timeout}")

        class FakeTelemetry:
            def _trigger_flush(self):
                events.append("telemetry_flush")

            def _wait_until_drained_sync(self):
                events.append("telemetry_drained")

            def stop(self):
                events.append("telemetry_stop")

        class FakeHolder:
            def get_telemetry(self):
                return FakeTelemetry()

            def _async_cleanup(self):
                events.append("holder_async_cleanup")
                return "cleanup-coro"

            def run_coroutine_threadsafe(self, coro):
                events.append(f"holder_run:{coro}")
                return FakeFuture()

        class FakeTrainerManager:
            def delete(self, job_id):
                events.append(f"delete:{job_id}")

        handle = _ManagedTinkerHandle(
            service_client=object(),
            training_client=type("FakeTrainingClient", (), {"holder": FakeHolder()})(),
            trainer_endpoint=type("FakeEndpoint", (), {"job_id": "ref-job"})(),
            trainer_manager=FakeTrainerManager(),
            cleanup_trainer_on_close=True,
        )

        handle.close()

        assert events == [
            "telemetry_flush",
            "telemetry_drained",
            "telemetry_stop",
            "holder_async_cleanup",
            "holder_run:cleanup-coro",
            "holder_cleanup_result:5.0",
            "delete:ref-job",
        ]
