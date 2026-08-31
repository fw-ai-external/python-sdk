"""Agent-environment-local OpenAI-compatible sidecar for TITO trajectories."""

from __future__ import annotations

import json
import time
import uuid
import asyncio
import secrets
from typing import Any, Mapping, Callable
from collections import OrderedDict

from fireworks.training.sdk.sampling import DeploymentSampler
from fireworks.training.sdk.tito._types import (
    TITOError,
    TITORenderer,
    TITOCallResult,
    TITOPromptMode,
    TITOChatRequest,
    TITOClassification,
    TrajectoryDriftPolicy,
    TITOTrajectoryArtifact,
    TITOTrajectoryEndpoint,
    _canonical_bytes,
)
from fireworks.training.sdk.tito._engine import (
    TITOEventObserver,
    TITOTrajectoryEngine,
    _ExactTokenSampler,
    _LinearTrajectoryCore,
)

_FORBIDDEN_AFFINITY_HEADERS = frozenset({"x-multi-turn-session-id", "x-session-affinity"})
_REQUEST_LOCAL_HEADERS = frozenset({"authorization", "x-api-key", "x-fireworks-session-id"})
_TERMINAL_ENGINE_LIMIT = 4096


class TITOSidecar:
    """Loopback runtime scoped to one Docker or remote-sandbox environment."""

    _MAX_HTTP_REQUEST_BYTES = 64 * 1024 * 1024

    def __init__(
        self,
        sampler: _ExactTokenSampler,
        *,
        renderer: TITORenderer,
        max_context_tokens: int,
        max_output_tokens: int,
        call_classifier: Callable[[TITOChatRequest], TITOClassification] | None = None,
        sampling_defaults: Mapping[str, Any] | None = None,
        backend_headers_snapshot: Mapping[str, str] | None = None,
        observer: TITOEventObserver | None = None,
        default_drift_policy: TrajectoryDriftPolicy | None = None,
        prompt_mode: TITOPromptMode = "full_history",
        keepalive_seconds: float = 5.0,
    ) -> None:
        self._sampler = sampler
        self._renderer = renderer
        self._max_context_tokens = max_context_tokens
        self._max_output_tokens = max_output_tokens
        self._call_classifier = call_classifier
        self._sampling_defaults = dict(sampling_defaults or {})
        self._backend_headers_snapshot = dict(backend_headers_snapshot or {})
        self._observer = observer
        self._default_drift_policy = default_drift_policy
        self._prompt_mode = prompt_mode
        self._engines: dict[str, TITOTrajectoryEngine] = {}
        self._terminal_engines: OrderedDict[str, TITOTrajectoryEngine] = OrderedDict()
        self._trajectory_credentials: dict[str, str] = {}
        self._pending_trajectory_ids: set[str] = set()
        self.keepalive_seconds = keepalive_seconds
        self._runner: Any = None
        self._site: Any = None
        self._base_url: str | None = None
        self._port: int = 0

    @property
    def port(self) -> int:
        return self._port

    @classmethod
    def from_deployment_sampler(
        cls,
        sampler: DeploymentSampler,
        *,
        renderer: TITORenderer,
        max_context_tokens: int,
        max_output_tokens: int,
        call_classifier: Callable[[TITOChatRequest], TITOClassification] | None = None,
        sampling_defaults: Mapping[str, Any] | None = None,
        observer: TITOEventObserver | None = None,
        keepalive_seconds: float = 5.0,
        default_drift_policy: TrajectoryDriftPolicy | None = None,
        prompt_mode: TITOPromptMode = "full_history",
    ) -> "TITOSidecar":
        source = dict(sampler.additional_headers or {})
        normalized = {name.lower(): value for name, value in source.items()}
        conflict = sorted(_FORBIDDEN_AFFINITY_HEADERS.intersection(normalized))
        if conflict:
            raise ValueError("sampler additional_headers contains a fixed affinity header: " + ", ".join(conflict))
        request_local_conflict = sorted(_REQUEST_LOCAL_HEADERS.intersection(normalized))
        if request_local_conflict:
            raise ValueError(
                "sampler additional_headers overrides SDK request-local headers: " + ", ".join(request_local_conflict)
            )
        return cls(
            sampler,
            renderer=renderer,
            max_context_tokens=max_context_tokens,
            max_output_tokens=max_output_tokens,
            call_classifier=call_classifier,
            sampling_defaults=sampling_defaults,
            backend_headers_snapshot=normalized,
            observer=observer,
            keepalive_seconds=keepalive_seconds,
            default_drift_policy=default_drift_policy,
            prompt_mode=prompt_mode,
        )

    def create_trajectory(
        self,
        *,
        trajectory_id: str | None = None,
        serving_affinity_key: str | None = None,
        metadata: Mapping[str, Any] | None = None,
        drift_policy: TrajectoryDriftPolicy | None = None,
    ) -> TITOTrajectoryEndpoint:
        if self._base_url is None:
            raise RuntimeError("start the sidecar before creating a trajectory")
        trajectory_id = trajectory_id or uuid.uuid4().hex
        if (
            trajectory_id in self._engines
            or trajectory_id in self._terminal_engines
            or trajectory_id in self._pending_trajectory_ids
        ):
            raise ValueError(f"duplicate trajectory_id: {trajectory_id}")
        core = _LinearTrajectoryCore(
            self._sampler,
            self._renderer,
            max_context_tokens=self._max_context_tokens,
            max_output_tokens=self._max_output_tokens,
            call_classifier=self._call_classifier,
            sampling_defaults=self._sampling_defaults,
            backend_headers_snapshot=self._backend_headers_snapshot,
            observer=self._observer,
            default_drift_policy=self._default_drift_policy,
            prompt_mode=self._prompt_mode,
        )
        trajectory_id = core.create_trajectory(
            trajectory_id=trajectory_id,
            serving_affinity_key=serving_affinity_key,
            metadata=metadata,
            drift_policy=drift_policy,
        )
        engine = TITOTrajectoryEngine(core, trajectory_id)
        self._engines[trajectory_id] = engine
        return self._trajectory_endpoint(trajectory_id)

    async def create_trajectory_async(
        self,
        *,
        trajectory_id: str | None = None,
        serving_affinity_key: str | None = None,
        metadata: Mapping[str, Any] | None = None,
        drift_policy: TrajectoryDriftPolicy | None = None,
    ) -> TITOTrajectoryEndpoint:
        """Create a trajectory without blocking the caller's event loop on debug I/O."""
        if self._base_url is None:
            raise RuntimeError("start the sidecar before creating a trajectory")
        trajectory_id = trajectory_id or uuid.uuid4().hex
        if (
            trajectory_id in self._engines
            or trajectory_id in self._terminal_engines
            or trajectory_id in self._pending_trajectory_ids
        ):
            raise ValueError(f"duplicate trajectory_id: {trajectory_id}")
        requested_trajectory_id = trajectory_id
        self._pending_trajectory_ids.add(requested_trajectory_id)
        core = _LinearTrajectoryCore(
            self._sampler,
            self._renderer,
            max_context_tokens=self._max_context_tokens,
            max_output_tokens=self._max_output_tokens,
            call_classifier=self._call_classifier,
            sampling_defaults=self._sampling_defaults,
            backend_headers_snapshot=self._backend_headers_snapshot,
            observer=self._observer,
            default_drift_policy=self._default_drift_policy,
            prompt_mode=self._prompt_mode,
        )
        try:
            trajectory_id = await core.create_trajectory_async(
                trajectory_id=requested_trajectory_id,
                serving_affinity_key=serving_affinity_key,
                metadata=metadata,
                drift_policy=drift_policy,
            )
        finally:
            self._pending_trajectory_ids.discard(requested_trajectory_id)
        engine = TITOTrajectoryEngine(core, trajectory_id)
        self._engines[trajectory_id] = engine
        return self._trajectory_endpoint(trajectory_id)

    def _trajectory_endpoint(self, trajectory_id: str) -> TITOTrajectoryEndpoint:
        if self._base_url is None:
            raise RuntimeError("sidecar is not running")
        api_key = self._credential_for(trajectory_id)
        return TITOTrajectoryEndpoint(
            trajectory_id=trajectory_id,
            openai_base_url=f"{self._base_url}/trajectories/{trajectory_id}/v1",
            api_key=api_key,
        )

    def _engine_for(self, trajectory_id: str) -> TITOTrajectoryEngine:
        engine = self._engines.get(trajectory_id) or self._terminal_engines.get(trajectory_id)
        if engine is None:
            raise TITOError("tito_trajectory_not_found", 404, "unknown trajectory")
        return engine

    def _retire_engine(self, trajectory_id: str, engine: TITOTrajectoryEngine) -> None:
        if self._engines.get(trajectory_id) is not engine:
            return
        self._engines.pop(trajectory_id)
        self._terminal_engines[trajectory_id] = engine
        while len(self._terminal_engines) > _TERMINAL_ENGINE_LIMIT:
            evicted_id, _engine = self._terminal_engines.popitem(last=False)
            self._trajectory_credentials.pop(evicted_id, None)

    async def finish_trajectory(self, trajectory_id: str) -> TITOTrajectoryArtifact:
        engine = self._engine_for(trajectory_id)
        artifact = await engine.finish()
        self._retire_engine(trajectory_id, engine)
        return artifact

    async def abandon_trajectory(self, trajectory_id: str, reason: str = "caller_abandoned") -> TITOTrajectoryArtifact:
        engine = self._engine_for(trajectory_id)
        try:
            artifact = await engine.abandon(reason)
        finally:
            if engine.is_terminal:
                self._retire_engine(trajectory_id, engine)
        if artifact is None:
            engine.require_active()
            raise AssertionError("active trajectory abandonment returned no artifact")
        return artifact

    async def fail_trajectory(self, trajectory_id: str, reason: str) -> TITOTrajectoryArtifact:
        engine = self._engine_for(trajectory_id)
        try:
            artifact = await engine.fail(reason)
        finally:
            if engine.is_terminal:
                self._retire_engine(trajectory_id, engine)
        if artifact is None:
            engine.require_active()
            raise AssertionError("active trajectory failure returned no artifact")
        return artifact

    async def observe_agent_wall(self, trajectory_id: str, seconds: float) -> None:
        await self._engine_for(trajectory_id).observe_agent_wall_async(seconds)

    async def start(self, port: int = 0) -> None:
        """Start the environment-private HTTP adapter on loopback."""
        if self._runner is not None:
            return
        from aiohttp import web

        # A long agent history can legitimately exceed aiohttp's 1 MiB default
        # before it reaches the sidecar's exact token budget check.
        application = web.Application(client_max_size=self._MAX_HTTP_REQUEST_BYTES)
        application.router.add_post(
            "/trajectories/{trajectory_id}/v1/chat/completions",
            self._handle_openai_chat,
        )
        application.router.add_get("/trajectories/{trajectory_id}/v1/models", self._handle_openai_models)
        runner = web.AppRunner(application)
        await runner.setup()
        site = web.TCPSite(runner, "127.0.0.1", port)
        await site.start()
        sockets = site._server.sockets  # noqa: SLF001 - aiohttp exposes no bound-port API
        bound_port = sockets[0].getsockname()[1]
        self._runner = runner
        self._site = site
        self._port = int(bound_port)
        self._base_url = f"http://127.0.0.1:{bound_port}"

    async def _write_error(self, request: Any, error: TITOError) -> Any:
        from aiohttp import web

        headers = {"x-should-retry": "true" if error.should_retry else "false"}
        return web.json_response(error.openai_body(), status=error.status, headers=headers)

    @staticmethod
    def _upstream_error() -> TITOError:
        return TITOError(
            "tito_upstream_error",
            502,
            "policy inference failed before commit",
            should_retry=True,
        )

    def _credential_for(self, trajectory_id: str) -> str:
        return self._trajectory_credentials.setdefault(
            trajectory_id,
            f"tito_{secrets.token_urlsafe(32)}",
        )

    def _authenticate_trajectory(self, request: Any) -> str:
        authorization = request.headers.get("authorization", "")
        if not authorization.startswith("Bearer "):
            raise TITOError("invalid_api_key", 401, "invalid trajectory credential")
        supplied = authorization[len("Bearer ") :]
        trajectory_id = request.match_info.get("trajectory_id")
        if trajectory_id is None:
            raise TITOError("invalid_api_key", 401, "invalid trajectory credential")
        expected = self._trajectory_credentials.get(trajectory_id)
        if expected is None or not secrets.compare_digest(supplied, expected):
            raise TITOError("invalid_api_key", 401, "invalid trajectory credential")
        return trajectory_id

    async def _handle_openai_models(self, request: Any) -> Any:
        from aiohttp import web

        try:
            trajectory_id = self._authenticate_trajectory(request)
            engine = self._engine_for(trajectory_id)
            engine.require_active()
        except TITOError as exc:
            return await self._write_error(request, exc)
        model = str(getattr(engine.sampler, "model", "policy"))
        model_ids = list(dict.fromkeys(("policy", model)))
        return web.json_response(
            {
                "object": "list",
                "data": [
                    {
                        "id": model_id,
                        "object": "model",
                        "created": 0,
                        "owned_by": "fireworks",
                    }
                    for model_id in model_ids
                ],
            }
        )

    async def _handle_openai_chat(self, request: Any) -> Any:
        from aiohttp import web

        started_at = time.time()
        transport_started_at = time.monotonic()
        try:
            trajectory_id = self._authenticate_trajectory(request)
            engine = self._engine_for(trajectory_id)
        except TITOError as exc:
            return await self._write_error(request, exc)
        wire_request_body: str | None = None
        payload: Any = None
        try:
            decoded_body = (await request.read()).decode("utf-8")
            wire_request_body = decoded_body
            payload = json.loads(decoded_body)
            normalized = TITOChatRequest.from_openai(
                payload,
                wire_request_body=wire_request_body,
            )
        except TITOError as exc:
            try:
                await engine.record_normalization_reject_async(
                    started_at=started_at,
                    error=exc,
                    wire_request=payload,
                    wire_request_body=wire_request_body,
                )
            except TITOError as accounting_error:
                return await self._write_error(request, accounting_error)
            return await self._write_error(request, exc)
        except Exception as exc:
            try:
                await engine.record_normalization_reject_async(
                    started_at=started_at,
                    error=exc,
                    wire_request=payload,
                    wire_request_body=wire_request_body,
                )
            except TITOError as accounting_error:
                return await self._write_error(request, accounting_error)
            return await self._write_error(request, TITOError("tito_invalid_request", 400, "invalid JSON request"))

        try:
            state = engine.require_active(
                count_terminal_request=True,
                request_started_at=started_at,
            )
        except TITOError as exc:
            return await self._write_error(request, exc)
        transport_task = asyncio.current_task()
        if transport_task is not None:
            state.transport_tasks.add(transport_task)
            transport_task.add_done_callback(state.transport_tasks.discard)

        idempotency_key = request.headers.get("idempotency-key")
        if not bool(payload.get("stream", False)):
            try:
                result = await engine.complete(normalized, idempotency_key=idempotency_key)
            except TITOError as exc:
                return await self._write_error(request, exc)
            except Exception:
                return await self._write_error(request, self._upstream_error())
            body = _canonical_bytes(dict(result.response))
            response = web.StreamResponse(
                status=200,
                headers={"content-type": "application/json"},
            )
            committed = result.turn_id
            wire_evidence = {
                "transport": "json",
                "status": 200,
                "content_type": "application/json",
                "body": body.decode("utf-8"),
                "body_bytes": len(body),
            }
            try:
                await response.prepare(request)
                await response.write(body)
                await response.write_eof()
                if committed is not None:
                    await engine.record_response_emission_async(
                        committed,
                        "completed",
                        wire_evidence=wire_evidence,
                    )
            except (ConnectionError, OSError):
                if committed is not None:
                    await engine.record_response_emission_async(
                        committed,
                        "ambiguous",
                        wire_evidence=wire_evidence,
                    )
                return response
            except BaseException:
                if committed is not None:
                    await engine.record_response_emission_async(
                        committed,
                        "ambiguous",
                        wire_evidence=wire_evidence,
                    )
                raise
            return response

        prepared = asyncio.Event()
        task = asyncio.create_task(
            engine.complete(
                normalized,
                idempotency_key=idempotency_key,
                prepared_event=prepared,
            )
        )
        response = web.StreamResponse(
            status=200,
            headers={"content-type": "text/event-stream", "cache-control": "no-cache"},
        )
        committed: str | None = None
        wire_events: list[dict[str, Any]] = []

        async def _write_sse(encoded: bytes, kind: str) -> None:
            await response.write(encoded)
            wire_events.append(
                {
                    "kind": kind,
                    "at_seconds": time.monotonic() - transport_started_at,
                    "data": encoded.decode("utf-8"),
                }
            )

        async def _settle_after_transport_loss() -> bool:
            """Cancel pre-commit work or expose a raced commit as ambiguous."""

            nonlocal committed
            if not task.done():
                task.cancel()
            outcome = (await asyncio.gather(task, return_exceptions=True))[0]
            if isinstance(outcome, TITOCallResult) and outcome.turn_id is not None:
                committed = outcome.turn_id
            if committed is None:
                return False
            await engine.record_response_emission_async(
                committed,
                "ambiguous",
                wire_evidence={"transport": "sse", "events": wire_events},
            )
            return True

        prepare_wait = asyncio.create_task(prepared.wait())
        try:
            done, _pending = await asyncio.wait(
                {task, prepare_wait},
                return_when=asyncio.FIRST_COMPLETED,
            )
            if task in done and not prepared.is_set():
                try:
                    result = task.result()
                except TITOError as exc:
                    return await self._write_error(request, exc)
                except Exception:
                    return await self._write_error(request, self._upstream_error())
                raise AssertionError(f"completion returned before preparation: {result}")
        except asyncio.CancelledError:
            await _settle_after_transport_loss()
            raise
        finally:
            prepare_wait.cancel()
            await asyncio.gather(prepare_wait, return_exceptions=True)

        async def _write_sse_error(error: TITOError) -> None:
            try:
                await response.write(b"event: error\ndata: " + _canonical_bytes(error.openai_body()) + b"\n\n")
                await response.write_eof()
            except (ConnectionError, OSError):
                pass

        try:
            # Stream preparation belongs to the same cancellation scope as the
            # sampler task. If the client disappears before headers commit, the
            # uncommitted inference is cancelled and awaited below.
            await response.prepare(request)
            state.metrics.observe(
                "transport/downstream_ready_seconds",
                time.monotonic() - transport_started_at,
            )
            while not task.done():
                try:
                    await asyncio.wait_for(asyncio.shield(task), timeout=self.keepalive_seconds)
                except asyncio.TimeoutError:
                    await _write_sse(b": keepalive\n\n", "keepalive")
                    state.metrics.increment("transport/keepalives_sent")
            result = await task
            committed = result.turn_id
            choice = dict(result.response)["choices"][0]
            message = choice["message"]
            delta = {
                "id": dict(result.response)["id"],
                "object": "chat.completion.chunk",
                "created": dict(result.response)["created"],
                "model": dict(result.response)["model"],
                "choices": [{"index": 0, "delta": message, "finish_reason": None}],
            }
            terminal = {
                "id": dict(result.response)["id"],
                "object": "chat.completion.chunk",
                "created": dict(result.response)["created"],
                "model": dict(result.response)["model"],
                "choices": [
                    {
                        "index": 0,
                        "delta": {},
                        "finish_reason": choice["finish_reason"],
                    }
                ],
            }
            await _write_sse(b"data: " + _canonical_bytes(delta) + b"\n\n", "assistant")
            await _write_sse(b"data: " + _canonical_bytes(terminal) + b"\n\n", "terminal")
            await _write_sse(b"data: [DONE]\n\n", "done")
            await response.write_eof()
            if committed is not None:
                await engine.record_response_emission_async(
                    committed,
                    "completed",
                    wire_evidence={"transport": "sse", "events": wire_events},
                )
            return response
        except TITOError as exc:
            await _settle_after_transport_loss()
            await _write_sse_error(exc)
            return response
        except (ConnectionError, OSError):
            await _settle_after_transport_loss()
            return response
        except asyncio.CancelledError:
            await _settle_after_transport_loss()
            raise
        except Exception:
            if not await _settle_after_transport_loss():
                await _write_sse_error(self._upstream_error())
            return response

    async def close(self) -> None:
        if self._runner is not None:
            await self._runner.cleanup()
            self._runner = None
            self._site = None
            self._port = 0
            self._base_url = None
        terminalization_errors: list[BaseException] = []
        for trajectory_id, engine in tuple(self._engines.items()):
            try:
                await engine.close()
            except BaseException as exc:
                terminalization_errors.append(exc)
            finally:
                if engine.is_terminal:
                    self._retire_engine(trajectory_id, engine)
        observer_close = getattr(self._observer, "close", None)
        if observer_close is not None:
            result = observer_close()
            if asyncio.iscoroutine(result):
                await result
        if terminalization_errors:
            raise terminalization_errors[0]

    async def __aenter__(self) -> "TITOSidecar":
        await self.start()
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        await self.close()
