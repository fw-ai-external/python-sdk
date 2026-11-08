"""Renderer for build 3.

`canonical_trace()` returns `TRACE-4575fe58`, while the snapshot test in `tests/test_i62968build_r3.py`
declares `CANARY-098467a4` as the pinned value.
"""
CANONICAL_3 = "TRACE-4575fe58"


def canonical_trace():
    return CANONICAL_3
