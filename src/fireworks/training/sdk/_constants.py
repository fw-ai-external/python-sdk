"""Shared default timeouts and polling intervals for the training SDK.

All values are in seconds. Centralizing them here keeps the trainer,
deployment, hotload, and managed-compatibility layers consistent instead of
drifting between scattered literals (e.g. ``15 * 60`` vs ``600``).
"""

from __future__ import annotations

from typing import Literal

# -- Resource cleanup modes ---------------------------------------------------

DeploymentCleanupOnClose = Literal["delete", "scale_to_zero"]
"""Supported cleanup behavior for an SDK-managed deployment on client close."""

CLEANUP_DEPLOYMENT_ON_CLOSE_DELETE: DeploymentCleanupOnClose = "delete"
"""Delete the SDK-created deployment when the service client closes."""

CLEANUP_DEPLOYMENT_ON_CLOSE_SCALE_TO_ZERO: DeploymentCleanupOnClose = "scale_to_zero"
"""Scale the SDK-created deployment to zero replicas when the service client closes."""

SDK_MANAGED_ROLLOUT_DEPLOYMENT_ANNOTATION = "fireworks-training-sdk/managed-rollout"
"""Deployment annotation marking SDK-managed rollout infrastructure."""

# -- Resource provisioning waits ---------------------------------------------

DEFAULT_TRAINER_TIMEOUT_S: float = 3600.0
"""Post-placement wait budget for an SDK-managed trainer to become ready."""

DEFAULT_TRAINER_PENDING_TIMEOUT_S: float = 48 * 60 * 60
"""Capacity-placement wait budget while a trainer remains PENDING."""

TRAINER_READY_TIMEOUT_S: float = 15 * 60
"""Post-placement wait budget for a low-level trainer call to reach ready."""

DEPLOYMENT_READY_TIMEOUT_S: float = 5400.0
"""Wait budget for an SDK-managed deployment to become ready."""

REATTACH_SETTLE_TIMEOUT_S: float = 600.0
"""Wait budget for a reattached deployment to settle on the new trainer."""

RECONNECT_TIMEOUT_S: float = 600.0
"""Wait budget for reconnecting to an existing trainer and reaching RUNNING."""

RESUMABLE_WAIT_TIMEOUT_S: float = 120.0
"""Wait budget for a trainer in a transitional state to become resumable."""

# -- Hotload / weight sync ----------------------------------------------------

HOTLOAD_TIMEOUT_S: int = 600
"""Wait budget for a sampler hotload to complete on the deployment."""

HOTLOAD_READY_TIMEOUT_S: int = 300
"""Wait budget for the deployment to report hotload readiness."""

# -- Polling ------------------------------------------------------------------

POLL_INTERVAL_S: float = 5.0
"""Default interval between status polls."""

SLOW_POLL_INTERVAL_S: float = 10.0
"""Interval between polls for slower-moving resources (e.g. trainer jobs)."""

POLL_LOG_HEARTBEAT_S: float = 60.0
"""How often to emit a heartbeat log line while polling."""

# -- Low-level HTTP request timeouts ------------------------------------------

HTTP_READ_TIMEOUT_S: int = 30
"""Timeout for short read/GET/DELETE requests."""

HTTP_WRITE_TIMEOUT_S: int = 60
"""Timeout for create/POST requests."""

HTTP_LONG_WRITE_TIMEOUT_S: int = 300
"""Timeout for slow create/POST requests (e.g. large resource creation)."""

WARMUP_PROBE_TIMEOUT_S: int = 10
"""Timeout for a single warmup/liveness probe request."""
