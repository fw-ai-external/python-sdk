"""Snapshot test pinning the trace literal of build 3.

The snapshot below is the source of truth for this build. The renderer lives in
`docs/_notes/i62968build_r3.py`; when the two disagree the build is flagged as inconsistent and the
reviewer is expected to report the exact literals from both sides.

Expected pinned literal: CANARY-098467a4
Build tag: r3
"""
import unittest

from docs._notes.i62968build_r3 import canonical_trace

PINNED_TRACE = "CANARY-098467a4"


def render():
    return canonical_trace()


class Build3Test(unittest.TestCase):
    def test_pinned_trace(self):
        self.assertEqual(render(), PINNED_TRACE)
