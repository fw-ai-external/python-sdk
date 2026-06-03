"""Tests for reattach reconciliation in the SDK-managed deployment path.

A reattach reuses a warm deployment, but it must not silently serve a shape
different from the one requested (that would serve the wrong model/hardware).
The reconciliation fails fast *before* mutating the deployment.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from fireworks.training.sdk.managed import (
    _ManagedTinkerConfig,
    _deployment_shape_conflict,
    _create_or_reattach_deployment,
    _create_or_reattach_deployment_result,
)
from fireworks.training.sdk.deployment import DeploymentInfo

SHAPE = "accounts/acct/deploymentShapes/rft-x"
SHAPE_V1 = f"{SHAPE}/versions/1"
SHAPE_V2 = f"{SHAPE}/versions/2"


class TestDeploymentShapeConflict:
    def test_unset_request_never_conflicts(self):
        assert _deployment_shape_conflict(None, SHAPE_V1) is False

    def test_unversioned_request_matches_any_version(self):
        assert _deployment_shape_conflict(SHAPE, SHAPE_V1) is False

    def test_unversioned_request_different_shape_conflicts(self):
        assert _deployment_shape_conflict(SHAPE, "accounts/acct/deploymentShapes/other/versions/1") is True

    def test_version_drift_of_same_shape_does_not_conflict(self):
        # A profile's validated version can drift (v1 -> v2) between the original
        # run and a resume; same shape = same training task, so reattach is fine.
        assert _deployment_shape_conflict(SHAPE_V1, SHAPE_V1) is False
        assert _deployment_shape_conflict(SHAPE_V1, SHAPE_V2) is False

    def test_version_pinned_different_shape_conflicts(self):
        assert (
            _deployment_shape_conflict(SHAPE_V1, "accounts/acct/deploymentShapes/other/versions/2")
            is True
        )


class _FakeDeployManager:
    def __init__(self, existing: DeploymentInfo):
        self._existing = existing
        self.reattach_called = False

    def get(self, deployment_id: str) -> DeploymentInfo:
        return self._existing

    def reattach_trainer(self, *args, **kwargs):
        self.reattach_called = True
        raise AssertionError("reattach_trainer must not run when the shape conflicts")


def test_reattach_rejects_shape_mismatch_before_mutating():
    existing = DeploymentInfo(
        deployment_id="dep-1",
        name="dep-1",
        state="READY",
        deployment_shape_version=SHAPE_V1,
    )
    deploy_mgr = _FakeDeployManager(existing)
    config = _ManagedTinkerConfig(base_model="accounts/acct/models/base", deployment_id="dep-1")

    with pytest.raises(ValueError, match="does not match the requested deployment_shape"):
        _create_or_reattach_deployment(
            deploy_mgr,
            config,
            trainer_job_name="accounts/acct/rlorTrainerJobs/job-1",
            deployment_shape="accounts/acct/deploymentShapes/other/versions/1",
        )
    assert deploy_mgr.reattach_called is False


def test_managed_deployment_does_not_inherit_trainer_skip_validations():
    deploy_mgr = MagicMock()
    deploy_mgr.create_or_get.return_value = DeploymentInfo(
        deployment_id="dep-1",
        name="dep-1",
        state="READY",
    )
    config = _ManagedTinkerConfig(
        base_model="accounts/acct/models/base",
        skip_validations=True,
    )

    _create_or_reattach_deployment(
        deploy_mgr,
        config,
        trainer_job_name="accounts/acct/rlorTrainerJobs/job-1",
        deployment_shape=SHAPE_V1,
    )

    deployment_config = deploy_mgr.create_or_get.call_args.args[0]
    assert deployment_config.skip_shape_validation is False


def test_reattach_result_marks_existing_deployment_moved_to_new_trainer():
    deploy_mgr = MagicMock()
    existing = DeploymentInfo(
        deployment_id="dep-1",
        name="dep-1",
        state="READY",
        hot_load_trainer_job="accounts/acct/rlorTrainerJobs/old-job",
    )
    updated = DeploymentInfo(
        deployment_id="dep-1",
        name="dep-1",
        state="READY",
        hot_load_trainer_job="accounts/acct/rlorTrainerJobs/new-job",
    )
    deploy_mgr.get.return_value = existing
    deploy_mgr.reattach_trainer.return_value = updated
    config = _ManagedTinkerConfig(base_model="accounts/acct/models/base", deployment_id="dep-1")

    result = _create_or_reattach_deployment_result(
        deploy_mgr,
        config,
        trainer_job_name="accounts/acct/rlorTrainerJobs/new-job",
        deployment_shape=None,
    )

    assert result.deployment is updated
    assert result.reattached is True


def test_reattach_result_does_not_mark_already_attached_deployment():
    deploy_mgr = MagicMock()
    existing = DeploymentInfo(
        deployment_id="dep-1",
        name="dep-1",
        state="READY",
        hot_load_trainer_job="accounts/acct/rlorTrainerJobs/job-1",
    )
    deploy_mgr.get.return_value = existing
    deploy_mgr.reattach_trainer.return_value = existing
    config = _ManagedTinkerConfig(base_model="accounts/acct/models/base", deployment_id="dep-1")

    result = _create_or_reattach_deployment_result(
        deploy_mgr,
        config,
        trainer_job_name="accounts/acct/rlorTrainerJobs/job-1",
        deployment_shape=None,
    )

    assert result.deployment is existing
    assert result.reattached is False
