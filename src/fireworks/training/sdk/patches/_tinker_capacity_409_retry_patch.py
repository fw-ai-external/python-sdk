"""Retry capacity/recovery HTTP 409s on serverless trainer future retrieve.

Scope: only requests whose URL is under ``/training/v1/serverless`` (managed /
recipe SFT & DPO on serverless trainers). Dedicated trainer URLs are unchanged.

Tinker retries 409 on submit but marks retrieve-path 409 as FATAL; this
reclassifies serverless capacity/lifecycle conflicts as ``RETRY_WITH_BACKOFF``.
Identity and other explicit, unrecognized conflicts stay FATAL.
"""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

import tinker.lib.api_future_impl as api_future_impl

_PATCH_SENTINEL = "_fireworks_capacity_409_retry_patch"
_SERVERLESS_ROUTE = "/training/v1/serverless"

_RETRYABLE_MARKERS = (
    "capacity_exhausted",
    "recovery_required",
    "out of capacity",
    "at capacity",
    "capacity is temporarily",
    "training capacity",
    "paused_capacity",
    "recovery is required",
    "fenced recovery",
    "lifecycle is closing",
    "lifecycle is releasing",
    "resource_exhausted",
)
_TERMINAL_MARKERS = (
    "already exists",
    "idempotency",
    "different request payload",
    "conflicts with durable model state",
    "model lifecycle conflicts with durable state",
)


def _is_serverless_trainer_request(exc: Any) -> bool:
    request = getattr(exc, "request", None)
    url = getattr(request, "url", None)
    if url is None:
        return False
    try:
        path = urlparse(str(url)).path
    except Exception:
        return False
    return path == _SERVERLESS_ROUTE or path.startswith(f"{_SERVERLESS_ROUTE}/")


def _exception_body(exc: Any) -> Any:
    body = getattr(exc, "body", None)
    if body is None:
        response = getattr(exc, "response", None)
        if response is not None:
            try:
                body = response.json()
            except Exception:
                body = getattr(response, "text", None)
    return body


def _exception_text(exc: Any, detail: str | None, body: Any) -> str:
    parts: list[str] = []
    if isinstance(detail, str) and detail.strip():
        parts.append(detail)
    if isinstance(body, dict):
        nested = body.get("error")
        for value in (
            body.get("detail"),
            body.get("message"),
            body.get("error_class"),
            nested.get("error_class") if isinstance(nested, dict) else None,
            nested.get("message") if isinstance(nested, dict) else None,
        ):
            if isinstance(value, str) and value.strip():
                parts.append(value)
    elif isinstance(body, str) and body.strip():
        parts.append(body)
    source = getattr(exc, "_fireworks_training_error_source", None)
    error_class = getattr(source, "error_class", None)
    if isinstance(error_class, str) and error_class.strip():
        parts.append(error_class)
    return " ".join(parts).lower()


def _is_retryable_capacity_409(exc: Any, detail: str | None) -> bool:
    body = _exception_body(exc)
    haystack = _exception_text(exc, detail, body)
    if any(marker in haystack for marker in _TERMINAL_MARKERS):
        return False
    if any(marker in haystack for marker in _RETRYABLE_MARKERS):
        return True
    # Only genuinely bare 409s get the capacity/migration compatibility fallback.
    # An explicit but unrecognized conflict (e.g. a FAILED/EXPIRED run) must
    # remain fatal: Tinker's backoff path has no retry budget.
    if getattr(exc, "_fireworks_training_error_source", None) is not None:
        return False
    return body is None or (isinstance(body, dict) and not body) or (isinstance(body, str) and not body.strip())


def _patch_rest_status_error_to_transport_error() -> bool:
    current = api_future_impl._rest_status_error_to_transport_error
    if getattr(current, _PATCH_SENTINEL, False):
        return False

    def _rest_status_error_to_transport_error(exc: Any) -> Any:
        transport = current(exc)
        if (
            getattr(transport, "status_code", None) != 409
            or getattr(transport, "kind", None) != api_future_impl._TransportErrorKind.FATAL
        ):
            return transport
        if not _is_serverless_trainer_request(exc):
            return transport
        detail = getattr(transport, "detail", None)
        if not _is_retryable_capacity_409(exc, detail if isinstance(detail, str) else None):
            return transport
        return api_future_impl._TransportError(
            kind=api_future_impl._TransportErrorKind.RETRY_WITH_BACKOFF,
            status_code=409,
            detail=getattr(transport, "detail", str(exc)),
            exception=getattr(transport, "exception", exc),
            try_again_body=getattr(transport, "try_again_body", None),
            response_headers=getattr(transport, "response_headers", None),
            request_headers=getattr(transport, "request_headers", None),
            response_body=getattr(transport, "response_body", None),
            event_name=getattr(transport, "event_name", "exception"),
        )

    setattr(_rest_status_error_to_transport_error, _PATCH_SENTINEL, True)
    api_future_impl._rest_status_error_to_transport_error = _rest_status_error_to_transport_error
    return True


_patch_rest_status_error_to_transport_error()
