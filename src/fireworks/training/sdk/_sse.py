"""Server-Sent Events decoding for streaming completions."""

from __future__ import annotations

from typing import Any


class _SSETruncationError(RuntimeError):
    """Server closed the SSE completion stream mid-generation.

    Raised by :meth:`DeploymentSampler.async_completions_stream` when the
    response stream ends without ``[DONE]``, ``finish_reason``, or
    ``raw_output``. The per-completion retry loop in
    :meth:`DeploymentSampler._do_one_completion` recognises this exact
    type and retries it; other ``RuntimeError`` subclasses propagate
    unchanged.
    """


# =============================================================================
# SSE decoder for streaming completions
# =============================================================================


class _SSEEvent:
    """A single Server-Sent Event."""

    __slots__ = ("data", "event")

    def __init__(self, data: str = "", event: str | None = None):
        self.data = data
        self.event = event


class _SSEDecoder:
    """Minimal async SSE decoder for ``httpx.Response.aiter_bytes``.

    Implements the subset of the `SSE spec`_ used by the Fireworks
    completions endpoint:

    * ``data:`` fields (single- and multi-line)
    * ``event:`` fields
    * Comment lines (``:…``) are skipped
    * ``[DONE]`` sentinel terminates the stream

    .. _SSE spec: https://html.spec.whatwg.org/multipage/server-sent-events.html
    """

    def __init__(self) -> None:
        self._event: str | None = None
        self._data: list[str] = []

    @staticmethod
    async def _aiter_chunks(stream: Any) -> Any:
        """Reassemble raw bytes into SSE chunks (delimited by blank lines)."""
        buf = b""
        async for raw in stream.aiter_bytes():
            for line in raw.splitlines(keepends=True):
                buf += line
                if buf.endswith((b"\r\r", b"\n\n", b"\r\n\r\n")):
                    yield buf
                    buf = b""
        if buf:
            yield buf

    async def aiter_events(self, response: Any) -> Any:
        """Yield :class:`_SSEEvent` objects from an ``httpx.Response``."""
        async for chunk in self._aiter_chunks(response):
            for raw_line in chunk.splitlines():
                line = raw_line.decode("utf-8")
                event = self._decode_line(line)
                if event is not None:
                    yield event

    def _decode_line(self, line: str) -> _SSEEvent | None:
        # Blank line → dispatch accumulated event.
        if not line:
            if not self._data and self._event is None:
                return None
            event = _SSEEvent(data="\n".join(self._data), event=self._event)
            self._data = []
            self._event = None
            return event

        # Comment line.
        if line.startswith(":"):
            return None

        field, _, value = line.partition(":")
        if value.startswith(" "):
            value = value[1:]

        if field == "data":
            self._data.append(value)
        elif field == "event":
            self._event = value

        return None
