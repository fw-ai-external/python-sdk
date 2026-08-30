"""Preserve private Fireworks structured context on Tinker exceptions."""

from __future__ import annotations

from typing import Any
from contextvars import ContextVar
from collections.abc import Mapping

from tinker.lib import api_future_impl
from tinker._client import AsyncTinker
from tinker._response import AsyncAPIResponse
from tinker._exceptions import RequestFailedError

from fireworks.training.sdk.errors import (
    _tinker_source_error,
    _is_serverless_gateway_url,
    _copy_training_error_source,
    _attach_training_error_source,
    _serverless_gateway_source_error,
)

_PATCH_SENTINEL = "_fireworks_structured_error_patch"
_FAILED_SOURCE_ATTR = "_fireworks_training_error_source"
_CAPTURE_FUTURE_SOURCE: ContextVar[bool] = ContextVar(
    "_fireworks_capture_tinker_future_source",
    default=False,
)
_CAPTURED_FUTURE_SOURCE: ContextVar[Any | None] = ContextVar(
    "_fireworks_captured_tinker_future_source",
    default=None,
)


def _future_source_from_result(value: Any) -> Any | None:
    if not isinstance(value, Mapping) or "error" not in value:
        return None
    return _tinker_source_error(
        error=value.get("error"),
        category=value.get("category"),
        error_class=value.get("error_class"),
    )


def _patch_response_json() -> bool:
    """Capture raw future fields before Tinker reduces them to ``_Failed``."""

    current = AsyncAPIResponse.json
    if getattr(current, _PATCH_SENTINEL, False):
        return False

    async def _json(self: AsyncAPIResponse[Any]) -> object:
        result = await current(self)
        if _CAPTURE_FUTURE_SOURCE.get():
            source = _future_source_from_result(result)
            if source is not None:
                _CAPTURED_FUTURE_SOURCE.set(source)
        return result

    setattr(_json, _PATCH_SENTINEL, True)
    AsyncAPIResponse.json = _json
    return True


def _make_fetch_via_rest_with_source_capture(current: Any) -> Any:
    async def _fetch_via_rest(self: Any, state: Any, iteration: int) -> Any:
        capture_token = _CAPTURE_FUTURE_SOURCE.set(True)
        source_token = _CAPTURED_FUTURE_SOURCE.set(None)
        try:
            outcome = await current(self, state, iteration)
            source = _CAPTURED_FUTURE_SOURCE.get()
            if (
                source is not None
                and isinstance(outcome, api_future_impl._Failed)
                and not hasattr(outcome, _FAILED_SOURCE_ATTR)
            ):
                setattr(outcome, _FAILED_SOURCE_ATTR, source)
            return outcome
        finally:
            _CAPTURED_FUTURE_SOURCE.reset(source_token)
            _CAPTURE_FUTURE_SOURCE.reset(capture_token)

    # Preserve the timeout marker when wrapping the current compatibility
    # implementation so its own idempotence check remains valid.
    if getattr(current, "_fireworks_body_timeout_patch", False):
        _fetch_via_rest._fireworks_body_timeout_patch = True
    setattr(_fetch_via_rest, _PATCH_SENTINEL, True)
    return _fetch_via_rest


def _patch_fetch_via_rest() -> bool:
    current = api_future_impl._APIFuture._fetch_via_rest
    if getattr(current, _PATCH_SENTINEL, False):
        return False
    api_future_impl._APIFuture._fetch_via_rest = _make_fetch_via_rest_with_source_capture(current)
    return True


def _request_targets_serverless_gateway(response: Any) -> bool:
    try:
        request = response.request
        url = request.url
    except Exception:
        return False
    return _is_serverless_gateway_url(url)


def _gateway_source(body: Any, response: Any) -> Any | None:
    candidate = body
    if not isinstance(candidate, Mapping):
        try:
            candidate = response.json()
        except Exception:
            return None
    return _serverless_gateway_source_error(candidate)


def _patch_make_status_error() -> bool:
    current = AsyncTinker._make_status_error
    if getattr(current, _PATCH_SENTINEL, False):
        return False

    def _make_status_error(
        self: AsyncTinker,
        err_msg: str,
        *,
        body: object,
        response: Any,
    ) -> Any:
        exc = current(self, err_msg, body=body, response=response)
        try:
            if _request_targets_serverless_gateway(response):
                _attach_training_error_source(
                    exc,
                    _gateway_source(body, response),
                )
        except Exception:
            # Classification is additive context and must never replace the
            # Tinker exception that callers already observe.
            pass
        return exc

    setattr(_make_status_error, _PATCH_SENTINEL, True)
    AsyncTinker._make_status_error = _make_status_error
    return True


def _patch_handle_outcome() -> bool:
    current = api_future_impl._APIFuture._handle_outcome
    if getattr(current, _PATCH_SENTINEL, False):
        return False

    async def _handle_outcome(
        self: Any,
        outcome: Any,
        state: Any,
        stack: Any,
        iteration: int,
        start_time: float,
    ) -> Any:
        try:
            return await current(self, outcome, state, stack, iteration, start_time)
        except RequestFailedError as exc:
            _attach_training_error_source(
                exc,
                getattr(outcome, _FAILED_SOURCE_ATTR, None),
            )
            raise

    setattr(_handle_outcome, _PATCH_SENTINEL, True)
    api_future_impl._APIFuture._handle_outcome = _handle_outcome
    return True


def _patch_handle_transport_error() -> bool:
    current = api_future_impl._APIFuture._handle_transport_error
    if getattr(current, _PATCH_SENTINEL, False):
        return False

    async def _handle_transport_error(
        self: Any,
        err: Any,
        state: Any,
        iteration: int,
        start_time: float,
    ) -> None:
        try:
            await current(self, err, state, iteration, start_time)
        except Exception as exc:
            _copy_training_error_source(exc, err.exception)
            raise

    setattr(_handle_transport_error, _PATCH_SENTINEL, True)
    api_future_impl._APIFuture._handle_transport_error = _handle_transport_error
    return True


def _apply_tinker_structured_error_patch() -> bool:
    """Install independently idempotent source-context propagation hooks."""

    changed = _patch_response_json()
    changed = _patch_fetch_via_rest() or changed
    changed = _patch_make_status_error() or changed
    changed = _patch_handle_outcome() or changed
    changed = _patch_handle_transport_error() or changed
    return changed


_apply_tinker_structured_error_patch()
