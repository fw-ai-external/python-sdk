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
    syncer.hotload(snapshot, checkpoint_type="base")
"""

from __future__ import annotations

import time
import logging
from typing import TYPE_CHECKING
from dataclasses import field, dataclass

from fireworks.training.sdk.client import FiretitanTrainingClient
from fireworks.training.sdk.deployment import DEFAULT_CHECKSUM_FORMAT

if TYPE_CHECKING:
    from fireworks.training.sdk.deployment import DeploymentManager, DeploymentSampler

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
    deploy_mgr: DeploymentManager | None = None
    deployment_id: str | None = None
    base_model: str = ""
    hotload_timeout: int = 600
    first_checkpoint_type: str = "base"
    dcp_timeout: int = 2700
    """Timeout in seconds for DCP save_state (default 45 min)."""
    compression_format: str = "arc_v2"
    warmup_after_hotload: bool = True
    """If True, send a warmup request after each successful hotload."""
    warmup_max_retries: int = 10
    """Max retries for post-hotload warmup (default 10 x 10s = ~100s)."""
    reset_prompt_cache: bool = True
    """If True, reset the prompt cache on the deployment after hotloading."""

    # Internal state — tracks the delta chain
    base_saved: bool = field(default=False, init=False)
    base_identity: str | None = field(default=None, init=False)
    _deployment_checked: bool = field(default=False, init=False)
    last_timing: dict = field(default_factory=dict, init=False)
    """Timing breakdown from the most recent operation (seconds).
    Reset at the start of each save/hotload/dcp call."""

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

        try:
            self.deploy_mgr.warmup(
                self._get_model(),
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

    def wait_for_hotload_ready(self, timeout_s: int = 300, poll_interval_s: int = 5) -> None:
        """Block until the deployment's hot load manager is initialized.

        The deployment's healthz may return 200 before the internal process
        group and hot load subsystem are fully ready.  Sending a hotload
        request in that window crashes the serving container.  This method
        polls the hotload status endpoint and waits for a valid ``replicas``
        response, which indicates the hot load manager is accepting requests.
        """
        if not self._hotload_enabled:
            return
        start = time.time()
        while time.time() - start < timeout_s:
            try:
                status = self.deploy_mgr.hotload_check_status(
                    deployment_id=self.deployment_id,
                    base_model=self.base_model,
                )
                replicas = status.get("replicas", [])
                if replicas:
                    logger.info(
                        "Hotload manager ready (replicas=%d, %ds)",
                        len(replicas),
                        int(time.time() - start),
                    )
                    return
            except Exception as e:
                logger.debug("Hotload status not ready yet: %s", e)

            elapsed = int(time.time() - start)
            logger.info("Waiting for hotload manager to initialize (%ds)...", elapsed)
            time.sleep(poll_interval_s)
        raise TimeoutError(
            f"Deployment hotload manager not ready after {timeout_s}s. "
            f"The serving container may still be initializing its process group."
        )

    def _ensure_deployment_checked(self) -> None:
        """One-time check of deployment state before the first hotload.

        Waits for the hotload manager to be initialized, then detects if the
        deployment has a snapshot from a previous session.  Forces the first
        hotload to be FULL (no incremental) regardless of internal state,
        since the previous session's delta chain is incompatible with this
        session's snapshots.
        """
        if self._deployment_checked:
            return
        self._deployment_checked = True

        self.wait_for_hotload_ready()
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
        self.last_timing = {}
        ckpt_type = checkpoint_type or self._next_checkpoint_type()
        try:
            t0 = time.time()
            save_result = self.policy_client.save_weights_for_sampler_ext(
                name,
                checkpoint_type=ckpt_type,
            )
            self.last_timing["save_time_s"] = time.time() - t0
            snapshot_name = save_result.snapshot_name
            self._mark_first_save_done()
            return snapshot_name
        except Exception as e:
            logger.warning("Save error for '%s': %s.", name, e)
            return None

    def _do_hotload(self, snapshot_name: str, checkpoint_type: str) -> None:
        """Core hotload logic shared by :meth:`hotload` and :meth:`save_and_hotload`.

        Raises on failure so callers can decide how to handle errors.
        """
        self._ensure_deployment_checked()
        incremental = self._build_incremental_metadata(checkpoint_type)
        t0 = time.time()
        ok = self.deploy_mgr.hotload_and_wait(
            deployment_id=self.deployment_id,
            base_model=self.base_model,
            snapshot_identity=snapshot_name,
            incremental_snapshot_metadata=incremental,
            reset_prompt_cache=self.reset_prompt_cache,
            timeout_seconds=self.hotload_timeout,
        )
        self.last_timing["hotload_time_s"] = time.time() - t0
        if not ok:
            raise RuntimeError(
                f"Hotload failed for '{snapshot_name}': deployment did not accept snapshot. "
                f"Check deployment hotLoadBucketUrl and base model match."
            )
        self.base_identity = snapshot_name
        logger.info("Hotload complete: %s", snapshot_name)
        t1 = time.time()
        self._warmup_after_hotload()
        self.last_timing["warmup_time_s"] = time.time() - t1

    def hotload(self, snapshot_name: str, checkpoint_type: str) -> bool:
        """Hotload a previously saved snapshot to the deployment.

        Use after :meth:`save_only` when save and hotload need to be
        separated (e.g., with a deployment warmup in between).

        Args:
            snapshot_name: Snapshot identity returned by :meth:`save_only`.
            checkpoint_type: Checkpoint type ("base" or "delta").  Must match
                the type used in the corresponding :meth:`save_only` call.

        Returns:
            True on success, False on failure.
        """
        self.last_timing = {}
        if not self._hotload_enabled:
            return False
        try:
            self._do_hotload(snapshot_name, checkpoint_type)
            return True
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
        self.last_timing = {}
        t_total = time.time()
        ckpt_type = checkpoint_type or self._next_checkpoint_type()
        try:
            t0 = time.time()
            save_result = self.policy_client.save_weights_for_sampler_ext(
                name,
                checkpoint_type=ckpt_type,
            )
            self.last_timing["save_time_s"] = time.time() - t0
            snapshot_name = save_result.snapshot_name
            self._mark_first_save_done()

            if self._hotload_enabled:
                self._do_hotload(snapshot_name, ckpt_type)

            self.last_timing["total_time_s"] = time.time() - t_total
            return snapshot_name
        except Exception as e:
            self.last_timing["total_time_s"] = time.time() - t_total
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
        self.last_timing = {}
        try:
            logger.info("Saving DCP checkpoint: %s", name)
            t0 = time.time()
            self.policy_client.save_state(name, timeout=self.dcp_timeout)
            self.last_timing["dcp_save_time_s"] = time.time() - t0
            return True
        except Exception as e:
            logger.warning(
                "Failed to save DCP checkpoint '%s': %s. "
                "Training continues but you may not be able to resume from this step.",
                name,
                e,
            )
            return False

    def _get_model(self) -> str:
        """Helper to construct the model name for deployment."""
        if not self.deploy_mgr or not self.deployment_id:
            raise ValueError("Deployment manager and deployment ID must be set for hotload operations.")
        return f"accounts/{self.deploy_mgr.account_id}/deployments/{self.deployment_id}"

    def get_deployment_sampler(self) -> DeploymentSampler:
        """Get the deployment's current sampler"""
        from fireworks.training.sdk.deployment import DeploymentSampler
        return DeploymentSampler(
            inference_url=self.deploy_mgr.inference_url,
            model=self._get_model(),
            api_key=self.deploy_mgr.api_key,
        )