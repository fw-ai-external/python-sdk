"""Capacity retry rules for explicitly opted-in serverless holders."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

_SERVERLESS_ROUTE = "/training/v1/serverless"
_HOLDER_ATTR = "_fireworks_serverless_supervised_409_retry"

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


def _mark_serverless_supervised_409_retry(holder: Any) -> None:
    """Mark one Tinker holder as an opted-in supervised serverless run."""
    setattr(holder, _HOLDER_ATTR, True)


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
