"""Shared default timeouts and polling intervals for the training SDK.

All values are in seconds. Centralizing them here keeps the trainer,
deployment, hotload, and managed-compatibility layers consistent instead of
drifting between scattered literals (e.g. ``15 * 60`` vs ``600``).
"""

from __future__ import annotations

# -- Resource provisioning waits ---------------------------------------------

DEFAULT_TRAINER_TIMEOUT_S: float = 3600.0
"""Wait budget for an SDK-managed trainer to become ready."""

TRAINER_READY_TIMEOUT_S: float = 15 * 60
"""Wait budget for a trainer create/reconnect call to reach a ready state."""

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
