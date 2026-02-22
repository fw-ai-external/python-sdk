"""Structured error formatting and API error parsing for the Firetitan SDK.

Provides:
  - format_sdk_error(): build multi-line "what / cause / solution / docs" messages
  - parse_api_error(): extract a human-readable string from an HTTP error response
  - request_with_retries(): retry HTTP requests with exponential backoff (Tinker pattern)
  - HTTP_STATUS_HINTS: status-code -> actionable one-liner
  - Docs URL constants (centralized for easy updates)
"""

from __future__ import annotations

import time
import logging
from typing import Any, Tuple, Callable

import requests as _requests

logger = logging.getLogger(__name__)

# =============================================================================
# Documentation URL constants
# =============================================================================

DOCS_HOTLOAD = "https://docs.fireworks.ai/fine-tuning/hotload"
DOCS_API_KEYS = "https://fireworks.ai/account/api-keys"
DOCS_RLOR = "https://docs.fireworks.ai/fine-tuning/rlor"
DOCS_DEPLOYMENTS = "https://docs.fireworks.ai/deployments"


# =============================================================================
# HTTP status code hints
# =============================================================================

HTTP_STATUS_HINTS: dict[int, str] = {
    400: "Check that all request parameters are valid.",
    401: "Check your API key. Get one at https://fireworks.ai/account/api-keys",
    403: "Your account may not have permission for this resource.",
    404: "The resource was not found. Verify the ID/name is correct.",
    409: "Resource conflict. It may already exist or be in a transitional state.",
    429: "Rate limited. Wait and retry, or contact support.",
    500: "Internal server error. Try again. If persistent, contact support.",
    503: "Service temporarily unavailable. Retry after a short wait.",
}


# =============================================================================
# Formatting helpers
# =============================================================================


def format_sdk_error(
    what: str,
    cause: str,
    solution: str,
    docs_url: str | None = None,
) -> str:
    """Build a structured, actionable error message.

    Example output::

        ERROR: RLOR job creation failed (HTTP 400)
          Cause: invalid request
          Solution: Check that all request parameters are valid.
          Docs: https://docs.fireworks.ai/fine-tuning/rlor

    Args:
        what: Short summary of what went wrong.
        cause: Why it might have happened.
        solution: How to fix it (may be multi-line).
        docs_url: Optional link to relevant documentation.
    """
    lines = [
        f"ERROR: {what}",
        f"  Cause: {cause}",
        f"  Solution: {solution}",
    ]
    if docs_url:
        lines.append(f"  Docs: {docs_url}")
    return "\n".join(lines)


def parse_api_error(resp) -> str:
    """Extract a human-readable error message from an HTTP response.

    Handles the Fireworks API conventions:
      - ``{"error": "message string"}``
      - ``{"error": {"message": "...", "code": ...}}``
      - Plain text bodies

    Args:
        resp: A ``requests.Response`` (or any object with ``.json()`` and
            ``.text`` attributes).

    Returns:
        A concise error string (at most 200 chars for raw-text fallback).
    """
    try:
        body = resp.json()
        err = body.get("error", body)
        if isinstance(err, dict):
            return err.get("message", str(err))
        return str(err)
    except Exception:
        text = getattr(resp, "text", str(resp))
        return text.strip()[:200]


# =============================================================================
# Retry utility (mirrors Tinker SDK's execute_with_retries pattern)
# =============================================================================

RETRYABLE_STATUS_CODES: Tuple[int, ...] = (408, 409, 429, 500, 502, 503, 504)
"""HTTP status codes that should trigger a retry.

Note: 425 (Too Early / hot-loading) is intentionally NOT retried here.
Hot-loads take minutes (not seconds), so the SDK's ~60s exponential backoff
would just waste time on futile retries.  Instead, 425 is returned immediately
to the caller so the training script can handle it with its own retry logic
at an appropriate interval (e.g. 30s between attempts).
"""

RETRYABLE_EXCEPTIONS: Tuple[type, ...] = (_requests.ConnectionError, _requests.Timeout)
"""Exception types that should trigger a retry."""


def _is_retryable_status_code(status_code: int) -> bool:
    """Check if an HTTP status code is retryable."""
    return status_code in RETRYABLE_STATUS_CODES


def request_with_retries(
    func: Callable[..., _requests.Response],
    *args: Any,
    max_wait_time: float = 60 * 5,
    **kwargs: Any,
) -> _requests.Response:
    """Execute an HTTP request with automatic retries and exponential backoff.

    Mirrors Tinker SDK's ``InternalClientHolder.execute_with_retries()`` pattern:
    exponential backoff ``min(2**attempt, 30)``, capped by a total wall-time
    budget, with retryable exception and status code classification.

    On retryable exceptions (``ConnectionError``, ``Timeout``) or retryable
    status codes (408, 409, 429, 5xx), the request is retried until
    ``max_wait_time`` is exhausted.

    The response is returned as-is (no ``raise_for_status``) so callers can
    handle error responses their own way.

    Args:
        func: A ``requests`` method (e.g. ``requests.get``, ``requests.post``).
        *args: Positional arguments forwarded to *func*.
        max_wait_time: Maximum total wall-time in seconds before giving up
            (default: 300s, same as Tinker's ``MAX_WAIT_TIME``).
        **kwargs: Keyword arguments forwarded to *func*.

    Returns:
        The ``requests.Response`` from a successful (or non-retryable) attempt.

    Raises:
        requests.ConnectionError: If all retries are exhausted on connection errors.
        requests.Timeout: If all retries are exhausted on timeouts.
    """
    start_time = time.time()
    attempt_count = 0
    while True:
        try:
            resp = func(*args, **kwargs)
        except RETRYABLE_EXCEPTIONS as e:
            current_time = time.time()
            elapsed_time = current_time - start_time
            if elapsed_time < max_wait_time:
                time_to_wait = min(2**attempt_count, 30)
                attempt_count += 1
                time_to_wait = min(time_to_wait, start_time + max_wait_time - current_time)
                logger.warning(
                    "Request failed (attempt %d, %.1fs elapsed), retrying in %.1fs: %s: %s",
                    attempt_count,
                    elapsed_time,
                    time_to_wait,
                    type(e).__name__,
                    e,
                )
                time.sleep(time_to_wait)
                continue
            raise

        # Check for retryable status codes
        if _is_retryable_status_code(resp.status_code):
            current_time = time.time()
            elapsed_time = current_time - start_time
            if elapsed_time < max_wait_time:
                time_to_wait = min(2**attempt_count, 30)
                attempt_count += 1
                time_to_wait = min(time_to_wait, start_time + max_wait_time - current_time)
                logger.warning(
                    "Request returned HTTP %d (attempt %d, %.1fs elapsed), retrying in %.1fs",
                    resp.status_code,
                    attempt_count,
                    elapsed_time,
                    time_to_wait,
                )
                time.sleep(time_to_wait)
                continue

        return resp
