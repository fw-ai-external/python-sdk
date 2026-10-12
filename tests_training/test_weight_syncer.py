"""Tests for fireworks.training.sdk.weight_syncer — delta chain state management."""

from __future__ import annotations

from unittest.mock import MagicMock

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
        path="snap-test1234", snapshot_name="snap-test1234"
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
        t.deploy_mgr.hotload_check_status.return_value = {
            "replicas": [
                {
                    "current_snapshot_identity": None,
                    "readiness": False,
                    "loading_state": {"stage": "pending"},
                }
            ]
        }
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
# Sampling client helpers
# ---------------------------------------------------------------------------


class TestGetSamplingClient:
    def test_returns_firetitan_sampling_client_for_deployment(self):
        deploy = _make_deploy_mgr()
        deploy.inference_url = "https://api.fireworks.ai"
        deploy.api_key = "test-key"
        t = _make_tracker(deploy_mgr=deploy, deployment_id="dep-123")

        from fireworks.training.sdk.deployment import FiretitanSamplingClient

        client = t.get_sampling_client()
        try:
            assert isinstance(client, FiretitanSamplingClient)
            assert client.deployment_sampler.base_url == "https://api.fireworks.ai"
            assert client.deployment_sampler.model == "accounts/test-acct/deployments/dep-123"
            assert client.deployment_sampler.api_key == "test-key"
        finally:
            client.close()


# ---------------------------------------------------------------------------
# Warmup model resolution
# ---------------------------------------------------------------------------


class TestWarmupModel:
    def test_get_model_uses_deployment_resource_name(self):
        t = _make_tracker(deployment_id="dep-123")
        assert t._get_model() == "accounts/test-acct/deployments/dep-123"

    def test_save_and_hotload_warms_up_deployment_model(self):
        deploy = _make_deploy_mgr()
        t = _make_tracker(deploy_mgr=deploy)
        t._deployment_checked = True
        t.policy_client.save_weights_for_sampler_ext.return_value = SaveSamplerResult(
            path="p1", snapshot_name="step-0-base-sess"
        )

        t.save_and_hotload("step-0-base")

        deploy.warmup.assert_called_once_with(
            "accounts/test-acct/deployments/dep-1",
            max_retries=t.warmup_max_retries,
            retry_interval_s=10.0,
        )


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


class TestResetDeltaChain:
    """Tests the contract: after reset, the next save must be a base checkpoint
    (no incremental metadata), regardless of prior chain state."""

    def test_reset_after_chain_then_save_uses_base(self):
        deploy = _make_deploy_mgr()
        t = _make_tracker(deploy_mgr=deploy)
        t._deployment_checked = True

        # Build up some chain state by performing a real save through the
        # public API (not by mutating internals).
        t.policy_client.save_weights_for_sampler_ext.return_value = SaveSamplerResult(
            path="p1", snapshot_name="t1-base-sess"
        )
        t.save_and_hotload("t1-base")

        # Re-attach happens here — caller resets the chain.
        t.reset_delta_chain()

        # Next save against the new trainer must be a base checkpoint (no
        # incremental metadata).
        t.policy_client.save_weights_for_sampler_ext.return_value = SaveSamplerResult(
            path="p2", snapshot_name="t2-base-sess"
        )
        t.save_and_hotload("t2-base")
        _, kwargs = deploy.hotload_and_wait.call_args_list[-1]
        assert kwargs.get("incremental_snapshot_metadata") is None

    def test_reset_when_already_clean_then_save_uses_base(self):
        """Reset on a fresh tracker is a no-op; subsequent save still produces base."""
        deploy = _make_deploy_mgr()
        t = _make_tracker(deploy_mgr=deploy)
        t._deployment_checked = True

        t.reset_delta_chain()  # idempotent on fresh state

        t.policy_client.save_weights_for_sampler_ext.return_value = SaveSamplerResult(
            path="p1", snapshot_name="fresh-base-sess"
        )
        t.save_and_hotload("fresh-base")
        _, kwargs = deploy.hotload_and_wait.call_args_list[-1]
        assert kwargs.get("incremental_snapshot_metadata") is None


# ---------------------------------------------------------------------------
# Snapshot identity plumbing
# ---------------------------------------------------------------------------


class TestSnapshotIdentityPlumbing:
    """Hotload uses the public snapshot identity, not a trainer storage path."""

    def test_save_and_hotload_uses_snapshot_identity_only(self):
        deploy = _make_deploy_mgr()
        t = _make_tracker(deploy_mgr=deploy)
        t._deployment_checked = True
        t.policy_client.save_weights_for_sampler_ext.return_value = SaveSamplerResult(
            path="step-0-base-sess",
            snapshot_name="step-0-base-sess",
        )

        t.save_and_hotload("step-0-base")

        kwargs = deploy.hotload_and_wait.call_args.kwargs
        assert kwargs["snapshot_identity"] == "step-0-base-sess"
        assert kwargs["path"] is None
        deploy.get.assert_not_called()

    def test_save_only_then_hotload_uses_snapshot_identity_only(self):
        deploy = _make_deploy_mgr()
        t = _make_tracker(deploy_mgr=deploy)
        t._deployment_checked = True
        t.policy_client.save_weights_for_sampler_ext.return_value = SaveSamplerResult(
            path="step-0-base-sess",
            snapshot_name="step-0-base-sess",
        )

        snapshot_name = t.save_only("step-0-base", checkpoint_type="base")
        assert snapshot_name == "step-0-base-sess"
        # No hotload yet.
        deploy.hotload_and_wait.assert_not_called()

        ok = t.hotload(snapshot_name, checkpoint_type="base")
        assert ok is True
        kwargs = deploy.hotload_and_wait.call_args.kwargs
        assert kwargs["snapshot_identity"] == "step-0-base-sess"
        assert kwargs["path"] is None
        deploy.get.assert_not_called()
