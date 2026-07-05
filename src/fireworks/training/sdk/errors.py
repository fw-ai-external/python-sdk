"""Structured error formatting, API error parsing, and retry utilities.

Provides:
  - format_sdk_error(): build multi-line "what / cause / solution / docs" messages
  - format_checkpoint_promotion_error(): format checkpoint-promotion HTTP failures
  - format_session_checkpoint_promotion_error(): format session checkpoint promotion HTTP failures
  - parse_api_error(): extract a human-readable string from an HTTP error response
  - request_with_retries(): sync retry with exponential backoff
  - async_request_with_retries(): async retry with exponential backoff
  - HTTP_STATUS_HINTS: status-code -> actionable one-liner
  - Docs URL constants
"""

from __future__ import annotations

import time
import asyncio
import logging
from typing import Any, Tuple, Callable, Awaitable

import httpx

logger = logging.getLogger(__name__)

DOCS_SDK = "https://docs.fireworks.ai/fine-tuning/training-sdk/introduction"
DISCORD_URL = "https://discord.gg/mMqQxvFD9A"
CONSOLE_URL = "https://app.fireworks.ai/account/home"
AGENT_DEBUG_INSTRUCTIONS = (
    "First search the Fireworks training cookbook skill for this error. "
    "If the cookbook is not available locally, clone "
    "https://github.com/fw-ai/cookbook and search cookbook/skills."
)

HTTP_STATUS_HINTS: dict[int, str] = {
    400: "Check that all request parameters are valid.",
    401: (
        "Check your API key. Training APIs require a training-scoped Fireworks key; "
        f"inference-only keys return 401. Manage keys at {CONSOLE_URL}"
    ),
    403: "Your key is valid, but it may not have permission for this account or resource.",
    404: "The resource was not found. Verify the ID/name is correct and belongs to the resolved account.",
    409: "Resource conflict. It may already exist or be in a transitional state.",
    429: f"Rate limited. Wait and retry, or reach out on Discord: {DISCORD_URL}",
    500: f"Internal server error. Try again. If persistent, reach out on Discord: {DISCORD_URL}",
    502: "Bad gateway. Retry after a short wait.",
    503: "Service temporarily unavailable. Retry after a short wait.",
    504: "Gateway timeout. The request took too long upstream. Retry after a short wait.",
}


def format_sdk_error(
    what: str,
    cause: str,
    solution: str,
    docs_url: str | None = None,
    show_support: bool = False,
) -> str:
    lines = [
        f"ERROR: {what}",
        f"  Cause: {cause}",
        f"  Solution: {solution}",
        f"  Agent debug: {AGENT_DEBUG_INSTRUCTIONS}",
    ]
    if docs_url:
        lines.append(f"  Docs: {docs_url}")
    if show_support:
        lines.append(f"  Support: {DISCORD_URL}")
    return "\n".join(lines)


def parse_api_error(resp) -> str:
    """Extract a human-readable error message from an httpx or requests Response."""
    try:
        body = resp.json()
        err = body.get("error", body)
        if isinstance(err, dict):
            return err.get("message", str(err))
        return str(err)
    except Exception:
        text = getattr(resp, "text", str(resp))
        return text.strip()[:200]


_PROMOTE_CHECKPOINT_CLIENT_ERROR_SOLUTION = (
    "Use a checkpoint name returned by list_checkpoints, ensure the row is promotable, "
    "and pass the base_model that matches the trainer.\n"
    f"  Console: {CONSOLE_URL}"
)

_PROMOTE_SESSION_CHECKPOINT_CLIENT_ERROR_SOLUTION = (
    "Use a checkpoint name returned by list_training_session_checkpoints, "
    "ensure the row is promotable, and pass the base_model that matches "
    "the trainer.\n"
    f"  Console: {CONSOLE_URL}"
)

_PROMOTE_PLATFORM_ERROR_SOLUTION = (
    "Retry checkpoint promotion. If the error persists, contact Fireworks support."
)


def format_checkpoint_promotion_error(
    resp,
    *,
    checkpoint_id: str,
) -> str:
    """Build a structured error for a failed job checkpoint promotion response."""
    return _format_promote_error(
        resp,
        what=f"Failed to promote checkpoint '{checkpoint_id}'",
        client_error_solution=_PROMOTE_CHECKPOINT_CLIENT_ERROR_SOLUTION,
    )


def format_session_checkpoint_promotion_error(
    resp,
    *,
    checkpoint_id: str,
) -> str:
    """Build a structured error for a failed session checkpoint promotion response."""
    return _format_promote_error(
        resp,
        what=f"Failed to promote session checkpoint '{checkpoint_id}'",
        client_error_solution=_PROMOTE_SESSION_CHECKPOINT_CLIENT_ERROR_SOLUTION,
    )


def _format_promote_error(resp, *, what: str, client_error_solution: str) -> str:
    status_code = resp.status_code
    is_platform_error = status_code >= 500
    return format_sdk_error(
        f"{what} (HTTP {status_code})",
        parse_api_error(resp),
        _PROMOTE_PLATFORM_ERROR_SOLUTION if is_platform_error else client_error_solution,
        docs_url=DOCS_SDK,
        show_support=is_platform_error,
    )


RETRYABLE_STATUS_CODES: Tuple[int, ...] = (408, 429, 500, 502, 503, 504)

RETRYABLE_EXCEPTIONS: Tuple[type, ...] = (
    httpx.ConnectError,
    httpx.TimeoutException,
)

MAX_WAIT_TIME = 60 * 5


def _is_retryable_status_code(status_code: int) -> bool:
    """Check if an HTTP status code is retryable."""
    return status_code in RETRYABLE_STATUS_CODES


def _backoff_delay(attempt: int, start_time: float, max_wait_time: float) -> float | None:
    """Return delay in seconds, or None if budget exhausted."""
    elapsed = time.time() - start_time
    if elapsed >= max_wait_time:
        return None
    delay = min(2 ** attempt, 30)
    return min(delay, start_time + max_wait_time - time.time())


def request_with_retries(
    func: Callable[..., Any],
    *args: Any,
    max_wait_time: float = MAX_WAIT_TIME,
    **kwargs: Any,
) -> Any:
    """Sync HTTP request with exponential backoff retries.

    Works with both ``httpx.Client`` and ``requests.Session`` methods.
    Retries on connection errors, timeouts, and retryable status codes.
    """
    start = time.time()
    attempt = 0
    while True:
        try:
            resp = func(*args, **kwargs)
        except Exception as e:
            if isinstance(e, RETRYABLE_EXCEPTIONS) or _is_requests_retryable(e):
                delay = _backoff_delay(attempt, start, max_wait_time)
                if delay is not None:
                    attempt += 1
                    logger.debug("Request failed (attempt %d): %s, retrying in %.1fs", attempt, e, delay)
                    time.sleep(delay)
                    continue
            raise

        if _is_retryable_status_code(resp.status_code):
            delay = _backoff_delay(attempt, start, max_wait_time)
            if delay is not None:
                attempt += 1
                logger.debug("HTTP %d (attempt %d), retrying in %.1fs", resp.status_code, attempt, delay)
                time.sleep(delay)
                continue

        return resp


async def async_request_with_retries(
    func: Callable[..., Awaitable[Any]],
    *args: Any,
    max_wait_time: float = MAX_WAIT_TIME,
    **kwargs: Any,
) -> Any:
    """Async HTTP request with exponential backoff retries."""
    start = time.time()
    attempt = 0
    while True:
        try:
            resp = await func(*args, **kwargs)
        except RETRYABLE_EXCEPTIONS as e:
            delay = _backoff_delay(attempt, start, max_wait_time)
            if delay is not None:
                attempt += 1
                logger.debug("Request failed (attempt %d): %s, retrying in %.1fs", attempt, e, delay)
                await asyncio.sleep(delay)
                continue
            raise

        if _is_retryable_status_code(resp.status_code):
            delay = _backoff_delay(attempt, start, max_wait_time)
            if delay is not None:
                attempt += 1
                logger.debug("HTTP %d (attempt %d), retrying in %.1fs", resp.status_code, attempt, delay)
                await asyncio.sleep(delay)
                continue

        return resp


def _is_requests_retryable(exc: Exception) -> bool:
    """Check if a ``requests`` library exception is retryable.

    Allows ``request_with_retries`` to work with both httpx and requests.
    """
    try:
        import requests as _req
        return isinstance(exc, (_req.ConnectionError, _req.Timeout))
    except ImportError:
        return False
