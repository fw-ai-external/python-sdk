"""Tests for fireworks.training.sdk.weight_syncer — delta chain state management."""

from __future__ import annotations

from unittest.mock import MagicMock, PropertyMock

import pytest

from fireworks.training.sdk.client import SaveSamplerResult
from fireworks.training.sdk.weight_syncer import WeightSyncer


def _make_policy_client():
    """Create a mock FiretitanTrainingClient."""
    client = MagicMock()
    client.session_id = "test1234"
    return client


def _make_deploy_mgr():
    """Create a mock DeploymentManager."""
    mgr = MagicMock()
    mgr.account_id = "test-acct"
    mgr.hotload_and_wait.return_value = True
    return mgr


def _make_tracker(
    deploy_mgr=None,
    deployment_id="dep-1",
    first_checkpoint_type="base",
):
    client = _make_policy_client()
    client.save_weights_for_sampler_ext.return_value = SaveSamplerResult(
        path="gs://bucket/snap", snapshot_name="snap-test1234"
    )
    return WeightSyncer(
        policy_client=client,
        deploy_mgr=deploy_mgr or _make_deploy_mgr(),
        deployment_id=deployment_id,
        base_model="accounts/test/models/m",
        first_checkpoint_type=first_checkpoint_type,
    )


# ---------------------------------------------------------------------------
# _build_incremental_metadata
# ---------------------------------------------------------------------------


class TestBuildIncrementalMetadata:
    def test_base_type_returns_none(self):
        t = _make_tracker()
        assert t._build_incremental_metadata("base") is None

    def test_delta_with_base_identity(self):
        t = _make_tracker()
        t.base_identity = "snap-prev"
        meta = t._build_incremental_metadata("delta")
        assert meta is not None
        assert meta["previous_snapshot_identity"] == "snap-prev"
        assert meta["compression_format"] == "arc_v2"
        assert meta["checksum_format"] == "alder32"

    def test_delta_without_base_identity(self):
        t = _make_tracker()
        t.base_identity = None
        assert t._build_incremental_metadata("delta") is None


# ---------------------------------------------------------------------------
# _mark_first_save_done
# ---------------------------------------------------------------------------


class TestMarkFirstSaveDone:
    def test_sets_base_saved(self):
        t = _make_tracker()
        t._mark_first_save_done()
        assert t.base_saved is True
        assert t.base_identity is None  # only set after successful hotload

    def test_idempotent(self):
        t = _make_tracker()
        t._mark_first_save_done()
        t._mark_first_save_done()
        assert t.base_saved is True


# ---------------------------------------------------------------------------
# _ensure_deployment_checked
# ---------------------------------------------------------------------------


class TestEnsureDeploymentChecked:
    def test_called_once_sets_flag(self):
        t = _make_tracker()
        t.deploy_mgr.hotload_check_status.return_value = {"replicas": []}
        t._ensure_deployment_checked()
        assert t._deployment_checked is True

    def test_second_call_is_noop(self):
        t = _make_tracker()
        t._deployment_checked = True
        t._ensure_deployment_checked()
        t.deploy_mgr.hotload_check_status.assert_not_called()

    def test_existing_snapshot_clears_base_identity(self):
        t = _make_tracker()
        t.base_identity = "old-snap"
        t.deploy_mgr.hotload_check_status.return_value = {
            "replicas": [
                {
                    "current_snapshot_identity": "stale-snap",
                    "readiness": True,
                    "loading_state": {"stage": "done"},
                }
            ]
        }
        t._ensure_deployment_checked()
        assert t.base_identity is None


# ---------------------------------------------------------------------------
# Delta chain progression: base -> delta -> delta
# ---------------------------------------------------------------------------


class TestDeltaChainProgression:
    def test_chain(self):
        deploy = _make_deploy_mgr()
        t = _make_tracker(deploy_mgr=deploy)
        t._deployment_checked = True

        # Step 1: base save
        t.policy_client.save_weights_for_sampler_ext.return_value = SaveSamplerResult(
            path="p1", snapshot_name="step-0-base-sess"
        )
        t.save_and_hotload("step-0-base")
        assert t.base_saved is True
        assert t.base_identity == "step-0-base-sess"

        # Step 2: delta save
        t.policy_client.save_weights_for_sampler_ext.return_value = SaveSamplerResult(
            path="p2", snapshot_name="step-1-sess"
        )
        t.save_and_hotload("step-1")

        # After hotload_and_wait succeeds, base_identity should update
        assert t.base_identity == "step-1-sess"

        # Verify incremental metadata was passed for the delta
        _, kwargs = deploy.hotload_and_wait.call_args_list[-1]
        meta = kwargs.get("incremental_snapshot_metadata")
        assert meta is not None
        assert meta["previous_snapshot_identity"] == "step-0-base-sess"

        # Step 3: another delta
        t.policy_client.save_weights_for_sampler_ext.return_value = SaveSamplerResult(
            path="p3", snapshot_name="step-2-sess"
        )
        t.save_and_hotload("step-2")
        _, kwargs = deploy.hotload_and_wait.call_args_list[-1]
        meta = kwargs.get("incremental_snapshot_metadata")
        assert meta["previous_snapshot_identity"] == "step-1-sess"
