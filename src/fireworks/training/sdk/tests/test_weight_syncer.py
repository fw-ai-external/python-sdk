"""Tests for fireworks.training.sdk.weight_syncer — delta chain state management."""

from __future__ import annotations

from types import SimpleNamespace
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


class TestSnapshotPathPropagation:
    """The trainer's GCS URI for the saved snapshot must reach the
    deployment manager so the serving side can fetch the bytes.
    """

    def test_save_and_hotload_forwards_gcs_path(self):
        deploy = _make_deploy_mgr()
        t = _make_tracker(deploy_mgr=deploy)
        t._deployment_checked = True
        t.policy_client.save_weights_for_sampler_ext.return_value = SaveSamplerResult(
            path="gs://bucket/run/step-0-base-sess",
            snapshot_name="step-0-base-sess",
        )

        t.save_and_hotload("step-0-base")

        _, kwargs = deploy.hotload_and_wait.call_args_list[-1]
        assert kwargs.get("path") == "gs://bucket/run/step-0-base-sess"

    def test_save_only_then_hotload_forwards_gcs_path(self):
        deploy = _make_deploy_mgr()
        t = _make_tracker(deploy_mgr=deploy)
        t._deployment_checked = True
        t.policy_client.save_weights_for_sampler_ext.return_value = SaveSamplerResult(
            path="gs://bucket/run/snap-x",
            snapshot_name="snap-x",
        )

        snap = t.save_only("snap-x", checkpoint_type="base")
        assert snap == "snap-x"
        deploy.hotload_and_wait.assert_not_called()

        ok = t.hotload(snap, checkpoint_type="base")
        assert ok is True
        _, kwargs = deploy.hotload_and_wait.call_args
        assert kwargs.get("path") == "gs://bucket/run/snap-x"

    def test_relative_path_is_combined_with_bucket_url(self):
        """In production the trainer returns the *relative* snapshot directory
        name in ``SaveSamplerResult.path``.  The syncer must combine it with
        the deployment's ``hot_load_bucket_url`` to form a full ``gs://`` URI
        before forwarding to the proxy.
        """
        deploy = _make_deploy_mgr()
        deploy.get.return_value = SimpleNamespace(
            hot_load_bucket_url="gs://fireworks-artifacts-acct/rl-checkpoints/acct/dep-1",
        )
        t = _make_tracker(deploy_mgr=deploy)
        t._deployment_checked = True
        t.policy_client.save_weights_for_sampler_ext.return_value = SaveSamplerResult(
            path="snap-relative-name",
            snapshot_name="snap-relative-name",
        )

        t.save_and_hotload("base")

        _, kwargs = deploy.hotload_and_wait.call_args_list[-1]
        assert kwargs.get("path") == (
            "gs://fireworks-artifacts-acct/rl-checkpoints/acct/dep-1/snap-relative-name"
        )

    def test_relative_path_not_forwarded_when_deployment_has_no_bucket(self):
        """If the deployment doesn't expose ``hot_load_bucket_url``, the syncer
        omits ``path`` and lets the proxy fall back to its own materialization
        (Alluxio / addons sidecar)."""
        deploy = _make_deploy_mgr()
        deploy.get.return_value = SimpleNamespace(hot_load_bucket_url=None)
        t = _make_tracker(deploy_mgr=deploy)
        t._deployment_checked = True
        t.policy_client.save_weights_for_sampler_ext.return_value = SaveSamplerResult(
            path="snap-relative-name",
            snapshot_name="snap-relative-name",
        )

        t.save_and_hotload("base")

        _, kwargs = deploy.hotload_and_wait.call_args_list[-1]
        assert kwargs.get("path") is None

    def test_full_uri_passes_through_bucket_combine(self):
        """Already-qualified URIs (gs://, s3://) bypass bucket lookup."""
        deploy = _make_deploy_mgr()
        deploy.get.side_effect = AssertionError(
            "deploy_mgr.get must not be called when path is already a full URI"
        )
        t = _make_tracker(deploy_mgr=deploy)
        t._deployment_checked = True
        t.policy_client.save_weights_for_sampler_ext.return_value = SaveSamplerResult(
            path="gs://other-bucket/run/snap",
            snapshot_name="snap",
        )

        t.save_and_hotload("base")

        _, kwargs = deploy.hotload_and_wait.call_args_list[-1]
        assert kwargs.get("path") == "gs://other-bucket/run/snap"

    def test_bucket_url_lookup_is_cached(self):
        """The bucket URL is fixed for a deployment's lifetime, so we only
        fetch it once even across many save_and_hotload calls."""
        deploy = _make_deploy_mgr()
        deploy.get.return_value = SimpleNamespace(
            hot_load_bucket_url="gs://b/dep-1",
        )
        t = _make_tracker(deploy_mgr=deploy)
        t._deployment_checked = True

        t.policy_client.save_weights_for_sampler_ext.side_effect = [
            SaveSamplerResult(path="snap-1", snapshot_name="snap-1"),
            SaveSamplerResult(path="snap-2", snapshot_name="snap-2"),
            SaveSamplerResult(path="snap-3", snapshot_name="snap-3"),
        ]
        t.save_and_hotload("step-1")
        t.save_and_hotload("step-2")
        t.save_and_hotload("step-3")

        assert deploy.get.call_count == 1


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
