"""Tests for the SDK-owned KL/DPO reference decision (single source of truth).

The shared-vs-separate-trainer choice for the reference model lives entirely in
``managed.py`` so every recipe and ``service.create_reference_client`` caller
gets the same behavior:

* LoRA policy without an explicit reference shape/job -> reuse the policy session.
* Full-parameter references use a separate forward-only runtime trainer. When
  no ``reference_training_shape_id`` is pinned, trainer creation asks the
  backend to auto-select a ``LORA_TRAINER`` shape.

These tests cover the decision predicate and the derived reference config; the
recipe-facing wrapper is tested in the cookbook suite.
"""

from __future__ import annotations

import threading
from types import SimpleNamespace
from datetime import timedelta

import pytest

import fireworks.training.sdk.managed as managed_module
from fireworks.training.sdk.managed import (
    _ManagedTinkerConfig,
    _ManagedTinkerHandle,
    _reference_managed_config,
    _use_shared_base_reference,
    _validate_reference_training_shape,
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
    """The separate reference trainer is forward-only at runtime and deployment-free."""

    def test_full_param_without_reference_shape_uses_backend_auto_selection(self):
        config = _policy_config(reference_training_shape_id=None)
        reference = _reference_managed_config(config, policy_lora_rank=0)
        assert reference.training_shape_id is None
        assert reference.trainer_job_id is None
        assert reference.forward_only is True
        assert reference.lora_rank == 0
        assert reference.create_deployment is False

    def test_fresh_trainer_and_no_deployment_reattach(self):
        # A fresh reference must never reattach the policy trainer or deployment.
        config = _policy_config(reference_training_shape_id="ts-ref")
        reference = _reference_managed_config(config, policy_lora_rank=0)
        assert reference.trainer_job_id is None
        assert reference.deployment_id is None

    def test_explicit_reference_job_carries_cleanup_policy_to_handle(self):
        config = _policy_config(reference_trainer_job_id="ref-job")
        reference = _reference_managed_config(config, policy_lora_rank=0)
        assert reference.training_shape_id is None
        assert reference.trainer_job_id == "ref-job"
        assert reference.deployment_id is None
        assert reference.cleanup_trainer_on_close is True

    def test_fresh_reference_can_be_kept_for_later_reattach(self):
        config = _policy_config(
            reference_training_shape_id="ts-ref",
            cleanup_reference_trainer_on_close=False,
        )
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

    def test_reference_drops_policy_hsdp_replicas(self):
        # HSDP replicas are a policy-trainer knob. A frozen reference is
        # single-replica on its own shape and must never inherit the policy
        # trainer_replica_count (would mis-size + launch a replicated ref).
        config = _policy_config(
            reference_training_shape_id="ts-ref",
            trainer_replica_count=2,
        )
        reference = _reference_managed_config(config, policy_lora_rank=0)
        assert reference.trainer_replica_count is None


class TestManagedProvisioning:
    def test_trainer_create_keeps_region_unset_when_user_does_not_set_it(self):
        created_configs = []

        class FakeTrainerManager:
            account_id = "acct"

            def create(self, trainer_config):
                created_configs.append(trainer_config)
                return CreatedTrainerJob(
                    job_name="accounts/acct/rlorTrainerJobs/policy-job",
                    job_id="policy-job",
                )

        result = managed_module._start_or_reuse_trainer(
            FakeTrainerManager(),
            _policy_config(region=None, trainer_job_id=None),
            max_context_length=32768,
            profile_training_shape="accounts/fireworks/trainingShapes/shape/versions/v1",
        )

        assert result.job.job_id == "policy-job"
        assert result.created is True
        assert len(created_configs) == 1
        assert created_configs[0].region is None
        assert created_configs[0].training_shape_ref == "accounts/fireworks/trainingShapes/shape/versions/v1"

    def test_trainer_create_passes_explicit_region_through(self):
        created_configs = []

        class FakeTrainerManager:
            account_id = "acct"

            def create(self, trainer_config):
                created_configs.append(trainer_config)
                return CreatedTrainerJob(
                    job_name="accounts/acct/rlorTrainerJobs/policy-job",
                    job_id="policy-job",
                )

        managed_module._start_or_reuse_trainer(
            FakeTrainerManager(),
            _policy_config(region="US_OHIO_1", trainer_job_id=None),
            max_context_length=32768,
            profile_training_shape="accounts/fireworks/trainingShapes/shape/versions/v1",
        )

        assert len(created_configs) == 1
        assert created_configs[0].region == "US_OHIO_1"

    def test_extra_args_keep_auto_shape_selection(self):
        # extra_args are runtime training flags forwarded on the auto-shape
        # payload; they must not flip the job onto the manual path (which would
        # send skipValidations=true and 400 for non-superuser keys).
        trainer_config = managed_module._build_trainer_job_config(
            _policy_config(
                training_shape_id=None,
                extra_args=["--pp", "2"],
            ),
            max_context_length=32768,
            profile_training_shape=None,
        )

        assert trainer_config.training_shape_ref is None
        assert trainer_config.auto_select_training_shape is True
        assert trainer_config.extra_args == ["--pp", "2"]

    def test_empty_extra_args_keep_auto_shape_selection(self):
        trainer_config = managed_module._build_trainer_job_config(
            _policy_config(
                training_shape_id=None,
                extra_args=[],
            ),
            max_context_length=32768,
            profile_training_shape=None,
        )

        assert trainer_config.training_shape_ref is None
        assert trainer_config.auto_select_training_shape is True
        assert trainer_config.extra_args == []

    def test_skip_validations_keep_auto_shape_selection(self):
        trainer_config = managed_module._build_trainer_job_config(
            _policy_config(
                training_shape_id=None,
                skip_validations=True,
            ),
            max_context_length=32768,
            profile_training_shape=None,
        )

        assert trainer_config.training_shape_ref is None
        assert trainer_config.auto_select_training_shape is True
        assert trainer_config.skip_validations is True

    def test_custom_image_tag_keeps_auto_shape_selection(self):
        trainer_config = managed_module._build_trainer_job_config(
            _policy_config(
                training_shape_id=None,
                custom_image_tag="0.33.0",
            ),
            max_context_length=32768,
            profile_training_shape=None,
        )

        assert trainer_config.training_shape_ref is None
        assert trainer_config.auto_select_training_shape is True
        assert trainer_config.custom_image_tag == "0.33.0"

    def test_inactivity_cleanup_fields_flow_to_trainer_config(self):
        trainer_config = managed_module._build_trainer_job_config(
            _policy_config(
                inactivity_timeout=timedelta(hours=2),
                disable_inactivity_cleanup=True,
            ),
            max_context_length=32768,
            profile_training_shape="accounts/fireworks/trainingShapes/shape/versions/v1",
        )

        assert trainer_config.inactivity_timeout == timedelta(hours=2)
        assert trainer_config.disable_inactivity_cleanup is True

    def test_generated_trainer_job_id_is_stored_for_retry(self, monkeypatch):
        created_configs = []
        config = _policy_config(trainer_job_id=None)
        monkeypatch.setattr(managed_module, "_new_trainer_job_id", lambda: "trn-auto")

        class FirstTrainerManager:
            account_id = "acct"

            def create(self, trainer_config):
                created_configs.append(trainer_config)
                return CreatedTrainerJob(
                    job_name="accounts/acct/rlorTrainerJobs/trn-auto",
                    job_id="trn-auto",
                )

        first = managed_module._start_or_reuse_trainer(
            FirstTrainerManager(),
            config,
            max_context_length=32768,
            profile_training_shape="accounts/fireworks/trainingShapes/shape/versions/v1",
        )

        assert first.job.job_id == "trn-auto"
        assert config.trainer_job_id == "trn-auto"
        assert created_configs[0].requested_job_id == "trn-auto"

        class RetryTrainerManager:
            account_id = "acct"

            def try_get(self, job_id):
                assert job_id == "trn-auto"
                return {"state": "JOB_STATE_RUNNING"}

            def create(self, _trainer_config):
                raise AssertionError("retry should reuse the stored trainer id")

        retry = managed_module._start_or_reuse_trainer(
            RetryTrainerManager(),
            config,
            max_context_length=32768,
            profile_training_shape="accounts/fireworks/trainingShapes/shape/versions/v1",
        )

        assert retry.job.job_id == "trn-auto"
        assert retry.created is False

    def test_deployment_create_does_not_get_deployment_shape_for_region(self):
        events: list[str] = []
        created_configs = []

        class FakeDeployManager:
            def get(self, deployment_id):
                events.append(f"get_deployment:{deployment_id}")
                return None

            def _get(self, path, **_kwargs):
                raise AssertionError(f"unexpected deployment-shape GET: {path}")

            def create_or_get(self, deployment_config):
                events.append("create_or_get")
                created_configs.append(deployment_config)
                return SimpleNamespace(deployment_id=deployment_config.deployment_id, state="READY")

        result = managed_module._create_or_reattach_deployment_result(
            FakeDeployManager(),
            _policy_config(region=None),
            trainer_job_name="accounts/acct/rlorTrainerJobs/policy-job",
            deployment_shape="accounts/fireworks/deploymentShapes/private/versions/v1",
        )

        assert result.deployment.deployment_id == "dep-1"
        assert events == ["get_deployment:dep-1", "create_or_get"]
        assert len(created_configs) == 1
        assert created_configs[0].deployment_shape == "accounts/fireworks/deploymentShapes/private/versions/v1"
        assert created_configs[0].region is None

    def test_deployment_create_passes_explicit_region_through(self):
        created_configs = []

        class FakeDeployManager:
            def get(self, deployment_id):
                return None

            def _get(self, path, **_kwargs):
                raise AssertionError(f"unexpected deployment-shape GET: {path}")

            def create_or_get(self, deployment_config):
                created_configs.append(deployment_config)
                return SimpleNamespace(deployment_id=deployment_config.deployment_id, state="READY")

        managed_module._create_or_reattach_deployment_result(
            FakeDeployManager(),
            _policy_config(region="US_OHIO_1"),
            trainer_job_name="accounts/acct/rlorTrainerJobs/policy-job",
            deployment_shape="accounts/fireworks/deploymentShapes/private/versions/v1",
        )

        assert len(created_configs) == 1
        assert created_configs[0].region == "US_OHIO_1"

    def test_policy_reference_and_deployment_provision_in_parallel(self, monkeypatch):
        events: list[str] = []
        deployment_started = threading.Event()
        reference_started = threading.Event()

        class FakeTrainerManager:
            account_id = "acct"

            def resolve_training_profile(self, training_shape_id):
                events.append(f"resolve:{training_shape_id}")
                trainer_mode = "LORA_TRAINER" if training_shape_id == "ts-reference" else "POLICY_TRAINER"
                return SimpleNamespace(
                    training_shape_version=f"{training_shape_id}/versions/v1",
                    deployment_shape="deployment-shape/versions/v1",
                    max_supported_context_length=32768,
                    trainer_mode=trainer_mode,
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

            def try_get(self, job_id):
                return None

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
            return SimpleNamespace(deployment_id="deployment-1"), object(), False, True

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

    def test_full_param_reference_without_shape_auto_selects_at_trainer_create(self):
        reference = _reference_managed_config(
            _policy_config(reference_training_shape_id=None),
            policy_lora_rank=0,
        )

        trainer_config = managed_module._build_trainer_job_config(
            reference,
            max_context_length=32768,
            profile_training_shape=None,
        )

        assert trainer_config.training_shape_ref is None
        assert trainer_config.auto_select_training_shape is True
        assert trainer_config.forward_only is True
        assert trainer_config.max_context_length == 32768
        assert trainer_config.node_count is None
        assert trainer_config.accelerator_type is None
        assert trainer_config.accelerator_count is None

    def test_legacy_node_count_default_does_not_disable_auto_shape_selection(self):
        with pytest.warns(DeprecationWarning, match="node_count"):
            config = _ManagedTinkerConfig(
                base_model=BASE_MODEL,
                node_count=1,
            )

        trainer_config = managed_module._build_trainer_job_config(
            config,
            max_context_length=32768,
            profile_training_shape=None,
        )

        assert config.node_count is None
        assert trainer_config.training_shape_ref is None
        assert trainer_config.auto_select_training_shape is True
        assert trainer_config.node_count is None
        assert trainer_config.accelerator_type is None
        assert trainer_config.accelerator_count is None

    def test_stale_node_count_on_config_does_not_disable_auto_shape_selection(self):
        config = _ManagedTinkerConfig(base_model=BASE_MODEL)
        object.__setattr__(config, "node_count", 1)

        trainer_config = managed_module._build_trainer_job_config(
            config,
            max_context_length=32768,
            profile_training_shape=None,
        )

        assert trainer_config.training_shape_ref is None
        assert trainer_config.auto_select_training_shape is True
        assert trainer_config.node_count is None
        assert trainer_config.accelerator_type is None
        assert trainer_config.accelerator_count is None

    def test_auto_shape_resolved_max_context_flows_to_handle(self, monkeypatch):
        class FakeTrainerManager:
            account_id = "acct"

            def create(self, trainer_config):
                assert trainer_config.training_shape_ref is None
                assert trainer_config.auto_select_training_shape is True
                assert trainer_config.max_context_length is None
                return CreatedTrainerJob(
                    job_name="accounts/acct/rlorTrainerJobs/policy-job",
                    job_id="policy-job",
                )

            def try_get(self, job_id):
                assert job_id == "policy-job"
                return None

            def wait_for_ready(self, job_id, *, job_name, timeout_s):
                return TrainerServiceEndpoint(
                    job_name=job_name,
                    job_id=job_id,
                    base_url="https://trainer.test",
                    max_context_length=32768,
                )

        class FakeTrainingClient:
            pass

        class FakeServiceClient:
            def __init__(self, *, base_url, api_key):
                assert base_url == "https://trainer.test"
                assert api_key == "fw-key"

            def create_training_client(self, *, base_model, lora_rank, user_metadata):
                assert base_model == BASE_MODEL
                assert lora_rank == 0
                return FakeTrainingClient()

        def fake_build_resource_managers(**_kwargs):
            return FakeTrainerManager(), object()

        monkeypatch.setattr(
            managed_module,
            "_build_resource_managers",
            fake_build_resource_managers,
        )
        monkeypatch.setattr(managed_module, "FiretitanServiceClient", FakeServiceClient)

        handle = managed_module._create_managed_tinker_client(
            api_key="fw-key",
            config=_policy_config(
                training_shape_id=None,
                trainer_job_id=None,
                create_deployment=False,
                max_context_length=None,
            ),
        )

        assert handle.trainer_endpoint.max_context_length == 32768
        assert handle.max_context_length == 32768

    def test_full_param_reference_accepts_lora_trainer_shape(self):
        config = _policy_config(reference_training_shape_id="ts-ref-lora")
        reference = _reference_managed_config(config, policy_lora_rank=0)
        assert reference.lora_rank == 0
        assert reference.forward_only is True

        class FakeTrainerManager:
            account_id = "acct"

            def resolve_training_profile(self, training_shape_id):
                assert training_shape_id == "ts-ref-lora"
                return SimpleNamespace(
                    training_shape_version="ts-ref-lora/versions/v1",
                    deployment_shape="deployment-shape/versions/v1",
                    max_supported_context_length=32768,
                    trainer_mode="LORA_TRAINER",
                )

        _validate_reference_training_shape(FakeTrainerManager(), reference)

    def test_full_param_reference_rejects_forward_only_trainer_shape(self):
        config = _policy_config(reference_training_shape_id="ts-ref-forward-only")
        reference = _reference_managed_config(config, policy_lora_rank=0)
        assert reference.lora_rank == 0
        assert reference.forward_only is True

        class FakeTrainerManager:
            account_id = "acct"

            def resolve_training_profile(self, training_shape_id):
                assert training_shape_id == "ts-ref-forward-only"
                return SimpleNamespace(
                    training_shape_version="ts-ref-forward-only/versions/v1",
                    deployment_shape="deployment-shape/versions/v1",
                    max_supported_context_length=32768,
                    trainer_mode="FORWARD_ONLY",
                )

        with pytest.raises(ValueError, match="trainer_mode in"):
            _validate_reference_training_shape(FakeTrainerManager(), reference)

    def test_reference_shape_mode_mismatch_fails_before_creating(self, monkeypatch):
        events: list[str] = []

        class FakeTrainerManager:
            account_id = "acct"

            def resolve_training_profile(self, training_shape_id):
                events.append(f"resolve:{training_shape_id}")
                return SimpleNamespace(
                    training_shape_version=f"{training_shape_id}/versions/v1",
                    deployment_shape="deployment-shape/versions/v1",
                    max_supported_context_length=32768,
                    trainer_mode="POLICY_TRAINER",
                )

            def create(self, _config):
                events.append("create")
                raise AssertionError("trainer create should not run after preflight failure")

        def fake_build_resource_managers(**_kwargs):
            return FakeTrainerManager(), object()

        monkeypatch.setattr(
            managed_module,
            "_build_resource_managers",
            fake_build_resource_managers,
        )

        with pytest.raises(ValueError, match="trainer_mode in"):
            managed_module._create_managed_tinker_client(
                api_key="fw-key",
                config=_policy_config(
                    trainer_job_id=None,
                    deployment_id=None,
                    reference_training_shape_id="ts-reference",
                    reference_required=True,
                ),
            )

        assert events == ["resolve:ts-policy", "resolve:ts-reference"]


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
