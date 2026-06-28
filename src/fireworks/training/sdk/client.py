"""Firetitan Tinker SDK — thin extensions for full-param training.

This layer extends the upstream tinker client with:
  1. FiretitanServiceClient.create_training_client() — supports lora_config=None
  2. FiretitanTrainingClient.optim_step() — adds grad_accumulation_normalization
     and grad-norm metrics controls
  3. FiretitanTrainingClient.forward_backward() — backfills response_tokens for cross_entropy
  4. FiretitanTrainingClient.save_state() — supports blocking waits and guards unsupported overwrite
  5. FiretitanTrainingClient.save_weights_for_sampler_ext() — adds checkpoint_type
  6. FiretitanTrainingClient.list_checkpoints() — firetitan-specific DCP checkpoint listing
  7. FiretitanTrainingClient.load_adapter() — HF PEFT adapter warm-start (weights-only)

Most other methods (forward, forward_backward_custom, etc.) are inherited from
tinker.
"""

from __future__ import annotations

import os
import time
import uuid
import asyncio
import logging
import warnings
import threading
from enum import Enum
from typing import Any, Literal, TypeVar, Callable, Optional, NamedTuple
from datetime import datetime, timezone
from dataclasses import replace, dataclass
from collections.abc import AsyncGenerator

import httpx
from tinker import types
from pydantic import BaseModel
from transformers import AutoTokenizer
from tinker.lib.api_future_impl import _APIFuture, _CombinedAPIFuture
from tinker.lib.queue_state_logger import QueueStateLogger
from tinker.lib.client_connection_pool_type import ClientConnectionPoolType
from tinker.lib.public_interfaces.api_future import APIFuture
from tinker.lib.public_interfaces.service_client import ServiceClient
from tinker.lib.public_interfaces.training_client import (
    TrainingClient,
    combine_fwd_bwd_output_results,
)

# Explicitly apply the tinker-type patches this module depends on, rather than
# relying on the package ``__init__`` side effect. ``create_training_client``
# constructs ``types.LoraConfig(alpha=...)``, and the ``alpha`` field only
# exists after ``_tinker_lora_alpha_patch`` runs; importing it here guarantees
# the field is present whenever this module is loaded (the patch is idempotent).
import fireworks.training.sdk.patches  # noqa: F401  (applies LoraConfig.alpha + others)
from fireworks.training.sdk._constants import (
    CLEANUP_DEPLOYMENT_ON_CLOSE_DELETE,
    CLEANUP_DEPLOYMENT_ON_CLOSE_SCALE_TO_ZERO,
    DeploymentCleanupOnClose,
)
from fireworks.training.sdk.deployment import (
    DeploymentConfig,
    DeploymentManager,
    DeploymentSampler,
    FiretitanSamplingClient,
)
from fireworks.training.sdk._snapshot_chain import (
    SamplerCheckpointType,
    normalize_checkpoint_type,
    resolve_next_checkpoint_type,
)


class LoadAdapterResponse(BaseModel):
    """Response from /api/v1/load_adapter after the op completes."""

    model_id: str
    adapter_path: Optional[str] = None
    type: Literal["load_adapter"] = "load_adapter"

    model_config = {"protected_namespaces": ()}


logger = logging.getLogger(__name__)
T = TypeVar("T")
DEFAULT_FIREWORKS_API_URL = "https://api.fireworks.ai"
_INFERENCE_DEPLOYMENT_TERMINAL_STATES = frozenset({"FAILED", "DELETED", "DELETING"})
FIRETITAN_TINKER_CLIENT_CONFIG: dict[str, bool] = {
    "parallel_fwdbwd_chunks": False,
    "proto_write_fwdbwd": False,
    "proto_compress_fwdbwd": False,
    "sample_no_retries": False,
    "use_pyqwest_transport": True,
}
_TINKER_AUTH_PROVIDER_PATCH_LOCK = threading.Lock()


class _BaseOnlyCreateModelRequest(types.CreateModelRequest):
    base_only: bool = True


# Default LoRA alpha. Tinker pins alpha to this value regardless of rank; the
# FireTitan backend would otherwise default to 2 * rank, so we send it
# explicitly to keep the alpha/rank scale consistent across stacks.
DEFAULT_LORA_ALPHA = 32


class _TrainingKey(NamedTuple):
    base_model: str
    lora_rank: int
    seed: int | None
    train_mlp: bool
    train_attn: bool
    train_unembed: bool
    lora_alpha: int | None


class _MappedAPIFuture(APIFuture[T]):
    """Apply a post-processing transform to another API future."""

    def __init__(self, inner: APIFuture[T], transform: Callable[[T], T]):
        self._inner = inner
        self._transform = transform

    def result(self, timeout: float | None = None) -> T:
        return self._transform(self._inner.result(timeout))

    async def result_async(self, timeout: float | None = None) -> T:
        return self._transform(await self._inner.result_async(timeout))

    def __await__(self):
        return self.result_async().__await__()


class _FireworksApiKeyAuthProvider(httpx.Auth):
    """Tinker auth provider that accepts Fireworks API keys for FireTitan.

    Tinker 0.22.x validates API keys before sending requests and only accepts
    ``tml-`` keys or JWTs. FireTitan trainer endpoints are authenticated by the
    Fireworks control plane, which expects Fireworks API keys on ``X-API-Key``.
    """

    def __init__(self, api_key: str):
        self._api_key = api_key

    async def async_auth_flow(
        self,
        request: httpx.Request,
    ) -> AsyncGenerator[httpx.Request, httpx.Response]:
        request.headers["X-API-Key"] = self._api_key
        yield request


class _ImmediateAPIFuture(APIFuture[T]):
    """Already-completed API future for compatibility wrappers."""

    def __init__(self, value: T):
        self._value = value

    def result(self, timeout: float | None = None) -> T:
        return self._value

    async def result_async(self, timeout: float | None = None) -> T:
        return self._value

    def __await__(self):
        return self.result_async().__await__()


class _FailedAPIFuture(APIFuture[T]):
    """Future that fails with a known exception when awaited or resolved."""

    def __init__(self, error: Exception):
        self._error = error

    def result(self, timeout: float | None = None) -> T:
        raise self._error

    async def result_async(self, timeout: float | None = None) -> T:
        raise self._error

    def __await__(self):
        return self.result_async().__await__()


class _LazyManagedRestClient:
    """Small REST metadata shim before a managed Tinker session exists."""

    def __init__(
        self,
        managed_config: Any,
        user_metadata: dict[str, str] | None = None,
    ):
        self._managed_config = managed_config
        self._user_metadata = dict(user_metadata or {})

    def _model_owner(self) -> str:
        parts = self._managed_config.base_model.split("/")
        if len(parts) >= 2 and parts[0] == "accounts":
            return parts[1]
        return "fireworks"

    def _training_run_id(self) -> str:
        return self._managed_config.trainer_job_id or "firetitan-managed"

    def _training_run(self) -> types.TrainingRun:
        is_lora = self._managed_config.lora_rank > 0
        return types.TrainingRun(
            training_run_id=self._training_run_id(),
            base_model=self._managed_config.base_model,
            model_owner=self._model_owner(),
            is_lora=is_lora,
            lora_rank=self._managed_config.lora_rank if is_lora else None,
            last_request_time=datetime.now(timezone.utc),
            user_metadata=self._user_metadata,
        )

    def _weights_info(self) -> types.WeightsInfoResponse:
        is_lora = self._managed_config.lora_rank > 0
        return types.WeightsInfoResponse(
            base_model=self._managed_config.base_model,
            is_lora=is_lora,
            lora_rank=self._managed_config.lora_rank if is_lora else None,
            train_unembed=self._managed_config.train_unembed,
            train_mlp=self._managed_config.train_mlp,
            train_attn=self._managed_config.train_attn,
        )

    @staticmethod
    def _cursor(limit: int, offset: int) -> types.Cursor:
        return types.Cursor(offset=offset, limit=limit, total_count=0)

    def _unsupported(self, method: str) -> NotImplementedError:
        return NotImplementedError(
            f"FireTitan lazy managed REST client does not support {method}. "
            "Create a trainer-backed service client or use Fireworks checkpoint APIs for this operation."
        )

    def _unsupported_future(self, method: str) -> _FailedAPIFuture[Any]:
        return _FailedAPIFuture(self._unsupported(method))

    def get_training_run(self, training_run_id: str, access_scope: str = "owned"):
        return _ImmediateAPIFuture(self._training_run())

    async def get_training_run_async(
        self,
        training_run_id: str,
        access_scope: str = "owned",
    ):
        return self._training_run()

    def get_training_run_by_tinker_path(
        self,
        path: str,
        access_scope: str = "owned",
    ):
        return _ImmediateAPIFuture(self._training_run())

    async def get_training_run_by_tinker_path_async(
        self,
        path: str,
        access_scope: str = "owned",
    ):
        return self._training_run()

    def get_weights_info_by_tinker_path(self, path: str):
        return _ImmediateAPIFuture(self._weights_info())

    def list_training_runs(
        self,
        limit: int = 20,
        offset: int = 0,
        access_scope: str = "owned",
    ):
        return _ImmediateAPIFuture(
            types.TrainingRunsResponse(
                training_runs=[self._training_run()],
                cursor=self._cursor(limit, offset),
            )
        )

    async def list_training_runs_async(
        self,
        limit: int = 20,
        offset: int = 0,
        access_scope: str = "owned",
    ):
        return self.list_training_runs(
            limit=limit,
            offset=offset,
            access_scope=access_scope,
        ).result()

    def list_checkpoints(self, training_run_id: str):
        return _ImmediateAPIFuture(
            types.CheckpointsListResponse(
                checkpoints=[],
                cursor=self._cursor(100, 0),
            )
        )

    async def list_checkpoints_async(self, training_run_id: str):
        return self.list_checkpoints(training_run_id).result()

    def list_user_checkpoints(self, limit: int = 100, offset: int = 0):
        return _ImmediateAPIFuture(
            types.CheckpointsListResponse(
                checkpoints=[],
                cursor=self._cursor(limit, offset),
            )
        )

    async def list_user_checkpoints_async(self, limit: int = 100, offset: int = 0):
        return self.list_user_checkpoints(limit=limit, offset=offset).result()

    def get_session(self, session_id: str, access_scope: str = "owned"):
        return _ImmediateAPIFuture(types.GetSessionResponse(training_run_ids=[], sampler_ids=[]))

    async def get_session_async(self, session_id: str, access_scope: str = "owned"):
        return self.get_session(session_id, access_scope=access_scope).result()

    def list_sessions(
        self,
        limit: int = 20,
        offset: int = 0,
        access_scope: str = "owned",
    ):
        return _ImmediateAPIFuture(types.ListSessionsResponse(sessions=[]))

    async def list_sessions_async(
        self,
        limit: int = 20,
        offset: int = 0,
        access_scope: str = "owned",
    ):
        return self.list_sessions(
            limit=limit,
            offset=offset,
            access_scope=access_scope,
        ).result()

    def get_sampler(self, sampler_id: str):
        return _ImmediateAPIFuture(
            types.GetSamplerResponse(
                sampler_id=sampler_id,
                base_model=self._managed_config.base_model,
                model_path=None,
            )
        )

    async def get_sampler_async(self, sampler_id: str):
        return self.get_sampler(sampler_id).result()

    def get_checkpoint_archive_url(self, training_run_id: str, checkpoint_id: str):
        return self._unsupported_future("get_checkpoint_archive_url")

    async def get_checkpoint_archive_url_async(
        self,
        training_run_id: str,
        checkpoint_id: str,
    ):
        raise self._unsupported("get_checkpoint_archive_url_async")

    def get_checkpoint_archive_url_from_tinker_path(self, tinker_path: str):
        return self._unsupported_future("get_checkpoint_archive_url_from_tinker_path")

    async def get_checkpoint_archive_url_from_tinker_path_async(self, tinker_path: str):
        raise self._unsupported("get_checkpoint_archive_url_from_tinker_path_async")

    def get_audit_log(
        self,
        event_type: Literal["all", "checkpoints"] = "all",
        day: Any | None = None,
    ):
        return self._unsupported_future("get_audit_log")

    async def get_audit_log_async(
        self,
        event_type: Literal["all", "checkpoints"] = "all",
        day: Any | None = None,
    ):
        raise self._unsupported("get_audit_log_async")

    def assign_session_project(self, session_id: str, project_id: str):
        return self._unsupported_future("assign_session_project")

    async def assign_session_project_async(self, session_id: str, project_id: str) -> None:
        raise self._unsupported("assign_session_project_async")

    def delete_checkpoint_from_tinker_path(self, path: str):
        return _ImmediateAPIFuture(None)

    async def delete_checkpoint_from_tinker_path_async(self, path: str) -> None:
        return None

    def delete_checkpoint(self, training_run_id: str, checkpoint_id: str):
        return _ImmediateAPIFuture(None)

    async def delete_checkpoint_async(
        self,
        training_run_id: str,
        checkpoint_id: str,
    ) -> None:
        return None

    def publish_checkpoint_from_tinker_path(self, tinker_path: str):
        return self._unsupported_future("publish_checkpoint_from_tinker_path")

    async def publish_checkpoint_from_tinker_path_async(self, tinker_path: str):
        raise self._unsupported("publish_checkpoint_from_tinker_path_async")

    def unpublish_checkpoint_from_tinker_path(self, tinker_path: str):
        return self._unsupported_future("unpublish_checkpoint_from_tinker_path")

    async def unpublish_checkpoint_from_tinker_path_async(self, tinker_path: str):
        raise self._unsupported("unpublish_checkpoint_from_tinker_path_async")

    def set_checkpoint_ttl_from_tinker_path(
        self,
        tinker_path: str,
        ttl_seconds: int | None,
    ):
        return self._unsupported_future("set_checkpoint_ttl_from_tinker_path")

    async def set_checkpoint_ttl_from_tinker_path_async(
        self,
        tinker_path: str,
        ttl_seconds: int | None,
    ):
        raise self._unsupported("set_checkpoint_ttl_from_tinker_path_async")

    def get_telemetry(self) -> None:
        return None


class GradAccNormalization(str, Enum):
    """Gradient accumulation normalization modes for ``optim_step``."""

    NUM_LOSS_TOKENS = "num_loss_tokens"
    """Divide accumulated gradients by total non-zero-grad tokens (per-token mean)."""
    NUM_SEQUENCES = "num_sequences"
    """Divide accumulated gradients by total sequences with non-zero grads (per-sequence mean)."""
    NONE = "none"
    """No normalization -- gradients used as-is."""


class GradNormMetricsMode(str, Enum):
    """Trainer-side grad-norm metric emission modes for ``optim_step``."""

    OFF = "off"
    """Do not compute or emit grad-norm metrics."""
    BASIC = "basic"
    """Emit global/RMS grad-norm metrics only."""
    DETAILED = "detailed"
    """Emit global/RMS grad-norm metrics plus coarse parameter buckets."""


def _grad_accumulation_normalization_value(
    value: GradAccNormalization | str | None,
) -> str | None:
    if value is None:
        return None
    if isinstance(value, GradAccNormalization):
        return value.value
    try:
        return GradAccNormalization(str(value).lower()).value
    except ValueError as exc:
        valid = ", ".join(mode.value for mode in GradAccNormalization)
        raise ValueError(f"Unknown grad_accumulation_normalization {value!r}; expected one of: {valid}") from exc


def _grad_norm_metrics_mode_value(
    value: GradNormMetricsMode | bool | str | None,
) -> bool | str | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, GradNormMetricsMode):
        return value.value
    try:
        return GradNormMetricsMode(str(value).lower()).value
    except ValueError as exc:
        valid = ", ".join(mode.value for mode in GradNormMetricsMode)
        raise ValueError(
            f"Unknown emit_grad_norm_metrics {value!r}; expected bool or one of: {valid}"
        ) from exc


def _pop_alias(
    values: dict[str, Any],
    canonical: str,
    *aliases: str,
) -> None:
    present_aliases = [alias for alias in aliases if alias in values]
    if canonical in values and present_aliases:
        alias_list = ", ".join(present_aliases)
        raise ValueError(f"Pass either {canonical!r} or alias {alias_list}, not both")
    if len(present_aliases) > 1:
        alias_list = ", ".join(present_aliases)
        raise ValueError(f"Pass only one alias for {canonical!r}; got {alias_list}")
    if present_aliases:
        values[canonical] = values.pop(present_aliases[0])


def _managed_config_from_kwargs(kwargs: dict[str, Any]):
    """Build a ``FiretitanProvisioningConfig`` from recipe kwargs.

    Resolves alias names, then drops the deprecated trainer accelerator fields
    with a ``DeprecationWarning`` (the training shape owns accelerator
    selection; use ``trainer_replica_count`` for data-parallel trainer scaling).
    """
    from fireworks.training.sdk.managed import FiretitanProvisioningConfig

    _pop_alias(kwargs, "base_model", "model_name")
    _pop_alias(kwargs, "training_shape_id", "training_shape", "training_shape_ref")
    _pop_alias(kwargs, "trainer_job_id", "trainer_id")
    _pop_alias(kwargs, "replica_count", "deployment_replica_count")
    for optional_ref_field in ("reference_training_shape_id", "reference_trainer_job_id"):
        if kwargs.get(optional_ref_field) == "":
            kwargs[optional_ref_field] = None
    for infra_field in ("accelerator_type", "accelerator_count", "node_count"):
        if kwargs.pop(infra_field, None) is not None:
            warnings.warn(
                f"{infra_field!r} is deprecated and ignored: trainer infrastructure "
                "is configured by the training shape. Use "
                "'trainer_replica_count' for data-parallel scaling.",
                DeprecationWarning,
                stacklevel=3,
            )
    return FiretitanProvisioningConfig(**kwargs)


def _warn_deprecated_override(method: str, field: str, passed: Any, configured: Any) -> None:
    """Warn that a managed-service-configured value was overridden at create time.

    ``base_model``/``lora_rank`` are owned by the managed service config; passing
    a different value to ``create_training_client`` / ``create_reference_client``
    is deprecated and ignored (the service config is authoritative). All such
    override deprecation warnings route through this one helper. (The deprecated
    trainer accelerator fields are a different shape — they are dropped at config
    build time in ``_managed_config_from_kwargs``.)
    """
    if configured is not None and passed is not None and passed != configured:
        warnings.warn(
            f"{field}={passed!r} passed to {method} differs from the service-configured "
            f"{field}={configured!r}; this override is deprecated and ignored — the service "
            "config is authoritative. Create a separate FiretitanServiceClient for a "
            "different training configuration.",
            DeprecationWarning,
            stacklevel=3,
        )


def _is_serverless_session_id(session_id: Any) -> bool:
    """True for a CP-minted serverless training session id (``ts-<hex>``).

    The serverless gateway mints these at ``create_session``; managed / dedicated
    direct trainers use a different id shape, so the CP training-session resource
    name only applies to ``ts-`` sessions.
    """
    return isinstance(session_id, str) and session_id.startswith("ts-")


def _run_id_from_model_id(model_id: Any) -> str | None:
    """The CP run id from a run-scoped ``model_id`` (``{run_id}:train:{seq}``).

    The control plane owns ``run_id`` (``run-<hex>``); the trainer owns the
    ``:train:<seq>`` suffix. Returns None for non-run-scoped ids (base-only
    reference models, managed / dedicated trainers).
    """
    if not isinstance(model_id, str):
        return None
    run_id, sep, _ = model_id.partition(":train:")
    return run_id if sep and run_id.startswith("run-") else None


def _create_base_only_training_client(
    holder: Any,
    base_model: str,
    user_metadata: dict[str, str] | None,
    *,
    request_type: str,
) -> FiretitanTrainingClient:
    session_id = holder.get_session_id()
    model_seq_id = holder.get_training_client_id()

    async def _create():
        start = time.time()
        with holder.aclient(ClientConnectionPoolType.TRAIN) as client:
            future = await client.models.create(
                request=_BaseOnlyCreateModelRequest(
                    session_id=session_id,
                    model_seq_id=model_seq_id,
                    base_model=base_model,
                    base_only=True,
                    user_metadata=user_metadata,
                ),
            )
        resp = await _APIFuture(
            types.CreateModelResponse,
            holder,
            future,
            request_start_time=start,
            request_type=request_type,
            queue_state_observer=QueueStateLogger(base_model, "Base model creation"),
        ).result_async()
        return resp.model_id

    model_id = holder.run_coroutine_threadsafe(_create()).result()
    logger.info("Created base-only model %s (reference)", model_id)
    # Base-only reference models are not run-scoped (model_id is a base id), so
    # they have no run_name; the owning session lives on the service client.
    return FiretitanTrainingClient(
        holder=holder,
        model_seq_id=model_seq_id,
        model_id=model_id,
        lora_rank=0,
    )


def _fireworks_api_key(api_key: str | None) -> str | None:
    if api_key is not None:
        return api_key
    return os.environ.get("FIREWORKS_API_KEY")


def _fireworks_base_url(base_url: str | None) -> str:
    return base_url or os.environ.get("FIREWORKS_BASE_URL") or DEFAULT_FIREWORKS_API_URL


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


def _count_response_tokens(data: list[types.Datum]) -> float:
    """Count response tokens in a cross-entropy batch.

    Prefer non-zero ``weights`` when present, since those mark exactly which
    shifted target positions contribute to the loss. Fall back to the length of
    ``target_tokens`` if no weights were supplied.
    """
    total = 0.0
    for datum in data:
        loss_fn_inputs = datum.loss_fn_inputs
        weights = loss_fn_inputs.get("weights")
        if weights is not None:
            total += float(sum(1 for value in weights.data if value != 0))
            continue

        target_tokens = loss_fn_inputs.get("target_tokens")
        if target_tokens is not None:
            total += float(len(target_tokens.data))

    return total


def _add_cross_entropy_response_tokens(
    output: types.ForwardBackwardOutput,
    *,
    data: list[types.Datum],
) -> types.ForwardBackwardOutput:
    if "response_tokens" in output.metrics:
        return output

    output.metrics["response_tokens"] = _count_response_tokens(data)
    return output


def _dump_tinker_model(obj: Any) -> Any:
    if hasattr(obj, "model_dump"):
        return obj.model_dump(exclude_unset=True, mode="json")
    if hasattr(obj, "dict"):
        return obj.dict(exclude_unset=True)
    return obj


def _serialize_input_for_extra_body(fb_input: Any) -> dict:
    """Convert a tinker public ``ForwardBackwardInput`` (or ``ForwardInput`` —
    same shape) to a JSON-safe dict suitable for ``extra_body`` override.

    tinker 0.22+ split public types (Datum, ModelInput, ForwardBackwardInput,
    EncodedTextChunk, ...) into plain dataclasses with internal pydantic mirrors.
    ``dataclasses.asdict`` can't recurse through the mixed dataclass/pydantic/
    typed-dict tree, but tinker's own ``to_pydantic_input`` does the full
    conversion and the result is a normal pydantic BaseModel that ``model_dump``
    knows how to JSON-encode.

    This is a temporary hack so the embedding APIs work against tinker 0.22.2;
    a proper fix at ``_dump_tinker_model`` should land in a follow-up PR.
    """
    from tinker._compat import model_dump as _tinker_model_dump
    from tinker.lib._pydantic_conv import to_pydantic_input
    return _tinker_model_dump(
        to_pydantic_input(fb_input),
        mode="json",
        exclude_none=True,
    )


def _text_token_count(datum: types.Datum) -> int:
    raw_datum = _dump_tinker_model(datum)
    model_input = raw_datum.get("model_input", {})
    return sum(
        len(chunk.get("tokens", []))
        for chunk in model_input.get("chunks", [])
        if chunk.get("type", "encoded_text") == "encoded_text"
    )


def _pool_embedding_tensor(
    embedding,
    datum: types.Datum,
    pooling: Literal["mean", "last"],
):
    if embedding.ndim <= 1:
        return embedding
    token_count = _text_token_count(datum)
    if token_count <= 0:
        raise ValueError("Cannot pool embedding from an empty text sequence")
    token_embeddings = embedding[:token_count]
    if pooling == "mean":
        return token_embeddings.mean(dim=0)
    if pooling == "last":
        return token_embeddings[-1]
    raise ValueError(f"Unsupported pooling={pooling!r}; expected 'mean' or 'last'")


def _check_cos_similarity_matrix_single_chunk(
    chunks: list, *, output: str,
) -> None:
    """Guard ``cos_similarity_matrix`` against silent batch-splitting.

    The trainer builds ``S = Z @ Z.T`` over the per-HTTP-request batch
    (``B_local``), so if the SDK split ``data`` across multiple chunks each
    chunk would only see its own datums and every cross-chunk similarity
    would be dropped — a client ``loss_fn`` that stacks the returned rows
    into a single ``[N, N]`` matrix would then be wrong without any error.

    This function is called with the *natural* chunking the SDK would
    otherwise produce (``MAX_CHUNK_LEN = 1024`` and
    ``MAX_CHUNK_BYTES_COUNT = 5_000_000``). If that produces more than one
    chunk, we raise with a clear remediation hint instead of issuing
    multiple sub-batch similarity matrices.

    Stateless on purpose: takes the already-computed chunk list so it can
    be unit-tested without standing up a real ``FiretitanTrainingClient``.
    """
    if len(chunks) > 1:
        sizes = [len(c) for c in chunks]
        raise ValueError(
            f"output={output!r} requires the entire batch to fit in a single "
            f"HTTP request because the trainer computes the similarity matrix "
            f"S = Z @ Z.T over the per-request batch — splitting across "
            f"chunks would silently drop every cross-chunk pair. "
            f"len(data)={sum(sizes)} would otherwise be split into "
            f"{len(chunks)} chunks of sizes {sizes} "
            f"(SDK caps: MAX_CHUNK_LEN=1024, MAX_CHUNK_BYTES_COUNT=5_000_000). "
            f"Options: (a) reduce len(data) so it fits in one chunk; "
            f"(b) switch to output='contrastive_loss' (server-side InfoNCE, "
            f"no client-side matrix assembly); or (c) switch to "
            f"output='embedding' (per-datum and therefore chunk-safe)."
        )


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


SAMPLING_CLIENT_FROM_TRAINER_MESSAGE = (
    "FiretitanTrainingClient does not support save_weights_and_get_sampling_client(). "
    "Fireworks serves sampling from a separate hot-load inference deployment, not from "
    "an in-service ephemeral sampling session as Tinker's managed service does. Save a "
    "sampler snapshot and open a sampling client against the deployment instead:\n"
    "    saved = training_client.save_weights_for_sampler(name).result()\n"
    "    sampler = service.create_sampling_client(model_path=saved.path)\n"
    "The SDK resolves base vs. delta hot-load automatically from the snapshot chain."
)


class FiretitanTrainingClient(TrainingClient):
    """TrainingClient with firetitan-specific extensions.

    Adds:
      - save_weights_for_sampler_ext(): checkpoint_type support + session_id suffixing
      - list_checkpoints(): DCP checkpoint listing from the trainer
      - Checkpoint name reuse detection (warns on duplicate names within a session)
      - Session-scoped snapshot name qualification (prevents Alluxio cache staleness)
      - run_id / run_name: the CP serverless training run this model is
        (``run-<hex>`` / ``accounts/<a>/trainingRuns/<run_id>``), parsed from
        ``model_id``; what run-based routing and checkpoints key on. None for
        non-run-scoped models. The owning *session* lives on the service client.

    A unique ``session_id`` is generated on creation.  All sampler snapshot
    names are automatically suffixed with it in
    :meth:`save_weights_for_sampler_ext`, ensuring GCS paths never collide
    across training sessions that share the same ``deployment_id``.

    Overrides:
      - optim_step(): adds ``grad_accumulation_normalization`` parameter
      - forward_backward(): backfills ``response_tokens`` for ``cross_entropy``
      - save_state(): supports blocking waits and rejects unsupported overwrite
      - load_state()/load_state_with_optimizer(): reject unsupported cross-account tokens
      - get_tokenizer(): loads from the managed tokenizer_model name, no get_info RPC
      - save_weights_and_get_sampling_client(): raises NotImplementedError —
        Fireworks samples from a separate hot-load deployment, not an in-service
        ephemeral sampling session (see SAMPLING_CLIENT_FROM_TRAINER_MESSAGE)

    The async/sync surface is otherwise complete by inheritance: the base
    ``forward_backward_async`` / ``save_state_async`` wrappers call our
    overridden sync methods, so they pick up FireTitan behavior unchanged.
    Other core methods (forward, forward_backward_custom) are inherited from
    tinker.TrainingClient.
    """

    def __init__(
        self,
        holder,
        model_seq_id: int,
        model_id,
        *,
        lora_rank: int = 0,
        first_sampler_checkpoint_type: SamplerCheckpointType = "base",
        run_name: str | None = None,
    ):
        super().__init__(holder=holder, model_seq_id=model_seq_id, model_id=model_id)
        # Full CP resource name of the serverless training run this model is, i.e.
        # accounts/<a>/trainingRuns/<run_id>. ``run_id`` is exposed as a property
        # derived from ``model_id`` ("{run_id}:train:{seq}"). Both are None for
        # non-serverless / non-run-scoped models (managed, dedicated, base-only).
        # The owning *session* lives on the FiretitanServiceClient, not here — one
        # session holds many runs (1:N). Distinct from ``self.session_id`` below,
        # a local id used only to disambiguate sampler snapshot names.
        self.run_name: str | None = run_name
        # Track checkpoint names to detect reuse within a session.
        # Sampler and state names are tracked separately because the same name
        # (e.g., "step-4") is intentionally used for both — they are different
        # storage types.
        self._saved_sampler_names: set[str] = set()
        self._saved_state_names: set[str] = set()
        self._sampler_backend: Any | None = None
        self._tokenizer_model: str | None = None
        self._lora_rank = lora_rank
        self._sampler_checkpoint_saved = False
        self._first_sampler_checkpoint_type = self._normalize_sampler_checkpoint_type(first_sampler_checkpoint_type)

        # Unique session identifier — appended to all sampler snapshot names
        # so that GCS paths are unique even when the deployment_id is reused.
        self.session_id: str = generate_session_id()
        logger.info("FiretitanTrainingClient session_id: %s", self.session_id)

    @property
    def run_id(self) -> str | None:
        """The CP serverless training run id (``run-<hex>``) this model is, parsed
        from ``model_id`` (``{run_id}:train:{seq}``). None for non-run-scoped
        models (managed / dedicated / base-only)."""
        return _run_id_from_model_id(self.model_id)

    def _attach_sampler_backend(self, backend: Any) -> "FiretitanTrainingClient":
        """Attach SDK-owned sampler backend state to this training client."""
        self._sampler_backend = backend
        return self

    def _require_sampler_backend(self) -> Any:
        if self._sampler_backend is None:
            raise NotImplementedError(
                "FiretitanTrainingClient sampling requires SDK-managed sampler state. "
                "Create the client through the FireTitan SDK Tinker compatibility path."
            )
        return self._sampler_backend

    def _warn_if_name_reused(self, name: str, names_set: set[str], kind: str) -> None:
        """Log a warning if a checkpoint name has already been used."""
        if name in names_set:
            logger.warning(
                "%s checkpoint name '%s' already used in this session — overwriting",
                kind,
                name,
            )

    @staticmethod
    def _normalize_sampler_checkpoint_type(checkpoint_type: str | None) -> SamplerCheckpointType | None:
        return normalize_checkpoint_type(checkpoint_type)

    def _next_sampler_checkpoint_type(self, checkpoint_type: str | None = None) -> SamplerCheckpointType:
        return resolve_next_checkpoint_type(
            lora_rank=self._lora_rank,
            base_saved=self._sampler_checkpoint_saved,
            first_checkpoint_type=self._first_sampler_checkpoint_type or "base",
            explicit=checkpoint_type,
        )

    def optim_step(
        self,
        adam_params: types.AdamParams,
        grad_accumulation_normalization: GradAccNormalization | str | None = None,
        emit_grad_norm_metrics: GradNormMetricsMode | bool | str | None = None,
    ):
        """Update model parameters using Adam optimizer.

        Extends the base ``optim_step`` with ``grad_accumulation_normalization``
        to normalize accumulated gradients before clipping and stepping, and
        with ``emit_grad_norm_metrics`` to opt in to trainer-side grad-norm
        telemetry.

        The default is ``None`` (no server-side normalization). Callers whose
        loss function returns a **raw sum** (e.g. RL/GRPO) should pass
        ``GradAccNormalization.NUM_LOSS_TOKENS`` so the server divides by
        total loss tokens.  Callers whose loss function already returns a
        per-token or per-sequence mean (e.g. SFT, DPO, ORPO) should leave
        this as ``None`` to avoid double-normalization.

        Args:
            adam_params: Adam optimizer parameters.
            grad_accumulation_normalization: Server-side normalization mode.
                ``None``: no normalization (default, safe for pre-normalized losses).
                ``GradAccNormalization.NUM_LOSS_TOKENS``: per-token mean
                (use with raw-sum losses like GRPO).
                ``GradAccNormalization.NUM_SEQUENCES``: per-sequence mean.
                ``GradAccNormalization.NONE``: explicit no-op (same as ``None``).
            emit_grad_norm_metrics: Optional grad-norm telemetry mode.
                ``None``: use ``adam_params.emit_grad_norm_metrics`` if set;
                otherwise omit the field, which defaults to off on the trainer.
                ``False``/``GradNormMetricsMode.OFF``: explicitly off.
                ``True``/``GradNormMetricsMode.BASIC``: global/RMS metrics only.
                ``GradNormMetricsMode.DETAILED``: global/RMS plus bucket metrics.
        """
        extra_body: dict = {}
        normalization_value = _grad_accumulation_normalization_value(grad_accumulation_normalization)
        if normalization_value is not None:
            extra_body["grad_accumulation_normalization"] = normalization_value
        grad_norm_metrics_value = _grad_norm_metrics_mode_value(emit_grad_norm_metrics)
        if grad_norm_metrics_value is not None:
            adam_params = adam_params.model_copy(
                update={"emit_grad_norm_metrics": grad_norm_metrics_value}
            )
        request_id = self._get_request_id()

        async def _optim_step_async():
            start = time.time()

            async def _send():
                request = types.OptimStepRequest(
                    adam_params=adam_params,
                    model_id=self._guaranteed_model_id(),
                    seq_id=request_id + 1,
                )
                with self.holder.aclient(ClientConnectionPoolType.TRAIN) as client:
                    return await client.training.optim_step(
                        request=request,
                        extra_body=extra_body,
                    )

            async with self._take_turn(request_id):
                future = await self.holder.execute_with_retries(_send)
            return await _APIFuture(
                types.OptimStepResponse,
                self.holder,
                future,
                request_start_time=start,
                request_type="OptimStep",
                queue_state_observer=self._queue_state_logger,
            )

        return self.holder.run_coroutine_threadsafe(_optim_step_async())

    async def optim_step_async(
        self,
        adam_params: types.AdamParams,
        grad_accumulation_normalization: GradAccNormalization | str | None = None,
        emit_grad_norm_metrics: GradNormMetricsMode | bool | str | None = None,
    ) -> APIFuture[types.OptimStepResponse]:
        return self.optim_step(
            adam_params,
            grad_accumulation_normalization=grad_accumulation_normalization,
            emit_grad_norm_metrics=emit_grad_norm_metrics,
        )

    def forward_backward(
        self,
        data: list[types.Datum],
        loss_fn: types.LossFnType,
        loss_fn_config: dict[str, float] | None = None,
    ) -> APIFuture[types.ForwardBackwardOutput]:
        holder = getattr(self, "holder", None)
        client_config = getattr(holder, "_client_config", None)
        proto_write = getattr(client_config, "proto_write_fwdbwd", False)
        proto_compress = getattr(client_config, "proto_compress_fwdbwd", False)
        if proto_write or proto_compress:
            raise NotImplementedError(
                "FiretitanTrainingClient does not support Tinker's proto forward_backward transport. "
                "Use the JSON forward_backward path."
            )
        if getattr(client_config, "parallel_fwdbwd_chunks", False):
            client_config.parallel_fwdbwd_chunks = False
        future = super().forward_backward(data, loss_fn, loss_fn_config)
        if loss_fn != "cross_entropy":
            return future

        return _MappedAPIFuture(
            future,
            lambda output: _add_cross_entropy_response_tokens(output, data=data),
        )

    async def _send_single_forward_embedding_request(
        self,
        request_id: int,
        data: list[types.Datum],
        pooling: Literal["mean", "last"],
        output: Literal["embedding", "cos_similarity_matrix"] = "embedding",
    ):
        fwd_input = types.ForwardBackwardInput(
            data=data,
            loss_fn="cross_entropy",
            loss_fn_config=None,
        )
        request = types.ForwardRequest(
            forward_input=fwd_input,
            model_id=self._guaranteed_model_id(),
            seq_id=request_id + 1,
        )
        # tinker 0.22+ requires the to_pydantic_input dance for JSON wire safety.
        fwd_input_dict = _serialize_input_for_extra_body(fwd_input)
        fwd_input_dict["loss_fn_config"] = {"output": output, "pooling": pooling}
        extra_body = {"forward_input": fwd_input_dict}
        with self.holder.aclient(ClientConnectionPoolType.TRAIN) as client:
            return await client.training.forward(
                request=request,
                extra_body=extra_body,
            )

    async def _send_single_forward_backward_embedding_request(
        self,
        request_id: int,
        data: list[types.Datum],
        pooling: Literal["mean", "last"],
        output: Literal["embedding", "cos_similarity_matrix"] = "embedding",
    ):
        fb_input = types.ForwardBackwardInput(
            data=data,
            loss_fn="cross_entropy",
            loss_fn_config=None,
        )
        request = types.ForwardBackwardRequest(
            forward_backward_input=fb_input,
            model_id=self._guaranteed_model_id(),
            seq_id=request_id + 1,
        )
        # tinker 0.22+ requires the to_pydantic_input dance for JSON wire safety.
        fb_input_dict = _serialize_input_for_extra_body(fb_input)
        fb_input_dict["loss_fn_config"] = {"output": output, "pooling": pooling}
        extra_body = {"forward_backward_input": fb_input_dict}
        with self.holder.aclient(ClientConnectionPoolType.TRAIN) as client:
            return await client.training.forward_backward(
                request=request,
                extra_body=extra_body,
            )

    def _build_embedding_requests(
        self,
        data: list[types.Datum],
        output: Literal["embedding", "cos_similarity_matrix"],
    ) -> list[tuple[int, list[types.Datum]]]:
        # ``embedding`` is per-datum and chunk-safe — split via the inherited
        # chunked-requests helper to respect MAX_CHUNK_LEN / MAX_CHUNK_BYTES.
        # ``cos_similarity_matrix`` is fundamentally single-request: the trainer
        # builds ``S = Z @ Z.T`` over the per-request (B_local) batch, so any
        # split would silently drop every cross-chunk similarity. Pre-check the
        # natural chunking and refuse if it would split, then send as one HTTP
        # request with the full batch.
        if output != "cos_similarity_matrix":
            return self._chunked_requests(data)
        natural_chunks = list(self._chunked_requests_generator(data))
        _check_cos_similarity_matrix_single_chunk(natural_chunks, output=output)
        return [(self._get_request_id(), data)]

    async def _forward_embedding_async(
        self,
        data: list[types.Datum],
        pooling: Literal["mean", "last"],
        output: Literal["embedding", "cos_similarity_matrix"] = "embedding",
    ) -> APIFuture[types.ForwardBackwardOutput]:
        requests = self._build_embedding_requests(data, output)
        futures = []
        start_time = time.time()
        for request_id, chunk in requests:
            async with self._take_turn(request_id):
                untyped_future = await self.holder.execute_with_retries(
                    self._send_single_forward_embedding_request,
                    request_id,
                    chunk,
                    pooling,
                    output,
                )
            futures.append(
                _APIFuture(
                    types.ForwardBackwardOutput,
                    self.holder,
                    untyped_future,
                    request_start_time=start_time,
                    request_type="Forward",
                    queue_state_observer=self._queue_state_logger,
                )
            )
        return _CombinedAPIFuture(futures, combine_fwd_bwd_output_results, self.holder)

    async def _forward_backward_embedding_async(
        self,
        data: list[types.Datum],
        pooling: Literal["mean", "last"],
        output: Literal["embedding", "cos_similarity_matrix"] = "embedding",
    ) -> APIFuture[types.ForwardBackwardOutput]:
        requests = self._build_embedding_requests(data, output)
        futures = []
        start_time = time.time()
        for request_id, chunk in requests:
            async with self._take_turn(request_id):
                untyped_future = await self.holder.execute_with_retries(
                    self._send_single_forward_backward_embedding_request,
                    request_id,
                    chunk,
                    pooling,
                    output,
                )
            futures.append(
                _APIFuture(
                    types.ForwardBackwardOutput,
                    self.holder,
                    untyped_future,
                    request_start_time=start_time,
                    request_type="ForwardBackward",
                    queue_state_observer=self._queue_state_logger,
                )
            )
        return _CombinedAPIFuture(futures, combine_fwd_bwd_output_results, self.holder)

    async def forward_backward_custom_async(
        self,
        data: list[types.Datum],
        loss_fn: Callable,
        *,
        loss_type_input: Literal["logprobs"] = "logprobs",
        output: Literal["logprobs", "embedding", "cos_similarity_matrix"] = "logprobs",
        pooling: Literal["mean", "last"] = "mean",
    ) -> APIFuture[types.ForwardBackwardOutput]:
        if output == "logprobs":
            return await super().forward_backward_custom_async(
                data,
                loss_fn,
                loss_type_input=loss_type_input,
            )
        if output not in ("embedding", "cos_similarity_matrix"):
            raise ValueError(
                f"Unsupported output={output!r}; expected 'logprobs', 'embedding', or 'cos_similarity_matrix'"
            )
        if loss_type_input != "logprobs":
            raise ValueError(
                f"Set output='{output}' instead of loss_type_input for embedding/cos_similarity_matrix custom loss."
            )
        if pooling not in ("mean", "last"):
            raise ValueError(f"Unsupported pooling={pooling!r}; expected 'mean' or 'last'")

        try:
            import torch
        except ImportError as err:
            raise ImportError("PyTorch is not installed. Cannot run custom forward_backward.") from err

        # For cos_similarity_matrix mode, the trainer returns rows of a [B, B] similarity
        # matrix (each datum's "embedding" field has length B = the batch size,
        # NOT the hidden dim D). Functionally identical client-side handling:
        # the user's loss_fn stacks the per-datum tensors back into a [B, B]
        # matrix and computes its loss against that. Backward gives each row a
        # gradient of length B, which we ship back as embedding_grads (the
        # trainer interprets these as rows of dL/dS in cos_similarity_matrix mode).
        forward_future = await self._forward_embedding_async(data, pooling, output=output)
        forward_result = await forward_future.result_async()

        embeddings = []
        for datum, out in zip(data, forward_result.loss_fn_outputs, strict=True):
            if "embedding" not in out:
                raise ValueError(f"{output} response missing 'embedding' tensor")
            embedding_data = out["embedding"]
            embedding = torch.tensor(embedding_data.data, dtype=torch.float32)
            if embedding_data.shape is not None:
                embedding = embedding.reshape(embedding_data.shape)
            if output == "embedding":
                # Only pool further for legacy "embedding" mode — cos_similarity_matrix
                # rows are already 1-D and should pass through untouched.
                embedding = _pool_embedding_tensor(embedding, datum, pooling)
            embeddings.append(embedding.clone().detach().requires_grad_(True))

        loss, metrics = loss_fn(data, embeddings)
        loss.backward()

        backward_data = []
        for datum, embedding in zip(data, embeddings, strict=True):
            if embedding.grad is None:
                raise ValueError("No gradient computed for embedding tensor")
            grad = embedding.grad.detach().to(dtype=torch.float32).reshape(-1).cpu().tolist()
            backward_data.append(
                types.Datum(
                    model_input=datum.model_input,
                    loss_fn_inputs={
                        "embedding_grads": types.TensorData(
                            data=grad,
                            dtype="float32",
                            shape=list(embedding.grad.shape),
                        )
                    },
                )
            )

        backward_future = await self._forward_backward_embedding_async(
            backward_data, pooling, output=output,
        )

        def add_custom_metrics(
            output_value: types.ForwardBackwardOutput,
        ) -> types.ForwardBackwardOutput:
            output_value.metrics.update(metrics)
            return output_value

        return _MappedAPIFuture(backward_future, add_custom_metrics)

    def forward_backward_custom(
        self,
        data: list[types.Datum],
        loss_fn: Callable,
        *,
        loss_type_input: Literal["logprobs"] = "logprobs",
        output: Literal["logprobs", "embedding", "cos_similarity_matrix"] = "logprobs",
        pooling: Literal["mean", "last"] = "mean",
    ) -> APIFuture[types.ForwardBackwardOutput]:
        if output == "logprobs":
            return super().forward_backward_custom(
                data,
                loss_fn,
                loss_type_input=loss_type_input,
            )
        return self.holder.run_coroutine_threadsafe(
            self.forward_backward_custom_async(
                data,
                loss_fn,
                loss_type_input=loss_type_input,
                output=output,
                pooling=pooling,
            )
        ).result()

    async def forward_backward_contrastive_async(
        self,
        data: list[types.Datum],
        *,
        num_queries: int,
        temperature: float,
        pooling: Literal["mean", "last"] = "last",
        num_extra_negatives: int = 0,
    ) -> APIFuture[types.ForwardBackwardOutput]:
        """Server-side bidirectional InfoNCE contrastive loss.

        Single round trip: client sends ``data`` only (no embeddings, no
        gradients), trainer runs forward + pool + L2-normalize + sim
        matrix + cross-entropy + backward, returns scalar loss + metrics.
        ~3-5× faster per step than the embedding-output flow because we
        eliminate both the per-call embedding payload AND one HTTP round
        trip per step.

        Two batch layouts (selected by ``num_extra_negatives``):

        - **Standard** (``num_extra_negatives == 0``, the default):
          ``data == [Q_0..Q_{B-1}, D_0..D_{B-1}]`` where ``B == num_queries``.
          ``D_i`` is the positive for ``Q_i``; the other ``B-1`` D's act as
          in-batch random negatives.

        - **Hard-negative mode** (``num_extra_negatives == K_total > 0``):
          ``data == [Q_0..Q_{B-1}, D_0..D_{B-1}, EN_0..EN_{K_total-1}]``.
          The ``K_total`` extras are unpaired hard negatives that compete
          against the ``B`` positives only in the query→doc direction of
          the bidirectional loss (the doc→query side still sees only the
          ``B`` paired positives — extras have no query to attract).

        Args:
            data: tokenized Datum objects in the layout above.
            num_queries: how many of those datums are queries (``B``).
            temperature: scale for the cosine sim matrix (typical: 0.01-0.05).
            pooling: how to pool last-layer hidden states ("mean" or "last").
            num_extra_negatives: number of tail items that are unpaired hard
                negatives (default ``0``, fully backward-compatible).

        Returns:
            APIFuture whose result carries a ``metrics`` dict with at least
            ``loss``.
        """
        expected_len = 2 * num_queries + num_extra_negatives
        if len(data) != expected_len:
            raise ValueError(
                f"forward_backward_contrastive expects len(data) == "
                f"2*num_queries + num_extra_negatives = "
                f"2*{num_queries} + {num_extra_negatives} = {expected_len}; "
                f"got len(data)={len(data)}."
            )
        if num_extra_negatives < 0:
            raise ValueError(
                f"num_extra_negatives must be >= 0, got {num_extra_negatives}"
            )

        request_id = self._get_request_id()
        loss_fn_config = {
            "output": "contrastive_loss",
            "num_queries": num_queries,
            "temperature": temperature,
            "pooling": pooling,
            "num_extra_negatives": num_extra_negatives,
        }

        async def _send():
            fb_input = types.ForwardBackwardInput(
                data=data,
                loss_fn="cross_entropy",
                loss_fn_config=None,
            )
            request = types.ForwardBackwardRequest(
                forward_backward_input=fb_input,
                model_id=self._guaranteed_model_id(),
                seq_id=request_id + 1,
            )
            # tinker 0.22+ requires the to_pydantic_input dance for JSON wire safety.
            fb_input_dict = _serialize_input_for_extra_body(fb_input)
            fb_input_dict["loss_fn_config"] = loss_fn_config
            extra_body = {"forward_backward_input": fb_input_dict}
            with self.holder.aclient(ClientConnectionPoolType.TRAIN) as client:
                return await client.training.forward_backward(
                    request=request,
                    extra_body=extra_body,
                )

        start = time.time()
        async with self._take_turn(request_id):
            untyped_future = await self.holder.execute_with_retries(_send)

        return _APIFuture(
            types.ForwardBackwardOutput,
            self.holder,
            untyped_future,
            request_start_time=start,
            request_type="ForwardBackward",
            queue_state_observer=self._queue_state_logger,
        )

    def forward_backward_contrastive(
        self,
        data: list[types.Datum],
        *,
        num_queries: int,
        temperature: float,
        pooling: Literal["mean", "last"] = "last",
        num_extra_negatives: int = 0,
    ) -> APIFuture[types.ForwardBackwardOutput]:
        """Sync wrapper for forward_backward_contrastive_async — see that docstring."""
        return self.holder.run_coroutine_threadsafe(
            self.forward_backward_contrastive_async(
                data,
                num_queries=num_queries,
                temperature=temperature,
                pooling=pooling,
                num_extra_negatives=num_extra_negatives,
            )
        ).result()

    def list_checkpoints(self) -> list[str]:
        """List available DCP checkpoints from the trainer.

        This is a firetitan-specific endpoint (not in tinker SDK).
        Uses the trainer's own HTTP connection.

        Returns:
            Sorted checkpoint name list (e.g., ``["step-2", "step-4"]``).
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
            return result.get("checkpoints", [])
        except Exception as e:
            logger.warning(
                "LIST_CHECKPOINTS_ERROR: %s: %s (resume may start from scratch)",
                type(e).__name__,
                e,
            )
            return []

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

        Passes the resolved ``checkpoint_type`` via the tinker SDK's
        ``extra_body`` parameter, which merges it into the HTTP request JSON
        body.         Full-parameter training saves a base checkpoint first and deltas
        after that by default. LoRA training always saves base checkpoints.
        Callers can override with ``checkpoint_type="base"`` or ``"delta"``.
        LoRA sessions may also pass ``checkpoint_type="merged_base"`` to fold the
        active adapter into the base weights and export a full base checkpoint
        (no adapter metadata), which promotes to an ``HF_BASE_MODEL``. Load the
        adapter first via :meth:`load_adapter`; saving from a fresh LoRA session
        would export base-identical weights.

        Returns:
            :class:`SaveSamplerResult` with the public snapshot identity in both
            ``path`` and ``snapshot_name``.  The trainer's physical storage path
            is intentionally not part of this SDK contract.
        """
        actual_name = qualify_snapshot_name(self.session_id, name)
        self._warn_if_name_reused(actual_name, self._saved_sampler_names, "Sampler")

        resolved_checkpoint_type = self._next_sampler_checkpoint_type(checkpoint_type)
        extra_body = {"checkpoint_type": resolved_checkpoint_type}
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
            return actual_name

        snapshot_name = self.holder.run_coroutine_threadsafe(_save()).result()
        self._saved_sampler_names.add(actual_name)
        self._sampler_checkpoint_saved = True
        self._record_saved_snapshot(actual_name, resolved_checkpoint_type)
        return SaveSamplerResult(path=snapshot_name, snapshot_name=actual_name)

    def _record_saved_snapshot(self, snapshot_name: str, checkpoint_type: str) -> None:
        """Hand the saved snapshot type to the sampler backend.

        This is in-memory bookkeeping that pins each ``delta`` snapshot to the
        base it was computed against; the next hotload reads it to build the
        incremental metadata. If it fails the delta chain is silently corrupted
        (subsequent deltas reference a stale or missing base), so we surface the
        failure instead of swallowing it — a hard error here is strictly safer
        than serving a corrupted checkpoint to the sampler.
        """
        if self._sampler_backend is None or not hasattr(self._sampler_backend, "remember_saved_snapshot"):
            return
        try:
            self._sampler_backend.remember_saved_snapshot(snapshot_name, checkpoint_type=checkpoint_type)
        except Exception as e:
            logger.error(
                "Failed to record sampler snapshot type for '%s'; the "
                "delta checkpoint chain would be corrupted, aborting the save: %s",
                snapshot_name,
                e,
            )
            raise

    def save_weights_for_sampler(
        self,
        name: str,
        ttl_seconds: int | None = None,
        *,
        checkpoint_type: str | None = None,
    ) -> APIFuture[types.SaveWeightsForSamplerResponse]:
        """Save sampler weights and return a FireTitan snapshot identity.

        The returned ``path`` is not a raw storage URI. It is the public
        snapshot identity consumed by ``create_sampling_client(model_path=...)``
        on a client/service with an SDK-managed deployment sampler backend.
        """
        result = self.save_weights_for_sampler_ext(
            name,
            checkpoint_type=checkpoint_type,
            ttl_seconds=ttl_seconds,
        )
        return _ImmediateAPIFuture(types.SaveWeightsForSamplerResponse(path=result.snapshot_name))

    async def save_weights_for_sampler_async(
        self,
        name: str,
        ttl_seconds: int | None = None,
        *,
        checkpoint_type: str | None = None,
    ) -> APIFuture[types.SaveWeightsForSamplerResponse]:
        return await asyncio.to_thread(
            self.save_weights_for_sampler,
            name,
            ttl_seconds=ttl_seconds,
            checkpoint_type=checkpoint_type,
        )

    def create_sampling_client(
        self,
        model_path: str,
        retry_config=None,
    ) -> FiretitanSamplingClient:
        """Return a Tinker-shaped sampler for the attached deployment.

        ``model_path`` must be a snapshot identity returned by
        ``save_weights_for_sampler`` / ``save_weights_for_sampler_ext``.
        FireTitan cannot create a sampler without an SDK-managed hot-load
        deployment attached to this client.
        """
        if retry_config is not None:
            logger.warning("retry_config is currently ignored by FiretitanSamplingClient")
        sampler_backend = self._require_sampler_backend()
        if not sampler_backend.hotload_saved_snapshot(model_path):
            raise RuntimeError(f"Hotload failed for sampler snapshot {model_path!r}")
        return sampler_backend.get_sampling_client()

    async def create_sampling_client_async(
        self,
        model_path: str,
        retry_config=None,
    ) -> FiretitanSamplingClient:
        return await asyncio.to_thread(
            self.create_sampling_client,
            model_path,
            retry_config=retry_config,
        )

    def save_weights_and_get_sampling_client(
        self,
        name: str | None = None,
        retry_config: Any = None,
    ):
        """Unsupported on FireTitan — see :data:`SAMPLING_CLIENT_FROM_TRAINER_MESSAGE`.

        Tinker's managed service samples from an ephemeral in-service snapshot;
        FireTitan hot-loads a snapshot into a separate inference deployment, so
        the combined call has no equivalent. Raises with the two-step idiom.
        """
        raise NotImplementedError(SAMPLING_CLIENT_FROM_TRAINER_MESSAGE)

    async def save_weights_and_get_sampling_client_async(
        self,
        name: str | None = None,
        retry_config: Any = None,
    ):
        """Unsupported on FireTitan — see :data:`SAMPLING_CLIENT_FROM_TRAINER_MESSAGE`."""
        raise NotImplementedError(SAMPLING_CLIENT_FROM_TRAINER_MESSAGE)

    def save_weights_and_get_sampling_client_submit(
        self,
        retry_config: Any = None,
    ):
        """Unsupported on FireTitan — see :data:`SAMPLING_CLIENT_FROM_TRAINER_MESSAGE`."""
        raise NotImplementedError(SAMPLING_CLIENT_FROM_TRAINER_MESSAGE)

    def get_tokenizer(self):
        """Return the HuggingFace tokenizer for this trainer's base model.

        Loads from the managed ``tokenizer_model`` name (e.g. ``"Qwen/Qwen3-1.7B"``),
        set via ``from_firetitan_config`` / ``install_tinker_service_client``.
        Unlike Tinker's managed service, FireTitan does not resolve a tokenizer
        server-side, so ``tokenizer_model`` must be supplied.
        """
        if not self._tokenizer_model:
            raise ValueError(
                "get_tokenizer() requires a tokenizer_model. FireTitan does not "
                "resolve tokenizers server-side; pass tokenizer_model to "
                "from_firetitan_config()/install_tinker_service_client()."
            )
        return AutoTokenizer.from_pretrained(self._tokenizer_model)

    def create_base_training_client(
        self,
        base_model: str,
        user_metadata: dict[str, str] | None = None,
    ) -> "FiretitanTrainingClient":
        """Create a frozen base-only reference model on this training session."""
        return _create_base_only_training_client(
            self.holder,
            base_model,
            user_metadata,
            request_type="CreateBaseModel",
        )

    def save_state(
        self,
        name: str,
        ttl_seconds: int | None = None,
        overwrite: bool = False,
        *,
        timeout: float | None = None,
    ):
        """Save model weights to persistent storage (DCP checkpoint).

        Overrides the base ``save_state`` to add checkpoint-name reuse
        detection and a compatibility ``timeout`` keyword used by older
        cookbook helpers.

        Warns if ``name`` was already used for a DCP checkpoint in this
        session, then delegates to the parent implementation.

        When ``timeout`` is provided, this method blocks on the returned
        future before returning it. This preserves the original return type
        while supporting call sites that expect ``save_state(name, timeout=...)``
        to wait for completion.
        """
        if overwrite:
            raise NotImplementedError(
                "FiretitanTrainingClient.save_state(overwrite=True) is not supported. "
                "Use a new checkpoint name instead."
            )
        self._warn_if_name_reused(name, self._saved_state_names, "DCP")
        self._saved_state_names.add(name)
        future = super().save_state(name, ttl_seconds=ttl_seconds, overwrite=overwrite)
        if timeout is not None:
            future.result(timeout=timeout)
        return future

    async def save_state_async(
        self,
        name: str,
        ttl_seconds: int | None = None,
        overwrite: bool = False,
    ):
        return self.save_state(name, ttl_seconds=ttl_seconds, overwrite=overwrite)

    def load_state(
        self,
        path: str,
        weights_access_token: str | None = None,
    ):
        if weights_access_token is not None:
            raise NotImplementedError(
                "FiretitanTrainingClient.load_state(weights_access_token=...) is not supported. "
                "Load checkpoints that are accessible to the current Fireworks API key."
            )
        return super().load_state(path, weights_access_token=weights_access_token)

    async def load_state_async(
        self,
        path: str,
        weights_access_token: str | None = None,
    ):
        return self.load_state(path, weights_access_token=weights_access_token)

    def load_state_with_optimizer(
        self,
        path: str,
        weights_access_token: str | None = None,
    ):
        if weights_access_token is not None:
            raise NotImplementedError(
                "FiretitanTrainingClient.load_state_with_optimizer(weights_access_token=...) is not supported. "
                "Load checkpoints that are accessible to the current Fireworks API key."
            )
        return super().load_state_with_optimizer(path, weights_access_token=weights_access_token)

    async def load_state_with_optimizer_async(
        self,
        path: str,
        weights_access_token: str | None = None,
    ):
        return self.load_state_with_optimizer(path, weights_access_token=weights_access_token)

    def load_adapter(self, adapter_path: str) -> APIFuture[LoadAdapterResponse]:
        """Load HF PEFT adapter weights into a LoRA training session (weights-only)."""
        adapter_path = (adapter_path or "").strip()
        if not adapter_path:
            raise ValueError("adapter_path must be a non-empty string")

        request_id = self._get_request_id()

        async def _load_adapter_async():
            start = time.time()
            body = {
                "adapter_path": adapter_path,
                "model_id": self._guaranteed_model_id(),
                "seq_id": request_id + 1,
            }

            async def _send():
                with self.holder.aclient(ClientConnectionPoolType.TRAIN) as client:
                    return await client.post(
                        "/api/v1/load_adapter",
                        body=body,
                        cast_to=types.UntypedAPIFuture,
                    )

            async with self._take_turn(request_id):
                future = await self.holder.execute_with_retries(_send)
            return await _APIFuture(
                LoadAdapterResponse,
                self.holder,
                future,
                request_start_time=start,
                request_type="LoadAdapter",
                queue_state_observer=self._queue_state_logger,
            )

        return self.holder.run_coroutine_threadsafe(_load_adapter_async())


# -- FiretitanServiceClient ----------------------------------------------------


class FiretitanServiceClient(ServiceClient):
    """ServiceClient that can create full-param (no LoRA) training clients.

    Managed instances are lazy: they do not create a Tinker holder until the
    SDK has provisioned or reattached a FireTitan trainer endpoint.
    """

    def __init__(self, *args, api_key: str | None = None, **kwargs):
        api_key = _fireworks_api_key(api_key)
        self._managed_config = kwargs.pop("managed_config", None)
        managed_base_url = kwargs.pop("managed_base_url", None)
        constructor_base_url = kwargs.get("base_url")
        self._managed_base_url = managed_base_url or _fireworks_base_url(constructor_base_url)
        self._managed_inference_url = kwargs.pop("managed_inference_url", None)
        self._managed_hotload_api_url = kwargs.pop("managed_hotload_api_url", None)
        self._managed_additional_headers = kwargs.pop(
            "managed_additional_headers",
            None,
        )
        self._managed_verify_ssl = kwargs.pop("managed_verify_ssl", None)
        self._managed_handle: Any | None = None
        self._fireworks_api_key = api_key if api_key and not api_key.startswith("tml-") else None
        self._created_training_configs: set[_TrainingKey] = set()
        self._sampler_backend: Any | None = None
        self._reference_handle: Any | None = None
        # Separate frozen reference trainers this service provisioned and owns
        # (full-param / explicit reference shape). Torn down on close().
        self._owned_reference_handles: list[Any] = []
        self._owned_inference_deployments: list[tuple[DeploymentManager, str, DeploymentCleanupOnClose]] = []
        self._default_user_metadata: dict[str, str] | None = kwargs.get("user_metadata")
        self._default_project_id: str | None = kwargs.get("project_id")

        if self._managed_config is not None:
            return

        if self._fireworks_api_key is not None:
            headers = dict(kwargs.pop("default_headers", None) or {})
            headers.setdefault("X-API-Key", self._fireworks_api_key)
            kwargs["default_headers"] = headers
            kwargs.setdefault("_client_config", dict(FIRETITAN_TINKER_CLIENT_CONFIG))
            from tinker.lib import internal_client_holder as holder_module

            original_auth_provider = getattr(holder_module, "ApiKeyAuthProvider", None)
            if original_auth_provider is None:
                super().__init__(*args, api_key=api_key, **kwargs)
            else:
                with _TINKER_AUTH_PROVIDER_PATCH_LOCK:
                    holder_module.ApiKeyAuthProvider = lambda *_, **__: _FireworksApiKeyAuthProvider(  # type: ignore[assignment]
                        self._fireworks_api_key or ""
                    )
                    try:
                        super().__init__(*args, api_key=api_key, **kwargs)
                    finally:
                        holder_module.ApiKeyAuthProvider = original_auth_provider
            return
        super().__init__(*args, api_key=api_key, **kwargs)

    def _user_metadata(
        self,
        user_metadata: dict[str, str] | None,
    ) -> dict[str, str] | None:
        return user_metadata if user_metadata is not None else self._default_user_metadata

    def get_telemetry(self):
        if not hasattr(self, "holder"):
            return None
        return super().get_telemetry()

    def create_rest_client(self):
        if not hasattr(self, "holder") and self._managed_config is not None:
            return _LazyManagedRestClient(
                self._managed_config,
                user_metadata=self._default_user_metadata,
            )
        return super().create_rest_client()

    def _current_session_id(self) -> Any:
        """The serverless session id this service is bound to, or None (managed /
        dedicated services have no holder; an unconnected service has no session
        yet)."""
        if not hasattr(self, "holder"):
            return None
        return self.holder.get_session_id()

    @property
    def training_session_id(self) -> str | None:
        """The CP serverless training session id (``ts-<hex>``) this service owns,
        or None for non-serverless services / before the session is created.

        One service owns one session; the many models created on it are separate
        runs (see ``FiretitanTrainingClient.run_id``).
        """
        session_id = self._current_session_id()
        return session_id if _is_serverless_session_id(session_id) else None

    @property
    def training_session_name(self) -> str | None:
        """Full CP resource name (``accounts/<a>/trainingSessions/<ts-id>``) of the
        session this service owns, for CP ops (GetTrainingSession, checkpoint
        list/promote, DeleteTrainingSession). None for non-serverless services."""
        return self._serverless_training_session_name(self._current_session_id())

    def _resolved_account_id(self) -> str | None:
        """The Fireworks account id, resolved once and cached, or ``None`` if it
        can't be resolved without an extra control-plane round-trip.

        The durable handles are the ids (``training_session_id`` / ``run_id``),
        which are always available with no I/O; the account is needed only to
        *qualify* them into full resource names, so this is best-effort and
        degrades to ``None`` rather than failing the caller. Resolved via a
        Fireworks REST client; cached across calls.
        """
        cached = getattr(self, "_cp_account_id", "unset")
        if cached != "unset":
            return cached
        # Resolve into a local and publish the cache exactly once, with the final
        # value — never an in-progress None. Otherwise a concurrent caller could
        # observe the transient None (a terminal value here), skip its own lookup,
        # and bake run_name=None into a client created mid-resolution. Worst case
        # two threads both resolve (idempotent, same answer); never a premature None.
        account: str | None = None
        api_key = getattr(self, "_fireworks_api_key", None)
        if api_key:
            try:
                from fireworks.training.sdk.fireworks_client import FireworksClient

                base_url = getattr(self, "_managed_base_url", None) or "https://api.fireworks.ai"
                account = FireworksClient(api_key=api_key, base_url=base_url).account_id
            except Exception:
                account = None
        self._cp_account_id = account
        return account

    def _serverless_training_session_name(self, session_id: Any) -> str | None:
        """Full CP resource name (``accounts/<a>/trainingSessions/<ts-id>``) for a
        serverless training session, or ``None`` for non-serverless ids / when the
        account can't be resolved (use ``training_session_id`` + your account)."""
        if not _is_serverless_session_id(session_id):
            return None
        account = self._resolved_account_id()
        return f"accounts/{account}/trainingSessions/{session_id}" if account else None

    def _serverless_run_name(self, model_id: Any) -> str | None:
        """Full CP resource name (``accounts/<a>/trainingRuns/<run_id>``) for a
        run-scoped model, or ``None`` for non-run-scoped ids (base-only) / when the
        account can't be resolved (use ``run_id`` + your account)."""
        run_id = _run_id_from_model_id(model_id)
        if run_id is None:
            return None
        account = self._resolved_account_id()
        return f"accounts/{account}/trainingRuns/{run_id}" if account else None

    def _lazy_managed_server_capabilities(self) -> types.GetServerCapabilitiesResponse:
        managed_config = self._managed_config
        if managed_config is None:
            return types.GetServerCapabilitiesResponse(supported_models=[])
        return types.GetServerCapabilitiesResponse(
            supported_models=[types.SupportedModel(model_name=managed_config.base_model)]
        )

    def get_server_capabilities(self) -> types.GetServerCapabilitiesResponse:
        if not hasattr(self, "holder"):
            return self._lazy_managed_server_capabilities()
        return super().get_server_capabilities()

    async def get_server_capabilities_async(
        self,
    ) -> types.GetServerCapabilitiesResponse:
        if not hasattr(self, "holder"):
            return self._lazy_managed_server_capabilities()
        return await super().get_server_capabilities_async()

    @classmethod
    def from_firetitan_config(
        cls,
        *,
        api_key: str | None = None,
        managed_config=None,
        base_url: str | None = None,
        inference_url: str | None = None,
        hotload_api_url: str | None = None,
        additional_headers: dict[str, str] | None = None,
        verify_ssl: bool | None = None,
        user_metadata: dict[str, str] | None = None,
        project_id: str | None = None,
        **managed_config_kwargs,
    ) -> "FiretitanServiceClient":
        """Create a lazy SDK-managed FireTitan service client for recipes."""
        api_key = _fireworks_api_key(api_key)
        base_url = _fireworks_base_url(base_url)
        if managed_config is None:
            managed_config = _managed_config_from_kwargs(managed_config_kwargs)
        elif managed_config_kwargs:
            raise ValueError("Pass either managed_config or managed config keyword arguments, not both")

        return cls(
            base_url=base_url,
            api_key=api_key,
            managed_config=managed_config,
            managed_base_url=base_url,
            managed_inference_url=inference_url,
            managed_hotload_api_url=hotload_api_url,
            managed_additional_headers=additional_headers,
            managed_verify_ssl=verify_ssl,
            user_metadata=user_metadata,
            project_id=project_id,
        )

    def _ensure_managed_handle(
        self,
        *,
        user_metadata: dict[str, str] | None = None,
    ) -> Any:
        """Provision (once) and return the SDK-managed trainer/deployment handle.

        Returns ``None`` for a non-managed service. A managed service provisions
        exactly one trainer/deployment from its immutable ``_managed_config``, so
        the handle is cached on first use and reused thereafter — independent of
        any call-site arguments. Deprecated divergent ``base_model``/``lora_rank``
        passed to ``create_*_client`` are warned at that boundary and ignored;
        because caching keys off nothing but the single managed config, an ignored
        override can never make a later canonical call look like a different
        training configuration.
        """
        managed_config = self._managed_config
        if managed_config is None:
            return None
        if self._managed_handle is not None:
            return self._managed_handle
        if self._fireworks_api_key is None:
            raise ValueError(
                "FireTitan SDK-managed Tinker compatibility requires a Fireworks API key. "
                "Construct FiretitanServiceClient with api_key=fw_... or set FIREWORKS_API_KEY."
            )
        return self._provision_managed_handle(managed_config, user_metadata=user_metadata)

    def _provision_managed_handle(
        self,
        managed_config: Any,
        *,
        user_metadata: dict[str, str] | None,
    ) -> Any:
        """Create and cache the one managed trainer/deployment handle.

        Provisions entirely from the immutable ``managed_config`` (the single
        source of truth); call-site ``base_model``/``lora_rank`` never reach here.
        """
        from fireworks.training.sdk.managed import _create_managed_tinker_client

        self._managed_handle = _create_managed_tinker_client(
            api_key=self._fireworks_api_key,
            config=managed_config,
            user_metadata=user_metadata,
            base_url=self._managed_base_url,
            inference_url=self._managed_inference_url,
            hotload_api_url=self._managed_hotload_api_url,
            additional_headers=self._managed_additional_headers,
            verify_ssl=self._managed_verify_ssl,
        )
        if self._managed_handle.sampler_backend is not None:
            self._attach_sampler_backend(self._managed_handle.sampler_backend)
        reference_handle = getattr(self._managed_handle, "reference_handle", None)
        if reference_handle is not None:
            self._reference_handle = reference_handle
            self._owned_reference_handles.append(reference_handle)
        return self._managed_handle

    def _attach_sampler_backend(self, backend: Any) -> "FiretitanServiceClient":
        """Attach SDK-owned sampler backend state to this service client."""
        self._sampler_backend = backend
        return self

    def _require_sampler_backend(self) -> Any:
        if self._sampler_backend is None:
            raise NotImplementedError(
                "FiretitanServiceClient.create_sampling_client(model_path=...) requires SDK-managed sampler state. "
                "Create the service through the FireTitan SDK Tinker compatibility path."
            )
        return self._sampler_backend

    @staticmethod
    def _require_managed_value(value: T | None, name: str) -> T:
        if value is None:
            raise RuntimeError(
                f"SDK-managed service did not resolve {name}. "
                "Create the service with FiretitanServiceClient.from_firetitan_config(...) "
                "and call create_training_client() before reading provisioned metadata."
            )
        return value

    @property
    def managed_trainer_job_id(self) -> str | None:
        if self._managed_handle is not None:
            return self._managed_handle.trainer_endpoint.job_id
        if self._managed_config is None:
            return None
        return self._managed_config.trainer_job_id

    @property
    def managed_deployment_id(self) -> str | None:
        if self._managed_handle is not None and self._managed_handle.deployment is not None:
            return self._managed_handle.deployment.deployment_id
        if self._managed_config is None:
            return None
        return self._managed_config.deployment_id

    @property
    def managed_training_profile(self) -> Any | None:
        if self._managed_handle is not None:
            return getattr(self._managed_handle, "training_profile", None)
        return None

    @property
    def managed_accelerator_type(self) -> str | None:
        if self._managed_config is not None and self._managed_config.accelerator_type is not None:
            return self._managed_config.accelerator_type
        profile = self.managed_training_profile
        return getattr(profile, "accelerator_type", None)

    @property
    def managed_accelerator_count(self) -> int | None:
        if self._managed_config is not None and self._managed_config.accelerator_count is not None:
            return self._managed_config.accelerator_count
        profile = self.managed_training_profile
        return getattr(profile, "accelerator_count", None)

    @property
    def managed_max_context_length(self) -> int | None:
        # Prefer the provisioned handle: when the recipe leaves context length
        # unset, it is resolved from the training shape during provisioning and
        # only the handle carries that resolved value (the original config still
        # reads None). Mirror managed_trainer_job_id's handle-first lookup.
        if self._managed_handle is not None and self._managed_handle.max_context_length is not None:
            return self._managed_handle.max_context_length
        if self._managed_config is not None and self._managed_config.max_context_length is not None:
            return self._managed_config.max_context_length
        # Defensive fallback: under backend auto-shape selection the resolved
        # max context length is computed on the child trainer job and may not be
        # surfaced onto the handle/config, leaving this None and hard-failing in
        # _require_managed_value even though the training shape itself carries a
        # valid limit (the 2026-06-28 SDK-managed max-context incident). Fall
        # back to the shape profile's max_supported_context_length when present.
        profile = self.managed_training_profile
        shape_max = getattr(profile, "max_supported_context_length", None)
        if shape_max:
            return shape_max
        return None

    @property
    def managed_deployment_shape(self) -> str | None:
        if self._managed_handle is not None:
            deployment_shape = getattr(self._managed_handle, "deployment_shape", None)
            if deployment_shape is not None:
                return deployment_shape
        if self._managed_config is None:
            return None
        return self._managed_config.deployment_shape

    @property
    def trainer_job_id(self) -> str:
        """Resolved SDK-managed policy trainer job id."""
        return self._require_managed_value(self.managed_trainer_job_id, "trainer job id")

    @property
    def deployment_id(self) -> str:
        """Resolved SDK-managed hot-load deployment id."""
        return self._require_managed_value(self.managed_deployment_id, "deployment id")

    @property
    def max_context_length(self) -> int:
        """Resolved max context length from config or training shape."""
        return self._require_managed_value(self.managed_max_context_length, "max context length")

    @property
    def deployment_shape(self) -> str:
        """Resolved SDK-managed deployment shape from config or training shape."""
        return self._require_managed_value(self.managed_deployment_shape, "deployment shape")

    @property
    def training_profile(self) -> Any | None:
        """Resolved training shape profile, when a training shape is configured."""
        return self.managed_training_profile

    @property
    def accelerator_type(self) -> str | None:
        """Resolved accelerator type from the training shape profile."""
        return self.managed_accelerator_type

    @property
    def accelerator_count(self) -> int | None:
        """Resolved accelerator count from the training shape profile."""
        return self.managed_accelerator_count

    def _control_plane_client(self) -> Any:
        """Return the managed control-plane trainer client (TrainerJobManager).

        Cookbook checkpoint management (TrainingCheckpoints) treats the service
        as the authoritative control-plane lister/promoter. The actual REST
        client lives on the provisioned handle; surface it so list/promote
        delegate there instead of failing with AttributeError.
        """
        handle = self._managed_handle
        manager = getattr(handle, "trainer_manager", None) if handle is not None else None
        if manager is None:
            raise RuntimeError(
                "Control-plane checkpoint operations require a provisioned trainer. "
                "Call create_training_client() before listing or promoting checkpoints."
            )
        return manager

    def list_checkpoints(self, job_id: str, *, page_size: int = 200) -> list[dict]:
        """Control-plane checkpoint listing for a trainer job.

        Delegates to the managed TrainerJobManager (the cookbook passes the
        service as its control-plane checkpoint client). Returns the same rows
        as ``TrainerJobManager.list_checkpoints`` — sampler + DCP checkpoints
        with promotability metadata.
        """
        return self._control_plane_client().list_checkpoints(job_id, page_size=page_size)

    def promote_checkpoint(self, *args: Any, **kwargs: Any) -> dict:
        """Promote a trainer checkpoint to a Fireworks model.

        Delegates to the managed TrainerJobManager; accepts the same calling
        forms (``name=`` or ``job_id``/``checkpoint_id`` positional).
        """
        return self._control_plane_client().promote_checkpoint(*args, **kwargs)

    def close(self) -> None:
        close_error: Exception | None = None

        def record_close_error(exc: Exception) -> None:
            nonlocal close_error
            if close_error is None:
                close_error = exc

        try:
            self.release_references()
        except Exception as exc:
            logger.warning("Reference cleanup failed: %s", exc)
            record_close_error(exc)

        try:
            owned_inference_deployments = getattr(self, "_owned_inference_deployments", [])
            for deploy_mgr, deployment_id, cleanup in owned_inference_deployments:
                try:
                    if cleanup == CLEANUP_DEPLOYMENT_ON_CLOSE_SCALE_TO_ZERO:
                        deploy_mgr.scale_to_zero(deployment_id)
                    elif cleanup == CLEANUP_DEPLOYMENT_ON_CLOSE_DELETE:
                        deploy_mgr.delete(deployment_id)
                    else:
                        allowed = ", ".join(
                            [
                                CLEANUP_DEPLOYMENT_ON_CLOSE_DELETE,
                                CLEANUP_DEPLOYMENT_ON_CLOSE_SCALE_TO_ZERO,
                            ]
                        )
                        raise ValueError(f"cleanup_on_close must be one of: {allowed}")
                except Exception as exc:
                    logger.warning("Inference deployment cleanup failed for %s: %s", deployment_id, exc)
                    record_close_error(exc)
        finally:
            getattr(self, "_owned_inference_deployments", []).clear()

        if self._managed_handle is not None:
            try:
                self._managed_handle.close()
            except Exception as exc:
                logger.warning("Managed service cleanup failed: %s", exc)
                record_close_error(exc)

        if close_error is not None:
            raise close_error

    @property
    def reference_job_id(self) -> str | None:
        """Trainer job id of the separate reference trainer, or None if shared.

        Returns None when the reference reused the policy session (LoRA) or no
        reference was created. Used by recipes for run metadata.
        """
        if self._reference_handle is not None:
            return self._reference_handle.trainer_endpoint.job_id
        return None

    @property
    def reference_trainer_job_id(self) -> str | None:
        """Separate reference trainer job id; None when reference is shared."""
        return self.reference_job_id

    @property
    def reference_client_job_id(self) -> str:
        """Trainer job id used by the reference client.

        Shared LoRA references run on the policy trainer. Full-parameter
        references use a separate reference trainer, either auto-selected by the
        backend, explicitly pinned by a LoRA-capable shape, or reattached from
        an existing job. Recipes should use this for reference reconnect
        metadata.
        """
        return self.reference_job_id or self.trainer_job_id

    def release_references(self) -> None:
        """Tear down any separate reference trainers this service provisioned.

        No-op for shared-session references (nothing extra was provisioned).
        Recipes (e.g. DPO) call this to free the reference trainer as soon as
        all reference forwards finish, while policy training continues.
        """
        while self._owned_reference_handles:
            handle = self._owned_reference_handles.pop()
            try:
                handle.close()
            except Exception as e:  # best-effort cleanup
                logger.warning("Failed to release reference trainer: %s", e)
        self._reference_handle = None

    def create_training_client(
        self,
        base_model: str,
        lora_rank: int = 0,
        seed: int | None = None,
        train_mlp: bool = True,
        train_attn: bool = True,
        train_unembed: bool = True,
        lora_alpha: int | None = DEFAULT_LORA_ALPHA,
        user_metadata: dict[str, str] | None = None,
    ) -> FiretitanTrainingClient:
        """Create a FiretitanTrainingClient (full-param or LoRA).

        ``lora_alpha`` defaults to ``DEFAULT_LORA_ALPHA`` (32) and is ignored for
        full-parameter training (``lora_rank == 0``). Pass ``None`` to let the
        backend choose its own default (``2 * lora_rank``).
        """
        if self._managed_config is not None:
            _warn_deprecated_override(
                "create_training_client", "base_model", base_model, self._managed_config.base_model
            )
            _warn_deprecated_override("create_training_client", "lora_rank", lora_rank, self._managed_config.lora_rank)
        managed_handle = self._ensure_managed_handle(
            user_metadata=self._user_metadata(user_metadata),
        )
        if managed_handle is not None:
            return managed_handle.training_client

        effective_alpha = lora_alpha if lora_rank > 0 else None
        config_key = _TrainingKey(
            base_model, lora_rank, seed, train_mlp, train_attn, train_unembed, effective_alpha
        )
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
            alpha=effective_alpha,
            seed=seed,
            train_mlp=train_mlp,
            train_attn=train_attn,
            train_unembed=train_unembed,
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
                        user_metadata=self._user_metadata(user_metadata),
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
            lora_rank=lora_rank,
            run_name=self._serverless_run_name(model_id),
        )

    def create_lora_training_client(
        self,
        base_model: str,
        rank: int = 32,
        seed: int | None = None,
        train_mlp: bool = True,
        train_attn: bool = True,
        train_unembed: bool = True,
        alpha: int | None = DEFAULT_LORA_ALPHA,
        user_metadata: dict[str, str] | None = None,
    ) -> FiretitanTrainingClient:
        """Tinker-compatible LoRA factory name.

        ``alpha`` defaults to ``DEFAULT_LORA_ALPHA`` (32); pass ``None`` to let
        the backend pick its own default (``2 * rank``).
        """
        return self.create_training_client(
            base_model=base_model,
            lora_rank=rank,
            seed=seed,
            train_mlp=train_mlp,
            train_attn=train_attn,
            train_unembed=train_unembed,
            lora_alpha=alpha,
            user_metadata=user_metadata,
        )

    async def create_lora_training_client_async(
        self,
        base_model: str,
        rank: int = 32,
        seed: int | None = None,
        train_mlp: bool = True,
        train_attn: bool = True,
        train_unembed: bool = True,
        alpha: int | None = DEFAULT_LORA_ALPHA,
        user_metadata: dict[str, str] | None = None,
    ) -> FiretitanTrainingClient:
        return await asyncio.to_thread(
            self.create_lora_training_client,
            base_model,
            rank=rank,
            seed=seed,
            train_mlp=train_mlp,
            train_attn=train_attn,
            train_unembed=train_unembed,
            alpha=alpha,
            user_metadata=user_metadata,
        )

    def _managed_config_for_resume(self) -> Any | None:
        if self._managed_config is None or hasattr(self, "holder"):
            return None
        return self._managed_config

    @staticmethod
    def _reject_weights_access_token(method: str, weights_access_token: str | None) -> None:
        if weights_access_token is not None:
            raise NotImplementedError(
                f"FiretitanServiceClient.{method}(weights_access_token=...) is not supported. "
                "Load checkpoints that are accessible to the current Fireworks API key."
            )

    def create_training_client_from_state(
        self,
        path: str,
        user_metadata: dict[str, str] | None = None,
        weights_access_token: str | None = None,
    ) -> FiretitanTrainingClient:
        self._reject_weights_access_token("create_training_client_from_state", weights_access_token)
        managed_config = self._managed_config_for_resume()
        if managed_config is None:
            weights_info = self.create_rest_client().get_weights_info_by_tinker_path(path).result()
            training_client = self._create_training_client_from_weights_info(
                weights_info,
                user_metadata=user_metadata,
            )
            training_client.load_state(path).result()
            return training_client

        training_client = self.create_lora_training_client(
            base_model=managed_config.base_model,
            rank=managed_config.lora_rank,
            seed=managed_config.seed,
            train_unembed=managed_config.train_unembed,
            train_mlp=managed_config.train_mlp,
            train_attn=managed_config.train_attn,
            user_metadata=user_metadata,
        )
        training_client.load_state(path).result()
        return training_client

    async def create_training_client_from_state_async(
        self,
        path: str,
        user_metadata: dict[str, str] | None = None,
        weights_access_token: str | None = None,
    ) -> FiretitanTrainingClient:
        self._reject_weights_access_token("create_training_client_from_state_async", weights_access_token)
        managed_config = self._managed_config_for_resume()
        if managed_config is None:
            rest_client = self.create_rest_client()
            weights_info = await rest_client.get_weights_info_by_tinker_path(path)
            training_client = await self._create_training_client_from_weights_info_async(
                weights_info,
                user_metadata=user_metadata,
            )
        else:
            training_client = await self.create_lora_training_client_async(
                base_model=managed_config.base_model,
                rank=managed_config.lora_rank,
                seed=managed_config.seed,
                train_unembed=managed_config.train_unembed,
                train_mlp=managed_config.train_mlp,
                train_attn=managed_config.train_attn,
                user_metadata=user_metadata,
            )

        load_future = await training_client.load_state_async(path)
        await load_future.result_async()
        return training_client

    def create_training_client_from_state_with_optimizer(
        self,
        path: str,
        user_metadata: dict[str, str] | None = None,
        weights_access_token: str | None = None,
    ) -> FiretitanTrainingClient:
        self._reject_weights_access_token(
            "create_training_client_from_state_with_optimizer",
            weights_access_token,
        )
        managed_config = self._managed_config_for_resume()
        if managed_config is None:
            weights_info = self.create_rest_client().get_weights_info_by_tinker_path(path).result()
            training_client = self._create_training_client_from_weights_info(
                weights_info,
                user_metadata=user_metadata,
            )
            training_client.load_state_with_optimizer(path).result()
            return training_client

        training_client = self.create_lora_training_client(
            base_model=managed_config.base_model,
            rank=managed_config.lora_rank,
            seed=managed_config.seed,
            train_unembed=managed_config.train_unembed,
            train_mlp=managed_config.train_mlp,
            train_attn=managed_config.train_attn,
            user_metadata=user_metadata,
        )
        training_client.load_state_with_optimizer(path).result()
        return training_client

    async def create_training_client_from_state_with_optimizer_async(
        self,
        path: str,
        user_metadata: dict[str, str] | None = None,
        weights_access_token: str | None = None,
    ) -> FiretitanTrainingClient:
        self._reject_weights_access_token(
            "create_training_client_from_state_with_optimizer_async",
            weights_access_token,
        )
        managed_config = self._managed_config_for_resume()
        if managed_config is None:
            rest_client = self.create_rest_client()
            weights_info = await rest_client.get_weights_info_by_tinker_path(path)
            training_client = await self._create_training_client_from_weights_info_async(
                weights_info,
                user_metadata=user_metadata,
            )
        else:
            training_client = await self.create_lora_training_client_async(
                base_model=managed_config.base_model,
                rank=managed_config.lora_rank,
                seed=managed_config.seed,
                train_unembed=managed_config.train_unembed,
                train_mlp=managed_config.train_mlp,
                train_attn=managed_config.train_attn,
                user_metadata=user_metadata,
            )

        load_future = await training_client.load_state_with_optimizer_async(path)
        await load_future.result_async()
        return training_client

    def _create_training_client_from_weights_info(
        self,
        weights_info: Any,
        *,
        user_metadata: dict[str, str] | None = None,
    ) -> FiretitanTrainingClient:
        if weights_info.is_lora:
            assert weights_info.lora_rank is not None
            return self.create_lora_training_client(
                base_model=weights_info.base_model,
                rank=weights_info.lora_rank,
                train_unembed=weights_info.train_unembed if weights_info.train_unembed is not None else True,
                train_mlp=weights_info.train_mlp if weights_info.train_mlp is not None else True,
                train_attn=weights_info.train_attn if weights_info.train_attn is not None else True,
                user_metadata=user_metadata,
            )
        return self.create_training_client(
            base_model=weights_info.base_model,
            lora_rank=0,
            user_metadata=user_metadata,
        )

    async def _create_training_client_from_weights_info_async(
        self,
        weights_info: Any,
        *,
        user_metadata: dict[str, str] | None = None,
    ) -> FiretitanTrainingClient:
        if weights_info.is_lora:
            assert weights_info.lora_rank is not None
            return await self.create_lora_training_client_async(
                base_model=weights_info.base_model,
                rank=weights_info.lora_rank,
                train_unembed=weights_info.train_unembed if weights_info.train_unembed is not None else True,
                train_mlp=weights_info.train_mlp if weights_info.train_mlp is not None else True,
                train_attn=weights_info.train_attn if weights_info.train_attn is not None else True,
                user_metadata=user_metadata,
            )
        return self.create_training_client(
            base_model=weights_info.base_model,
            lora_rank=0,
            user_metadata=user_metadata,
        )

    def create_base_training_client(
        self,
        base_model: str,
        user_metadata: dict[str, str] | None = None,
    ) -> FiretitanTrainingClient:
        """Create a base-only FiretitanTrainingClient (frozen, no LoRA adapter).

        The returned client runs forward passes through the frozen base model
        weights with all LoRA adapters disabled.  This is useful as a KL
        divergence reference model when training with LoRA — no separate
        reference-only trainer job is needed.

        Args:
            base_model: Model name (e.g. ``"accounts/fireworks/models/qwen3-8b"``).
            user_metadata: Optional run metadata.

        Returns:
            A :class:`FiretitanTrainingClient` whose ``forward()`` calls
            run on the base weights only.  Do **not** call ``forward_backward``
            or ``optim_step`` on this client — it exists solely for
            reference log-prob computation.
        """
        return _create_base_only_training_client(
            self.holder,
            base_model,
            self._user_metadata(user_metadata),
            request_type="CreateModel",
        )

    def create_sampling_client(
        self,
        model_path=None,
        base_model=None,
        retry_config=None,
        deployment_sampler: DeploymentSampler | None = None,
        *,
        tokenizer: Any | None = None,
        concurrency_controller: Any | None = None,
    ) -> FiretitanSamplingClient:
        """Create a Tinker-shaped sampler backed by a configured deployment.

        ``tokenizer`` (for client-side ``/v1/completions`` tokenization) and
        ``concurrency_controller`` are applied to the underlying
        ``DeploymentSampler`` at creation, so callers don't mutate it after the
        fact.
        """
        if retry_config is not None:
            logger.warning("retry_config is currently ignored by FiretitanSamplingClient")
        if deployment_sampler is not None:
            if tokenizer is not None:
                deployment_sampler.tokenizer = tokenizer
            if concurrency_controller is not None:
                deployment_sampler.concurrency_controller = concurrency_controller
            return FiretitanSamplingClient(deployment_sampler)

        managed_config = self._managed_config
        if model_path is not None:
            self.hotload_sampler_snapshot(model_path)
            return self._require_sampler_backend().get_sampling_client(tokenizer, concurrency_controller)

        if self._sampler_backend is not None:
            return self._sampler_backend.get_sampling_client(tokenizer, concurrency_controller)

        if managed_config is not None:
            handle = self._ensure_managed_handle()
            if handle.sampler_backend is not None:
                return handle.sampler_backend.get_sampling_client(tokenizer, concurrency_controller)

        raise NotImplementedError(
            "create_sampling_client requires SDK-managed sampler state or deployment_sampler=.... "
            "Base-model/serverless sampling is not supported in this path."
        )

    def hotload_sampler_snapshot(self, model_path: str) -> None:
        """Hot-load an SDK-managed sampler snapshot into the attached deployment."""
        if self._sampler_backend is None and self._managed_config is not None:
            self._ensure_managed_handle()
        sampler_backend = self._require_sampler_backend()
        if not sampler_backend.hotload_saved_snapshot(model_path):
            raise RuntimeError(f"Hotload failed for sampler snapshot {model_path!r}")
        handle = getattr(self, "_managed_handle", None)
        if handle is not None:
            handle.requires_initial_sampler_sync = False

    def requires_initial_sampler_sync(self) -> bool:
        """Return whether managed setup requires a pre-rollout sampler sync.

        Managed deployment reattach changes the trainer namespace while serving
        may still hold an old hotload snapshot. Recipes use this to trigger one
        explicit base save+hotload before rollout.
        """
        handle = getattr(self, "_managed_handle", None)
        return bool(handle is not None and getattr(handle, "requires_initial_sampler_sync", False))

    def _require_fireworks_api_key(self, operation: str) -> str:
        api_key = getattr(self, "_fireworks_api_key", None)
        if api_key is None:
            raise ValueError(
                f"{operation} requires a Fireworks API key. "
                "Construct FiretitanServiceClient with api_key=fw_... or set FIREWORKS_API_KEY."
            )
        return api_key

    def _managed_deployment_manager(self) -> DeploymentManager:
        handle = None
        if self._managed_config is not None:
            handle = self._ensure_managed_handle()
        deploy_mgr = getattr(handle, "deployment_manager", None)
        if deploy_mgr is not None:
            return deploy_mgr
        return DeploymentManager(
            api_key=self._require_fireworks_api_key("deployment management"),
            base_url=getattr(self, "_managed_base_url", None) or DEFAULT_FIREWORKS_API_URL,
            inference_url=getattr(self, "_managed_inference_url", None),
            hotload_api_url=getattr(self, "_managed_hotload_api_url", None),
            additional_headers=getattr(self, "_managed_additional_headers", None),
            verify_ssl=getattr(self, "_managed_verify_ssl", None),
        )

    def _resolve_inference_deployment_region(self, requested_region: str | None) -> str | None:
        managed_region = getattr(self._managed_config, "region", None) if self._managed_config is not None else None
        if requested_region is not None and managed_region is not None and requested_region != managed_region:
            raise ValueError(
                "Inference deployment region conflicts with managed trainer region: "
                f"region={requested_region!r}, managed region={managed_region!r}."
            )
        return requested_region or managed_region

    def _resolve_inference_deployment_shape(self, config: DeploymentConfig) -> str | None:
        if config.deployment_shape is not None:
            return config.deployment_shape
        managed_config = self._managed_config
        if managed_config is not None and config.base_model == managed_config.base_model:
            return self.deployment_shape
        return None

    def _track_inference_deployment_cleanup(
        self,
        deploy_mgr: DeploymentManager,
        deployment_id: str,
        cleanup_on_close: DeploymentCleanupOnClose | None,
    ) -> None:
        if cleanup_on_close is None:
            return
        if not hasattr(self, "_owned_inference_deployments"):
            self._owned_inference_deployments = []
        self._owned_inference_deployments.append((deploy_mgr, deployment_id, cleanup_on_close))

    def create_deployment_sampler_for_model(
        self,
        model: str,
        *,
        tokenizer: Any | None = None,
        concurrency_controller: Any | None = None,
        inference_url: str | None = None,
    ) -> DeploymentSampler:
        """Create a FireTitan-native sampler for an existing inference model."""
        sampler = DeploymentSampler(
            inference_url=(
                inference_url
                or getattr(self, "_managed_inference_url", None)
                or getattr(self, "_managed_base_url", None)
                or DEFAULT_FIREWORKS_API_URL
            ),
            model=model,
            api_key=self._require_fireworks_api_key("deployment sampling"),
            tokenizer=tokenizer,
        )
        if concurrency_controller is not None:
            sampler.concurrency_controller = concurrency_controller
        return sampler

    def create_inference_deployment_sampler(
        self,
        config: DeploymentConfig,
        *,
        timeout_s: float = 5400,
        cleanup_on_close: DeploymentCleanupOnClose | None = None,
        tokenizer: Any | None = None,
        concurrency_controller: Any | None = None,
    ) -> DeploymentSampler:
        """Create or reuse an inference deployment and return a sampler for it.

        Managed services reuse the canonical trainer region. If the requested
        deployment is for the same base model as the managed student, the SDK
        also reuses the resolved managed deployment shape unless the caller
        passes an explicit deployment shape.
        """
        if config.max_replica_count <= 0:
            raise ValueError("DeploymentConfig.max_replica_count must be positive for inference sampling.")
        deploy_mgr = self._managed_deployment_manager()
        deployment_shape = self._resolve_inference_deployment_shape(config)
        region = self._resolve_inference_deployment_region(config.region)
        resolved_config = replace(config, deployment_shape=deployment_shape, region=region)

        existing = deploy_mgr.get(resolved_config.deployment_id)
        if existing is not None:
            state = getattr(existing, "state", None)
            if state in _INFERENCE_DEPLOYMENT_TERMINAL_STATES:
                raise RuntimeError(
                    f"Inference deployment {resolved_config.deployment_id!r} is in terminal state {state!r}. "
                    "Use a different deployment_id or restore/delete the old resource."
                )
            logger.info("Re-using inference deployment: %s", resolved_config.deployment_id)
        else:
            deploy_mgr.create_or_get(resolved_config)
            logger.info("Requested inference deployment: %s", resolved_config.deployment_id)
            self._track_inference_deployment_cleanup(
                deploy_mgr,
                resolved_config.deployment_id,
                cleanup_on_close,
            )

        ready = deploy_mgr.wait_for_ready(resolved_config.deployment_id, timeout_s=timeout_s)
        model = ready.inference_model or f"accounts/{deploy_mgr.account_id}/deployments/{resolved_config.deployment_id}"
        return self.create_deployment_sampler_for_model(
            model,
            tokenizer=tokenizer,
            concurrency_controller=concurrency_controller,
            inference_url=deploy_mgr.inference_url,
        )

    async def create_sampling_client_async(
        self,
        model_path=None,
        base_model=None,
        retry_config=None,
        deployment_sampler: DeploymentSampler | None = None,
    ) -> FiretitanSamplingClient:
        return await asyncio.to_thread(
            self.create_sampling_client,
            model_path=model_path,
            base_model=base_model,
            retry_config=retry_config,
            deployment_sampler=deployment_sampler,
        )

    def create_deployment_sampler(
        self,
        model_path: str | None = None,
        *,
        tokenizer: Any | None = None,
        concurrency_controller: Any | None = None,
    ) -> DeploymentSampler:
        """Return the FireTitan ``DeploymentSampler`` directly (not the Tinker wrapper).

        The recipes drive the FireTitan-native sampler — client-side
        tokenization, ``/v1/completions`` token-in/out, logprobs, routing
        matrices, TIS echo — which the Tinker-shaped ``SamplingClient`` doesn't
        expose. ``create_sampling_client`` returns that Tinker wrapper; this
        hands back the underlying ``DeploymentSampler`` so callers don't unwrap
        ``.deployment_sampler`` themselves. Same deployment + hot-load.
        """
        return self.create_sampling_client(
            model_path=model_path,
            tokenizer=tokenizer,
            concurrency_controller=concurrency_controller,
        ).deployment_sampler

    def create_reference_client(
        self,
        base_model: str,
        *,
        lora_rank: int = 0,
        user_metadata: dict[str, str] | None = None,
    ) -> FiretitanTrainingClient:
        """Create a frozen reference client for KL/DPO baseline logprobs.

        The SDK hides the shared-vs-separate-trainer decision; pass the policy
        ``lora_rank`` and the SDK picks the right backing:

        * LoRA policy without a ``reference_training_shape_id`` → the reference
          reuses the policy trainer session with the adapter disabled (base
          weights). No second trainer is provisioned.
        * Full-parameter policies use a separate frozen reference trainer that
          the SDK owns and tears down on :meth:`close` (or early via
          :meth:`release_references`). If ``reference_training_shape_id`` is not
          set, trainer creation asks the backend to select a LoRA-capable shape.
        """
        managed_config = self._managed_config
        if not hasattr(self, "holder") and managed_config is not None:
            from fireworks.training.sdk.managed import _use_shared_base_reference

            _warn_deprecated_override("create_reference_client", "base_model", base_model, managed_config.base_model)
            policy_lora_rank = lora_rank or managed_config.lora_rank
            if _use_shared_base_reference(managed_config, policy_lora_rank=policy_lora_rank):
                handle = self._ensure_managed_handle(
                    user_metadata=self._user_metadata(user_metadata),
                )
                return handle.service_client.create_base_training_client(
                    base_model,
                    user_metadata=self._user_metadata(user_metadata),
                )
            handle = self._ensure_managed_handle(user_metadata=self._user_metadata(user_metadata))
            if handle.reference_handle is not None:
                self._reference_handle = handle.reference_handle
                return handle.reference_handle.training_client
            reference_handle = self._provision_reference_handle(
                policy_lora_rank=policy_lora_rank,
                user_metadata=self._user_metadata(user_metadata),
            )
            return reference_handle.training_client
        # Direct (non-managed) holder service: base-only on the same session.
        return self.create_base_training_client(
            base_model,
            user_metadata=self._user_metadata(user_metadata),
        )

    def _provision_reference_handle(
        self,
        *,
        policy_lora_rank: int,
        user_metadata: dict[str, str] | None,
    ) -> Any:
        """Provision a separate frozen reference trainer this service owns."""
        from fireworks.training.sdk.managed import (
            _reference_managed_config,
            _create_managed_tinker_client,
        )

        if self._fireworks_api_key is None:
            raise ValueError(
                "Provisioning a separate reference trainer requires a Fireworks API key. "
                "Construct FiretitanServiceClient with api_key=fw_... or set FIREWORKS_API_KEY."
            )
        # The reference config (the one remaining config derivation) carries the
        # runtime forward-only flag and the policy base_model; it is the single
        # source for provisioning. base_model here is only used to detect a
        # deprecated override (warned at the create_reference_client boundary).
        reference_config = _reference_managed_config(self._managed_config, policy_lora_rank=policy_lora_rank)
        handle = _create_managed_tinker_client(
            api_key=self._fireworks_api_key,
            config=reference_config,
            user_metadata=user_metadata,
            base_url=self._managed_base_url,
            inference_url=self._managed_inference_url,
            hotload_api_url=self._managed_hotload_api_url,
            additional_headers=self._managed_additional_headers,
            verify_ssl=self._managed_verify_ssl,
        )
        self._reference_handle = handle
        self._owned_reference_handles.append(handle)
        return handle
