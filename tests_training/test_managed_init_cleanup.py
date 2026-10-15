"""Managed setup must clean up if model creation or transport attachment fails."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from fireworks.training.sdk import managed


@pytest.fixture
def setup_resources(monkeypatch: pytest.MonkeyPatch) -> SimpleNamespace:
    trainer_mgr = Mock()
    deploy_mgr = Mock()
    endpoint = SimpleNamespace(job_id="trainer", base_url="https://trainer.invalid", max_context_length=1024)
    started = SimpleNamespace(created=True, job=SimpleNamespace(job_name="accounts/test/rlorTrainerJobs/trainer"))
    deployment = SimpleNamespace(deployment_id="rollout")
    backend = Mock()
    service = Mock()
    training = service.create_training_client.return_value
    reference = Mock()
    attach = Mock(return_value=(deployment, backend, False, True))
    monkeypatch.setattr(managed, "_build_resource_managers", lambda **_kwargs: (trainer_mgr, deploy_mgr))
    monkeypatch.setattr(managed, "_start_or_reuse_trainer", lambda *_args, **_kwargs: started)
    monkeypatch.setattr(managed, "_wait_for_started_trainer", lambda *_args: endpoint)
    monkeypatch.setattr(managed, "_attach_managed_deployment", attach)
    monkeypatch.setattr(managed, "FiretitanServiceClient", lambda **_kwargs: service)
    monkeypatch.setattr(managed, "_should_provision_reference", lambda _config: True)
    monkeypatch.setattr(managed, "_reference_managed_config", lambda config, **_kwargs: config)
    monkeypatch.setattr(managed, "_validate_reference_training_shape", lambda *_args: None)
    # Only the recursive reference provisioner is mocked; exercise the real policy setup.
    create = managed._create_managed_tinker_client
    monkeypatch.setattr(managed, "_create_managed_tinker_client", lambda **_kwargs: reference)
    return SimpleNamespace(
        create=create,
        service=service,
        training=training,
        reference=reference,
        trainer_mgr=trainer_mgr,
        deploy_mgr=deploy_mgr,
        started=started,
        deployment=deployment,
        backend=backend,
        attach=attach,
    )


@pytest.mark.parametrize("phase", ["create_model", "training_attach", "service_attach"])
def test_setup_failure_releases_owned_resources(setup_resources: SimpleNamespace, phase: str) -> None:
    r = setup_resources
    error = RuntimeError("RDMA initialization failed")
    method = {
        "create_model": r.service.create_training_client,
        "training_attach": r.training._attach_sampler_backend,
        "service_attach": r.service._attach_sampler_backend,
    }[phase]
    method.side_effect = error
    with pytest.raises(RuntimeError) as raised:
        r.create(
            api_key="test",
            config=managed._ManagedTinkerConfig(
                base_model="test/model",
                cleanup_trainer_on_close=True,
                cleanup_deployment_on_close="delete",
            ),
        )
    assert raised.value is error
    r.service.holder.close.assert_called_once()
    r.trainer_mgr.delete.assert_called_once_with("trainer")
    r.deploy_mgr.delete.assert_called_once_with("rollout")
    r.reference.close.assert_called_once()


@pytest.mark.parametrize("trainer_created,deployment_created", [(False, False), (True, False), (False, True)])
def test_setup_failure_preserves_reused_resources(
    setup_resources: SimpleNamespace,
    trainer_created: bool,
    deployment_created: bool,
) -> None:
    r = setup_resources
    r.started.created = trainer_created
    r.attach.return_value = (r.deployment, r.backend, not deployment_created, deployment_created)
    r.training._attach_sampler_backend.side_effect = RuntimeError("RDMA initialization failed")
    with pytest.raises(RuntimeError, match="RDMA initialization failed"):
        r.create(
            api_key="test",
            config=managed._ManagedTinkerConfig(
                base_model="test/model",
                cleanup_trainer_on_close=True,
                cleanup_deployment_on_close="delete",
            ),
        )
    assert r.trainer_mgr.delete.call_count == int(trainer_created)
    assert r.deploy_mgr.delete.call_count == int(deployment_created)
    r.service.holder.close.assert_called_once()


@pytest.mark.parametrize("cleanup", [None, "scale_to_zero"])
def test_setup_failure_respects_cleanup_settings(setup_resources: SimpleNamespace, cleanup: str | None) -> None:
    r = setup_resources
    r.training._attach_sampler_backend.side_effect = RuntimeError("RDMA initialization failed")
    with pytest.raises(RuntimeError, match="RDMA initialization failed"):
        r.create(
            api_key="test",
            config=managed._ManagedTinkerConfig(
                base_model="test/model",
                cleanup_trainer_on_close=False,
                cleanup_deployment_on_close=cleanup,
            ),
        )
    r.trainer_mgr.delete.assert_not_called()
    r.deploy_mgr.delete.assert_not_called()
    assert r.deploy_mgr.scale_to_zero.call_count == int(cleanup == "scale_to_zero")
    r.service.holder.close.assert_called_once()


def test_cleanup_errors_do_not_mask_setup_failure_or_skip_other_resources(setup_resources: SimpleNamespace) -> None:
    r = setup_resources
    error = RuntimeError("RDMA initialization failed")
    r.training._attach_sampler_backend.side_effect = error
    r.reference.close.side_effect = RuntimeError("reference cleanup failed")
    r.deploy_mgr.delete.side_effect = RuntimeError("rollout cleanup failed")
    r.trainer_mgr.delete.side_effect = RuntimeError("trainer cleanup failed")
    with pytest.raises(RuntimeError) as raised:
        r.create(
            api_key="test",
            config=managed._ManagedTinkerConfig(
                base_model="test/model",
                cleanup_trainer_on_close=True,
                cleanup_deployment_on_close="delete",
            ),
        )
    assert raised.value is error
    r.reference.close.assert_called_once()
    r.service.holder.close.assert_called_once()
    r.deploy_mgr.delete.assert_called_once_with("rollout")
    r.trainer_mgr.delete.assert_called_once_with("trainer")


def test_success_transfers_cleanup_to_caller(setup_resources: SimpleNamespace) -> None:
    r = setup_resources
    handle = r.create(
        api_key="test",
        config=managed._ManagedTinkerConfig(
            base_model="test/model",
            cleanup_trainer_on_close=True,
            cleanup_deployment_on_close="delete",
        ),
    )
    assert handle.training_client is r.training
    assert handle.training_clients == [r.training]
    assert handle.reference_handle is r.reference
    r.service.holder.close.assert_not_called()
    r.trainer_mgr.delete.assert_not_called()
    r.deploy_mgr.delete.assert_not_called()
    r.reference.close.assert_not_called()
    handle.close()
    handle.close()
    r.service.holder.close.assert_called_once()
    r.trainer_mgr.delete.assert_called_once_with("trainer")
    r.deploy_mgr.delete.assert_called_once_with("rollout")
