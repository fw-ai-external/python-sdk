"""Structured, payload-free observability for deployment sampling requests.

Makes a terminal sampling failure attributable back to the SDK request and the
serving component, without recording prompts, generated tokens, API keys, or
request payloads.

:class:`SamplingRequestError` carries identity (logical + server request id,
model), the final status / error kind, the attempt count, and optional
non-sensitive context. ``as_error_record()`` serializes it for logs using only
whitelisted fields.
"""

from __future__ import annotations

from typing import Any, Mapping

# ---------------------------------------------------------------------------
# Header names (lowercase; httpx headers are case-insensitive)
# ---------------------------------------------------------------------------

# Correlation id the SDK sends and the gateway/fw-proxy echoes back.
REQUEST_ID_HEADER = "x-request-id"
# Response headers, in priority order, that may carry a server/gateway request id.
REQUEST_ID_RESPONSE_HEADERS = ("x-request-id", "x-fireworks-request-id", "cf-ray")

# Non-sensitive context keys a caller may attach (via the sampler's
# ``request_context`` or a per-call ``sampling_context`` kwarg).
CONTEXT_KEYS = ("session", "run", "checkpoint", "step", "group", "item")

# Error kinds (coarse classification of the terminal failure).
ERROR_KIND_HTTP_STATUS = "http_status"
ERROR_KIND_SSE_TRUNCATION = "sse_truncation"
ERROR_KIND_CONNECTION = "connection"
ERROR_KIND_TIMEOUT = "timeout"


def extract_request_id(headers: Mapping[str, str] | None) -> str | None:
    """Return the first present server/gateway request id header, or ``None``."""
    if not headers:
        return None
    for name in REQUEST_ID_RESPONSE_HEADERS:
        value = headers.get(name)
        if value:
            return str(value)
    return None


def clean_context(raw: Mapping[str, Any] | None) -> dict[str, Any]:
    """Keep only recognized, non-``None`` context keys (drops payloads/junk)."""
    if not raw:
        return {}
    return {k: raw[k] for k in CONTEXT_KEYS if raw.get(k) is not None}


class SamplingRequestError(RuntimeError):
    """Terminal error for a logical sampling request after all attempts failed.

    Carries identity and the terminal status so the caller can attribute the
    failure without parsing logs. Never carries prompts, tokens, or keys.

    Accepts an optional positional ``message`` for backward compatibility with
    callers (e.g. the timeout subclass) that pass a preformatted diagnostic.
    """

    def __init__(
        self,
        message: str | None = None,
        *,
        logical_request_id: str | None = None,
        model: str | None = None,
        attempts: int | None = None,
        final_status: int | None = None,
        final_error_kind: str | None = None,
        request_id: str | None = None,
        context: Mapping[str, Any] | None = None,
    ) -> None:
        self.logical_request_id = logical_request_id
        self.model = model
        self.attempts = attempts
        self.final_status = final_status
        self.final_error_kind = final_error_kind
        self.request_id = request_id  # server/gateway request id of the last attempt
        self.context = clean_context(context)
        super().__init__(message if message is not None else self._build_message())

    def _build_message(self) -> str:
        """A single, plain line: what failed and where. No prescriptive advice."""
        parts = [f"Sampling request failed after {self.attempts} attempts:"]
        if self.final_status is not None:
            parts.append(f"HTTP {self.final_status}")
        elif self.final_error_kind:
            parts.append(self.final_error_kind)
        if self.model:
            parts.append(f"model={self.model}")
        if self.request_id:
            parts.append(f"request_id={self.request_id}")
        parts.extend(f"{k}={v}" for k, v in self.context.items())
        if self.logical_request_id:
            parts.append(f"logical_request_id={self.logical_request_id}")
        return " ".join(parts)

    def as_error_record(self) -> dict[str, Any]:
        """Compact structured record for logs (identity + terminal status only)."""
        record: dict[str, Any] = {
            "logical_request_id": self.logical_request_id,
            "model": self.model,
            "attempts": self.attempts,
            "final_status": self.final_status,
            "final_error_kind": self.final_error_kind,
            "request_id": self.request_id,
        }
        if self.context:
            record["context"] = dict(self.context)
        return record


class DeploymentSamplerTimeoutError(SamplingRequestError):
    """Terminal timeout-like failure (408/504/httpx timeouts) after retries.

    Subclass of :class:`SamplingRequestError` so existing
    ``except DeploymentSamplerTimeoutError`` sites keep working.
    """
