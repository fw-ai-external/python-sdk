"""Firetitan Tinker SDK — Thin extensions for full-param training.

Three additions to the tinker SDK:
  1. FiretitanServiceClient.create_training_client() — supports lora_config=None
  2. FiretitanTrainingClient.save_weights_for_sampler_ext() — adds checkpoint_type
  3. FiretitanTrainingClient.list_checkpoints() — firetitan-specific DCP checkpoint listing

Everything else (forward, forward_backward, forward_backward_custom, optim_step,
save_state, load_state, get_tokenizer, etc.) is inherited unchanged from tinker.
"""

from __future__ import annotations

import time
import uuid
import logging
from dataclasses import dataclass

from tinker import types
from tinker.lib.api_future_impl import _APIFuture
from tinker.lib.queue_state_logger import QueueStateLogger
from tinker.lib.client_connection_pool_type import ClientConnectionPoolType
from tinker.lib.public_interfaces.service_client import ServiceClient
from tinker.lib.public_interfaces.training_client import TrainingClient

logger = logging.getLogger(__name__)

# -- Cross-job checkpoint references ------------------------------------------

CROSS_JOB_CHECKPOINT_REF_PREFIX = "cross_job://"


def make_cross_job_checkpoint_ref(*, source_job_id: str, checkpoint_name: str) -> str:
    """Build an opaque checkpoint reference for cross-job resume."""
    normalized_source_job_id = source_job_id.strip()
    normalized_checkpoint_name = checkpoint_name.strip()
    if not normalized_source_job_id:
        raise ValueError("source_job_id cannot be empty")
    if not normalized_checkpoint_name:
        raise ValueError("checkpoint_name cannot be empty")
    if normalized_checkpoint_name.startswith("gs://") or normalized_checkpoint_name.startswith("/"):
        raise ValueError("checkpoint_name must be a logical checkpoint name, not a full path")
    return f"{CROSS_JOB_CHECKPOINT_REF_PREFIX}{normalized_source_job_id}/{normalized_checkpoint_name}"


# -- Session-scoped snapshot name qualification --------------------------------
#
# Ensures sampler snapshot GCS paths are unique per training session,
# preventing Alluxio cache staleness when deployment_id is reused.
# By suffixing every sampler snapshot name with a unique session_id,
# the GCS paths are guaranteed to be unique by construction.


def generate_session_id() -> str:
    """Generate a unique 8-char hex session identifier.

    Called once per training session (including on resume) to produce
    a fresh identifier that namespaces all sampler snapshot GCS paths.
    """
    return uuid.uuid4().hex[:8]


def qualify_snapshot_name(session_id: str, name: str) -> str:
    """Suffix a snapshot name with *session_id* for GCS path uniqueness.

    Uses ``-`` as separator (not ``/``) because ``os.path.basename()``
    is used downstream in ``xor_extensions.py`` and ``tinker_api.py``
    to extract the snapshot name from the local directory path.  A
    ``/`` separator would be stripped by ``basename()``, defeating the
    purpose.

    Args:
        session_id: Unique per-session identifier (from
            :func:`generate_session_id`).
        name: Original snapshot name (e.g. ``"step-0-base"``,
            ``"step-4"``).

    Returns:
        Qualified name, e.g. ``"step-0-base-a1b2c3d4"``.
    """
    return f"{name}-{session_id}"


# -- SaveSamplerResult ---------------------------------------------------------


@dataclass
class SaveSamplerResult:
    """Result of :meth:`FiretitanTrainingClient.save_weights_for_sampler_ext`.

    Attributes:
        path: The snapshot name returned by the trainer (same as
            *snapshot_name*).  Internal GCS paths are not exposed to
            SDK users -- they are only logged server-side.
        snapshot_name: The actual snapshot name used (with session_id suffix).
            Use this for ``hotload(snapshot_identity=...)`` calls.
    """

    path: str
    snapshot_name: str


# -- FiretitanTrainingClient ---------------------------------------------------


class FiretitanTrainingClient(TrainingClient):
    """TrainingClient with firetitan-specific extensions.

    Adds:
      - save_weights_for_sampler_ext(): checkpoint_type support + session_id suffixing
      - list_checkpoints(): DCP checkpoint listing from the trainer
      - Checkpoint name reuse detection (warns on duplicate names within a session)
      - Session-scoped snapshot name qualification (prevents Alluxio cache staleness)

    A unique ``session_id`` is generated on creation.  All sampler snapshot
    names are automatically suffixed with it in
    :meth:`save_weights_for_sampler_ext`, ensuring GCS paths never collide
    across training sessions that share the same ``deployment_id``.

    All core methods (forward, forward_backward, forward_backward_custom,
    optim_step, load_state_with_optimizer, get_tokenizer) are
    inherited unchanged from tinker.TrainingClient.
    """

    def __init__(self, holder, model_seq_id: int, model_id):
        super().__init__(holder=holder, model_seq_id=model_seq_id, model_id=model_id)
        # Track checkpoint names to detect reuse within a session.
        # Sampler and state names are tracked separately because the same name
        # (e.g., "step-4") is intentionally used for both — they are different
        # storage types.
        self._saved_sampler_names: set[str] = set()
        self._saved_state_names: set[str] = set()

        # Unique session identifier — appended to all sampler snapshot names
        # so that GCS paths are unique even when the deployment_id is reused.
        self.session_id: str = generate_session_id()
        logger.info("FiretitanTrainingClient session_id: %s", self.session_id)

    def _warn_if_name_reused(self, name: str, names_set: set[str], kind: str) -> None:
        """Log a warning if a checkpoint name has already been used."""
        if name in names_set:
            logger.warning(
                "%s checkpoint name '%s' already used in this session — overwriting",
                kind,
                name,
            )

    def list_checkpoints(self) -> tuple[list[str], str | None]:
        """List available DCP checkpoints from the trainer.

        This is a firetitan-specific endpoint (not in tinker SDK).
        Uses the trainer's own HTTP connection.

        Returns:
            (checkpoint_names, gcs_checkpoint_dir):
            - checkpoint_names: sorted list (e.g., ["step-2", "step-4"])
            - gcs_checkpoint_dir: Always None (kept for backward compatibility)
        """

        async def _list():
            with self.holder.aclient(ClientConnectionPoolType.TRAIN) as client:
                resp = await client.get(
                    "/api/v1/list_checkpoints",
                    cast_to=dict,
                )
                return resp

        try:
            result = self.holder.run_coroutine_threadsafe(_list()).result()
            return result.get("checkpoints", []), None
        except Exception as e:
            logger.warning(
                "LIST_CHECKPOINTS_ERROR: %s: %s (resume may start from scratch)",
                type(e).__name__,
                e,
            )
            return [], None

    def resolve_checkpoint_path(
        self,
        checkpoint_name: str,
        source_job_id: str | None = None,
    ) -> str:
        """Resolve checkpoint input to a loadable checkpoint reference.

        Handles two common cases:

        1. *checkpoint_name* is already a full ``gs://`` or local path
           -- returned as-is.
        2. *source_job_id* is given -- returns an opaque cross-job
           checkpoint reference. The trainer resolves this server-side.
        3. Otherwise -- returns checkpoint_name unchanged.

        Args:
            checkpoint_name: Checkpoint name (e.g. ``"step-4"``) or a
                full GCS / local path.
            source_job_id: RLOR job ID that originally saved the
                checkpoint. When provided, the returned value is an opaque
                reference resolved on the trainer side.

        Returns:
            Loadable checkpoint reference suitable for
            ``load_state_with_optimizer()``.
        """
        # Already a full path -- nothing to resolve
        if checkpoint_name.startswith("gs://") or checkpoint_name.startswith("/"):
            return checkpoint_name

        if source_job_id:
            checkpoint_ref = make_cross_job_checkpoint_ref(
                source_job_id=source_job_id,
                checkpoint_name=checkpoint_name,
            )
            logger.info(
                "Resolved checkpoint '%s' from job '%s' into opaque reference",
                checkpoint_name,
                source_job_id,
            )
            return checkpoint_ref

        return checkpoint_name

    def save_weights_for_sampler_ext(
        self,
        name: str,
        checkpoint_type: str | None = None,
        ttl_seconds: int | None = None,
    ) -> SaveSamplerResult:
        """save_weights_for_sampler with checkpoint_type and session_id suffixing.

        The ``name`` is automatically suffixed with :attr:`session_id` so
        that the resulting GCS path is unique per training session.  This
        prevents Alluxio cache staleness when the same ``deployment_id``
        is reused across sessions.

        Passes ``checkpoint_type`` via the tinker SDK's ``extra_body``
        parameter, which merges it into the HTTP request JSON body.

        Returns:
            :class:`SaveSamplerResult` with the GCS/local ``path`` and the
            actual ``snapshot_name`` (session-suffixed).  Callers should use
            ``result.snapshot_name`` for ``hotload(snapshot_identity=...)``.
        """
        actual_name = qualify_snapshot_name(self.session_id, name)
        self._warn_if_name_reused(actual_name, self._saved_sampler_names, "Sampler")

        extra_body = {"checkpoint_type": checkpoint_type} if checkpoint_type else None
        request_id = self._get_request_id()

        async def _save():
            request = types.SaveWeightsForSamplerRequest(
                model_id=self._guaranteed_model_id(),
                path=actual_name,
                seq_id=request_id + 1,
                ttl_seconds=ttl_seconds,
            )
            start = time.time()

            async def _send():
                with self.holder.aclient(ClientConnectionPoolType.TRAIN) as client:
                    return await client.weights.save_for_sampler(
                        request=request,
                        extra_body=extra_body,
                    )

            async with self._take_turn(request_id):
                future = await self.holder.execute_with_retries(_send)
            resp = await _APIFuture(
                types.SaveWeightsForSamplerResponseInternal,
                self.holder,
                future,
                request_start_time=start,
                request_type="SaveWeightsForSampler",
                queue_state_observer=self._queue_state_logger,
            )
            assert resp.path is not None
            return resp.path

        path = self.holder.run_coroutine_threadsafe(_save()).result()
        self._saved_sampler_names.add(actual_name)
        return SaveSamplerResult(path=path, snapshot_name=actual_name)

    def save_state(
        self,
        name: str,
        ttl_seconds: int | None = None,
    ):
        """Save model weights to persistent storage (DCP checkpoint).

        Overrides the base ``save_state`` to add checkpoint-name reuse
        detection. Warns if ``name`` was already used for a DCP checkpoint
        in this session, then delegates to the parent implementation.
        """
        self._warn_if_name_reused(name, self._saved_state_names, "DCP")
        self._saved_state_names.add(name)
        return super().save_state(name, ttl_seconds=ttl_seconds)


# -- FiretitanServiceClient ----------------------------------------------------


class FiretitanServiceClient(ServiceClient):
    """ServiceClient that can create full-param (no LoRA) training clients.

    Tracks ``(base_model, lora_rank)`` pairs to detect accidental
    double-creation on the same trainer.

    Usage::

        service = FiretitanServiceClient(base_url=trainer_url, api_key=key)

        # Full-param
        client = service.create_training_client(base_model="accounts/.../qwen3-8b")

        # LoRA (same as tinker)
        client = service.create_training_client(
            base_model="accounts/.../qwen3-8b", lora_rank=32,
        )
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._created_training_configs: set[tuple[str, int]] = set()

    def create_training_client(
        self,
        base_model: str,
        lora_rank: int = 0,
        user_metadata: dict[str, str] | None = None,
    ) -> FiretitanTrainingClient:
        """Create a FiretitanTrainingClient (full-param or LoRA).

        Args:
            base_model: Model name.
            lora_rank: 0 = full-param, >0 = LoRA with that rank.
            user_metadata: Optional run metadata.

        Raises:
            ValueError: If a training client with the same (base_model, lora_rank)
                has already been created on this service instance.
        """
        config_key = (base_model, lora_rank)
        if config_key in self._created_training_configs:
            raise ValueError(
                f"A training client for '{base_model}' (lora_rank={lora_rank}) "
                f"already exists on this service. Create a new "
                f"FiretitanServiceClient for a separate trainer."
            )

        session_id = self.holder.get_session_id()
        model_seq_id = self.holder.get_training_client_id()

        lora_config = types.LoraConfig(
            rank=lora_rank,
            seed=None,
            train_mlp=True,
            train_attn=True,
            train_unembed=True,
        )

        async def _create():
            start = time.time()
            with self.holder.aclient(ClientConnectionPoolType.TRAIN) as client:
                future = await client.models.create(
                    request=types.CreateModelRequest(
                        session_id=session_id,
                        model_seq_id=model_seq_id,
                        base_model=base_model,
                        lora_config=lora_config,
                        user_metadata=user_metadata,
                    ),
                )
            resp = await _APIFuture(
                types.CreateModelResponse,
                self.holder,
                future,
                request_start_time=start,
                request_type="CreateModel",
                queue_state_observer=QueueStateLogger(base_model, "Model creation"),
            ).result_async()
            return resp.model_id

        model_id = self.holder.run_coroutine_threadsafe(_create()).result()
        self._created_training_configs.add(config_key)
        logger.info("Created model %s (lora_rank=%d)", model_id, lora_rank)

        return FiretitanTrainingClient(
            holder=self.holder,
            model_seq_id=model_seq_id,
            model_id=model_id,
        )
