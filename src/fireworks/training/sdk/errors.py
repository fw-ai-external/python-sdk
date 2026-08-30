"""Structured error formatting, API error parsing, and retry utilities.

Provides:
  - format_sdk_error(): build multi-line "what / cause / solution / docs" messages
  - format_checkpoint_promotion_error(): format checkpoint-promotion HTTP failures
  - format_session_checkpoint_promotion_error(): format session checkpoint promotion HTTP failures
  - parse_api_error(): extract a human-readable string from an HTTP error response
  - parse_training_api_error(): preserve structured Training API classification
  - request_with_retries(): sync retry with exponential backoff
  - async_request_with_retries(): async retry with exponential backoff
  - HTTP_STATUS_HINTS: status-code -> actionable one-liner
  - Docs URL constants
"""

from __future__ import annotations

import copy
import time
import asyncio
import logging
from typing import Any, Tuple, Union, Literal, Mapping, Callable, Awaitable
from dataclasses import dataclass

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

_ERROR_INFO_TYPE = "type.googleapis.com/google.rpc.ErrorInfo"
_MAX_ERROR_INFO_METADATA_VALUE_LENGTH = 128
_MAX_SOURCE_ERROR_FIELD_LENGTH = 128
_COMPATIBILITY_ERROR_INFO_METADATA_KEYS = frozenset(
    {
        "quota_required",
        "quota_available",
    }
)

_SOURCE_TINKER = "tinker"
_SOURCE_SERVERLESS_GATEWAY = "serverless_gateway"
_SOURCE_LIFECYCLE = "lifecycle"


@dataclass(frozen=True)
class _LifecycleStatus:
    status: Mapping[str, Any]

    @property
    def grpc_code(self) -> Any:
        return self.status.get("code")

    @property
    def public_message(self) -> Any:
        return self.status.get("message")

    @property
    def reason(self) -> Any:
        detail = _legacy_error_info_projection(self.status)
        return detail.get("reason") if detail is not None else None

    @property
    def domain(self) -> Any:
        detail = _legacy_error_info_projection(self.status)
        return detail.get("domain") if detail is not None else None

    @property
    def source(self) -> Any:
        detail = _legacy_error_info_projection(self.status)
        metadata = detail.get("metadata") if detail is not None else None
        if isinstance(metadata, Mapping):
            return metadata.get("source")
        return None

    @property
    def metadata(self) -> Mapping[str, Any]:
        detail = _legacy_error_info_projection(self.status)
        metadata = detail.get("metadata") if detail is not None else None
        if not isinstance(metadata, Mapping):
            return {}
        return {key: copy.deepcopy(value) for key, value in metadata.items() if key not in {"version", "source"}}


@dataclass(frozen=True)
class _TinkerSourceError:
    source: Literal["tinker"]
    error: str | None
    category: str | None
    error_class: str | None
    malformed: bool = False


@dataclass(frozen=True)
class _ServerlessGatewaySourceError:
    source: Literal["serverless_gateway"]
    code: str | None
    type: str | None
    malformed: bool = False


_FireworksTrainingErrorSource = Union[
    _TinkerSourceError,
    _ServerlessGatewaySourceError,
]


class TrainingAPIError(RuntimeError):
    """A Training API failure with stable machine-readable classification.

    ``reason`` comes only from ``google.rpc.ErrorInfo``. It is never inferred
    from the diagnostic message, which remains available through ``str(exc)``.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None,
        reason: str | None = None,
        metadata: Mapping[str, str] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.reason = reason
        self.metadata = dict(metadata or {})


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


def parse_training_api_error(
    resp: Any,
    *,
    context: str | None = None,
) -> TrainingAPIError:
    """Parse a Training API response without classifying from free-form text."""
    message = parse_api_error(resp)
    status_code = getattr(resp, "status_code", None)
    reason: str | None = None
    metadata: dict[str, str] = {}
    lifecycle_status: _LifecycleStatus | None = None

    try:
        body = resp.json()
        status_body = body
        if isinstance(body, dict) and isinstance(body.get("error"), dict):
            status_body = body["error"]
        # Keep the existing public SDK view source-preserving and
        # forward-compatible. The private carrier independently preserves the
        # complete Lifecycle status without interpreting its policy.
        reason, metadata = _compatibility_error_info(status_body)
        lifecycle_status = _lifecycle_status(status_body)
    except Exception:
        # Message parsing already provides the compatibility fallback. A
        # malformed details block must not turn one API failure into another.
        pass

    rendered = message
    if context:
        http_suffix = f" (HTTP {status_code})" if status_code is not None else ""
        rendered = f"{context}{http_suffix}: {message}"
    error = TrainingAPIError(
        rendered,
        status_code=status_code,
        reason=reason,
        metadata=metadata,
    )
    if lifecycle_status is not None:
        error._fireworks_training_error_status = lifecycle_status
    return error


def _attach_training_error_status(exc: BaseException, resp: Any) -> bool:
    """Attach a trusted Lifecycle carrier without changing the exception."""

    if hasattr(exc, "_fireworks_training_error_source"):
        return False
    parsed = parse_training_api_error(resp)
    status = getattr(parsed, "_fireworks_training_error_status", None)
    if not isinstance(status, _LifecycleStatus):
        return False
    exc._fireworks_training_error_status = status  # type: ignore[attr-defined]
    return True


def _training_api_runtime_error(
    resp: Any,
    *,
    context: str,
) -> RuntimeError:
    parsed = parse_training_api_error(resp, context=context)
    error = RuntimeError(str(parsed))
    status = getattr(parsed, "_fireworks_training_error_status", None)
    if isinstance(status, _LifecycleStatus):
        error._fireworks_training_error_status = status  # type: ignore[attr-defined]
    return error


def _bounded_source_error_field(value: Any) -> str | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        encoded = value.encode("utf-8")
    except UnicodeError:
        return None
    if len(encoded) > _MAX_SOURCE_ERROR_FIELD_LENGTH:
        return None
    return value


def _tinker_source_error(
    *,
    error: Any,
    category: Any,
    error_class: Any,
) -> _TinkerSourceError | None:
    bounded_error = _bounded_source_error_field(error)
    bounded_category = _bounded_source_error_field(category)
    bounded_error_class = _bounded_source_error_field(error_class)
    malformed = any(
        original is not None and bounded is None
        for original, bounded in (
            (error, bounded_error),
            (category, bounded_category),
            (error_class, bounded_error_class),
        )
    )
    source = _TinkerSourceError(
        source=_SOURCE_TINKER,
        error=bounded_error,
        category=bounded_category,
        error_class=bounded_error_class,
        malformed=malformed,
    )
    if not malformed and source.error is None and source.category is None and source.error_class is None:
        return None
    return source


def _serverless_gateway_source_error(
    value: Any,
) -> _ServerlessGatewaySourceError | None:
    if not isinstance(value, dict) or not isinstance(value.get("error"), dict):
        return None
    envelope = value["error"]
    code = _bounded_source_error_field(envelope.get("code"))
    error_type = _bounded_source_error_field(envelope.get("type"))
    # ``code`` and ``type`` are independently optional upstream fields. Reject
    # malformed present values, but preserve whichever valid fields exist.
    malformed = (
        envelope.get("code") is not None and code is None or envelope.get("type") is not None and error_type is None
    )
    if code is None and error_type is None:
        if not malformed:
            return None
    return _ServerlessGatewaySourceError(
        source=_SOURCE_SERVERLESS_GATEWAY,
        code=code,
        type=error_type,
        malformed=malformed,
    )


def _is_serverless_gateway_url(value: Any) -> bool:
    try:
        path = httpx.URL(str(value)).path
    except Exception:
        return False
    route = "/training/v1/serverless"
    return path == route or path.startswith(f"{route}/")


def _attach_training_error_source(
    exc: BaseException,
    source: _FireworksTrainingErrorSource | None,
) -> bool:
    if not isinstance(source, (_TinkerSourceError, _ServerlessGatewaySourceError)):
        return False
    if hasattr(exc, "_fireworks_training_error_status"):
        return False
    exc._fireworks_training_error_source = source  # type: ignore[attr-defined]
    return True


def _copy_training_error_source(
    exc: BaseException,
    source_exc: BaseException,
) -> bool:
    source = getattr(source_exc, "_fireworks_training_error_source", None)
    return _attach_training_error_source(exc, source)


def _compatibility_error_info(value: Any) -> tuple[str | None, dict[str, str]]:
    """Return the legacy narrow public view of the first ErrorInfo detail.

    This preserves the existing ``TrainingAPIError.reason`` / ``metadata``
    contract without treating those fields as trusted managed policy. The
    private writer carrier is validated independently below.
    """

    if not isinstance(value, dict):
        return None, {}
    details = value.get("details", [])
    if not isinstance(details, list):
        return None, {}
    for detail in details:
        if not isinstance(detail, dict) or detail.get("@type") != _ERROR_INFO_TYPE:
            continue
        candidate = detail.get("reason")
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip(), _compatibility_error_info_metadata(detail.get("metadata"))
    return None, {}


def _first_error_info(value: Mapping[str, Any]) -> Mapping[str, Any] | None:
    details = value.get("details", [])
    if not isinstance(details, list):
        return None
    for detail in details:
        if isinstance(detail, Mapping) and detail.get("@type") == _ERROR_INFO_TYPE:
            return detail
    return None


def _legacy_error_info_projection(
    value: Mapping[str, Any],
) -> Mapping[str, Any] | None:
    details = value.get("details", [])
    if not isinstance(details, list):
        return None

    trusted: Mapping[str, Any] | None = None
    for detail in details:
        if not isinstance(detail, Mapping) or detail.get("@type") != _ERROR_INFO_TYPE:
            continue
        if detail.get("domain") != "training.fireworks.ai":
            continue
        reason = detail.get("reason")
        metadata = detail.get("metadata")
        if (
            not isinstance(reason, str)
            or not reason
            or reason.strip() != reason
            or not isinstance(metadata, Mapping)
            or metadata.get("version") != "1"
            or metadata.get("source") not in {"lifecycle", "managed"}
        ):
            return None
        for key, item in metadata.items():
            if not isinstance(key, str) or not isinstance(item, str):
                return None
            try:
                if len(item.encode("utf-8")) > _MAX_ERROR_INFO_METADATA_VALUE_LENGTH:
                    return None
            except UnicodeError:
                return None
        candidate = copy.deepcopy(dict(detail))
        if trusted is not None and trusted != candidate:
            return None
        trusted = candidate
    return trusted


def _compatibility_error_info_metadata(value: Any) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    safe: dict[str, str] = {}
    for key in _COMPATIBILITY_ERROR_INFO_METADATA_KEYS:
        item = value.get(key)
        if isinstance(item, str):
            safe[key] = item[:_MAX_ERROR_INFO_METADATA_VALUE_LENGTH]
    return safe


def _lifecycle_status(value: Any) -> _LifecycleStatus | None:
    if not isinstance(value, dict):
        return None
    grpc_code = value.get("code")
    public_message = value.get("message")
    if (
        not isinstance(grpc_code, int)
        or isinstance(grpc_code, bool)
        or not 0 <= grpc_code <= 16
        or not isinstance(public_message, str)
    ):
        return None
    return _LifecycleStatus(
        status=copy.deepcopy(value),
    )


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

_PROMOTE_PLATFORM_ERROR_SOLUTION = "Retry checkpoint promotion. If the error persists, contact Fireworks support."


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


def parse_retry_after(resp: Any) -> float | None:
    """Return the ``Retry-After`` delay in seconds from a response, or ``None``.

    Accepts both header forms: an integer number of seconds, or an HTTP-date.
    Never returns a negative value. Any parse failure yields ``None`` so callers
    can fall back to their own backoff.
    """
    headers = getattr(resp, "headers", None)
    if not headers:
        return None
    # httpx headers are case-insensitive; requests/dict headers may not be.
    raw = headers.get("retry-after")
    if raw is None and hasattr(headers, "get"):
        raw = headers.get("Retry-After")
    if raw is None:
        return None
    raw = str(raw).strip()
    if not raw:
        return None
    try:
        return max(0.0, float(raw))
    except (TypeError, ValueError):
        pass
    try:
        from email.utils import parsedate_to_datetime

        when = parsedate_to_datetime(raw)
    except (TypeError, ValueError):
        return None
    if when is None:
        return None
    import datetime as _dt

    now = _dt.datetime.now(when.tzinfo) if when.tzinfo is not None else _dt.datetime.now()
    return max(0.0, (when - now).total_seconds())


def _backoff_delay(attempt: int, start_time: float, max_wait_time: float) -> float | None:
    """Return delay in seconds, or None if budget exhausted."""
    elapsed = time.time() - start_time
    if elapsed >= max_wait_time:
        return None
    delay = min(2**attempt, 30)
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
    retry_status_codes: Tuple[int, ...] | None = None,
    retry_exceptions: Tuple[type, ...] | None = None,
    **kwargs: Any,
) -> Any:
    """Async HTTP request with exponential backoff retries.

    ``retry_status_codes`` / ``retry_exceptions`` default to the module-level
    ``RETRYABLE_STATUS_CODES`` / ``RETRYABLE_EXCEPTIONS`` so existing callers are
    unchanged. Pass an empty tuple to opt out of status- or exception-based
    retries for a single call -- used by the sampling path, which owns its own
    retry budget one layer up (see ``DeploymentSampler._do_one_completion``) and
    must not have that budget silently multiplied by a second retry loop here.
    """
    status_codes = RETRYABLE_STATUS_CODES if retry_status_codes is None else retry_status_codes
    exc_types = RETRYABLE_EXCEPTIONS if retry_exceptions is None else retry_exceptions
    start = time.time()
    attempt = 0
    while True:
        try:
            resp = await func(*args, **kwargs)
        except exc_types as e:
            delay = _backoff_delay(attempt, start, max_wait_time)
            if delay is not None:
                attempt += 1
                logger.debug("Request failed (attempt %d): %s, retrying in %.1fs", attempt, e, delay)
                await asyncio.sleep(delay)
                continue
            raise

        if resp.status_code in status_codes:
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
