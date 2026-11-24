from __future__ import annotations

import json
import zlib
import hashlib

import pytest

from fireworks.training.sdk.tito import _artifact_stream


def test_input_chunk_larger_than_output_block_does_not_copy_unbounded_zlib_tails(monkeypatch):
    magic = b"TITOART\x01"
    original = bytes(range(256)) * 32768
    encoded = magic + zlib.compress(original, level=0)
    inflater = zlib.decompressobj()
    max_input = 0

    class MeteredInflater:
        def __getattr__(self, name):
            return getattr(inflater, name)

        def decompress(self, data, max_length):
            nonlocal max_input
            max_input = max(max_input, len(data))
            return inflater.decompress(data, max_length)

    monkeypatch.setattr(_artifact_stream.zlib, "decompressobj", MeteredInflater)
    blocks = _artifact_stream.inflate_verified(
        [encoded],
        magic=magic,
        expected_bytes=len(encoded),
        expected_sha256=hashlib.sha256(encoded).hexdigest(),
        max_expanded_bytes=len(original),
    )
    assert b"".join(blocks) == original
    assert max_input <= _artifact_stream.INFLATE_CHUNK_BYTES


def test_paused_reader_can_resume_and_still_requires_full_digest():
    magic = b"TITOART\x01"
    plaintext = b"a" * (3 * _artifact_stream.INFLATE_CHUNK_BYTES)
    encoded = magic + zlib.compress(plaintext, level=0)
    delivered = 0

    def provider():
        nonlocal delivered
        for offset in range(0, len(encoded), 16 * 1024):
            part = encoded[offset : offset + 16 * 1024]
            delivered += len(part)
            yield part

    blocks = _artifact_stream.inflate_verified(
        provider(),
        magic=magic,
        expected_bytes=len(encoded),
        expected_sha256="0" * 64,
        max_expanded_bytes=len(plaintext),
    )
    assert next(blocks)
    assert delivered < len(encoded)
    with pytest.raises(ValueError, match="checksum"):
        list(blocks)


@pytest.mark.parametrize("block_size", [1, 3, 17, 4096])
@pytest.mark.parametrize("nested", [False, True])
@pytest.mark.parametrize("scanner", ["python", "native"])
def test_incomplete_compound_records_do_not_break_on_quoted_delimiters(
    block_size: int, nested: bool, scanner: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    if scanner == "python":
        monkeypatch.setattr(_artifact_stream, "_scan_composite", _artifact_stream._scan_json_composite)
    elif _artifact_stream._scan_composite is _artifact_stream._scan_json_composite:
        pytest.skip("native scanner unavailable")
    value = {
        "arrays": [[i, {f"quoted \\ {i}": '[{}]"雪😀\\'}] for i in range(600)],
        "nested": {"true": True, "false": False, "none": None},
        "number": -31.43e-15,
    }
    encoded = json.dumps({"前缀😀": value} if nested else value, ensure_ascii=False).encode("utf-8")
    reader = _artifact_stream.ArtifactJSONReader(
        (encoded[i : i + block_size] for i in range(0, len(encoded), block_size))
    )
    if nested:
        assert {key: reader.value() for key in reader.members()} == {"前缀😀": value}
    else:
        assert reader.value() == value
    reader.finish()


def test_preverified_input_still_requires_complete_bounded_framing():
    magic = b"TITOART\x01"
    raw = b"valid content" * 2000
    encoded = magic + zlib.compress(raw)
    for data, limit, message in (
        (encoded + b"suffix", len(raw), "trailing bytes"),
        (encoded[:-1], len(raw), "incomplete"),
        (encoded, len(raw) - 1, "expanded size"),
    ):
        with pytest.raises(ValueError, match=message):
            list(
                _artifact_stream.inflate_verified(
                    [data],
                    magic=magic,
                    expected_bytes=len(data),
                    expected_sha256=None,
                    max_expanded_bytes=limit,
                )
            )
