"""Weight syncer for the Firetitan SDK.

Encapsulates the save-weights-then-sync-to-deployment pattern that is
repeated across training scripts.  Manages:

  - Delta checkpoint chain (base_saved / base_identity state)
  - Incremental hotload metadata (compression_format, checksum_format)
  - Error handling with graceful fallback

DCP (resume checkpoints) and sampler/hotload (inference deployment sync) are
fully decoupled — the syncer provides independent methods for each:

Usage::

    syncer = WeightSyncer(
        policy_client=policy_client,
        deploy_mgr=deploy_mgr,
        deployment_id="my-deployment",
        base_model="accounts/.../qwen3-8b",
        hotload_timeout=600,
    )

    # Sync weights: save sampler weights + push to deployment
    syncer.save_and_hotload("step-1")

    # DCP: save optimizer state for resume (independent of weight sync)
    syncer.save_dcp("step-1")

    # Split save/hotload (for resume ordering: save -> warmup -> hotload)
    snapshot = syncer.save_only("resume-step-0", checkpoint_type="base")
    deploy_mgr.warmup(model)
    syncer.hotload(snapshot)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from fireworks.training.sdk.client import FiretitanTrainingClient
from fireworks.training.sdk.deployment import DEFAULT_CHECKSUM_FORMAT

logger = logging.getLogger(__name__)


@dataclass
class WeightSyncer:
    """Manages checkpoint state and weight-sync-to-deployment lifecycle.

    Tracks the delta checkpoint chain so callers don't need to manage
    ``base_saved`` / ``base_identity`` state manually.

    Args:
        policy_client: The training client (for save_weights_for_sampler_ext / save_state).
        deploy_mgr: The deployment manager (for hotload_and_wait).  May be None
            if hotloading is not configured.
        deployment_id: Target deployment for hotload.  None = no hotloading.
        base_model: Model name for hotload API calls.
        hotload_timeout: Timeout in seconds for hotload_and_wait.
        first_checkpoint_type: Type for the first checkpoint ("base" or "delta").
    """

    policy_client: FiretitanTrainingClient
    deploy_mgr: object | None = None  # DeploymentManager, but avoid circular import
    deployment_id: str | None = None
    base_model: str = ""
    hotload_timeout: int = 600
    first_checkpoint_type: str = "base"
    compression_format: str = "arc_v2"
    warmup_after_hotload: bool = True
    """If True, send a warmup request after each successful hotload."""
    warmup_max_retries: int = 10
    """Max retries for post-hotload warmup (default 10 x 10s = ~100s)."""

    # Internal state — tracks the delta chain
    base_saved: bool = field(default=False, init=False)
    base_identity: str | None = field(default=None, init=False)
    _deployment_checked: bool = field(default=False, init=False)

    @property
    def _hotload_enabled(self) -> bool:
        return self.deployment_id is not None and self.deploy_mgr is not None

    def _warmup_after_hotload(self) -> None:
        """Send a lightweight warmup request after hotload completes.

        After a hotload the deployment has new weights loaded, but the first
        inference request may be slow or fail while CUDA graphs are compiled
        and KV cache is reallocated.  This sends a small test request and
        retries until the deployment responds with HTTP 200.
        """
        if not self.warmup_after_hotload or not self.deploy_mgr:
            return
        model = f"accounts/{self.deploy_mgr.account_id}/deployments/{self.deployment_id}"
        try:
            self.deploy_mgr.warmup(
                model,
                max_retries=self.warmup_max_retries,
                retry_interval_s=10.0,
            )
        except Exception as e:
            logger.warning("Post-hotload warmup failed (non-fatal): %s", e)

    def check_deployment_state(self) -> str | None:
        """Query the deployment's current hotload state.

        Logs the current snapshot identity and readiness.  Useful for
        diagnosing issues when reusing a deployment across training sessions
        (the deployment may have stale state from a previous delta chain).

        Returns:
            The deployment's current_snapshot_identity, or None if unknown.
        """
        if not self._hotload_enabled:
            return None
        try:
            status = self.deploy_mgr.hotload_check_status(
                deployment_id=self.deployment_id,
                base_model=self.base_model,
            )
            replicas = status.get("replicas", [])
            if replicas:
                replica = replicas[0]
                current = replica.get("current_snapshot_identity")
                readiness = replica.get("readiness", False)
                stage = replica.get("loading_state", {}).get("stage", "unknown")
                logger.info(
                    "Deployment state: identity=%s, ready=%s, stage=%s",
                    current,
                    readiness,
                    stage,
                )
                return current
            else:
                logger.info("Deployment state: no replicas (deployment may be scaling up)")
                return None
        except Exception as e:
            logger.warning("Could not check deployment state: %s", e)
            return None

    def _ensure_deployment_checked(self) -> None:
        """One-time check of deployment state before the first hotload.

        Detects if the deployment has a snapshot from a previous session.
        Forces the first hotload to be FULL (no incremental) regardless
        of internal state, since the previous session's delta chain is
        incompatible with this session's snapshots.
        """
        if self._deployment_checked:
            return
        self._deployment_checked = True

        current = self.check_deployment_state()
        if current:
            # Deployment has an existing snapshot. Our session's snapshots
            # use a different session_id prefix, so the old delta chain is
            # stale. Ensure first hotload is FULL by clearing base_identity.
            logger.info(
                "Deployment has existing snapshot '%s' from a previous session. "
                "First hotload will be FULL to reset the delta chain.",
                current,
            )
            self.base_identity = None

    def _next_checkpoint_type(self) -> str:
        """Return 'delta' if a base has been saved, else first_checkpoint_type."""
        return "delta" if self.base_saved else self.first_checkpoint_type

    def _build_incremental_metadata(self, ckpt_type: str) -> dict | None:
        """Build incremental hotload metadata for delta checkpoints."""
        if ckpt_type == "delta" and self.base_identity:
            return {
                "previous_snapshot_identity": self.base_identity,
                "compression_format": self.compression_format,
                "checksum_format": DEFAULT_CHECKSUM_FORMAT,
            }
        return None

    def _mark_first_save_done(self) -> None:
        """Record that at least one checkpoint has been saved.

        Flips ``base_saved`` so ``_next_checkpoint_type`` switches to delta.
        ``base_identity`` is set separately after a successful hotload,
        since it represents the last snapshot the deployment actually has.
        """
        self.base_saved = True

    def save_only(self, name: str, checkpoint_type: str | None = None) -> str | None:
        """Save sampler weights WITHOUT hotloading.

        Use when you need to separate save from hotload (e.g., save before
        deployment warmup, then hotload after).

        Returns:
            The snapshot_name on success, None on failure.
        """
        ckpt_type = checkpoint_type or self._next_checkpoint_type()
        try:
            save_result = self.policy_client.save_weights_for_sampler_ext(
                name,
                checkpoint_type=ckpt_type,
            )
            snapshot_name = save_result.snapshot_name
            self._mark_first_save_done()
            return snapshot_name
        except Exception as e:
            logger.warning("Save error for '%s': %s.", name, e)
            return None

    def hotload(self, snapshot_name: str) -> bool:
        """Hotload a previously saved snapshot to the deployment.

        Use after :meth:`save_only` when save and hotload need to be
        separated (e.g., with a deployment warmup in between).

        Returns:
            True on success, False on failure.
        """
        if not self._hotload_enabled:
            return False
        self._ensure_deployment_checked()
        try:
            ckpt_type = "delta" if self.base_identity and self.base_identity != snapshot_name else "base"
            incremental = self._build_incremental_metadata(ckpt_type)
            ok = self.deploy_mgr.hotload_and_wait(
                deployment_id=self.deployment_id,
                base_model=self.base_model,
                snapshot_identity=snapshot_name,
                incremental_snapshot_metadata=incremental,
                timeout_seconds=self.hotload_timeout,
            )
            if ok:
                self.base_identity = snapshot_name
                logger.info("Hotload complete: %s", snapshot_name)
                self._warmup_after_hotload()
            else:
                logger.warning("Hotload failed for snapshot '%s'.", snapshot_name)
            return ok
        except Exception as e:
            logger.warning("Hotload error for '%s': %s.", snapshot_name, e)
            return False

    def save_and_hotload(self, name: str, checkpoint_type: str | None = None) -> str | None:
        """Save sampler weights and hotload to deployment.

        This is the lightweight path (no DCP checkpoint).  Use for per-step
        or per-epoch hotloading where DCP is saved separately at intervals.

        Args:
            name: Checkpoint name (e.g. "onpolicy-step-5", "epoch-0").
            checkpoint_type: Override checkpoint type ("base" or "delta").
                If None, auto-determined from delta chain state.

        Returns:
            The snapshot_name on success, None on failure.
        """
        ckpt_type = checkpoint_type or self._next_checkpoint_type()
        try:
            save_result = self.policy_client.save_weights_for_sampler_ext(
                name,
                checkpoint_type=ckpt_type,
            )
            snapshot_name = save_result.snapshot_name
            self._mark_first_save_done()

            if self._hotload_enabled:
                self._ensure_deployment_checked()
                incremental = self._build_incremental_metadata(ckpt_type)
                ok = self.deploy_mgr.hotload_and_wait(
                    deployment_id=self.deployment_id,
                    base_model=self.base_model,
                    snapshot_identity=snapshot_name,
                    incremental_snapshot_metadata=incremental,
                    timeout_seconds=self.hotload_timeout,
                )
                if ok:
                    self.base_identity = snapshot_name
                    logger.info("Hotload complete: %s", snapshot_name)
                    self._warmup_after_hotload()
                else:
                    raise RuntimeError(
                        f"Hotload failed for '{name}': deployment did not accept snapshot. "
                        f"Check deployment hotLoadBucketUrl and base model match."
                    )
            return snapshot_name
        except Exception as e:
            logger.error(
                "Save/hotload error for '%s': %s",
                name,
                e,
            )
            raise

    def save_dcp(self, name: str) -> bool:
        """Save DCP checkpoint only (for resume).  No sampler, no hotload.

        Returns True on success, False on failure.
        """
        try:
            logger.info("Saving DCP checkpoint: %s", name)
            self.policy_client.save_state(name).result(timeout=1800)
            return True
        except Exception as e:
            logger.warning(
                "Failed to save DCP checkpoint '%s': %s. "
                "Training continues but you may not be able to resume from this step.",
                name,
                e,
            )
            return False
