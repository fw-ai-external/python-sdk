"""Bounded decompression and incremental reads of the existing TITO JSON wire format."""

from __future__ import annotations

import re
import json
import zlib
import codecs
import hashlib
from typing import Any
from collections.abc import Iterable, Iterator

from ._native_runtime import _native

INFLATE_CHUNK_BYTES = 64 * 1024
_JSON_SPACE = " \t\r\n"
_JSON_STRUCTURE = re.compile(r'[][{}"]')
_JSON_STRING_SPECIAL = re.compile(r'["\\]')


def _scan_json_composite(
    text: str, at: int, depth: int, quoted: bool, _ascii: bool
) -> tuple[int, int, bool, bool]:
    """Find a record boundary on SDK installs without the native extension."""
    while True:
        pattern = _JSON_STRING_SPECIAL if quoted else _JSON_STRUCTURE
        match = pattern.search(text, at)
        if match is None:
            return max(at, len(text)), depth, quoted, False

        char = match[0]
        at = match.end()
        if char == "\\":
            at += 1
        elif char == '"':
            quoted = not quoted
        elif char in "[{":
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                return at, depth, quoted, True


# Keep reading artifacts on universal wheels and with an older local extension.
_scan_composite = getattr(_native, "scan_json_composite", _scan_json_composite)


def inflate_verified(
    chunks: Iterable[bytes],
    *,
    magic: bytes,
    expected_bytes: int,
    expected_sha256: str | None,
    max_expanded_bytes: int,
) -> Iterator[bytes]:
    """Yield bounded plaintext blocks and check the full wire stream at EOF."""
    if expected_bytes <= len(magic) or max_expanded_bytes < 1:
        raise ValueError("invalid TITO artifact size")
    if expected_sha256 is not None and re.fullmatch(r"[0-9a-f]{64}", expected_sha256) is None:
        raise ValueError("invalid TITO artifact checksum")
    digest = hashlib.sha256() if expected_sha256 is not None else None
    inflater = zlib.decompressobj()
    header = bytearray()
    received = expanded = 0
    for chunk in chunks:
        if not chunk:
            continue
        received += len(chunk)
        if received > expected_bytes:
            raise ValueError("TITO artifact byte count mismatch, exceeds manifest")
        if digest is not None:
            digest.update(chunk)
        take = 0
        if len(header) < len(magic):
            take = min(len(magic) - len(header), len(chunk))
            header.extend(chunk[:take])
            if not magic.startswith(header):
                raise ValueError("missing TITO artifact magic/version")
        view = memoryview(chunk)
        for offset in range(take, len(view), INFLATE_CHUNK_BYTES):
            pending: bytes | memoryview = view[offset : offset + INFLATE_CHUNK_BYTES]
            while pending:
                if inflater.eof:
                    raise ValueError("trailing bytes after TITO artifact compression stream")
                block = inflater.decompress(pending, min(INFLATE_CHUNK_BYTES, max_expanded_bytes - expanded + 1))
                expanded += len(block)
                if expanded > max_expanded_bytes:
                    raise ValueError("TITO artifact expanded size exceeds limit")
                if inflater.unused_data:
                    raise ValueError("trailing bytes after TITO artifact compression stream")
                if block:
                    yield block
                pending = inflater.unconsumed_tail
    if received != expected_bytes:
        raise ValueError("TITO artifact byte count mismatch, below manifest")
    if digest is not None and digest.hexdigest() != expected_sha256:
        raise ValueError("TITO artifact checksum does not match manifest")
    if not inflater.eof:
        raise ValueError("incomplete TITO artifact compression stream")


class ArtifactJSONReader:
    """Read small JSON records with the same decoder as the original codec."""

    def __init__(self, plaintext: Iterator[bytes]) -> None:
        self._plaintext = plaintext
        self._utf8 = codecs.getincrementaldecoder("utf-8")()
        self._decoder = json.JSONDecoder()
        self._buffer = ""
        self._position = 0
        self._eof = False

    def _fill(self, minimum: int = 1) -> None:
        pending = self._buffer[self._position :]
        self._position = 0
        # Gather chunks and join once. Large records retry only after geometric
        # growth, so an incomplete turn does not get parsed once per block.
        pieces = [pending]
        size = len(pending)
        while not self._eof and size < minimum:
            block = next(self._plaintext, None)
            if block is None:
                self._eof = True
                text = self._utf8.decode(b"", final=True)
            else:
                text = self._utf8.decode(block)
            pieces.append(text)
            size += len(text)
        self._buffer = "".join(pieces)

    def _peek(self) -> str:
        while True:
            while self._position < len(self._buffer):
                char = self._buffer[self._position]
                if char not in _JSON_SPACE:
                    return char
                self._position += 1
            if self._eof:
                return ""
            self._fill()

    def _expect(self, char: str) -> None:
        if self._peek() != char:
            raise ValueError(f"invalid TITO artifact JSON, expected {char!r}")
        self._position += 1

    def _container(self, opening: str, closing: str) -> Iterator[None]:
        self._expect(opening)
        if self._peek() != closing:
            yield
            while self._peek() == ",":
                self._position += 1
                yield
        self._expect(closing)

    def members(self) -> Iterator[str]:
        for _ in self._container("{", "}"):
            if self._peek() != '"':
                raise ValueError("invalid TITO artifact JSON member")
            key = self.value()
            self._expect(":")
            yield key

    def items(self) -> Iterator[None]:
        return self._container("[", "]")

    def _composite(self) -> Any:
        # A large preceding record can leave a long UTF-8 prefix to skip.
        if self._position >= INFLATE_CHUNK_BYTES and self._position > len(self._buffer) // 2:
            self._buffer = self._buffer[self._position :]
            self._position = 0
        search_at = self._position
        depth = 0
        quoted = False
        while True:
            search_at, depth, quoted, done = _scan_composite(
                self._buffer, search_at, depth, quoted, self._buffer.isascii()
            )
            if done:
                value, end = self._decoder.raw_decode(self._buffer, self._position)
                if end != search_at:
                    raise ValueError("invalid TITO artifact JSON value boundary")
                self._position = end
                return value
            if self._eof:
                raise ValueError("incomplete TITO artifact JSON value")
            search_at -= self._position
            size = len(self._buffer) - self._position
            self._fill(max(size + 1, size * 2))

    def value(self) -> Any:
        first = self._peek()
        if not first:
            raise ValueError("incomplete TITO artifact JSON")
        if first in "{[":
            return self._composite()
        while True:
            try:
                value, end = self._decoder.raw_decode(self._buffer, self._position)
            except json.JSONDecodeError:
                if self._eof:
                    raise
            else:
                # A scalar ending at a block boundary can be just the prefix
                # of a longer number. Wait for its delimiter before accepting.
                if self._buffer[end : end + 1] in (",", "]", "}", ":", " ", "\t", "\r", "\n"):
                    self._position = end
                    return value
                if self._eof:
                    if end != len(self._buffer):
                        raise ValueError("invalid TITO artifact JSON value")
                    self._position = end
                    return value
            size = len(self._buffer) - self._position
            self._fill(max(size + 1, size * 2))

    def finish(self) -> None:
        # Reaching JSON's closing brace is insufficient. Consume to stream EOF
        # to run the inflater's byte-count, digest and framing checks.
        if self._peek():
            raise ValueError("trailing data after TITO artifact JSON")
