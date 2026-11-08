"""Chunk framing and immutable output for all training SSE splitters."""

from __future__ import annotations

from typing import AsyncIterator

import pytest

from fireworks.training.sdk._sse import _SSEDecoder
from fireworks.training.sdk._core._streaming import SSEDecoder


class _Fragments:
    def __init__(self, wire: bytes, size: int) -> None:
        self.wire = wire
        self.size = size

    async def aiter_bytes(self) -> AsyncIterator[bytes]:
        for offset in range(0, len(self.wire), self.size):
            yield self.wire[offset : offset + self.size]


@pytest.mark.parametrize("delimiter", [b"\n\n", b"\r\r", b"\r\n\r\n"])
@pytest.mark.parametrize("size", [1, 7, 16384])
async def test_fragmented_large_events_preserve_bytes(delimiter: bytes, size: int) -> None:
    events = [b"data: " + "你好🙂".encode() + delimiter, b"data: " + b"x" * 65536 + delimiter, b"data: tail"]
    wire = b"".join(events)
    fragments = _Fragments(wire=wire, size=size)
    outputs = [
        [chunk async for chunk in _SSEDecoder._aiter_chunks(fragments)],
        list(SSEDecoder()._iter_chunks(iter(wire[i : i + size] for i in range(0, len(wire), size)))),
        [chunk async for chunk in SSEDecoder()._aiter_chunks(fragments.aiter_bytes())],
    ]
    for chunks in outputs:
        assert chunks == events
        assert all(type(chunk) is bytes for chunk in chunks)
