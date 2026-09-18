"""Compact routing ranges. SDK operations never read or expand routing files."""

from __future__ import annotations

from typing import Literal
from dataclasses import dataclass

RoutingMatrixFormat = Literal["base64_inline", "parquet_v1"]
R3_STORE_HEADER = "x-fireworks-r3-store-id"
R3_TTL_HEADER = "x-fireworks-r3-ttl-seconds"


@dataclass(frozen=True)
class RoutingReferences:
    length: int
    files: tuple[dict, ...]
    spans: tuple[dict, ...]

    def __post_init__(self):
        # Slices and multi-turn concatenation must not duplicate whole file tables.
        files, spans, indices = [], [], {}
        for original in self.spans:
            span = dict(original)
            if span.get("file_index") is not None:
                file = self.files[span["file_index"]]
                key = tuple(sorted(file.items()))
                if key not in indices:
                    indices[key] = len(files)
                    files.append(dict(file))
                span["file_index"] = indices[key]
            if (
                spans
                and spans[-1].get("file_index") == span.get("file_index")
                and spans[-1]["input_token_start"] + spans[-1]["count"] == span["input_token_start"]
                and (
                    span.get("file_index") is None
                    or spans[-1]["file_row_start"] + spans[-1]["count"] == span["file_row_start"]
                )
            ):
                spans[-1]["count"] += span["count"]
            else:
                spans.append(span)
        object.__setattr__(self, "files", tuple(files))
        object.__setattr__(self, "spans", tuple(spans))

    @classmethod
    def from_dict(cls, value: dict) -> RoutingReferences:
        length = value["length"]
        if type(length) is not int or length < 0:
            raise ValueError("Invalid R3 reference length")
        files = tuple(dict(file) for file in value["files"])
        spans = tuple(dict(span) for span in value["spans"])
        position = 0
        for span in spans:
            count = span["count"]
            if type(count) is not int or count <= 0 or span["input_token_start"] != position:
                raise ValueError("R3 ranges must cover input positions exactly once")
            index = span.get("file_index")
            if index is not None:
                start = span["file_row_start"]
                if type(index) is not int or not 0 <= index < len(files):
                    raise ValueError("Invalid R3 file index")
                if type(start) is not int or start < 0 or start + count > files[index]["row_count"]:
                    raise ValueError("Invalid R3 file range")
                if files[index].get("format") != "parquet_v1":
                    raise ValueError("Unsupported R3 file format")
            position += count
        if position != length:
            raise ValueError("R3 ranges do not match input length")
        return cls(length, files, spans)

    def to_dict(self) -> dict:
        return {
            "length": self.length,
            "files": [dict(f) for f in self.files],
            "spans": [{k: v for k, v in s.items() if v is not None} for s in self.spans],
        }

    def __len__(self) -> int:
        return self.length

    def __getitem__(self, key: slice) -> RoutingReferences:
        if not isinstance(key, slice):
            raise TypeError("R3 references support range slicing, not per-token expansion")
        start, end, step = key.indices(self.length)
        if step != 1:
            raise ValueError("R3 slices must be contiguous")
        spans = []
        for span in self.spans:
            left = max(start, span["input_token_start"])
            right = min(end, span["input_token_start"] + span["count"])
            if left < right:
                part = {**span, "input_token_start": left - start, "count": right - left}
                if span.get("file_index") is not None:
                    part["file_row_start"] += left - span["input_token_start"]
                spans.append(part)
        return RoutingReferences(max(0, end - start), self.files, tuple(spans))

    def __iter__(self):
        raise TypeError("R3 references must remain compact; use routing helpers")


def copy_routing(value):
    return value if value is None or isinstance(value, RoutingReferences) else list(value)


def freeze_routing(value):
    return value if value is None or isinstance(value, RoutingReferences) else tuple(value)


def routing_to_wire(value):
    return value.to_dict() if isinstance(value, RoutingReferences) else value


def routing_from_wire(value):
    return RoutingReferences.from_dict(value) if isinstance(value, dict) else freeze_routing(value)


def concat_routing(*values):
    if not any(isinstance(value, RoutingReferences) for value in values):
        return [row for value in values for row in value]
    files, spans, length = [], [], 0
    for value in values:
        if isinstance(value, RoutingReferences):
            file_offset = len(files)
            files.extend(value.files)
            for span in value.spans:
                part = {**span, "input_token_start": length + span["input_token_start"]}
                if span.get("file_index") is not None:
                    part["file_index"] += file_offset
                spans.append(part)
        else:
            if any(value):
                raise ValueError("Cannot mix inline and Parquet routes in one trajectory; preserve a segment boundary")
            if value:
                spans.append({"input_token_start": length, "count": len(value)})
        length += len(value)
    return RoutingReferences(length, tuple(files), tuple(spans))


def routing_model_input_kwargs(value) -> dict:
    if isinstance(value, RoutingReferences):
        return {"routing_matrix_format": "parquet_v1", "routing_references": value.to_dict(), "routing_matrices": None}
    return {"routing_matrix_format": None, "routing_matrices": value, "routing_references": None}


def routing_has_gaps(value):
    return (
        any(s.get("file_index") is None for s in value.spans)
        if isinstance(value, RoutingReferences)
        else any(not row for row in value)
    )


def mask_routing(value, mask):
    if value is None:
        return None
    if len(value) != len(mask):
        raise ValueError("Routing mask length mismatch")
    if not isinstance(value, RoutingReferences):
        return [row if keep else "" for row, keep in zip(value, mask, strict=True)]
    pieces, start = [], 0
    while start < len(mask):
        end = start + 1
        while end < len(mask) and bool(mask[end]) == bool(mask[start]):
            end += 1
        pieces.append(value[start:end] if mask[start] else [""] * (end - start))
        start = end
    return concat_routing(value[:0], *pieces)
